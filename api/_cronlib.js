import { createClient } from '@supabase/supabase-js'

function dataIsoBR(offsetDias = 0) {
  const d = new Date(Date.now() + offsetDias * 86400000)
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(d)
}

function diasDesdeRegistroBR(dataBR) {
  const m = /^(\d{2})\/(\d{2})$/.exec(dataBR || '')
  if (!m) return null
  const hoje = new Date()
  const anoAtual = hoje.getFullYear()
  let dataReg = new Date(Date.UTC(anoAtual, Number(m[2]) - 1, Number(m[1])))
  if (dataReg.getTime() > hoje.getTime() + 86400000) dataReg = new Date(Date.UTC(anoAtual - 1, Number(m[2]) - 1, Number(m[1])))
  return Math.floor((hoje.getTime() - dataReg.getTime()) / 86400000)
}

export function horaLocalBR(dataISO) {
  const partes = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).formatToParts(new Date(dataISO))
  const h = partes.find((p) => p.type === 'hour')?.value || '00'
  const m = partes.find((p) => p.type === 'minute')?.value || '00'
  return `${h}:${m}`
}

const GOOGLE_CLIENT_ID = '386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'

export const BUSCA_DOMI_POR_DIA = { 1: { busca: '12:50', sair: '12:35' }, 2: { busca: '11:40', sair: '11:25' }, 3: { busca: '12:50', sair: '12:35' }, 4: { busca: '11:40', sair: '11:25' }, 5: { busca: '13:00', sair: '12:45' } }
export const PLANO_TREINO_SEMANA = { 0: null, 1: 'Calistenia', 2: 'Caminhada', 3: 'Calistenia', 4: 'Caminhada', 5: 'Calistenia', 6: 'Mobilidade' }

export function getEvoConfig() {
  const baseUrl = (process.env.EVOLUTION_API_URL || '').replace(/\/+$/, '')
  const apiKey = process.env.EVOLUTION_API_KEY
  const instance = process.env.EVOLUTION_INSTANCE || 'denise-os'
  return { baseUrl, apiKey, instance }
}

export async function sendWhatsappText(number, text) {
  const { baseUrl, apiKey, instance } = getEvoConfig()
  if (!baseUrl || !apiKey) throw new Error('Evolution API nao configurada.')
  const resp = await fetch(`${baseUrl}/message/sendText/${instance}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', apikey: apiKey },
    body: JSON.stringify({ number, text })
  })
  if (!resp.ok) {
    const corpo = await resp.text().catch(() => '')
    throw new Error(`Falha ao enviar WhatsApp (status ${resp.status}): ${corpo.slice(0, 300)}`)
  }
}

export async function transcribeAudio(base64, mediaType) {
  const geminiKey = process.env.GEMINI_API_KEY
  if (!geminiKey) throw new Error('GEMINI_API_KEY nao configurada.')
  const geminiResp = await fetch(
    'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + geminiKey,
    {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [
            { text: 'Transcreva este audio em portugues do Brasil. Responda apenas com o texto transcrito, sem comentarios.' },
            { inline_data: { mime_type: mediaType || 'audio/ogg', data: base64 } }
          ]
        }]
      })
    }
  )
  const geminiData = await geminiResp.json()
  if (!geminiResp.ok) throw new Error(geminiData?.error?.message || 'Erro ao transcrever audio.')
  return (geminiData.candidates?.[0]?.content?.parts?.[0]?.text || '').trim()
}

export async function askLuna(systemPrompt, userContent, history) {
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY nao configurada.')
  const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 4096,
      output_config: { effort: 'low' },
      system: systemPrompt,
      messages: [...(Array.isArray(history) ? history : []), { role: 'user', content: userContent }]
    })
  })
  const data = await anthropicResp.json()
  if (!anthropicResp.ok) throw new Error(data?.error?.message || 'Erro ao consultar a IA.')
  const texto = data.content?.find((b) => b.type === 'text')?.text
  if (!texto) throw new Error('Luna nao gerou texto (stop_reason: ' + (data.stop_reason || '?') + ')')
  return texto
}

export async function getGoogleAccessToken(supabase) {
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

function addHoraStr(hhmm) {
  const partes = String(hhmm || '').split(':').map(Number)
  const hh = partes[0] || 0, mm = partes[1] || 0
  const d = new Date(); d.setHours(hh + 1, mm, 0, 0)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function montarGoogleBody({ nome, data, hora, horaFim, local, descricao }) {
  const body = { summary: nome || '(sem título)' }
  if (local) body.location = local
  if (descricao) body.description = descricao
  if (hora) {
    body.start = { dateTime: `${data}T${hora}:00`, timeZone: 'America/Sao_Paulo' }
    body.end = { dateTime: `${data}T${horaFim || addHoraStr(hora)}:00`, timeZone: 'America/Sao_Paulo' }
  } else {
    body.start = { date: data }
    body.end = { date: data }
  }
  return body
}

export async function insertGoogleCalendarEvento(supabase, evento) {
  const accessToken = await getGoogleAccessToken(supabase)
  if (!accessToken) return null
  const resp = await fetch('https://www.googleapis.com/calendar/v3/calendars/primary/events', {
    method: 'POST',
    headers: { authorization: `Bearer ${accessToken}`, 'content-type': 'application/json' },
    body: JSON.stringify(montarGoogleBody(evento))
  })
  if (!resp.ok) return null
  return await resp.json()
}

export async function updateGoogleCalendarEvento(supabase, googleEventId, evento) {
  if (!googleEventId) return null
  const accessToken = await getGoogleAccessToken(supabase)
  if (!accessToken) return null
  const resp = await fetch(`https://www.googleapis.com/calendar/v3/calendars/primary/events/${encodeURIComponent(googleEventId)}`, {
    method: 'PATCH',
    headers: { authorization: `Bearer ${accessToken}`, 'content-type': 'application/json' },
    body: JSON.stringify(montarGoogleBody(evento))
  })
  if (!resp.ok) return null
  return await resp.json()
}

