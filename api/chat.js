import { getSupabaseAdmin, buildLunaContext, transcribeAudio } from './_cronlib.js'
import { processarComando } from './whatsapp-webhook.js'

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
  const { message, history, images, audio } = req.body || {}

  try {
    let userText = (message || '').trim()

    if (audio && audio.base64) {
      let transcript = ''
      try {
        transcript = await transcribeAudio(audio.base64, audio.mediaType || 'audio/webm')
      } catch (err) {
        res.status(500).json({ error: err?.message || 'Erro ao transcrever audio.' })
        return
      }
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

    const supabase = getSupabaseAdmin()
    const context = await buildLunaContext()

    if (userText && supabase) {
      const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
      const d = snap?.data || {}
      const mensagemAcao = await processarComando(userText, context.data_hoje, supabase, d)
      if (mensagemAcao) {
        res.status(200).json({ reply: mensagemAcao, transcript: audio ? userText : undefined })
        return
      }
    }

    const systemPrompt = 'Voce e a Luna, assistente pessoal da Denise dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em portugues do Brasil, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - nao puxe lembretes, contas, agenda ou avisos por conta propria. Se ela so cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informacoes do contexto. Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente numeros, datas ou fatos que nao estao ali. Se um dado nao estiver no contexto, diga com naturalidade que ele ainda nao foi registrado no app.\n\nSe a Denise pedir para criar, editar, cancelar ou reagendar um evento da agenda: responda normalmente confirmando o que voce entendeu, e ao final da mensagem inclua um bloco cercado por tres crases com a palavra agenda_action seguido do JSON da acao proposta - voce NUNCA executa a acao, o app pede confirmacao antes de aplicar. Formatos: para criar, ```agenda_action\n{"acao":"criar","evento":{"nome":"...","data":"YYYY-MM-DD","hora":"HH:MM","horaFim":"HH:MM","local":"...","descricao":"...","categoria":"pessoal|familia|trabalho|saude|casa"}}\n```; para editar ou excluir, use o id exato de agenda_eventos_editaveis_pela_luna no contexto: ```agenda_action\n{"acao":"editar","id":"...","evento":{"campos alterados apenas"}}\n``` ou ```agenda_action\n{"acao":"excluir","id":"..."}\n```. So os campos hora/data sao obrigatorios em evento; omita os que nao mudam. Se a data, o horario ou qual evento editar/excluir nao estiverem claros dentre as opcoes do contexto, pergunte antes - nao inclua o bloco agenda_action nesse caso. Se a Denise so estiver perguntando sobre a agenda sem pedir mudanca, responda so com texto.\n\nNunca transforme automaticamente reflexoes do devocional (respostas, gratidao, aprendizado) em tarefa, lembrete ou compromisso. Se identificar ali uma possivel acao (ex: "preciso ligar pra minha mae"), pode comentar que percebeu isso, mas so crie algo se a Denise confirmar explicitamente que quer.\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context || {}, null, 2)

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
