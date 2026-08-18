import json
from pathlib import Path

applied = []

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# --- 1) api/whatsapp.js (novo arquivo) ---
api_dir = Path("api")
wa_file = api_dir / "whatsapp.js"
if wa_file.exists():
    raise SystemExit("ABORTADO (whatsapp-js-exists): api/whatsapp.js ja existe. Nada foi alterado.")

api_dir.mkdir(exist_ok=True)
wa_content = """const APP_URL = 'https://denise-os.vercel.app'

function getConfig() {
  const baseUrl = (process.env.EVOLUTION_API_URL || '').replace(/\\/+$/, '')
  const apiKey = process.env.EVOLUTION_API_KEY
  const instance = process.env.EVOLUTION_INSTANCE || 'denise-os'
  return { baseUrl, apiKey, instance }
}

async function evoFetch(baseUrl, apiKey, path, opts = {}) {
  const resp = await fetch(baseUrl + path, {
    ...opts,
    headers: { 'content-type': 'application/json', apikey: apiKey, ...(opts.headers || {}) }
  })
  const data = await resp.json().catch(() => ({}))
  return { ok: resp.ok, status: resp.status, data }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Metodo nao permitido.' })
    return
  }
  const { baseUrl, apiKey, instance } = getConfig()
  if (!baseUrl || !apiKey) {
    res.status(500).json({ error: 'Evolution API nao configurada no servidor (EVOLUTION_API_URL / EVOLUTION_API_KEY).' })
    return
  }
  const { action } = req.body || {}

  try {
    if (action === 'status') {
      const r = await evoFetch(baseUrl, apiKey, `/instance/connectionState/${instance}`)
      if (!r.ok) {
        res.status(200).json({ state: 'nao_criada' })
        return
      }
      const state = r.data?.instance?.state || r.data?.state || 'close'
      res.status(200).json({ state })
      return
    }

    if (action === 'connect') {
      let r = await evoFetch(baseUrl, apiKey, `/instance/connect/${instance}`)
      if (!r.ok) {
        await evoFetch(baseUrl, apiKey, '/instance/create', {
          method: 'POST',
          body: JSON.stringify({
            instanceName: instance,
            qrcode: true,
            integration: 'WHATSAPP-BAILEYS',
            webhook: {
              url: `${APP_URL}/api/whatsapp-webhook`,
              byEvents: false,
              base64: true,
              events: ['MESSAGES_UPSERT']
            }
          })
        })
        r = await evoFetch(baseUrl, apiKey, `/instance/connect/${instance}`)
      }
      if (!r.ok) {
        res.status(502).json({ error: r.data?.message || r.data?.error || 'Erro ao conectar a instancia na Evolution API.' })
        return
      }
      const base64 = r.data?.base64 || r.data?.qrcode?.base64 || null
      const pairingCode = r.data?.pairingCode || r.data?.code || null
      if (!base64 && !pairingCode) {
        res.status(200).json({ base64: null, pairingCode: null, message: 'Numero ja pode estar conectado. Verifique o status.' })
        return
      }
      res.status(200).json({ base64, pairingCode })
      return
    }

    if (action === 'logout') {
      await evoFetch(baseUrl, apiKey, `/instance/logout/${instance}`, { method: 'DELETE' })
      res.status(200).json({ ok: true })
      return
    }

    res.status(400).json({ error: 'Acao invalida.' })
  } catch (err) {
    res.status(500).json({ error: 'Falha ao falar com a Evolution API: ' + (err?.message || 'erro desconhecido') })
  }
}
"""
wa_file.write_text(wa_content)
applied.append("create-api-whatsapp")

# --- 2) api/whatsapp-webhook.js (novo arquivo) ---
wh_file = api_dir / "whatsapp-webhook.js"
if wh_file.exists():
    raise SystemExit("ABORTADO (webhook-js-exists): api/whatsapp-webhook.js ja existe. Nada foi alterado.")

