import { getSupabaseAdmin } from './_cronlib.js'

const GOOGLE_CLIENT_ID = '386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'

export default async function handler(req, res) {
  const supabase = getSupabaseAdmin()
  if (!supabase) {
    res.status(500).json({ error: 'Supabase nao configurado no servidor.' })
    return
  }
  try {
    const { data: row } = await supabase.from('google_tokens').select('*').eq('id', 'denise').maybeSingle()
    if (!row || !row.refresh_token) {
      res.status(200).json({ connected: false })
      return
    }
    if (row.access_token && row.expires_at && Number(row.expires_at) - 60000 > Date.now()) {
      res.status(200).json({ connected: true, access_token: row.access_token, expires_at: Number(row.expires_at) })
      return
    }
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET
    if (!clientSecret) {
      res.status(500).json({ error: 'GOOGLE_CLIENT_SECRET nao configurado no servidor.' })
      return
    }
    const tokenResp = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: GOOGLE_CLIENT_ID,
        client_secret: clientSecret,
        refresh_token: row.refresh_token,
        grant_type: 'refresh_token'
      })
    })
    const tokenData = await tokenResp.json()
    if (!tokenResp.ok || !tokenData.access_token) {
      res.status(200).json({ connected: false, error: tokenData?.error_description || tokenData?.error || 'Falha ao renovar token.' })
      return
    }
    const expiresAt = Date.now() + (tokenData.expires_in || 3600) * 1000
    await supabase.from('google_tokens').upsert({ id: 'denise', access_token: tokenData.access_token, expires_at: expiresAt, updated_at: new Date().toISOString() })
    res.status(200).json({ connected: true, access_token: tokenData.access_token, expires_at: expiresAt })
  } catch (err) {
    res.status(500).json({ error: 'Falha ao obter token do Google: ' + (err?.message || 'erro desconhecido') })
  }
}
