from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# ============================================================
# 1) src/main.tsx - o app sincroniza sozinho a cada 30s e sempre sobrescrevia o banco com
#    o que tava no seu celular/pc, apagando qualquer coisa marcada como feita pelo servidor
#    (via WhatsApp). Agora antes de mandar pro banco, o app busca o que ja tem la, junta com
#    o que tem local (sem perder nada de nenhum dos dois lados) e so depois manda.
# ============================================================
main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_sync = """    function sincronizarSnapshot(){
      const dados:Record<string,any>={}
      for(let i=0;i<localStorage.length;i++){
        const k=localStorage.key(i)
        if(!k||!k.startsWith('dos_')||EXCLUIR.includes(k))continue
        const v=localStorage.getItem(k)
        if(v===null)continue
        try{dados[k]=JSON.parse(v)}catch{dados[k]=v}
      }
      supabase.from('app_snapshot').upsert({id:'denise',data:dados,updated_at:new Date().toISOString()}).then(()=>{})
    }"""
new_sync = """    async function sincronizarSnapshot(){
      const dados:Record<string,any>={}
      for(let i=0;i<localStorage.length;i++){
        const k=localStorage.key(i)
        if(!k||!k.startsWith('dos_')||EXCLUIR.includes(k))continue
        const v=localStorage.getItem(k)
        if(v===null)continue
        try{dados[k]=JSON.parse(v)}catch{dados[k]=v}
      }
      try{
        const {data:snap}=await supabase.from('app_snapshot').select('data').eq('id','denise').maybeSingle()
        const remoto=snap?.data||{}
        const chaveHoje=`dos_rotina_done_${isoBR(new Date())}`
        if(Array.isArray(remoto[chaveHoje])){
          const uniao=Array.from(new Set([...(dados[chaveHoje]||[]),...remoto[chaveHoje]]))
          dados[chaveHoje]=uniao
          localStorage.setItem(chaveHoje,JSON.stringify(uniao))
        }
      }catch{}
      supabase.from('app_snapshot').upsert({id:'denise',data:dados,updated_at:new Date().toISOString()}).then(()=>{})
    }"""
s = replace_once(s, old_sync, new_sync, "sync-merge-done-hoje")
main_file.write_text(s)

# ============================================================
# 2) api/_cronlib.js - contexto passa a saber o que ficou pendente da rotina de ONTEM
#    (comparando os itens que valiam pra ontem com o que foi marcado feito naquele dia).
# ============================================================
cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_ctx1 = """  const rotinaItens = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
  const rotinaDoneHoje = Array.isArray(d[`dos_rotina_done_${hojeIso}`]) ? d[`dos_rotina_done_${hojeIso}`] : []"""
new_ctx1 = """  const rotinaItens = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
  const rotinaDoneHoje = Array.isArray(d[`dos_rotina_done_${hojeIso}`]) ? d[`dos_rotina_done_${hojeIso}`] : []
  const ontemIso = dataIsoBR(-1)
  const diaSemanaOntem = new Date(ontemIso + 'T12:00:00-03:00').getDay()
  const rotinaDoneOntem = Array.isArray(d[`dos_rotina_done_${ontemIso}`]) ? d[`dos_rotina_done_${ontemIso}`] : []
  const rotinaPendenteOntem = rotinaItens
    .map((it, i) => ({ it, i }))
    .filter(({ it, i }) => (!it.dias || it.dias.includes(diaSemanaOntem)) && !rotinaDoneOntem.includes(i))
    .map(({ it }) => ({ horario: it.t, nome: it.n, categoria: it.cat }))"""
c = replace_once(c, old_ctx1, new_ctx1, "cronlib-pendente-ontem-calculo")

old_ctx2 = """    rotina_de_hoje: rotinaItens.map((it, i) => ({ horario: it.t, nome: it.n, categoria: it.cat, feito_hoje: rotinaDoneHoje.includes(i) })),"""
new_ctx2 = """    rotina_de_hoje: rotinaItens.map((it, i) => ({ horario: it.t, nome: it.n, categoria: it.cat, feito_hoje: rotinaDoneHoje.includes(i) })),
    rotina_pendente_ontem: rotinaPendenteOntem,"""
