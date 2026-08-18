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
    const systemPrompt = lunaSystemPrompt('Você está enviando o resumo da noite (20:00) pelo WhatsApp.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)
    const pedido = 'Escreva a mensagem de encerramento do dia da Denise. Comece com "Boa noite, Denise 🌙" e mostre: o que foi feito hoje (itens da rotina marcados como feito hoje, treino/leitura/devocional se houver registro de hoje), e o que fica pendente para amanhã (itens da agenda de amanhã, itens da rotina de hoje que não foram feitos). Se uma categoria estiver vazia, não mencione ela. Termine com uma frase curta e acolhedora. Formato de WhatsApp, emojis com moderação, sem markdown de negrito.'
    const texto = await askLuna(systemPrompt, [{ type: 'text', text: pedido }])
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
