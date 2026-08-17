from pathlib import Path

def replace_once(s, old, new, label):
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"ABORTADO ({label}): encontrado {c} vezes, esperado 1. Nada foi alterado.")
    return s.replace(old, new, 1)

applied = []
p = Path("src/main.tsx")
s = p.read_text()

# --- 1. navItems: Assistente IA -> Luna ---
old1 = "['/assistente','Assistente IA','✨']"
new1 = "['/assistente','Luna','🌙']"
s = replace_once(s, old1, new1, "navitem-luna")
applied.append("navitem-luna")

# --- 2. Home: card "IA Assistente" -> "Luna" / botao "Abrir assistente" -> "Falar com a Luna" ---
old2 = """<Card title="IA Assistente"><div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'12px 13px',fontSize:13,color:'rgba(255,255,255,.7)',lineHeight:1.5,marginBottom:11}}>{g}, Denise! ☀️ Estoque tirzepatida: {tzBalance} mg. Próxima: {fmtIsoH(tzSched.denise?.next_application_date)}. Vamos juntas? 💜</div><NavLink to="/assistente" style={{display:'flex',alignItems:'center',justifyContent:'center',gap:6,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,textDecoration:'none'}}>Abrir assistente</NavLink></Card>"""
new2 = """<Card title="Luna"><div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'12px 13px',fontSize:13,color:'rgba(255,255,255,.7)',lineHeight:1.5,marginBottom:11}}>{g}, Denise! ☀️ Estoque tirzepatida: {tzBalance} mg. Próxima: {fmtIsoH(tzSched.denise?.next_application_date)}. Vamos juntas? 💜</div><NavLink to="/assistente" style={{display:'flex',alignItems:'center',justifyContent:'center',gap:6,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,textDecoration:'none'}}>Falar com a Luna</NavLink></Card>"""
s = replace_once(s, old2, new2, "home-card-luna")
applied.append("home-card-luna")

# --- 3. Reescreve Assistente() por completo: Luna de verdade (texto + imagem + audio) ---
old3 = """function Assistente(){const h=new Date().getHours(),g=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite';const [msgs,setMsgs]=React.useState([{me:false,t:`${g}, Denise! ☀️ Estoque tirzepatida: 217,5 mg (~151 dias). Sua próxima: 02/08. Flávio: 31/07. Como posso ajudar? 💜`}]);const [inp,setInp]=React.useState('');function reply(q:string){const ql=q.toLowerCase();if(ql.includes('estoque')||ql.includes('tirzepatida'))return'Estoque: 217,5 mg (~151 dias). Você: 02/08 · Flávio: 31/07.';if(ql.includes('próxim'))return'Sua próxima: 02/08 (5 mg). Flávio: 31/07 (2,5 mg).';if(ql.includes('água'))return'Registrado 💧 Quer que eu some no total?';if(ql.includes('score'))return'Score hoje: 75% — 12 de 16 hábitos.';if(ql.includes('rotina'))return'Hoje: Devocional ✓, escola ✓, calistenia ✓. Próximo: buscar Domi.';return'Anotado! 💜'}function send(){if(!inp.trim())return;const q=inp;setInp('');setMsgs(m=>[...m,{me:true,t:q}]);setTimeout(()=>setMsgs(m=>[...m,{me:false,t:reply(q)}]),400)}return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Assistente IA</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Direto, acolhedor e sem julgamento.</p><div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const,height:'60vh'}}><div style={{flex:1,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:12,paddingBottom:12}}>{msgs.map((m,i)=>(<div key={i} style={{maxWidth:'80%',padding:'11px 14px',borderRadius:14,fontSize:13.5,lineHeight:1.5,alignSelf:m.me?'flex-end':'flex-start',background:m.me?`linear-gradient(135deg,${C.acc},#7c3aed)`:'rgba(255,255,255,.06)',border:m.me?'none':`1px solid ${C.line}`}}>{m.t}</div>))}</div><div style={{display:'flex',flexWrap:'wrap' as const,gap:6,margin:'12px 0'}}>{['Resumo do dia','Próxima aplicação','Estoque tirzepatida','Score hoje'].map(c=>(<button key={c} onClick={()=>setInp(c)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:20,padding:'6px 12px',fontSize:11,color:'rgba(255,255,255,.6)',cursor:'pointer'}}>{c}</button>))}</div><div style={{display:'flex',gap:8,background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:12,padding:'8px 8px 8px 14px'}}><input value={inp} onChange={e=>setInp(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder="Pergunte qualquer coisa…" style={{flex:1,background:'none',border:'none',color:'#fff',fontSize:13.5,outline:'none'}}/><button onClick={send} style={{width:36,height:36,borderRadius:10,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',cursor:'pointer',fontSize:18}}>↑</button></div></div></div>)}"""

