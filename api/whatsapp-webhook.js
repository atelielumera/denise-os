import { createClient } from '@supabase/supabase-js'

function getEvoConfig() {
  const baseUrl = (process.env.EVOLUTION_API_URL || '').replace(/\/+$/, '')
  const apiKey = process.env.EVOLUTION_API_KEY
  const instance = process.env.EVOLUTION_INSTANCE || 'denise-os'
  return { baseUrl, apiKey, instance }
}

async function sendWhatsappText(baseUrl, apiKey, instance, number, text) {
  await fetch(`${baseUrl}/message/sendText/${instance}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', apikey: apiKey },
    body: JSON.stringify({ number, text })
  })
}

async function transcribeAudio(base64, mediaType) {
  const geminiKey = process.env.GEMINI_API_KEY
  if (!geminiKey) throw new Error('GEMINI_API_KEY nao configurada.')
  const geminiResp = await fetch(
    'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + geminiKey,
    {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [
            { text: 'Transcreva este audio em portugues do Brasil. Responda apenas com o texto transcrito, sem comentarios.' },
            { inline_data: { mime_type: mediaType || 'audio/ogg', data: base64 } }
          ]
        }]
      })
    }
  )
  const geminiData = await geminiResp.json()
  if (!geminiResp.ok) throw new Error(geminiData?.error?.message || 'Erro ao transcrever audio.')
  return (geminiData.candidates?.[0]?.content?.parts?.[0]?.text || '').trim()
}

async function buildContext() {
  const url = process.env.VITE_SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  const hojeIso = new Date().toISOString().slice(0, 10)
  if (!url || !serviceKey) {
    return { data_hoje: hojeIso, tirzepatida: null }
  }
  const supabase = createClient(url, serviceKey)
  const [{ data: sched }, { data: bal }] = await Promise.all([
    supabase.from('tirzepatida_schedule').select('*'),
    supabase.from('tirzepatida_stock_balance').select('*').maybeSingle()
  ])
  const map = {}
  ;(sched || []).forEach((row) => {
    map[row.person] = { planned_dose_mg: Number(row.planned_dose_mg), interval_days: row.interval_days, next_application_date: row.next_application_date }
  })
  return {
    data_hoje: hojeIso,
    tirzepatida: (sched || []).length > 0 ? { estoque_atual_mg: Number(bal?.current_balance_mg ?? 0), denise: map.denise || null, flavio: map.flavio || null } : null
  }
}

async function askLuna(systemPrompt, userContent) {
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY nao configurada.')
  const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 600,
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }]
    })
  })
  const data = await anthropicResp.json()
  if (!anthropicResp.ok) throw new Error(data?.error?.message || 'Erro ao consultar a IA.')
  return data.content?.find((b) => b.type === 'text')?.text || 'Desculpa, não consegui responder agora.'
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(200).json({ ok: true })
    return
  }
  const { baseUrl, apiKey, instance } = getEvoConfig()
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
    const number = remoteJid.split('@')[0]

    const allowed = (process.env.EVOLUTION_ALLOWED_NUMBERS || '').split(',').map((s) => s.trim()).filter(Boolean)
    if (allowed.length && !allowed.includes(number)) {
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
        await sendWhatsappText(baseUrl, apiKey, instance, number, 'Recebi seu áudio mas não consegui entender agora. Pode tentar de novo ou escrever?')
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

    const context = await buildContext()
    const systemPrompt = 'Você é a Luna, assistente pessoal da Denise, respondendo agora pelo WhatsApp dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em português do Brasil, com respostas curtas (2 a 5 frases). Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente números, datas ou fatos que não estão ali. Se um dado não estiver no contexto, diga com naturalidade que ele ainda não foi registrado no app.\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent)
    await sendWhatsappText(baseUrl, apiKey, instance, number, reply)
    res.status(200).json({ ok: true })
  } catch {
    res.status(200).json({ ok: true })
  }
}
