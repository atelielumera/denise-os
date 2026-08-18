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
    const systemPrompt = lunaSystemPrompt('Você está enviando o resumo da próxima semana (domingo 20:00) pelo WhatsApp.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)
    const pedido = 'Escreva a mensagem de preparação para a próxima semana da Denise. Comece com "Se preparando para a semana 🗓️" e liste os compromissos da agenda_proximos_7dias, contas a vencer, e a próxima aplicação de tirzepatida se cair nos próximos 7 dias. Se não houver nenhum compromisso registrado, diga isso com naturalidade. Termine com uma frase curta de incentivo para a semana que vem. Formato de WhatsApp, emojis com moderação, sem markdown de negrito.'
    const texto = await askLuna(systemPrompt, [{ type: 'text', text: pedido }])
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
