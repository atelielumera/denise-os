import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin } from './_cronlib.js'

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
    const supabase = getSupabaseAdmin()
    const hojeIso = dataIsoBR()
    if (supabase) {
      const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
      const d = snap?.data || {}
      const devocionais = Array.isArray(d.dos_devocionais) ? d.dos_devocionais : []
      if (devocionais.some((e) => e.data === hojeIso)) {
        res.status(200).json({ ok: true, ja_feito: true })
        return
      }
    }
    const texto = '🙏 Bom dia! Hora do devocional.\n\nExiste um mandamento a obedecer? Uma promessa a reivindicar? Um pecado a evitar? Uma aplicação a fazer? Algo novo sobre Deus?\n\nPergunte também: Quem? O quê? Quando? Onde? Por quê?\n\nPode me responder por aqui quando terminar que eu registro no seu histórico.'
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