wh_content = """import { createClient } from '@supabase/supabase-js'

function getEvoConfig() {
  const baseUrl = (process.env.EVOLUTION_API_URL || '').replace(/\\/+$/, '')
  const apiKey = process.env.EVOLUTION_API_KEY
  const instance = process.env.EVOLUTION_INSTANCE || 'denise-os'
  return { baseUrl, apiKey, instance }
}

async function sendWhatsappText(baseUrl, apiKey, instance, number, text) {
  await fetch(`${baseUrl}/message/sendText/${instance}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', apikey: apiKey },
    body: JSON.stringify({ number, text })
  })
}

async function transcribeAudio(base64, mediaType) {
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

async function buildContext() {
  const url = process.env.VITE_SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  const hojeIso = new Date().toISOString().slice(0, 10)
  if (!url || !serviceKey) {
    return { data_hoje: hojeIso, tirzepatida: null }
  }
  const supabase = createClient(url, serviceKey)
  const [{ data: sched }, { data: bal }] = await Promise.all([
    supabase.from('tirzepatida_schedule').select('*'),
    supabase.from('tirzepatida_stock_balance').select('*').maybeSingle()
  ])
  const map = {}
  ;(sched || []).forEach((row) => {
    map[row.person] = { planned_dose_mg: Number(row.planned_dose_mg), interval_days: row.interval_days, next_application_date: row.next_application_date }
  })
  return {
    data_hoje: hojeIso,
    tirzepatida: (sched || []).length > 0 ? { estoque_atual_mg: Number(bal?.current_balance_mg ?? 0), denise: map.denise || null, flavio: map.flavio || null } : null
  }
}

async function askLuna(systemPrompt, userContent) {
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY nao configurada.')
  const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 600,
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }]
    })
  })
  const data = await anthropicResp.json()
  if (!anthropicResp.ok) throw new Error(data?.error?.message || 'Erro ao consultar a IA.')
  return data.content?.find((b) => b.type === 'text')?.text || 'Desculpa, não consegui responder agora.'
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(200).json({ ok: true })
    return
  }
  const { baseUrl, apiKey, instance } = getEvoConfig()
  try {
    const body = req.body || {}
    const event = body.event || ''
    if (event && !/messages\\.?upsert/i.test(event)) {
      res.status(200).json({ ok: true })
      return
    }

    const data = body.data || {}
    const key = data.key || {}
    if (key.fromMe) {
      res.status(200).json({ ok: true })
      return
    }
    const remoteJid = key.remoteJid || ''
    if (!remoteJid || remoteJid.endsWith('@g.us')) {
      res.status(200).json({ ok: true })
      return
    }
    const number = remoteJid.split('@')[0]

    const allowed = (process.env.EVOLUTION_ALLOWED_NUMBERS || '').split(',').map((s) => s.trim()).filter(Boolean)
    if (allowed.length && !allowed.includes(number)) {
      res.status(200).json({ ok: true })
      return
    }

    const msg = data.message || {}
    let userText = (msg.conversation || msg.extendedTextMessage?.text || '').trim()

    if (msg.audioMessage && data.message.base64) {
      try {
        const transcript = await transcribeAudio(data.message.base64, msg.audioMessage.mimetype || 'audio/ogg')
        userText = userText ? (userText + '\\n\\n(audio transcrito): ' + transcript) : transcript
      } catch {
        await sendWhatsappText(baseUrl, apiKey, instance, number, 'Recebi seu áudio mas não consegui entender agora. Pode tentar de novo ou escrever?')
        res.status(200).json({ ok: true })
        return
      }
    }

    const userContent = []
    if (msg.imageMessage && data.message.base64) {
      userContent.push({ type: 'image', source: { type: 'base64', media_type: msg.imageMessage.mimetype || 'image/jpeg', data: data.message.base64 } })
    }

    if (!userText && userContent.length === 0) {
      res.status(200).json({ ok: true })
      return
    }
    userContent.push({ type: 'text', text: userText || 'A Denise enviou uma imagem sem legenda pelo WhatsApp. Comente o que você vê e pergunte no que pode ajudar.' })

    const context = await buildContext()
    const systemPrompt = 'Você é a Luna, assistente pessoal da Denise, respondendo agora pelo WhatsApp dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em português do Brasil, com respostas curtas (2 a 5 frases). Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente números, datas ou fatos que não estão ali. Se um dado não estiver no contexto, diga com naturalidade que ele ainda não foi registrado no app.\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent)
    await sendWhatsappText(baseUrl, apiKey, instance, number, reply)
    res.status(200).json({ ok: true })
  } catch {
    res.status(200).json({ ok: true })
  }
}
"""
wh_file.write_text(wh_content)
applied.append("create-api-whatsapp-webhook")

# --- 3) src/main.tsx: adiciona estado/funcoes do WhatsApp dentro de Config() ---
main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")

