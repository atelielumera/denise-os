import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento } from './_cronlib.js'

const CASA_CATS_VALIDAS = ['Mercado', 'Doméstico', 'Manutenção', 'Contas']
const STATUS_TRABALHO_VALIDOS = ['pendente', 'andamento', 'aguardando', 'concluído']

async function processarComando(number, userText, hojeIso, supabase, d) {
  if (!userText || !supabase) return false
  try {
    const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
    const rotina = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
    const chaveRotinaHoje = `dos_rotina_done_${hojeIso}`
    const doneRotina = Array.isArray(d[chaveRotinaHoje]) ? d[chaveRotinaHoje] : []
    const rotinaPendente = rotina
      .map((it, idx) => ({ idx, horario: it.t, nome: it.n, dias: it.dias }))
      .filter((it) => (!it.dias || it.dias.includes(diaSemanaHoje)) && !doneRotina.includes(it.idx))

    const casaItens = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
    const casaPendente = casaItens.map((it, idx) => ({ idx, nome: it.n, categoria: it.cat, done: it.done })).filter((it) => !it.done)

    const avals = d.dos_avals || {}
    const avalDomi = Array.isArray(avals.domi) ? avals.domi : []
    const avalDerick = Array.isArray(avals.derick) ? avals.derick : []
    const avalDomiPendente = avalDomi.map((a, idx) => ({ idx, data: a.data, tipo: a.tipo })).filter((_, idx) => !avalDomi[idx].feito)
    const avalDerickPendente = avalDerick.map((a, idx) => ({ idx, data: a.data, tipo: a.tipo })).filter((_, idx) => !avalDerick[idx].feito)

    const trabalhoTarefas = Array.isArray(d.dos_trabalho) ? d.dos_trabalho : []
    const trabalhoAbertas = trabalhoTarefas.map((t, idx) => ({ idx, tarefa: t.t, projeto: t.p, status: t.s })).filter((t) => t.status !== 'concluído')

    const livroAtual = d.dos_livro_atual || null

    const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria/i
    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && trabalhoAbertas.length === 0 && !GATE_RE.test(userText)) {
      return false
    }

    const DIAS_NOME = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']
    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos_rotina":[numeros],"feitos_casa":[numeros],"feitos_aval_domi":[numeros],"feitos_aval_derick":[numeros],"novos_casa":[{"nome":"...","categoria":"Mercado|Doméstico|Manutenção|Contas"}],"novos_compromissos":[{"nome":"...","dia_semana":numero de 0 a 6 (0=domingo,1=segunda,2=terca,3=quarta,4=quinta,5=sexta,6=sabado),"horario":"HH:MM"}],"novos_eventos_google":[{"nome":"...","data":"YYYY-MM-DD","hora":"HH:MM ou vazio se o dia todo"}],"tirzepatida_aplicada":{"pessoa":"denise|flavio"}|null,"trabalho_status":[{"id":numero,"novo_status":"pendente|andamento|aguardando|concluído"}],"leitura_registrada":{"paginas":numero|null,"minutos":numero|null,"parou_na_pagina":numero|null}|null,"treino_registrado":{"feito":true|false}|null,"devocional_resposta":"texto"|null,"agua_ml":numero|null,"proteina_g_avulsa":numero|null,"refeicao":{"tipo":"Café da manhã|Lanche|Almoço|Lanche da tarde|Jantar|Ceia|Outro","descricao":"...","proteina_g":numero|null,"calorias":numero|null}|null}. Hoje e ' + hojeIso + ' (' + DIAS_NOME[diaSemanaHoje] + '). A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '".\n\nRotina de hoje ainda pendente (id, horario, nome): ' + JSON.stringify(rotinaPendente.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '\nItens pendentes da Casa (id, nome, categoria): ' + JSON.stringify(casaPendente.map((p) => ({ id: p.idx, nome: p.nome, categoria: p.categoria }))) + '\nAvaliações pendentes da Domi (id, data, tipo): ' + JSON.stringify(avalDomiPendente) + '\nAvaliações pendentes do Derick (id, data, tipo): ' + JSON.stringify(avalDerickPendente) + '\nTarefas de trabalho em aberto (id, tarefa, projeto, status atual): ' + JSON.stringify(trabalhoAbertas) + '\nLivro que ela esta lendo agora: ' + JSON.stringify(livroAtual) + '\n\nRegras: Se a mensagem confirmar que ela fez algo dessas listas (ex: "ja fiz X", "paguei a luz", "registrei a prova de matematica da domi"), coloque os ids certos no campo correspondente. Se for lista de compras/tarefas novas pra Casa, coloque em novos_casa. Se pedir compromisso recorrente (toda segunda/terca/etc) na rotina, coloque em novos_compromissos. Se pedir para marcar/inserir uma reuniao, evento ou compromisso em uma DATA especifica (nao recorrente, ex: "marca reuniao com fulano dia 25 as 14h", "coloca consulta do dentista sexta que vem"), resolva a data relativa usando hoje=' + hojeIso + ' e coloque em novos_eventos_google (nome, data no formato YYYY-MM-DD, hora se houver). Se ela disser que aplicou a tirzepatida (dela ou do Flavio; se nao especificar a pessoa, assuma "denise"), preencha tirzepatida_aplicada. Se ela mencionar mudanca de status de alguma tarefa de trabalho (ex: "a tarefa X esta concluida", "comecei a tarefa Y", "Z esta aguardando resposta"), ache o id certo na lista de tarefas em aberto e coloque em trabalho_status. Se ela disser quantas paginas leu, quantos minutos leu, ou em que pagina parou, preencha leitura_registrada (campos que ela nao mencionou ficam null). Se ela disser que fez o treino de hoje ou que NAO fez o treino hoje, preencha treino_registrado. Se a mensagem for uma resposta as perguntas do devocional (reflexao sobre mandamento, promessa, pecado, aplicacao, algo novo sobre Deus, ou quem/o que/quando/onde/por que), coloque o texto completo da resposta dela em devocional_resposta. Se ela disser que bebeu ou tomou uma quantidade de agua, cha, suco ou agua com gas (ex: \'tomei 300ml de agua\', \'bebi um copo dagua\', \'tomei uma garrafa\'), converta para mililitros (copo comum ~200ml, garrafa comum ~500ml se ela nao especificar) e preencha agua_ml. Se ela mencionar uma quantidade de proteina avulsa sem descrever uma refeicao completa (ex: \'tomei um shake de 20g de proteina\', \'bati um whey\'), preencha proteina_g_avulsa. Se ela disser que comeu, almocou, jantou, lanchou ou tomou cafe da manha descrevendo o que comeu, preencha refeicao com o tipo mais proximo, a descricao do que ela comeu, e proteina_g/calorias somente se ela mencionar (senao null). Se nada de uma categoria se aplicar, deixe vazio/null nela.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\{[\s\S]*\}/)
    const parsed = match ? JSON.parse(match[0]) : {}

    const feitosRotina = Array.isArray(parsed.feitos_rotina) ? parsed.feitos_rotina.filter((n) => typeof n === 'number' && rotinaPendente.some((p) => p.idx === n)) : []
    const feitosCasa = Array.isArray(parsed.feitos_casa) ? parsed.feitos_casa.filter((n) => typeof n === 'number' && casaPendente.some((p) => p.idx === n)) : []
    const feitosAvalDomi = Array.isArray(parsed.feitos_aval_domi) ? parsed.feitos_aval_domi.filter((n) => typeof n === 'number' && avalDomiPendente.some((p) => p.idx === n)) : []
    const feitosAvalDerick = Array.isArray(parsed.feitos_aval_derick) ? parsed.feitos_aval_derick.filter((n) => typeof n === 'number' && avalDerickPendente.some((p) => p.idx === n)) : []
    const novosCasa = Array.isArray(parsed.novos_casa) ? parsed.novos_casa.filter((n) => n && n.nome) : []
    const novosCompromissos = Array.isArray(parsed.novos_compromissos) ? parsed.novos_compromissos.filter((n) => n && n.nome && typeof n.dia_semana === 'number' && n.dia_semana >= 0 && n.dia_semana <= 6 && /^\d{1,2}:\d{2}$/.test(n.horario || '')) : []
    const novosEventosGoogle = Array.isArray(parsed.novos_eventos_google) ? parsed.novos_eventos_google.filter((n) => n && n.nome && /^\d{4}-\d{2}-\d{2}$/.test(n.data || '')) : []
    const tirzepatidaAplicada = parsed.tirzepatida_aplicada && ['denise', 'flavio'].includes(parsed.tirzepatida_aplicada.pessoa) ? parsed.tirzepatida_aplicada : null
    const trabalhoStatus = Array.isArray(parsed.trabalho_status) ? parsed.trabalho_status.filter((n) => n && typeof n.id === 'number' && trabalhoAbertas.some((p) => p.idx === n.id) && STATUS_TRABALHO_VALIDOS.includes(n.novo_status)) : []
    const leituraRegistrada = parsed.leitura_registrada && (parsed.leitura_registrada.paginas || parsed.leitura_registrada.minutos || parsed.leitura_registrada.parou_na_pagina) ? parsed.leitura_registrada : null
    const treinoRegistrado = parsed.treino_registrado && typeof parsed.treino_registrado.feito === 'boolean' ? parsed.treino_registrado : null
    const devocionalResposta = typeof parsed.devocional_resposta === 'string' && parsed.devocional_resposta.trim() ? parsed.devocional_resposta.trim() : null
    const aguaMlAdicionada = typeof parsed.agua_ml === 'number' && parsed.agua_ml > 0 && parsed.agua_ml <= 3000 ? Math.round(parsed.agua_ml) : null
    const proteinaAvulsaG = typeof parsed.proteina_g_avulsa === 'number' && parsed.proteina_g_avulsa > 0 && parsed.proteina_g_avulsa <= 300 ? Math.round(parsed.proteina_g_avulsa) : null
    const TIPOS_REFEICAO_VALIDOS = ['Café da manhã', 'Lanche', 'Almoço', 'Lanche da tarde', 'Jantar', 'Ceia', 'Outro']
    const refeicaoRegistrada = parsed.refeicao && typeof parsed.refeicao.descricao === 'string' && parsed.refeicao.descricao.trim() && TIPOS_REFEICAO_VALIDOS.includes(parsed.refeicao.tipo) ? parsed.refeicao : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada) {
      return false
    }

    const partesConfirmacao = []

    if (feitosRotina.length > 0) {
      const uniao = Array.from(new Set([...doneRotina, ...feitosRotina]))
      d[chaveRotinaHoje] = uniao
      partesConfirmacao.push('✅ Marquei como feito: ' + rotinaPendente.filter((p) => feitosRotina.includes(p.idx)).map((p) => p.nome).join(', '))
    }

    let casaAtualizada = casaItens
    if (feitosCasa.length > 0) {
      casaAtualizada = casaAtualizada.map((c, idx) => (feitosCasa.includes(idx) ? { ...c, done: true } : c))
      partesConfirmacao.push('✅ Marquei como feito na Casa: ' + casaPendente.filter((p) => feitosCasa.includes(p.idx)).map((p) => p.nome).join(', '))
    }
    if (novosCasa.length > 0) {
      const adicionados = novosCasa.map((n) => ({ n: n.nome, cat: CASA_CATS_VALIDAS.includes(n.categoria) ? n.categoria : 'Mercado', done: false }))
      casaAtualizada = [...casaAtualizada, ...adicionados]
      partesConfirmacao.push('🛒 Adicionei na Casa: ' + adicionados.map((a) => a.n).join(', '))
    }
    if (feitosCasa.length > 0 || novosCasa.length > 0) d.dos_casa_items = casaAtualizada

    if (feitosAvalDomi.length > 0 || feitosAvalDerick.length > 0) {
      const novosAvals = { ...avals }
      if (feitosAvalDomi.length > 0) {
        novosAvals.domi = avalDomi.map((a, idx) => (feitosAvalDomi.includes(idx) ? { ...a, feito: true } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação da Domi: ' + avalDomiPendente.filter((p) => feitosAvalDomi.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      if (feitosAvalDerick.length > 0) {
        novosAvals.derick = avalDerick.map((a, idx) => (feitosAvalDerick.includes(idx) ? { ...a, feito: true } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação do Derick: ' + avalDerickPendente.filter((p) => feitosAvalDerick.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      d.dos_avals = novosAvals
    }

    if (novosCompromissos.length > 0) {
      const rotinaAtual = Array.isArray(d.dos_rotina) ? d.dos_rotina : rotina
      const adicionados = novosCompromissos.map((n) => ({ t: n.horario, n: n.nome, cat: 'Compromisso', dias: [n.dia_semana] }))
      d.dos_rotina = [...rotinaAtual, ...adicionados]
      partesConfirmacao.push('📅 Adicionei na sua rotina: ' + adicionados.map((a) => `${a.n} toda ${DIAS_NOME[a.dias[0]]} às ${a.t}`).join(', '))
    }

    if (novosEventosGoogle.length > 0) {
      const agendaAtual = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
      const adicionadosAgenda = []
      for (const ev of novosEventosGoogle) {
        adicionadosAgenda.push({ data: ev.data, hora: ev.hora || '', nome: ev.nome, cor: '#38bdf8' })
        await insertGoogleCalendarEvento(supabase, { nome: ev.nome, data: ev.data, hora: ev.hora || '' }).catch(() => null)
      }
      d.dos_agenda = [...agendaAtual, ...adicionadosAgenda].sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))
      partesConfirmacao.push('📅 Marquei na sua agenda (e no Google Agenda): ' + adicionadosAgenda.map((a) => `${a.nome} em ${a.data}${a.hora ? ' às ' + a.hora : ''}`).join(', '))
    }

    if (tirzepatidaAplicada) {
      try {
        const { data: jaHoje } = await supabase.from('tirzepatida_applications').select('id').eq('person', tirzepatidaAplicada.pessoa).gte('applied_at', `${hojeIso}T00:00:00`).lte('applied_at', `${hojeIso}T23:59:59`).maybeSingle()
        if (jaHoje) {
          const quemJa = tirzepatidaAplicada.pessoa === 'denise' ? 'Sua aplicação' : 'A aplicação do Flávio'
          partesConfirmacao.push(`💉 ${quemJa} de hoje já estava registrada — não registrei de novo pra não duplicar no estoque.`)
        } else {
          const { data: schedRow } = await supabase.from('tirzepatida_schedule').select('planned_dose_mg').eq('person', tirzepatidaAplicada.pessoa).maybeSingle()
          const doseMg = Number(schedRow?.planned_dose_mg || 0)
          if (doseMg > 0) {
            const appliedAt = new Date().toISOString()
            const { error } = await supabase.rpc('tirze_apply_dose', { p_person: tirzepatidaAplicada.pessoa, p_applied_at: appliedAt, p_dose_mg: doseMg })
            if (!error) {
              const { data: bal } = await supabase.from('tirzepatida_stock_balance').select('*').maybeSingle()
              const quem = tirzepatidaAplicada.pessoa === 'denise' ? 'sua' : 'do Flávio'
              partesConfirmacao.push(`💉 Registrei a aplicação ${quem} (${doseMg}mg). Estoque atualizado: ${Number(bal?.current_balance_mg ?? 0)}mg restantes.`)
            }
          }
        }
      } catch { /* nao bloqueia o resto */ }
    }

    if (trabalhoStatus.length > 0) {
      const novasTarefas = trabalhoTarefas.map((t, idx) => {
        const alteracao = trabalhoStatus.find((s) => s.id === idx)
        return alteracao ? { ...t, s: alteracao.novo_status } : t
      })
      d.dos_trabalho = novasTarefas
      partesConfirmacao.push('💼 Atualizei o status: ' + trabalhoStatus.map((s) => `"${trabalhoAbertas.find((t) => t.idx === s.id)?.tarefa}" → ${s.novo_status}`).join(', '))
    }

    if (leituraRegistrada) {
      const leiturasAtuais = Array.isArray(d.dos_leituras) ? d.dos_leituras : []
      const paginasLidas = Number(leituraRegistrada.paginas || 0)
      const reg = { data: hojeIso, pag: paginasLidas, min: Number(leituraRegistrada.minutos || 0), apren: '' }
      d.dos_leituras = [reg, ...leiturasAtuais]
      if (livroAtual && livroAtual.totalPaginas > 0) {
        const novaPagina = leituraRegistrada.parou_na_pagina != null ? Math.min(livroAtual.totalPaginas, Number(leituraRegistrada.parou_na_pagina)) : Math.min(livroAtual.totalPaginas, Number(livroAtual.paginaAtual || 0) + paginasLidas)
        d.dos_livro_atual = { ...livroAtual, paginaAtual: novaPagina }
        partesConfirmacao.push(`📖 Leitura registrada! Você parou na página ${novaPagina} de ${livroAtual.totalPaginas}.`)
      } else {
        partesConfirmacao.push('📖 Leitura registrada!')
      }
    }

    if (treinoRegistrado) {
      if (treinoRegistrado.feito) {
        const treinosAtuais = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
        d.dos_treinos = [{ data: hojeIso, tipo: 'Registrado via WhatsApp', duracaoMin: 0 }, ...treinosAtuais]
        partesConfirmacao.push('✅ Treino de hoje registrado como feito!')
      } else {
        partesConfirmacao.push('Ok, registrei que hoje não deu pra treinar. Sem culpa, amanhã tem mais.')
      }
      d[`dos_treino_registrado_${hojeIso}`] = true
    }

    if (devocionalResposta) {
      const devocionaisAtuais = Array.isArray(d.dos_devocionais) ? d.dos_devocionais : []
      const outros = devocionaisAtuais.filter((e) => e.data !== hojeIso)
      const existenteHoje = devocionaisAtuais.find((e) => e.data === hojeIso) || {}
      const reg = { ...existenteHoje, data: hojeIso, reflex: devocionalResposta }
      d.dos_devocionais = [reg, ...outros].sort((a, b) => b.data.localeCompare(a.data))
      partesConfirmacao.push('🙏 Devocional de hoje registrado no seu histórico!')
    }

    if (aguaMlAdicionada) {
      const aguaLogAtual = d.dos_agua_log || {}
      const aguaHojeAtualMl = Number(aguaLogAtual[hojeIso] || 0)
      const novaAguaMl = Math.min(aguaHojeAtualMl + aguaMlAdicionada, 6000)
      d.dos_agua_log = { ...aguaLogAtual, [hojeIso]: novaAguaMl }
      partesConfirmacao.push(`💧 Registrei +${aguaMlAdicionada}ml de água. Total hoje: ${novaAguaMl}ml.`)
    }

    if (proteinaAvulsaG || refeicaoRegistrada) {
      const horaAgoraHHMM = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).format(new Date())
      const refsLogAtual = d.dos_refs_log || {}
      let refsHojeAtual = Array.isArray(refsLogAtual[hojeIso]) ? refsLogAtual[hojeIso] : []
      if (proteinaAvulsaG) {
        refsHojeAtual = [{ id: `${Date.now()}_wa1`, tipo: 'Rápido', nome: 'Proteína (registro rápido)', prot: proteinaAvulsaG, hora: horaAgoraHHMM, origem: 'whatsapp' }, ...refsHojeAtual]
        partesConfirmacao.push(`🥩 Registrei +${proteinaAvulsaG}g de proteína.`)
      }
      if (refeicaoRegistrada) {
        const novaRef = { id: `${Date.now()}_wa2`, tipo: refeicaoRegistrada.tipo, nome: refeicaoRegistrada.descricao, prot: typeof refeicaoRegistrada.proteina_g === 'number' ? refeicaoRegistrada.proteina_g : undefined, cal: typeof refeicaoRegistrada.calorias === 'number' ? refeicaoRegistrada.calorias : undefined, hora: horaAgoraHHMM, origem: 'whatsapp' }
        refsHojeAtual = [novaRef, ...refsHojeAtual]
        partesConfirmacao.push(`🍽️ Registrei: ${refeicaoRegistrada.descricao}${novaRef.prot ? ` (${novaRef.prot}g proteína)` : ''}.`)
      }
      d.dos_refs_log = { ...refsLogAtual, [hojeIso]: refsHojeAtual }
    }

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    await sendWhatsappText(number, partesConfirmacao.join('\n'))
    return true
  } catch {
    return false
  }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(200).json({ ok: true })
    return
  }
  try {
    const body = req.body || {}
    const event = body.event || ''
    if (event && !/messages\.?upsert/i.test(event)) {
      res.status(200).json({ ok: true })
      return
    }

    const data = body.data || {}
    const key = data.key || {}
    if (key.fromMe) {
      res.status(200).json({ ok: true })
      return
    }
    const remoteJid = key.remoteJid || ''
    if (!remoteJid || remoteJid.endsWith('@g.us')) {
      res.status(200).json({ ok: true })
      return
    }
    const number = remoteJid.split('@')[0].split(':')[0]

    function normalizarNumeroBR(n) {
      const d = String(n || '').replace(/\D/g, '')
      return (d.length === 13 && d.startsWith('55') && d[4] === '9') ? d.slice(0, 4) + d.slice(5) : d
    }
    const allowed = (process.env.EVOLUTION_ALLOWED_NUMBERS || '').split(',').map((s) => s.trim()).filter(Boolean)
    if (allowed.length && !allowed.map(normalizarNumeroBR).includes(normalizarNumeroBR(number))) {
      res.status(200).json({ ok: true })
      return
    }

    const msg = data.message || {}
    let userText = (msg.conversation || msg.extendedTextMessage?.text || '').trim()

    if (msg.audioMessage && data.message.base64) {
      try {
        const transcript = await transcribeAudio(data.message.base64, msg.audioMessage.mimetype || 'audio/ogg')
        userText = userText ? (userText + '\n\n(audio transcrito): ' + transcript) : transcript
      } catch {
        await sendWhatsappText(number, 'Recebi seu áudio mas não consegui entender agora. Pode tentar de novo ou escrever?')
        res.status(200).json({ ok: true })
        return
      }
    }

    const userContent = []
    if (msg.imageMessage && data.message.base64) {
      userContent.push({ type: 'image', source: { type: 'base64', media_type: msg.imageMessage.mimetype || 'image/jpeg', data: data.message.base64 } })
    }

    if (!userText && userContent.length === 0) {
      res.status(200).json({ ok: true })
      return
    }
    userContent.push({ type: 'text', text: userText || 'A Denise enviou uma imagem sem legenda pelo WhatsApp. Comente o que você vê e pergunte no que pode ajudar.' })

    const context = await buildLunaContext()
    const supabase = getSupabaseAdmin()
    let d = {}
    if (supabase) {
      const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
      d = snap?.data || {}
    }

    if (userText) {
      const processou = await processarComando(number, userText, context.data_hoje, supabase, d)
      if (processou) {
        res.status(200).json({ ok: true })
        return
      }
    }

    const historico = Array.isArray(d.dos_luna_chat) ? d.dos_luna_chat.slice(-20) : []
    const historyMsgs = historico.map((m) => ({ role: m.me ? 'user' : 'assistant', content: String(m.t || '') }))
    while (historyMsgs.length > 0 && historyMsgs[0].role === 'assistant') historyMsgs.shift()

    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent, historyMsgs)
    await sendWhatsappText(number, reply)

    if (supabase) {
      const novoHistorico = [...historico, { me: true, t: userText || '(enviou uma imagem)' }, { me: false, t: reply }].slice(-40)
      await supabase.from('app_snapshot').upsert({ id: 'denise', data: { ...d, dos_luna_chat: novoHistorico }, updated_at: new Date().toISOString() })
    }

    res.status(200).json({ ok: true })
  } catch (err) {
    console.error('Erro no webhook do WhatsApp:', err)
    res.status(200).json({ ok: true })
  }
}
