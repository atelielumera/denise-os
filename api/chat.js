export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Metodo nao permitido.' })
    return
  }
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) {
    res.status(500).json({ error: 'ANTHROPIC_API_KEY nao configurada no servidor.' })
    return
  }
  const { message, history, context, images, audio } = req.body || {}

  try {
    let userText = (message || '').trim()

    if (audio && audio.base64) {
      const geminiKey = process.env.GEMINI_API_KEY
      if (!geminiKey) {
        res.status(500).json({ error: 'GEMINI_API_KEY nao configurada no servidor (necessaria para audio).' })
        return
      }
      const geminiResp = await fetch(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + geminiKey,
        {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({
            contents: [{
              parts: [
                { text: 'Transcreva este audio em portugues do Brasil. Responda apenas com o texto transcrito, sem comentarios.' },
                { inline_data: { mime_type: audio.mediaType || 'audio/webm', data: audio.base64 } }
              ]
            }]
          })
        }
      )
      const geminiData = await geminiResp.json()
      if (!geminiResp.ok) {
        res.status(502).json({ error: geminiData?.error?.message || 'Erro ao transcrever audio.' })
        return
      }
      const transcript = (geminiData.candidates?.[0]?.content?.parts?.[0]?.text || '').trim()
      if (!transcript) {
        res.status(422).json({ error: 'Nao consegui entender o audio. Pode tentar de novo ou digitar?' })
        return
      }
      userText = userText ? (userText + '\n\n(audio transcrito): ' + transcript) : transcript
    }

    if (!userText && !(images && images.length > 0)) {
      res.status(400).json({ error: 'Nenhuma mensagem recebida.' })
      return
    }

    const systemPrompt = 'Voce e a Luna, assistente pessoal da Denise dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em portugues do Brasil, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - nao puxe lembretes, contas, agenda ou avisos por conta propria. Se ela so cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informacoes do contexto. Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente numeros, datas ou fatos que nao estao ali. Se um dado nao estiver no contexto, diga com naturalidade que ele ainda nao foi registrado no app.\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context || {}, null, 2)

    const historico = Array.isArray(history) ? history.slice(-10).map(m => ({ role: m.me ? 'user' : 'assistant', content: String(m.t || '') })) : []

    const userContent = []
    for (const img of (images || [])) {
      userContent.push({ type: 'image', source: { type: 'base64', media_type: img.mediaType, data: img.base64 } })
    }
    userContent.push({ type: 'text', text: userText || 'A Denise enviou uma imagem sem legenda. Comente o que voce ve e pergunte no que pode ajudar.' })

    const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-5',
        max_tokens: 4096,
        output_config: { effort: 'low' },
        system: systemPrompt,
        messages: [...historico, { role: 'user', content: userContent }]
      })
    })
    const data = await anthropicResp.json()
    if (!anthropicResp.ok) {
      res.status(502).json({ error: data?.error?.message || 'Erro ao consultar a IA.' })
      return
    }
    const reply = data.content?.find(b => b.type === 'text')?.text
    if (!reply) {
      res.status(502).json({ error: 'Luna nao gerou texto (stop_reason: ' + (data.stop_reason || '?') + ')' })
      return
    }
    res.status(200).json({ reply, transcript: audio ? userText : undefined })
  } catch (err) {
    res.status(500).json({ error: 'Falha ao falar com a Luna: ' + (err?.message || 'erro desconhecido') })
  }
}
