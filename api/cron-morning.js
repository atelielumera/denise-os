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
    const systemPrompt = lunaSystemPrompt('Você está enviando o resumo da manhã (06:00) pelo WhatsApp.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)
    const pedido = 'Escreva a mensagem de bom dia da Denise. Comece com "Bom dia, Denise! ☀️" e liste, de forma organizada e curta, tudo que ela tem para fazer hoje: um lembrete de beber água ao longo do dia citando a meta_agua_ml em litros; se busca_domi_hoje existir no contexto (em dias de semana), lembre que ela precisa sair de casa no horário \'sair\' de busca_domi_hoje para buscar a Domi, que sai da escola às \'busca\' (15 minutos depois do horário de sair); itens da rotina de hoje ainda não feitos; compromissos da agenda de hoje; tirzepatida se for hoje o dia de aplicar; medicamentos em curso hoje (considere em curso QUALQUER medicamento que tenha \'horarios\' preenchido, independente de \'dias_desde_registro\' - a Denise ja remove o medicamento da lista quando o tratamento termina, entao se ele ainda esta na lista com horarios preenchido, esta em curso); e tarefas de trabalho pendentes se houver. Se uma dessas categorias estiver vazia ou sem dado (por exemplo busca_domi_hoje nulo no fim de semana), não mencione ela (não diga "nada registrado"). Termine com uma frase curta de incentivo. Formato de WhatsApp, use emojis com moderação, sem markdown de negrito.'
    const texto = await askLuna(systemPrompt, [{ type: 'text', text: pedido }])
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
