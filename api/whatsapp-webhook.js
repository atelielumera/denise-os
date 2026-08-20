import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin } from './_cronlib.js'

const CASA_CATS_VALIDAS = ['Mercado', 'Doméstico', 'Manutenção', 'Contas']

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

    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && !/compr|adicion|mercado|lista|coloca|agenda|toda |todo /i.test(userText)) {
      return false
    }

    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos_rotina":[numeros],"feitos_casa":[numeros],"feitos_aval_domi":[numeros],"feitos_aval_derick":[numeros],"novos_casa":[{"nome":"...","categoria":"Mercado|Doméstico|Manutenção|Contas"}],"novos_compromissos":[{"nome":"...","dia_semana":numero de 0 a 6 (0=domingo,1=segunda,2=terca,3=quarta,4=quinta,5=sexta,6=sabado),"horario":"HH:MM"}]}. A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '".\n\nRotina de hoje ainda pendente (id, horario, nome): ' + JSON.stringify(rotinaPendente.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '\nItens pendentes da Casa (id, nome, categoria): ' + JSON.stringify(casaPendente.map((p) => ({ id: p.idx, nome: p.nome, categoria: p.categoria }))) + '\nAvaliações pendentes da Domi (id, data, tipo): ' + JSON.stringify(avalDomiPendente) + '\nAvaliações pendentes do Derick (id, data, tipo): ' + JSON.stringify(avalDerickPendente) + '\n\nSe a mensagem confirmar que ela fez algo dessas listas (ex: "ja fiz X", "paguei a luz", "registrei a prova de matematica da domi"), coloque os ids certos no campo correspondente. Se a mensagem for uma lista de compras ou tarefas novas pra Casa (ex: "compra leite, pao e ovos", "adiciona pagar internet"), coloque cada item novo em novos_casa com nome e a categoria certa (Mercado para compras de supermercado, Contas para contas a pagar, Doméstico para tarefas de casa, Manutenção para consertos). Se a mensagem pedir pra colocar um compromisso recorrente (toda segunda/terca/etc) na agenda/rotina (ex: "coloca toda quinta Culto de mulheres das 13:30 as 16:00"), coloque em novos_compromissos com nome (inclua o horario de termino no nome se houver, ex: "Culto de mulheres (ate 16:00)"), dia_semana e horario de inicio. Se nada disso se aplicar, responda com todos os campos vazios.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\{[\s\S]*\}/)
    const parsed = match ? JSON.parse(match[0]) : {}

    const feitosRotina = Array.isArray(parsed.feitos_rotina) ? parsed.feitos_rotina.filter((n) => typeof n === 'number' && rotinaPendente.some((p) => p.idx === n)) : []
    const feitosCasa = Array.isArray(parsed.feitos_casa) ? parsed.feitos_casa.filter((n) => typeof n === 'number' && casaPendente.some((p) => p.idx === n)) : []
    const feitosAvalDomi = Array.isArray(parsed.feitos_aval_domi) ? parsed.feitos_aval_domi.filter((n) => typeof n === 'number' && avalDomiPendente.some((p) => p.idx === n)) : []
    const feitosAvalDerick = Array.isArray(parsed.feitos_aval_derick) ? parsed.feitos_aval_derick.filter((n) => typeof n === 'number' && avalDerickPendente.some((p) => p.idx === n)) : []
    const novosCasa = Array.isArray(parsed.novos_casa) ? parsed.novos_casa.filter((n) => n && n.nome) : []
    const novosCompromissos = Array.isArray(parsed.novos_compromissos) ? parsed.novos_compromissos.filter((n) => n && n.nome && typeof n.dia_semana === 'number' && n.dia_semana >= 0 && n.dia_semana <= 6 && /^\d{1,2}:\d{2}$/.test(n.horario || '')) : []

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0) {
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
      const DIAS_NOME = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']
      partesConfirmacao.push('📅 Adicionei na sua rotina: ' + adicionados.map((a) => `${a.n} toda ${DIAS_NOME[a.dias[0]]} às ${a.t}`).join(', '))
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
