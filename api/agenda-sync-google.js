import { getSupabaseAdmin, insertGoogleCalendarEvento } from './_cronlib.js'

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Metodo nao permitido.' })
    return
  }
  try {
    const body = req.body || {}
    const nome = String(body.nome || '').trim()
    const data = String(body.data || '').trim()
    const hora = body.hora ? String(body.hora).trim() : ''
    if (!nome || !/^\d{4}-\d{2}-\d{2}$/.test(data)) {
      res.status(400).json({ error: 'nome e data (YYYY-MM-DD) sao obrigatorios.' })
      return
    }
    const supabase = getSupabaseAdmin()
    if (!supabase) {
      res.status(500).json({ error: 'Supabase nao configurado.' })
      return
    }
    const evento = await insertGoogleCalendarEvento(supabase, { nome, data, hora })
    res.status(200).json({ ok: true, google_evento: evento })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
