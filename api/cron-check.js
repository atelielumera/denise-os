import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, BUSCA_DOMI_POR_DIA, PLANO_TREINO_SEMANA } from './_cronlib.js'

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

const JANELA_MIN = 30

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

    // Lembrete uma vez no horario, depois cobranca de hora em hora ate o corte (se ainda nao feito).
    function lembraOuCobra(hhmm, corteMin) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      if (agoraMin < min || agoraMin >= corteMin) return false
      return (agoraMin - min) % 60 < JANELA_MIN
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

    const buscaDomiHoje = BUSCA_DOMI_POR_DIA[diaSemanaHoje]
    if (buscaDomiHoje && estaNaJanela(buscaDomiHoje.sair)) {
      avisos.push(`🚗 Sair agora para buscar a Domi (sai da escola às ${buscaDomiHoje.busca})`)
    }

    const META_AGUA_ML = Number(d.dos_meta_agua_ml || 2500)
    const aguaLog = d.dos_agua_log || {}
    const aguaHojeMl = Number(aguaLog[hojeIso] || 0)
    const horaAgora = Math.floor(agoraMin / 60)
    const minutoDentroHora = agoraMin % 60
    if (aguaHojeMl < META_AGUA_ML && horaAgora >= 7 && horaAgora <= 22 && minutoDentroHora < JANELA_MIN) {
      avisos.push(`💧 Hidratação — ${aguaHojeMl} ml de ${META_AGUA_ML} ml hoje (água, chimarrão, suco, água com gás contam)`)
    }

    const treinoTipoHoje = PLANO_TREINO_SEMANA[diaSemanaHoje]
    const treinos = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
    const treinoRegistradoHoje = treinos.some((t) => t.data === hojeIso) || d[`dos_treino_registrado_${hojeIso}`]
    if (treinoTipoHoje && !treinoRegistradoHoje && lembraOuCobra('12:00', 21 * 60 + 30)) {
      avisos.push(`🏋️ Treino de hoje (${treinoTipoHoje}) — já fez ou não? Me conta pra eu registrar.`)
    }

    const leituras = Array.isArray(d.dos_leituras) ? d.dos_leituras : []
    const leituraFeitaHoje = leituras.some((l) => l.data === hojeIso)
    if (!leituraFeitaHoje && lembraOuCobra('21:00', 23 * 60)) {
      const livroAtual = d.dos_livro_atual || null
      const nomeLivro = livroAtual?.titulo ? ` — "${livroAtual.titulo}"` : ''
      avisos.push(`📖 Hora da leitura (20 min)${nomeLivro}. Registre quantas páginas leu e onde parou.`)
    }

    const casaItens = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
    const casaPendenteHoje = casaItens.filter((i) => !i.done)
    if (casaPendenteHoje.length > 0 && lembraOuCobra('12:00', 21 * 60)) {
      avisos.push(`🏠 Pendente na Casa: ${casaPendenteHoje.map((i) => i.n).join(', ')}. Já fez alguma coisa? Me conta pra eu registrar.`)
    }

    if (diaSemanaHoje === 4) {
      const [{ data: aplicacoesHoje }, { data: schedRows }] = await Promise.all([
        supabase.from('tirzepatida_applications').select('person,applied_at').gte('applied_at', `${hojeIso}T00:00:00`).lte('applied_at', `${hojeIso}T23:59:59`),
        supabase.from('tirzepatida_schedule').select('person,planned_dose_mg')
      ])
      const jaAplicou = new Set((aplicacoesHoje || []).map((a) => a.person))
      const doses = {}
      ;(schedRows || []).forEach((r) => { doses[r.person] = r.planned_dose_mg })
      const pendentes = ['denise', 'flavio'].filter((p) => !jaAplicou.has(p) && doses[p])
      if (pendentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
        const nomes = pendentes.map((p) => `${p === 'denise' ? 'sua' : 'do Flávio'} (${doses[p]}mg)`).join(' e ')
        avisos.push(`💉 Hoje é dia de aplicar a tirzepatida — falta registrar a aplicação ${nomes}. Me avise quando aplicar.`)
      }
    }

    if (avisos.length === 0) {
      res.status(200).json({ ok: true, avisos_enviados: 0 })
      return
    }

    const texto = '🔔 Está na hora de:\n\n' + avisos.join('\n')
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true, avisos_enviados: avisos.length })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