c = replace_once(c, old_ctx2, new_ctx2, "cronlib-pendente-ontem-no-contexto")
cronlib_file.write_text(c)

# ============================================================
# 3) api/cron-morning.js - a mensagem de bom dia passa a abrir com o que ficou em aberto
#    ontem, antes da lista de hoje.
# ============================================================
morning_file = Path("api/cron-morning.js")
if not morning_file.exists():
    raise SystemExit("ABORTADO (cron-morning-nao-encontrado): rode este script na raiz do projeto denise-os.")
m = morning_file.read_text()

old_pedido = """    const pedido = 'Escreva a mensagem de bom dia da Denise. Comece com "Bom dia, Denise! ☀️" e liste, de forma organizada e curta, tudo que ela tem para fazer hoje:"""
new_pedido = """    const pedido = 'Escreva a mensagem de bom dia da Denise. Comece com "Bom dia, Denise! ☀️". Se rotina_pendente_ontem tiver itens, inclua logo no início uma seção curta "📌 Ficou em aberto ontem" listando esses itens (nome e horário), sem cobrar de forma pesada, só lembrando com carinho. Depois liste, de forma organizada e curta, tudo que ela tem para fazer hoje:"""
m = replace_once(m, old_pedido, new_pedido, "cron-morning-pendente-ontem")
morning_file.write_text(m)

# ============================================================
# 4) api/whatsapp-webhook.js - antes de responder normal, a Luna checa se a mensagem da
#    Denise confirma que ela fez algo da rotina de hoje (tipo "ja fiz", "consegui buscar a
#    Domi"). Se confirmar, marca como feito de verdade no banco e responde confirmando -
#    a partir dai o cron-check (cobranca a cada 30 min) para de avisar sobre esse item.
# ============================================================
webhook_file = Path("api/whatsapp-webhook.js")
if not webhook_file.exists():
    raise SystemExit("ABORTADO (webhook-nao-encontrado): rode este script na raiz do projeto denise-os.")
w = webhook_file.read_text()

old_import = """import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt } from './_cronlib.js'"""
new_import = """import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin } from './_cronlib.js'

async function tentarMarcarFeito(number, userText, context) {
  const pendentes = (context.rotina_de_hoje || []).map((it, idx) => ({ idx, ...it })).filter((it) => !it.feito_hoje)
  if (pendentes.length === 0 || !userText) return false
  try {
    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos":[numeros]}. A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '". Aqui estao os itens da rotina de hoje que AINDA NAO foram marcados como feitos, cada um com seu id: ' + JSON.stringify(pendentes.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '. Se a mensagem confirmar que ela fez um ou mais desses itens agora (ex: "ja fiz o X", "feito", "acabei de Y", "consegui buscar a Domi"), coloque os ids correspondentes em "feitos". Se a mensagem nao for uma confirmacao de tarefa feita (for pergunta, comentario, ou nao bater com nenhum item da lista), responda {"feitos":[]}.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\\{[\\s\\S]*\\}/)
    const parsed = match ? JSON.parse(match[0]) : { feitos: [] }
    const feitos = Array.isArray(parsed.feitos) ? parsed.feitos.filter((n) => typeof n === 'number' && pendentes.some((p) => p.idx === n)) : []
    if (feitos.length === 0) return false
    const supabase = getSupabaseAdmin()
    if (!supabase) return false
    const chave = `dos_rotina_done_${context.data_hoje}`
    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}
    const atual = Array.isArray(d[chave]) ? d[chave] : []
    const uniao = Array.from(new Set([...atual, ...feitos]))
    await supabase.from('app_snapshot').upsert({ id: 'denise', data: { ...d, [chave]: uniao }, updated_at: new Date().toISOString() })
    const nomes = pendentes.filter((p) => feitos.includes(p.idx)).map((p) => p.nome)
    await sendWhatsappText(number, '✅ Marquei como feito: ' + nomes.join(', ') + '!')
    return true
  } catch {
    return false
  }
}"""
w = replace_once(w, old_import, new_import, "webhook-adiciona-classificador")

old_reply = """    const context = await buildLunaContext()
    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent)"""
