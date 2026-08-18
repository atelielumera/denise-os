import { createClient } from '@supabase/supabase-js'

export function getEvoConfig() {
  const baseUrl = (process.env.EVOLUTION_API_URL || '').replace(/\/+$/, '')
  const apiKey = process.env.EVOLUTION_API_KEY
  const instance = process.env.EVOLUTION_INSTANCE || 'denise-os'
  return { baseUrl, apiKey, instance }
}

export async function sendWhatsappText(number, text) {
  const { baseUrl, apiKey, instance } = getEvoConfig()
  if (!baseUrl || !apiKey) throw new Error('Evolution API nao configurada.')
  await fetch(`${baseUrl}/message/sendText/${instance}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', apikey: apiKey },
    body: JSON.stringify({ number, text })
  })
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

export async function askLuna(systemPrompt, userContent) {
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY nao configurada.')
  const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 800,
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }]
    })
  })
  const data = await anthropicResp.json()
  if (!anthropicResp.ok) throw new Error(data?.error?.message || 'Erro ao consultar a IA.')
  return data.content?.find((b) => b.type === 'text')?.text || 'Desculpa, não consegui gerar isso agora.'
}

export function getSupabaseAdmin() {
  const url = process.env.VITE_SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !serviceKey) return null
  return createClient(url, serviceKey)
}

export async function buildLunaContext() {
  const hojeIso = new Date().toISOString().slice(0, 10)
  const em7diasIso = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)
  const supabase = getSupabaseAdmin()
  if (!supabase) return { data_hoje: hojeIso, tirzepatida: null }

  const [{ data: sched }, { data: bal }, { data: snap }] = await Promise.all([
    supabase.from('tirzepatida_schedule').select('*'),
    supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
    supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
  ])

  const tzMap = {}
  ;(sched || []).forEach((row) => {
    tzMap[row.person] = { planned_dose_mg: Number(row.planned_dose_mg), interval_days: row.interval_days, next_application_date: row.next_application_date }
  })

  const d = snap?.data || {}
  const agendaLocal = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
  const agendaGoogle = Array.isArray(d.dos_google_events_cache) ? d.dos_google_events_cache : []
  const rotinaItens = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
  const rotinaDoneHoje = Array.isArray(d[`dos_rotina_done_${hojeIso}`]) ? d[`dos_rotina_done_${hojeIso}`] : []
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
      hora: ev.start?.dateTime ? new Date(ev.start.dateTime).toISOString().slice(11, 16) : '',
      titulo: ev.summary || '(sem titulo)',
      origem: 'google_calendar'
    }))
  ].filter((e) => e.data >= hojeIso && e.data <= em7diasIso).sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))

  const contasVencendo = casaItens.filter((i) => i.cat === 'Contas' && i.venc && !i.done && i.venc >= hojeIso && i.venc <= em7diasIso)

  return {
    data_hoje: hojeIso,
    ultima_sincronizacao_do_app: snap?.data ? d.__updated_at || null : null,
    tirzepatida: Object.keys(tzMap).length > 0 ? { estoque_atual_mg: Number(bal?.current_balance_mg ?? 0), denise: tzMap.denise || null, flavio: tzMap.flavio || null } : null,
    sequencia_treinos_dias: sequencia(diasUnicos(treinos)),
    sequencia_leitura_dias: sequencia(diasUnicos(leituras)),
    sequencia_devocional_dias: sequencia(diasUnicos(devocionais)),
    livro_atual: d.dos_livro_atual || null,
    contas_vencendo_7dias: contasVencendo.map((c) => ({ nome: c.n, vencimento: c.venc })),
    agenda_proximos_7dias: agendaProximos7Dias,
    rotina_de_hoje: rotinaItens.map((it, i) => ({ horario: it.t, nome: it.n, categoria: it.cat, feito_hoje: rotinaDoneHoje.includes(i) })),
    medicamentos: d.dos_medicamentos || {},
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
  return 'Você é a Luna, assistente pessoal da Denise dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em português do Brasil. Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente números, datas ou fatos que não estão ali. Se um dado não estiver no contexto, diga com naturalidade que ele ainda não foi registrado no app. ' + (extra || '')
}
