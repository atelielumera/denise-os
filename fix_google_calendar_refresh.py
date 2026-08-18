from pathlib import Path

applied = []

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

main_file = Path("src/main.tsx")
cronlib_file = Path("api/_cronlib.js")
if not main_file.exists() or not cronlib_file.exists():
    raise SystemExit("ABORTADO (arquivos-nao-encontrados): rode este script na raiz do projeto denise-os.")

token_file = Path("api/google-token.js")
callback_file = Path("api/google-oauth-callback.js")
if token_file.exists() or callback_file.exists():
    raise SystemExit("ABORTADO (ja-existe): api/google-token.js ou api/google-oauth-callback.js ja existem. Nada foi alterado.")

# --- 1) _cronlib.js: exportar getSupabaseAdmin pra reaproveitar em outros endpoints ---
c = cronlib_file.read_text()
c = replace_once(
    c,
    "function getSupabaseAdmin() {",
    "export function getSupabaseAdmin() {",
    "cronlib-export-supabase-admin",
)
cronlib_file.write_text(c)
applied.append("api/_cronlib.js: getSupabaseAdmin exportado")

# --- 2) api/google-token.js (NOVO): devolve um access_token sempre valido, renovando via refresh_token no servidor ---
token_file.write_text("""import { getSupabaseAdmin } from './_cronlib.js'

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
""")
applied.append("api/google-token.js criado")

# --- 3) api/google-oauth-callback.js (NOVO): troca o codigo de autorizacao por access_token + refresh_token e salva no Supabase ---
callback_file.write_text("""import { getSupabaseAdmin } from './_cronlib.js'

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
""")
applied.append("api/google-oauth-callback.js criado")

# --- 4) main.tsx: Agenda() passa a usar o fluxo com refresh_token no servidor em vez do popup do GIS ---
s = main_file.read_text()

old_mount = """  React.useEffect(()=>{
    if(gToken){buscarEventosGoogle(gToken);return}
    tentarReconectarSilencioso()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])"""
new_mount = """  React.useEffect(()=>{
    if(gToken){buscarEventosGoogle(gToken);return}
    tentarReconectarSilencioso()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  React.useEffect(()=>{
    const iv=setInterval(()=>{tentarReconectarSilencioso()},45*60*1000)
    return ()=>clearInterval(iv)
  },[])"""
s = replace_once(s, old_mount, new_mount, "agenda-mount-effect")

old_funcs = """  function salvarTokenGoogle(resp:any){
    setGToken(resp.access_token)
    const expiresAt=Date.now()+((resp.expires_in||3600)*1000)
    try{localStorage.setItem('dos_google_token',JSON.stringify({token:resp.access_token,expiresAt}))}catch{}
    buscarEventosGoogle(resp.access_token)
  }

  function tentarReconectarSilencioso(){
    const g=(window as any).google
    if(!g||!g.accounts||!g.accounts.oauth2)return
    const tokenClient=g.accounts.oauth2.initTokenClient({
      client_id:GOOGLE_CLIENT_ID,
      scope:GOOGLE_SCOPE,
      callback:(resp:any)=>{if(resp&&resp.access_token)salvarTokenGoogle(resp)}
    })
    try{tokenClient.requestAccessToken({prompt:''})}catch{}
  }

  function conectarGoogle(){
    const g=(window as any).google
    if(!g||!g.accounts||!g.accounts.oauth2){setGErro('Google ainda carregando, tenta de novo em alguns segundos.');return}
    const tokenClient=g.accounts.oauth2.initTokenClient({
      client_id:GOOGLE_CLIENT_ID,
      scope:GOOGLE_SCOPE,
      callback:(resp:any)=>{
        if(resp&&resp.access_token)salvarTokenGoogle(resp)
        else setGErro('Nao foi possivel conectar ao Google.')
      }
    })
    tokenClient.requestAccessToken()
  }"""
new_funcs = """  function tentarReconectarSilencioso(){
    fetch('/api/google-token').then(r=>r.json()).then(data=>{
      if(data&&data.access_token){
        setGToken(data.access_token)
        try{localStorage.setItem('dos_google_token',JSON.stringify({token:data.access_token,expiresAt:data.expires_at||(Date.now()+50*60*1000)}))}catch{}
        buscarEventosGoogle(data.access_token)
      }
    }).catch(()=>{})
  }

  function conectarGoogle(){
    const redirectUri=`${window.location.origin}/api/google-oauth-callback`
    const url=`https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&access_type=offline&prompt=consent&scope=${encodeURIComponent(GOOGLE_SCOPE)}`
    window.location.href=url
  }"""
s = replace_once(s, old_funcs, new_funcs, "agenda-google-funcs")

main_file.write_text(s)
applied.append("src/main.tsx: reconexao do Google Calendar reescrita (refresh_token via servidor)")

print("OK - alteracoes aplicadas:")
for a in applied:
    print(" -", a)
print()
print("Antes de rodar 'npm run build':")
print("1) No Google Cloud Console, no MESMO OAuth Client ID que ja existe (Web application):")
print("   - Copie o 'Client secret'.")
print("   - Em 'Authorized redirect URIs' adicione: https://denise-os.vercel.app/api/google-oauth-callback")
print("2) No terminal: vercel env add GOOGLE_CLIENT_SECRET production   (cole o Client secret)")
print("3) Rode a SQL abaixo no Supabase SQL Editor (cria a tabela google_tokens).")