new3 = """function Assistente(){
  const h=new Date().getHours(),g=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite'
  const [tzSched,setTzSched]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [tzBalance,setTzBalance]=React.useState(0)
  React.useEffect(()=>{(async()=>{
    const [{data:sched},{data:bal}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
    ])
    const map:Record<string,any>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={planned_dose_mg:Number(row.planned_dose_mg),interval_days:row.interval_days,next_application_date:row.next_application_date}})
    setTzSched(map)
    setTzBalance(Number(bal?.current_balance_mg??0))
  })()},[])
  const [msgs,setMsgs]=React.useState<{me:boolean,t:string}[]>([{me:false,t:`${g}, Denise! Sou a Luna 💜 Pode falar comigo por texto, áudio ou mandar uma foto. Como posso ajudar?`}])
  const [inp,setInp]=React.useState('')
  const [sending,setSending]=React.useState(false)
  const [pendingImg,setPendingImg]=React.useState<{mediaType:string,base64:string,preview:string}|null>(null)
  const [recording,setRecording]=React.useState(false)
  const fileRef=React.useRef<HTMLInputElement>(null)
  const mediaRecRef=React.useRef<MediaRecorder|null>(null)
  const chunksRef=React.useRef<Blob[]>([])

  function toBase64(blob:Blob):Promise<string>{return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(String(r.result).split(',')[1]||'');r.onerror=rej;r.readAsDataURL(blob)})}

  function montarContexto(){
    const treinosI=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]
    const leiturasI=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
    const devI=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
    const casaI=(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})() as any[]
    const livroI=(()=>{try{return JSON.parse(localStorage.getItem('dos_livro_atual')||'null')}catch{return null}})() as any
    function diasUnicos(entries:any[]):Set<string>{return new Set(entries.map((e:any)=>e.data))}
    function sequencia(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(d.toISOString().slice(0,10))){n++;d.setDate(d.getDate()-1)}return n}
    const hojeIso=new Date().toISOString().slice(0,10)
    const em7diasIso=new Date(Date.now()+7*86400000).toISOString().slice(0,10)
    const contasVencendo=casaI.filter((i:any)=>i.cat==='Contas'&&i.venc&&!i.done&&i.venc>=hojeIso&&i.venc<=em7diasIso)
    return {
      data_hoje:hojeIso,
      tirzepatida:Object.keys(tzSched).length>0?{estoque_atual_mg:tzBalance,denise:tzSched.denise||null,flavio:tzSched.flavio||null}:null,
      sequencia_treinos_dias:sequencia(diasUnicos(treinosI)),
      sequencia_leitura_dias:sequencia(diasUnicos(leiturasI)),
      sequencia_devocional_dias:sequencia(diasUnicos(devI)),
      livro_atual:livroI,
      contas_vencendo_7dias:contasVencendo.map((c:any)=>({nome:c.n,vencimento:c.venc})),
    }
  }

  async function send(extra?:{audio?:{mediaType:string,base64:string}}){
    if(sending)return
    const text=inp.trim()
    const img=pendingImg
    const audio=extra?.audio
    if(!text&&!img&&!audio)return
    setSending(true)
    setInp('')
    setPendingImg(null)
    const displayText=text||(img?'📷 Imagem enviada':'🎤 Áudio enviado')
    const historyForApi=[...msgs]
    setMsgs(m=>[...m,{me:true,t:displayText}])
    try{
      const resp=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
        message:text,
        history:historyForApi,
        context:montarContexto(),
        images:img?[{mediaType:img.mediaType,base64:img.base64}]:undefined,
        audio,
      })})
      const data=await resp.json()
      if(!resp.ok) throw new Error(data?.error||'Erro ao falar com a Luna.')
      setMsgs(m=>[...m,{me:false,t:data.reply}])
    }catch(err:any){
      setMsgs(m=>[...m,{me:false,t:'😕 '+(err?.message||'Não consegui responder agora. Tenta de novo?')}])
    }
    setSending(false)
  }

  async function escolherImagem(e:React.ChangeEvent<HTMLInputElement>){
    const file=e.target.files?.[0]
    e.target.value=''
    if(!file)return
    const base64=await toBase64(file)
    setPendingImg({mediaType:file.type,base64,preview:URL.createObjectURL(file)})
  }

  async function iniciarGravacao(){
    try{
      const stream=await navigator.mediaDevices.getUserMedia({audio:true})
      const rec=new MediaRecorder(stream)
      chunksRef.current=[]
      rec.ondataavailable=e=>chunksRef.current.push(e.data)
      rec.start()
      mediaRecRef.current=rec
      setRecording(true)
    }catch{
      setMsgs(m=>[...m,{me:false,t:'Não consegui acessar o microfone. Verifica a permissão de áudio do navegador.'}])
    }
  }

  function pararEEnviarGravacao(){
    const rec=mediaRecRef.current
    if(!rec)return
    rec.onstop=async()=>{
      rec.stream.getTracks().forEach(t=>t.stop())
      const blob=new Blob(chunksRef.current,{type:rec.mimeType||'audio/webm'})
      const base64=await toBase64(blob)
      send({audio:{mediaType:blob.type||'audio/webm',base64}})
    }
    rec.stop()
    setRecording(false)
  }

  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Luna</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Sua assistente pessoal — entende texto, áudio e imagem.</p>
    <div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const,height:'60vh'}}>
      <div style={{flex:1,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:12,paddingBottom:12}}>
        {msgs.map((m,i)=>(<div key={i} style={{maxWidth:'80%',padding:'11px 14px',borderRadius:14,fontSize:13.5,lineHeight:1.5,alignSelf:m.me?'flex-end':'flex-start',background:m.me?`linear-gradient(135deg,${C.acc},#7c3aed)`:'rgba(255,255,255,.06)',border:m.me?'none':`1px solid ${C.line}`,whiteSpace:'pre-wrap' as const}}>{m.t}</div>))}
        {sending&&<div style={{alignSelf:'flex-start',padding:'11px 14px',borderRadius:14,fontSize:13.5,background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)'}}>Luna está digitando…</div>}
      </div>
      {pendingImg&&<div style={{display:'flex',alignItems:'center',gap:8,margin:'8px 0',background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:10,padding:8}}>
        <img src={pendingImg.preview} style={{width:44,height:44,borderRadius:8,objectFit:'cover' as const}}/>
        <span style={{fontSize:12,color:'rgba(255,255,255,.5)',flex:1}}>Imagem anexada</span>
        <button onClick={()=>setPendingImg(null)} style={{background:'none',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:16}}>✕</button>
      </div>}
      <div style={{display:'flex',flexWrap:'wrap' as const,gap:6,margin:'12px 0'}}>{['Resumo do dia','Estoque tirzepatida','Contas a vencer','Sequência de leitura'].map(c=>(<button key={c} onClick={()=>setInp(c)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:20,padding:'6px 12px',fontSize:11,color:'rgba(255,255,255,.6)',cursor:'pointer'}}>{c}</button>))}</div>
      <div style={{display:'flex',gap:8,background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:12,padding:'8px 8px 8px 14px',alignItems:'center'}}>
        <input ref={fileRef} type="file" accept="image/*" style={{display:'none'}} onChange={escolherImagem}/>
        <button onClick={()=>fileRef.current?.click()} disabled={sending||recording} title="Anexar imagem" style={{background:'none',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:18,flexShrink:0}}>📷</button>
        <button onClick={recording?pararEEnviarGravacao:iniciarGravacao} disabled={sending} title={recording?'Parar e enviar':'Gravar áudio'} style={{background:'none',border:'none',color:recording?C.danger:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:18,flexShrink:0}}>{recording?'⏹':'🎤'}</button>
        <input value={inp} onChange={e=>setInp(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder={recording?'Gravando áudio…':'Pergunte qualquer coisa…'} disabled={recording} style={{flex:1,background:'none',border:'none',color:'#fff',fontSize:13.5,outline:'none'}}/>
        <button onClick={()=>send()} disabled={sending||recording||(!inp.trim()&&!pendingImg)} style={{width:36,height:36,borderRadius:10,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',cursor:'pointer',fontSize:18,flexShrink:0,opacity:(sending||recording||(!inp.trim()&&!pendingImg))?0.5:1}}>↑</button>
      </div>
    </div>
  </div>)
}"""

s = replace_once(s, old3, new3, "assistente-luna-rewrite")
applied.append("assistente-luna-rewrite")

p.write_text(s)
print("TUDO OK:", applied)