src = main_file.read_text()

old_hooks = "  const [saved,setSaved]=React.useState(false);\n  function salvarConfig(){"
new_hooks = """  const [saved,setSaved]=React.useState(false);
  const [waState,setWaState]=React.useState<'carregando'|'nao_criada'|'close'|'connecting'|'open'|'erro'>('carregando')
  const [waQr,setWaQr]=React.useState<string|null>(null)
  const [waPairingCode,setWaPairingCode]=React.useState<string|null>(null)
  const [waLoading,setWaLoading]=React.useState(false)
  const [waErro,setWaErro]=React.useState<string|null>(null)
  async function verificarStatusWhatsapp(){
    try{
      const resp=await fetch('/api/whatsapp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'status'})})
      const data=await resp.json()
      if(!resp.ok){setWaState('erro');setWaErro(data?.error||'Erro ao verificar status.');return}
      setWaState(data.state||'nao_criada')
      if(data.state==='open'){setWaQr(null);setWaPairingCode(null)}
    }catch{setWaState('erro');setWaErro('Não consegui falar com o servidor.')}
  }
  React.useEffect(()=>{verificarStatusWhatsapp()},[])
  React.useEffect(()=>{
    if(waState!=='connecting')return
    const t=setInterval(verificarStatusWhatsapp,4000)
    return()=>clearInterval(t)
  },[waState])
  async function conectarWhatsapp(){
    setWaLoading(true)
    setWaErro(null)
    try{
      const resp=await fetch('/api/whatsapp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'connect'})})
      const data=await resp.json()
      if(!resp.ok)throw new Error(data?.error||'Erro ao conectar.')
      setWaQr(data.base64||null)
      setWaPairingCode(data.pairingCode||null)
      setWaState('connecting')
    }catch(err:any){setWaErro(err?.message||'Erro ao conectar.')}
    setWaLoading(false)
  }
  function salvarConfig(){"""
src = replace_once(src, old_hooks, new_hooks, "config-hooks")
applied.append("config-hooks")

old_card = ">Limpar</button></div></Card></div><button onClick={salvarConfig}"
new_card = """>Limpar</button></div></Card><Card title="WhatsApp (Luna)"><p style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:14}}>Conecte seu WhatsApp para conversar com a Luna por lá também — o QR Code aparece aqui, sem sair do app.</p>{waState==='carregando'&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Verificando conexão...</div>}{waState==='open'&&<div style={{display:'flex',alignItems:'center',gap:10}}><span style={{width:10,height:10,borderRadius:'50%',background:C.ok,flexShrink:0}}/><span style={{fontSize:13,color:C.ok,fontWeight:600}}>WhatsApp conectado</span></div>}{(waState==='close'||waState==='nao_criada'||waState==='erro')&&<div><div style={{display:'flex',alignItems:'center',gap:10,marginBottom:12}}><span style={{width:10,height:10,borderRadius:'50%',background:'rgba(255,255,255,.25)',flexShrink:0}}/><span style={{fontSize:13,color:'rgba(255,255,255,.5)'}}>WhatsApp não conectado</span></div><button onClick={conectarWhatsapp} disabled={waLoading} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'9px 16px',fontSize:12,fontWeight:700,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Gerando QR Code...':'Gerar QR Code'}</button></div>}{waState==='connecting'&&<div style={{display:'flex',flexDirection:'column' as const,alignItems:'center',gap:10}}>{waQr&&<img src={`data:image/png;base64,${waQr}`} alt="QR Code do WhatsApp" style={{width:180,height:180,borderRadius:10,background:'#fff',padding:8}}/>}{waPairingCode&&<div style={{fontSize:13,color:'rgba(255,255,255,.7)'}}>Código: <strong>{waPairingCode}</strong></div>}<div style={{fontSize:12,color:'rgba(255,255,255,.4)',textAlign:'center' as const}}>Abra o WhatsApp {'>'} Aparelhos conectados {'>'} Conectar um aparelho e escaneie o QR Code.</div><button onClick={conectarWhatsapp} disabled={waLoading} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer'}}>Atualizar QR Code</button></div>}{waErro&&<div style={{marginTop:10,fontSize:12,color:C.danger}}>{waErro}</div>}</Card></div><button onClick={salvarConfig}"""
src = replace_once(src, old_card, new_card, "config-card")
applied.append("config-card")

main_file.write_text(src)

print("TUDO OK:", applied)
