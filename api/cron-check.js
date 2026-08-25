import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, buscaEfetivaFamiliaPorDia, minutosAntesStr, planoTreinoDoDia, normalizarAval, diasRestantesAval, calcularAutonomiaTirzepatida } from './_cronlib.js'

function dataIsoBR() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date())
}

function horaAgoraBR() {
  const partes = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).formatToParts(new Date())
  const h = Number(partes.find((p) => p.type === 'hour')?.value || '0')
  const m = Number(partes.find((p) => p.type === 'minute')?.value || '0')
  return h * 60 + m
}

function paraMinutos(hhmm) {
  const m = /^(\d{1,2}):(\d{2})$/.exec((hhmm || '').trim())
  if (!m) return null
  return Number(m[1]) * 60 + Number(m[2])
}

const JANELA_MIN = 15

export default async function handler(req, res) {
  if (!verificarCron(req)) {
    res.status(401).json({ error: 'Nao autorizado.' })
    return
  }
  const numero = getDeniseNumber()
  if (!numero) {
    res.status(500).json({ error: 'DENISE_WHATSAPP_NUMBER nao configurada.' })
    return
  }
  const supabase = getSupabaseAdmin()
  if (!supabase) {
    res.status(500).json({ error: 'Supabase nao configurado.' })
    return
  }
  try {
    const hojeIso = dataIsoBR()
    const agoraMin = horaAgoraBR()
    const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()

    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}
    const rotina = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
    const doneHoje = Array.isArray(d[`dos_rotina_done_${hojeIso}`]) ? d[`dos_rotina_done_${hojeIso}`] : []
    const medicamentos = d.dos_medicamentos || {}
    const agenda = Array.isArray(d.dos_agenda) ? d.dos_agenda : []

    function estaNaJanela(hhmm) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      return min <= agoraMin && min > agoraMin - JANELA_MIN
    }

    function estaNaJanelaAntecedencia(hhmm, minAntes) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      const alvo = min - minAntes
      return alvo <= agoraMin && alvo > agoraMin - JANELA_MIN
    }

    // Lembrete uma vez no horario, depois cobranca a cada `cadenciaMin` (padrao 3h) ate o corte (se ainda nao feito).
    function lembraOuCobra(hhmm, corteMin, cadenciaMin = 180) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      if (agoraMin < min || agoraMin >= corteMin) return false
      return (agoraMin - min) % cadenciaMin < JANELA_MIN
    }

    const avisos = []

    rotina.forEach((item, i) => {
      if (item.dias && !item.dias.includes(diaSemanaHoje)) return
      if (doneHoje.includes(i)) return
      if (lembraOuCobra(item.t, 22 * 60)) avisos.push(`⏰ ${item.t} · ${item.n}`)
    })

    Object.keys(medicamentos).forEach((pessoaId) => {
      const lista = Array.isArray(medicamentos[pessoaId]) ? medicamentos[pessoaId] : []
      lista.forEach((m) => {
        if (m.ate && m.ate < hojeIso) return
        const horarios = (m.horarios || '').split(',').map((h) => h.trim()).filter(Boolean)
        horarios.forEach((h) => {
          if (!estaNaJanela(h)) return
          const quem = pessoaId === 'denise' ? '' : ` (${pessoaId === 'flavio' ? 'Flávio' : pessoaId})`
          avisos.push(`💊 ${h} · ${m.nome}${m.dosagem ? ` ${m.dosagem}` : ''}${quem}`)
        })
      })
    })

    agenda.forEach((ev) => {
      if (ev.data !== hojeIso || ev.ehMestre) return
      const lembretes = Array.isArray(ev.lembretes) && ev.lembretes.length > 0 ? ev.lembretes : [0]
      lembretes.forEach((min) => {
        if (min === 0) {
          if (estaNaJanela(ev.hora)) avisos.push(`📅 ${ev.hora} · ${ev.nome}`)
        } else if (ev.hora && estaNaJanelaAntecedencia(ev.hora, min)) {
          const antecedencia = min >= 60 ? `${Math.round(min / 60)}h` : `${min} min`
          avisos.push(`⏳ Em ${antecedencia}: ${ev.hora} · ${ev.nome}`)
        }
      })
    })

    const eventosGoogleHoje = await fetchGoogleCalendarEventos(supabase, `${hojeIso}T00:00:00-03:00`, `${hojeIso}T23:59:59-03:00`).catch(() => [])
    eventosGoogleHoje.forEach((ev) => {
      if (!ev.start?.dateTime) return
      const hora = horaLocalBR(ev.start.dateTime)
      const titulo = ev.summary || '(sem título)'
      if (estaNaJanela(hora)) avisos.push(`📅 ${hora} · ${titulo} (Google Agenda)`)
      else if (estaNaJanelaAntecedencia(hora, 60)) avisos.push(`⏳ Em 1h: ${hora} · ${titulo} (Google Agenda)`)
    })

    ;['domi', 'derick'].forEach((kid) => {
      const efet = buscaEfetivaFamiliaPorDia(d, kid, hojeIso, diaSemanaHoje)
      if (efet.semAula || !efet.horario || efet.responsavel !== 'denise') return
      const horaSair = minutosAntesStr(efet.horario, 15)
      if (estaNaJanela(horaSair)) {
        const nomeKid = kid === 'domi' ? 'Domi' : 'Derick'
        avisos.push(`🚗 Sair agora para buscar a ${nomeKid} (sai da escola às ${efet.horario})`)
      }
    })

    const META_AGUA_ML = Number(d.dos_meta_agua_ml || 2500)
    const aguaLog = d.dos_agua_log || {}
    const aguaHojeMl = Number(aguaLog[hojeIso] || 0)
    const horaAgora = Math.floor(agoraMin / 60)
    const minutoDentroHora = agoraMin % 60
    if (aguaHojeMl < META_AGUA_ML && horaAgora >= 7 && horaAgora <= 22 && minutoDentroHora < JANELA_MIN) {
      avisos.push(`💧 Hidratação — ${aguaHojeMl} ml de ${META_AGUA_ML} ml hoje (água, chimarrão, suco, água com gás contam)`)
    }

    const planoTreinoHoje = planoTreinoDoDia(d, diaSemanaHoje)
    const treinos = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
    const treinoRegistradoHoje = treinos.some((t) => t.data === hojeIso) || d[`dos_treino_registrado_${hojeIso}`]
    let criarPendenteTreino = false
    if (planoTreinoHoje && !planoTreinoHoje.descanso && !treinoRegistradoHoje && lembraOuCobra('12:00', 21 * 60 + 30)) {
      avisos.push(`🏋️ Treino de hoje (${planoTreinoHoje.nome}) — já fez ou não? Me conta pra eu registrar.`)
      criarPendenteTreino = true
    }

    const leituras = Array.isArray(d.dos_leituras) ? d.dos_leituras : []
    const leituraFeitaHoje = leituras.some((l) => l.data === hojeIso)
    if (!leituraFeitaHoje && lembraOuCobra('21:00', 23 * 60)) {
      const livroAtual = d.dos_livro_atual || null
      const nomeLivro = livroAtual?.titulo ? ` — "${livroAtual.titulo}"` : ''
      avisos.push(`📖 Hora da leitura (20 min)${nomeLivro}. Registre quantas páginas leu e onde parou.`)
    }

    const casaItens = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
    const contasUrgentes = casaItens.filter((i) => i.cat === 'Contas' && !i.done && i.venc && i.venc <= hojeIso)
    if (contasUrgentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
      const detalheContas = contasUrgentes.map((c) => `${c.n}${typeof c.valor === 'number' ? ` (R$ ${c.valor.toFixed(2)})` : ''}${c.venc < hojeIso ? ' — atrasada' : ' — vence hoje'}`).join(', ')
      avisos.push(`💸 Conta(s) precisando de atenção: ${detalheContas}. Me avise quando pagar.`)
    }
    const idsContasUrgentes = new Set(contasUrgentes.map((i) => i.id))
    const casaPendenteHoje = casaItens.filter((i) => !i.done && !idsContasUrgentes.has(i.id))
    if (casaPendenteHoje.length > 0 && lembraOuCobra('12:00', 21 * 60)) {
      avisos.push(`🏠 Pendente na Casa: ${casaPendenteHoje.map((i) => i.n).join(', ')}. Já fez alguma coisa? Me conta pra eu registrar.`)
    }

    const avalsBrutas = d.dos_avals || {}
    const provasProximas = Object.keys(avalsBrutas).flatMap((kid) =>
      (Array.isArray(avalsBrutas[kid]) ? avalsBrutas[kid] : [])
        .map(normalizarAval)
        .filter((a) => a.status !== 'realizado')
        .map((a) => ({ crianca: kid, materia: a.materia, tipo: a.tipoAvaliacao, dias: diasRestantesAval(a.data) }))
    ).filter((a) => a.dias === 0 || a.dias === 1)
    if (provasProximas.length > 0 && lembraOuCobra('08:00', 21 * 60)) {
      const nomeKidLabel = { domi: 'Domi', derick: 'Derick' }
      const detalheProvas = provasProximas.map((p) => `${p.materia}${p.tipo ? ` (${p.tipo})` : ''} — ${nomeKidLabel[p.crianca] || p.crianca}, ${p.dias === 0 ? 'hoje' : 'amanhã'}`).join('; ')
      avisos.push(`📝 Prova ${provasProximas.some((p) => p.dias === 0) ? 'hoje' : 'chegando'}: ${detalheProvas}`)
    }

    const amanhaIso = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date(Date.now() + 86400000))
    const consultasBrutas = d.dos_consuls || {}
    const consultasProximas = Object.keys(consultasBrutas).flatMap((kid) =>
      (Array.isArray(consultasBrutas[kid]) ? consultasBrutas[kid] : [])
        .filter((c) => c.data === hojeIso || c.data === amanhaIso)
        .map((c) => ({ crianca: kid, tipo: c.tipo, hoje: c.data === hojeIso }))
    )
    if (consultasProximas.length > 0 && lembraOuCobra('08:00', 21 * 60)) {
      const nomeKidLabelConsulta = { domi: 'Domi', derick: 'Derick' }
      const detalheConsultas = consultasProximas.map((c) => `${c.tipo} — ${nomeKidLabelConsulta[c.crianca] || c.crianca}, ${c.hoje ? 'hoje' : 'amanhã'}`).join('; ')
      avisos.push(`🏥 Consulta médica ${consultasProximas.some((c) => c.hoje) ? 'hoje' : 'chegando'}: ${detalheConsultas}`)
    }

    {
      const [{ data: aplicacoesHoje }, { data: schedRows }] = await Promise.all([
        supabase.from('tirzepatida_applications').select('person,applied_at').gte('applied_at', `${hojeIso}T00:00:00`).lte('applied_at', `${hojeIso}T23:59:59`),
        supabase.from('tirzepatida_schedule').select('person,planned_dose_mg,next_application_date')
      ])
      const jaAplicou = new Set((aplicacoesHoje || []).map((a) => a.person))
      const doses = {}
      const proximaData = {}
      ;(schedRows || []).forEach((r) => { doses[r.person] = r.planned_dose_mg; proximaData[r.person] = r.next_application_date })
      const pendentes = ['denise', 'flavio'].filter((p) => !jaAplicou.has(p) && doses[p] && proximaData[p] === hojeIso)
      if (pendentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
        const nomes = pendentes.map((p) => `${p === 'denise' ? 'sua' : 'do Flávio'} (${doses[p]}mg)`).join(' e ')
        avisos.push(`💉 Hoje é dia de aplicar a tirzepatida — falta registrar a aplicação ${nomes}. Me avise quando aplicar.`)
      }
    }

    {
      const [{ data: tzSchedRows }, { data: tzBal }] = await Promise.all([
        supabase.from('tirzepatida_schedule').select('person,planned_dose_mg,interval_days'),
        supabase.from('tirzepatida_stock_balance').select('current_balance_mg').maybeSingle()
      ])
      const tzMap = {}
      ;(tzSchedRows || []).forEach((r) => { tzMap[r.person] = { planned_dose_mg: r.planned_dose_mg, interval_days: r.interval_days } })
      const saldoAtualMg = Number(tzBal?.current_balance_mg ?? 0)
      const autonomiaDias = calcularAutonomiaTirzepatida(tzMap, saldoAtualMg)
      if (autonomiaDias !== null && autonomiaDias <= 7 && estaNaJanela('10:00')) {
        avisos.push(`📦 Estoque de tirzepatida acabando: dá pra ~${autonomiaDias} dia${autonomiaDias === 1 ? '' : 's'} no ritmo atual (${saldoAtualMg}mg restantes). Bom repor.`)
      }
    }

    if (avisos.length === 0) {
      res.status(200).json({ ok: true, avisos_enviados: 0 })
      return
    }

    if (criarPendenteTreino && (!d.dos_luna_pendente || (Date.now() - (d.dos_luna_pendente.criadoEm || 0)) >= 30 * 60 * 1000)) {
      d.dos_luna_pendente = { tipo: 'treino_pergunta', dados: {}, criadoEm: Date.now() }
      await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    }

    await Promise.all(avisos.map((aviso) => sendWhatsappText(numero, aviso).catch(() => null)))
    res.status(200).json({ ok: true, avisos_enviados: avisos.length })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
