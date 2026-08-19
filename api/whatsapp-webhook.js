import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt } from './_cronlib.js'

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
    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent)
    await sendWhatsappText(number, reply)
    res.status(200).json({ ok: true })
  } catch {
    res.status(200).json({ ok: true })
  }
}
