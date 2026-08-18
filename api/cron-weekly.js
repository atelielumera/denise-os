import { verificarCron, getDeniseNumber, buildLunaContext, askLuna, sendWhatsappText, lunaSystemPrompt } from './_cronlib.js'

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
  try {
    const context = await buildLunaContext()
    const systemPrompt = lunaSystemPrompt('Você está enviando o resumo semanal (sexta-feira) pelo WhatsApp.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)
    const pedido = 'Escreva o resumo da semana da Denise. Comece com "Resumo da semana 📊" e use as sequências disponíveis (treinos, leitura, devocional) e os treinos/leituras recentes para comentar como foi a semana - sem inventar números que não estão no contexto. Se não houver dado suficiente para um tópico, não mencione ele. Termine com uma frase curta de reconhecimento pelo esforço da semana. Formato de WhatsApp, emojis com moderação, sem markdown de negrito.'
    const texto = await askLuna(systemPrompt, [{ type: 'text', text: pedido }])
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
