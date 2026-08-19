import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin } from './_cronlib.js'

async function tentarMarcarFeito(number, userText, context) {
  const pendentes = (context.rotina_de_hoje || []).map((it, idx) => ({ idx, ...it })).filter((it) => !it.feito_hoje)
  if (pendentes.length === 0 || !userText) return false
  try {
    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos":[numeros]}. A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '". Aqui estao os itens da rotina de hoje que AINDA NAO foram marcados como feitos, cada um com seu id: ' + JSON.stringify(pendentes.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '. Se a mensagem confirmar que ela fez um ou mais desses itens agora (ex: "ja fiz o X", "feito", "acabei de Y", "consegui buscar a Domi"), coloque os ids correspondentes em "feitos". Se a mensagem nao for uma confirmacao de tarefa feita (for pergunta, comentario, ou nao bater com nenhum item da lista), responda {"feitos":[]}.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\{[\s\S]*\}/)
    const parsed = match ? JSON.parse(match[0]) : { feitos: [] }
    const feitos = Array.isArray(parsed.feitos) ? parsed.feitos.filter((n) => typeof n === 'number' && pendentes.some((p) => p.idx === n)) : []
    if (feitos.length === 0) return false
    const supabase = getSupabaseAdmin()
    if (!supabase) return false
    const chave = `dos_rotina_done_${context.data_hoje}`
    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}
    const atual = Array.isArray(d[chave]) ? d[chave] : []
    const uniao = Array.from(new Set([...atual, ...feitos]))
    await supabase.from('app_snapshot').upsert({ id: 'denise', data: { ...d, [chave]: uniao }, updated_at: new Date().toISOString() })
    const nomes = pendentes.filter((p) => feitos.includes(p.idx)).map((p) => p.nome)
    await sendWhatsappText(number, '✅ Marquei como feito: ' + nomes.join(', ') + '!')
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

    if (userText) {
      const marcou = await tentarMarcarFeito(number, userText, context)
      if (marcou) {
        res.status(200).json({ ok: true })
        return
      }
    }

    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent)
    await sendWhatsappText(number, reply)
    res.status(200).json({ ok: true })
  } catch (err) {
    console.error('Erro no webhook do WhatsApp:', err)
    res.status(200).json({ ok: true })
  }
}
