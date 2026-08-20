import { getSupabaseAdmin, insertGoogleCalendarEvento, updateGoogleCalendarEvento, deleteGoogleCalendarEvento } from './_cronlib.js'

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Metodo nao permitido.' })
    return
  }
  try {
    const body = req.body || {}
    const acao = String(body.acao || 'criar')
    const supabase = getSupabaseAdmin()
    if (!supabase) {
      res.status(500).json({ error: 'Supabase nao configurado.' })
      return
    }

    if (acao === 'excluir') {
      const ok = await deleteGoogleCalendarEvento(supabase, body.googleEventId)
      res.status(200).json({ ok })
      return
    }

    const evento = body.evento || body
    const nome = String(evento.nome || '').trim()
    const data = String(evento.data || '').trim()
    if (!nome || !/^\d{4}-\d{2}-\d{2}$/.test(data)) {
      res.status(400).json({ error: 'nome e data (YYYY-MM-DD) sao obrigatorios.' })
      return
    }
    const campos = { nome, data, hora: evento.hora || '', horaFim: evento.horaFim || '', local: evento.local || '', descricao: evento.descricao || '' }

    if (acao === 'editar' && body.googleEventId) {
      const googleEvento = await updateGoogleCalendarEvento(supabase, body.googleEventId, campos)
      res.status(200).json({ ok: true, google_evento: googleEvento })
      return
    }

    const googleEvento = await insertGoogleCalendarEvento(supabase, campos)
    res.status(200).json({ ok: true, google_evento: googleEvento })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