export async function deleteGoogleCalendarEvento(supabase, googleEventId) {
  if (!googleEventId) return true
  const accessToken = await getGoogleAccessToken(supabase)
  if (!accessToken) return false
  const resp = await fetch(`https://www.googleapis.com/calendar/v3/calendars/primary/events/${encodeURIComponent(googleEventId)}`, {
    method: 'DELETE',
    headers: { authorization: `Bearer ${accessToken}` }
  })
  return resp.ok || resp.status === 410 || resp.status === 404
}

export function getSupabaseAdmin() {
  const url = process.env.VITE_SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !serviceKey) return null
  return createClient(url, serviceKey)
}

export async function buildLunaContext() {
  const hojeIso = dataIsoBR(0)
  const em7diasIso = dataIsoBR(7)
  const supabase = getSupabaseAdmin()
  if (!supabase) return { data_hoje: hojeIso, tirzepatida: null }

  const [{ data: sched }, { data: bal }, { data: snap }, eventosGoogleAoVivo] = await Promise.all([
    supabase.from('tirzepatida_schedule').select('*'),
    supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
    supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle(),
    fetchGoogleCalendarEventos(supabase, new Date().toISOString(), new Date(Date.now() + 7 * 86400000).toISOString()).catch(() => [])
  ])

  const tzMap = {}
  ;(sched || []).forEach((row) => {
    tzMap[row.person] = { planned_dose_mg: Number(row.planned_dose_mg), interval_days: row.interval_days, next_application_date: row.next_application_date }
  })

  const d = snap?.data || {}
  const agendaLocal = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
  const agendaGoogle = eventosGoogleAoVivo.length > 0 ? eventosGoogleAoVivo : (Array.isArray(d.dos_google_events_cache) ? d.dos_google_events_cache : [])
  const rotinaItens = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
  const rotinaDoneHoje = Array.isArray(d[`dos_rotina_done_${hojeIso}`]) ? d[`dos_rotina_done_${hojeIso}`] : []
  const ontemIso = dataIsoBR(-1)
  const diaSemanaOntem = new Date(ontemIso + 'T12:00:00-03:00').getDay()
  const rotinaDoneOntem = Array.isArray(d[`dos_rotina_done_${ontemIso}`]) ? d[`dos_rotina_done_${ontemIso}`] : []
  const rotinaPendenteOntem = rotinaItens
    .map((it, i) => ({ it, i }))
    .filter(({ it, i }) => (!it.dias || it.dias.includes(diaSemanaOntem)) && !rotinaDoneOntem.includes(i))
    .map(({ it }) => ({ horario: it.t, nome: it.n, categoria: it.cat }))
  const casaItens = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
  const treinos = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
  const leituras = Array.isArray(d.dos_leituras) ? d.dos_leituras : []
  const devocionais = Array.isArray(d.dos_devocionais) ? d.dos_devocionais : []

  function diasUnicos(entries) { return new Set(entries.map((e) => e.data)) }
  function sequencia(dias) {
    let n = 0
    const dt = new Date()
    while (dias.has(dt.toISOString().slice(0, 10))) { n++; dt.setDate(dt.getDate() - 1) }
    return n
  }

  const agendaProximos7Dias = [
    ...agendaLocal.map((e) => ({ data: e.data, hora: e.hora, titulo: e.nome, origem: 'app' })),
    ...agendaGoogle.map((ev) => ({
      data: (ev.start?.dateTime || ev.start?.date || '').slice(0, 10),
      hora: ev.start?.dateTime ? horaLocalBR(ev.start.dateTime) : '',
      titulo: ev.summary || '(sem titulo)',
      origem: 'google_calendar'
    }))
  ].filter((e) => e.data >= hojeIso && e.data <= em7diasIso).sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))

  const contasVencendo = casaItens.filter((i) => i.cat === 'Contas' && i.venc && !i.done && i.venc >= hojeIso && i.venc <= em7diasIso)
  const casaPendenteGeral = casaItens.filter((i) => i.cat !== 'Contas' && !i.done)

  const aguaLog = d.dos_agua_log || {}
  const aguaHojeMl = Number(aguaLog[hojeIso] || 0)

  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaDomiHoje = BUSCA_DOMI_POR_DIA[diaSemanaHoje] || null

  return {
    data_hoje: hojeIso,
    agua_hoje_ml: aguaHojeMl,
    meta_agua_ml: Number(d.dos_meta_agua_ml || 2500),
    busca_domi_hoje: buscaDomiHoje,
    ultima_sincronizacao_do_app: snap?.data ? d.__updated_at || null : null,
    tirzepatida: Object.keys(tzMap).length > 0 ? { estoque_atual_mg: Number(bal?.current_balance_mg ?? 0), denise: tzMap.denise || null, flavio: tzMap.flavio || null } : null,
    sequencia_treinos_dias: sequencia(diasUnicos(treinos)),
    sequencia_leitura_dias: sequencia(diasUnicos(leituras)),
    sequencia_devocional_dias: sequencia(diasUnicos(devocionais)),
    devocional_feito_hoje: devocionais.some((e) => e.data === hojeIso),
    devocionais_recentes: devocionais.slice(0, 14),
    pedidos_oracao: Array.isArray(d.dos_pedidos_oracao) ? d.dos_pedidos_oracao : [],
    planos_leitura_biblica: Array.isArray(d.dos_planos_biblia) ? d.dos_planos_biblia.map((p) => ({ nome: p.nome, concluidas: p.concluidas, total: p.total, leitura_de_hoje: p.leituraAtual })) : [],
    livro_atual: d.dos_livro_atual || null,
    contas_vencendo_7dias: contasVencendo.map((c) => ({ nome: c.n, vencimento: c.venc })),
    casa_pendente: casaPendenteGeral.map((c) => ({ nome: c.n, categoria: c.cat })),
    agenda_proximos_7dias: agendaProximos7Dias,
    rotina_de_hoje: rotinaItens.map((it, i) => ({ horario: it.t, nome: it.n, categoria: it.cat, feito_hoje: rotinaDoneHoje.includes(i) })),
    rotina_pendente_ontem: rotinaPendenteOntem,
    medicamentos: (() => {
      const bruto = d.dos_medicamentos || {}
      const comDias = {}
      Object.keys(bruto).forEach((kid) => {
        comDias[kid] = (bruto[kid] || [])
          .filter((m) => !m.ate || m.ate >= hojeIso)
          .map((m) => ({ ...m, dias_desde_registro: diasDesdeRegistroBR(m.data) }))
      })
      return comDias
    })(),
    trabalho_tarefas: d.dos_trabalho || [],
    treinos_recentes: treinos.slice(0, 10),
    leituras_recentes: leituras.slice(0, 10)
  }
}

export function verificarCron(req) {
  const secret = process.env.CRON_SECRET
  if (!secret) return true
  return req.headers.authorization === `Bearer ${secret}`
}

export function getDeniseNumber() {
  return process.env.DENISE_WHATSAPP_NUMBER || ''
}

export function lunaSystemPrompt(extra) {
  return 'Você é a Luna, assistente pessoal da Denise dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em português do Brasil. Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente números, datas ou fatos que não estão ali. Se um dado não estiver no contexto, diga com naturalidade que ele ainda não foi registrado no app. Nunca transforme automaticamente reflexões do devocional (respostas, gratidão, aprendizado) em tarefa, lembrete ou compromisso. Se identificar ali uma possível ação (ex: "preciso ligar para minha mãe"), pode comentar que percebeu isso, mas só crie algo se a Denise confirmar explicitamente que quer. ' + (extra || '')
}
