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
  const { pdfBase64 } = req.body || {}
  if (!pdfBase64) {
    res.status(400).json({ error: 'Nenhum PDF recebido.' })
    return
  }
  try {
    const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-5',
        max_tokens: 2000,
        messages: [{
          role: 'user',
          content: [
            { type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: pdfBase64 } },
            { type: 'text', text: 'Extraia todas as avaliacoes, provas e trabalhos deste calendario escolar. Retorne APENAS um JSON array com objetos: {"data":"DD/MM","tipo":"emoji + nome da materia + tipo (AV1/AV2/etc)","obs":"conteudo resumido","feito":false}. Ordene por data. Sem texto extra, sem markdown, apenas o JSON array.' }
          ]
        }]
      })
    })
    const data = await anthropicResp.json()
    if (!anthropicResp.ok) {
      res.status(502).json({ error: data?.error?.message || 'Erro ao consultar a IA.' })
      return
    }
    const text = (data.content?.[0]?.text || '').replace(/```json|```/g, '').trim()
    const avaliacoes = JSON.parse(text)
    res.status(200).json({ avaliacoes })
  } catch (err) {
    res.status(500).json({ error: 'Falha ao processar o PDF: ' + (err?.message || 'erro desconhecido') })
  }
}
