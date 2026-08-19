from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# --- api/_cronlib.js: buscar o Google Calendar direto do servidor, sem depender do navegador aberto ---
cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (_cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_import = "import { createClient } from '@supabase/supabase-js'"
new_import = "import { createClient } from '@supabase/supabase-js'\n\nconst GOOGLE_CLIENT_ID = '386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'"
c = replace_once(c, old_import, new_import, "cronlib-google-client-id")

old_fn = "export function getSupabaseAdmin() {"
new_fn = """export async function getGoogleAccessToken(supabase) {
  const { data: row } = await supabase.from('google_tokens').select('*').eq('id', 'denise').maybeSingle()
  if (!row || !row.refresh_token) return null
  if (row.access_token && row.expires_at && Number(row.expires_at) - 60000 > Date.now()) return row.access_token
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET
  if (!clientSecret) return null
  const tokenResp = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: GOOGLE_CLIENT_ID, client_secret: clientSecret, refresh_token: row.refresh_token, grant_type: 'refresh_token' })
  })
  const tokenData = await tokenResp.json()
  if (!tokenResp.ok || !tokenData.access_token) return null
  const expiresAt = Date.now() + (tokenData.expires_in || 3600) * 1000
  await supabase.from('google_tokens').upsert({ id: 'denise', access_token: tokenData.access_token, expires_at: expiresAt, updated_at: new Date().toISOString() })
  return tokenData.access_token
}

export async function fetchGoogleCalendarEventos(supabase, timeMinIso, timeMaxIso) {
  const accessToken = await getGoogleAccessToken(supabase)
  if (!accessToken) return []
  const url = new URL('https://www.googleapis.com/calendar/v3/calendars/primary/events')
  url.searchParams.set('timeMin', timeMinIso)
  url.searchParams.set('timeMax', timeMaxIso)
  url.searchParams.set('singleEvents', 'true')
  url.searchParams.set('orderBy', 'startTime')
  const resp = await fetch(url.toString(), { headers: { authorization: `Bearer ${accessToken}` } })
  if (!resp.ok) return []
  const data = await resp.json()
  return Array.isArray(data.items) ? data.items : []
}

export function getSupabaseAdmin() {"""
c = replace_once(c, old_fn, new_fn, "cronlib-google-calendar-fns")

old_build_start = """export async function buildLunaContext() {
  const hojeIso = new Date().toISOString().slice(0, 10)
  const em7diasIso = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)
  const supabase = getSupabaseAdmin()
  if (!supabase) return { data_hoje: hojeIso, tirzepatida: null }

  const [{ data: sched }, { data: bal }, { data: snap }] = await Promise.all([
    supabase.from('tirzepatida_schedule').select('*'),
    supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
    supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
  ])"""
new_build_start = """export async function buildLunaContext() {
  const hojeIso = new Date().toISOString().slice(0, 10)
  const em7diasIso = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)
  const supabase = getSupabaseAdmin()
  if (!supabase) return { data_hoje: hojeIso, tirzepatida: null }

  const [{ data: sched }, { data: bal }, { data: snap }, eventosGoogleAoVivo] = await Promise.all([
    supabase.from('tirzepatida_schedule').select('*'),
    supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
    supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle(),
    fetchGoogleCalendarEventos(supabase, new Date().toISOString(), new Date(Date.now() + 7 * 86400000).toISOString()).catch(() => [])
  ])"""
c = replace_once(c, old_build_start, new_build_start, "cronlib-buildcontext-fetch-eventos")

old_agenda_google = "  const agendaGoogle = Array.isArray(d.dos_google_events_cache) ? d.dos_google_events_cache : []"
new_agenda_google = "  const agendaGoogle = eventosGoogleAoVivo.length > 0 ? eventosGoogleAoVivo : (Array.isArray(d.dos_google_events_cache) ? d.dos_google_events_cache : [])"
c = replace_once(c, old_agenda_google, new_agenda_google, "cronlib-agenda-google-fonte")

cronlib_file.write_text(c)
print("OK - api/_cronlib.js: Luna agora busca o Google Calendar direto do servidor (token ja salvo),")
print("nao depende mais so do navegador estar aberto e ter sincronizado o snapshot.")