new_reply = """    const context = await buildLunaContext()

    if (userText) {
      const marcou = await tentarMarcarFeito(number, userText, context)
      if (marcou) {
        res.status(200).json({ ok: true })
        return
      }
    }

    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent)"""
w = replace_once(w, old_reply, new_reply, "webhook-usa-classificador-antes-do-chat")
webhook_file.write_text(w)

# ============================================================
# 5) api/cron-check.js - rota nova que cobra CADA item da Minha Rotina (todos os temas) e
#    de CADA remedio, no horario certo. Roda a cada 30 min pelo cron-job.org (a Vercel
#    gratuita so deixa 1x por dia, por isso essa rota nao entra no vercel.json).
# ============================================================
CONTEUDO_CRON_CHECK = '''import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin } from './_cronlib.js'

function dataIsoBR() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date())
}

function horaAgoraBR() {
  const partes = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).formatToParts(new Date())
  const h = Number(partes.find((p) => p.type === 'hour')?.value || '0')
  const m = Number(partes.find((p) => p.type === 'minute')?.value || '0')
  return h * 60 + m
}

function paraMinutos(hhmm) {
  const m = /^(\\d{1,2}):(\\d{2})$/.exec((hhmm || '').trim())
  if (!m) return null
  return Number(m[1]) * 60 + Number(m[2])
}

const JANELA_MIN = 30

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
  const supabase = getSupabaseAdmin()
  if (!supabase) {
    res.status(500).json({ error: 'Supabase nao configurado.' })
    return
  }
  try {
    const hojeIso = dataIsoBR()
    const agoraMin = horaAgoraBR()
    const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()

    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}
    const rotina = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
    const doneHoje = Array.isArray(d[`dos_rotina_done_${hojeIso}`]) ? d[`dos_rotina_done_${hojeIso}`] : []
    const medicamentos = d.dos_medicamentos || {}

    function estaNaJanela(hhmm) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      return min <= agoraMin && min > agoraMin - JANELA_MIN
    }

    const avisos = []

    rotina.forEach((item, i) => {
      if (item.dias && !item.dias.includes(diaSemanaHoje)) return
      if (doneHoje.includes(i)) return
      if (estaNaJanela(item.t)) avisos.push(`⏰ ${item.t} · ${item.n}`)
    })

    Object.keys(medicamentos).forEach((pessoaId) => {
      const lista = Array.isArray(medicamentos[pessoaId]) ? medicamentos[pessoaId] : []
      lista.forEach((m) => {
        if (m.ate && m.ate < hojeIso) return
        const horarios = (m.horarios || '').split(',').map((h) => h.trim()).filter(Boolean)
        horarios.forEach((h) => {
          if (!estaNaJanela(h)) return
          const quem = pessoaId === 'denise' ? '' : ` (${pessoaId === 'flavio' ? 'Flávio' : pessoaId})`
          avisos.push(`💊 ${h} · ${m.nome}${m.dosagem ? ` ${m.dosagem}` : ''}${quem}`)
        })
      })
    })

    if (avisos.length === 0) {
      res.status(200).json({ ok: true, avisos_enviados: 0 })
      return
    }

    const texto = '🔔 Está na hora de:\\n\\n' + avisos.join('\\n')
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true, avisos_enviados: avisos.length })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
'''

api_dir = Path("api")
if not api_dir.is_dir():
    raise SystemExit("ABORTADO (pasta-api-nao-encontrada): rode este script na raiz do projeto denise-os.")
(api_dir / "cron-check.js").write_text(CONTEUDO_CRON_CHECK)

print("OK - Tudo aplicado:")
print(" 1) Sincronizacao do app agora funde com o servidor, nao apaga mais o que a Luna marca.")
print(" 2) Bom dia agora avisa o que ficou em aberto de ontem, alem da lista de hoje.")
print(" 3) Se voce disser 'ja fiz X' pelo WhatsApp, a Luna marca de verdade e confirma.")
print(" 4) api/cron-check.js criado - cobra CADA item da rotina e remedio no horario certo,")
print("    a cada 30 min. PRECISA do cron-job.org configurado (rota nao entra no vercel.json):")
print("    URL: https://denise-os.vercel.app/api/cron-check | a cada 30 min | metodo POST")
