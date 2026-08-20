import { verificarCron, getDeniseNumber, buildLunaContext, askLuna, sendWhatsappText, lunaSystemPrompt, getSupabaseAdmin } from './_cronlib.js'

function horaAgoraBR() {
  const partes = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).formatToParts(new Date())
  return Number(partes.find((p) => p.type === 'hour')?.value || '0')
}

function dataIsoBR() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date())
}

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
    if (horaAgoraBR() < 6) {
      const supabase = getSupabaseAdmin()
      const hojeIso = dataIsoBR()
      if (supabase) {
        const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
        const devocionais = Array.isArray(snap?.data?.dos_devocionais) ? snap.data.dos_devocionais : []
        if (devocionais.some((e) => e.data === hojeIso)) {
          res.status(200).json({ ok: true, ja_feito: true })
          return
        }
      }
      const textoDevocional = '🙏 Bom dia! Hora do devocional.\n\nExiste um mandamento a obedecer? Uma promessa a reivindicar? Um pecado a evitar? Uma aplicação a fazer? Algo novo sobre Deus?\n\nPergunte também: Quem? O quê? Quando? Onde? Por quê?\n\nPode me responder por aqui quando terminar que eu registro no seu histórico.'
      await sendWhatsappText(numero, textoDevocional)
      res.status(200).json({ ok: true })
      return
    }
    const context = await buildLunaContext()
    const systemPrompt = lunaSystemPrompt('Você está enviando o resumo da manhã (06:00) pelo WhatsApp.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)
    const pedido = 'Escreva a mensagem de bom dia da Denise. Comece com "Bom dia, Denise! ☀️". Se rotina_pendente_ontem tiver itens, inclua logo no início uma seção curta "📌 Ficou em aberto ontem" listando esses itens (nome e horário), sem cobrar de forma pesada, só lembrando com carinho. Depois liste, de forma organizada e curta, tudo que ela tem para fazer hoje: um lembrete de beber água ao longo do dia citando a meta_agua_ml em litros; se busca_domi_hoje existir no contexto (em dias de semana), lembre que ela precisa sair de casa no horário \'sair\' de busca_domi_hoje para buscar a Domi, que sai da escola às \'busca\' (15 minutos depois do horário de sair); itens da rotina de hoje ainda não feitos; compromissos da agenda de hoje; tirzepatida se for hoje o dia de aplicar; medicamentos em curso hoje (considere em curso QUALQUER medicamento que tenha \'horarios\' preenchido, independente de \'dias_desde_registro\' - a Denise ja remove o medicamento da lista quando o tratamento termina, entao se ele ainda esta na lista com horarios preenchido, esta em curso); tarefas de trabalho pendentes se houver; contas perto do vencimento (contas_vencendo_7dias); e itens pendentes de casa (casa_pendente - compras, tarefas domesticas, manutencao), agrupados por categoria se houver mais de um. Se devocional_feito_hoje for false, inclua tambem uma seção "🙏 Devocional de hoje" com exatamente estas perguntas de reflexão, nesta ordem (não mude o texto delas): "Existe um mandamento a obedecer? Uma promessa a reivindicar? Um pecado a evitar? Uma aplicação a fazer? Algo novo sobre Deus?" e depois "Pergunte também: Quem? O quê? Quando? Onde? Por quê?" - é só um convite pra ela refletir mentalmente ao longo do dia, não peça pra responder por escrito. Se devocional_feito_hoje for true, não inclua essa seção. Se uma dessas categorias estiver vazia ou sem dado (por exemplo busca_domi_hoje nulo no fim de semana), não mencione ela (não diga "nada registrado"). Termine com uma frase curta de incentivo. Formato de WhatsApp, use emojis com moderação, sem markdown de negrito.'
    const texto = await askLuna(systemPrompt, [{ type: 'text', text: pedido }])
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
