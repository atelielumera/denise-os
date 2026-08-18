import { getSupabaseAdmin } from './_cronlib.js'

const APP_URL = 'https://denise-os.vercel.app'
const REDIRECT_URI = `${APP_URL}/api/google-oauth-callback`
const GOOGLE_CLIENT_ID = '386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'

export default async function handler(req, res) {
  const { code, error } = req.query || {}
  if (error) {
    res.redirect(302, `${APP_URL}/agenda?google_erro=1`)
    return
  }
  if (!code) {
    res.status(400).send('Codigo ausente.')
    return
  }
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET
  if (!clientSecret) {
    res.status(500).send('GOOGLE_CLIENT_SECRET nao configurado no servidor.')
    return
  }
  try {
    const tokenResp = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: GOOGLE_CLIENT_ID,
        client_secret: clientSecret,
        redirect_uri: REDIRECT_URI,
        grant_type: 'authorization_code'
      })
    })
    const tokenData = await tokenResp.json()
    if (!tokenResp.ok || !tokenData.access_token) {
      res.status(502).send('Erro ao trocar codigo por token: ' + (tokenData?.error_description || tokenData?.error || 'erro desconhecido'))
      return
    }
    const supabase = getSupabaseAdmin()
    if (!supabase) {
      res.status(500).send('Supabase nao configurado no servidor.')
      return
    }
    const expiresAt = Date.now() + (tokenData.expires_in || 3600) * 1000
    const update = {
      id: 'denise',
      access_token: tokenData.access_token,
      expires_at: expiresAt,
      updated_at: new Date().toISOString()
    }
    if (tokenData.refresh_token) update.refresh_token = tokenData.refresh_token
    await supabase.from('google_tokens').upsert(update)
    res.redirect(302, `${APP_URL}/agenda?google_conectado=1`)
  } catch (err) {
    res.status(500).send('Falha ao conectar ao Google: ' + (err?.message || 'erro desconhecido'))
  }
}
