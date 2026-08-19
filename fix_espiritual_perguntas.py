from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

# ---------------------------------------------------------------------------
# Troca o campo unico "Reflexao" pelas 10 perguntas de verdade que a Denise
# usa no devocional (metodo de estudo biblico), cada uma com seu proprio
# campo. Fica salvo por dia, igual antes, e da pra abrir qualquer dia
# anterior no historico pra ver as respostas daquele dia.
# ---------------------------------------------------------------------------

old_states = """function Espiritual(){
  const [ref,setRef]=React.useState('')
  const [reflex,setReflex]=React.useState('')
  const [grat,setGrat]=React.useState('')
  const [apren,setApren]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const [entries,setEntries]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})
  function isoHoje(){return isoBR(new Date())}
  function salvar(){
    const hoje=isoHoje()
    const reg={data:hoje,ref,reflex,grat,apren}
    const outros=entries.filter((e:any)=>e.data!==hoje)
    const n=[reg,...outros].sort((a:any,b:any)=>b.data.localeCompare(a.data))
    setEntries(n);localStorage.setItem('dos_devocionais',JSON.stringify(n))
    setSaved(true)
  }"""
new_states = """function Espiritual(){
  const PERGUNTAS_VAZIAS={mandamento:'',promessa:'',pecado:'',aplicacao:'',novoDeus:'',quem:'',oque:'',quando:'',onde:'',porque:''}
  const [ref,setRef]=React.useState('')
  const [perguntas,setPerguntas]=React.useState(PERGUNTAS_VAZIAS)
  const [grat,setGrat]=React.useState('')
  const [apren,setApren]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const [expandido,setExpandido]=React.useState<number|null>(null)
  const [entries,setEntries]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})
  function isoHoje(){return isoBR(new Date())}
  function setPergunta(campo:string,valor:string){setPerguntas(p=>({...p,[campo]:valor}))}
  function salvar(){
    const hoje=isoHoje()
    const reg={data:hoje,ref,...perguntas,grat,apren}
    const outros=entries.filter((e:any)=>e.data!==hoje)
    const n=[reg,...outros].sort((a:any,b:any)=>b.data.localeCompare(a.data))
    setEntries(n);localStorage.setItem('dos_devocionais',JSON.stringify(n))
    setSaved(true)
  }"""
s = replace_once(s, old_states, new_states, "espiritual-states-perguntas")

old_jsx = """        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Reflexão</label>
        <textarea value={reflex} onChange={e=>setReflex(e.target.value)} placeholder="O que Deus falou com você hoje?" rows={3} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12,resize:'none' as const}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Gratidão</label>
        <input value={grat} onChange={e=>setGrat(e.target.value)} placeholder="Sou grata por…" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Aprendizado</label>
        <input value={apren} onChange={e=>setApren(e.target.value)} placeholder="O que levo pro dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <button onClick={salvar} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Salvar devocional</button>
        {entries.length>0&&<div style={{marginTop:16,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:8,color:'rgba(255,255,255,.6)'}}>Últimos registros</div>
          {entries.slice(0,5).map((e:any,i:number)=>(<div key={i} style={{padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
            <div style={{display:'flex',justifyContent:'space-between' as const,marginBottom:2}}><span style={{fontWeight:700,fontSize:12.5,color:C.acc2}}>{e.ref||'—'}</span><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{e.data}</span></div>
            {e.grat&&<div style={{fontSize:11.5,color:'rgba(255,255,255,.5)'}}>Gratidão: {e.grat}</div>}
          </div>))}
        </div>}"""
new_jsx = """        <div style={{fontSize:12,fontWeight:700,color:'rgba(255,255,255,.6)',margin:'4px 0 8px'}}>Faça perguntas</div>
        {([
          ['mandamento','Existe um mandamento a obedecer?'],
          ['promessa','Uma promessa a reivindicar?'],
          ['pecado','Um pecado a evitar?'],
          ['aplicacao','Uma aplicação a fazer?'],
          ['novoDeus','Algo novo sobre Deus?'],
        ] as [string,string][]).map(([campo,label])=>(
          <div key={campo} style={{marginBottom:10}}>
            <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>{label}</label>
            <input value={(perguntas as any)[campo]} onChange={e=>setPergunta(campo,e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:13.5}}/>
          </div>
        ))}
        <div style={{fontSize:12,fontWeight:700,color:'rgba(255,255,255,.6)',margin:'12px 0 8px'}}>Pergunte</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
          {([
            ['quem','Quem?'],['oque','O quê?'],['quando','Quando?'],['onde','Onde?'],['porque','Por quê?'],
          ] as [string,string][]).map(([campo,label])=>(
            <div key={campo}>
              <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>{label}</label>
              <input value={(perguntas as any)[campo]} onChange={e=>setPergunta(campo,e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:13.5}}/>
            </div>
          ))}
        </div>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Gratidão</label>
        <input value={grat} onChange={e=>setGrat(e.target.value)} placeholder="Sou grata por…" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Aprendizado</label>
        <input value={apren} onChange={e=>setApren(e.target.value)} placeholder="O que levo pro dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <button onClick={salvar} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Salvar devocional</button>
        {entries.length>0&&<div style={{marginTop:16,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:8,color:'rgba(255,255,255,.6)'}}>Histórico ({entries.length} dia{entries.length===1?'':'s'})</div>
          {entries.slice(0,30).map((e:any,i:number)=>(<div key={i} style={{padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
            <div onClick={()=>setExpandido(x=>x===i?null:i)} style={{display:'flex',justifyContent:'space-between' as const,marginBottom:2,cursor:'pointer'}}><span style={{fontWeight:700,fontSize:12.5,color:C.acc2}}>{e.ref||'—'}</span><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{e.data} {expandido===i?'▲':'▼'}</span></div>
            {e.grat&&<div style={{fontSize:11.5,color:'rgba(255,255,255,.5)'}}>Gratidão: {e.grat}</div>}
            {expandido===i&&<div style={{marginTop:8,fontSize:11.5,color:'rgba(255,255,255,.6)',display:'grid',gap:5}}>
              {e.mandamento&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Mandamento a obedecer:</b> {e.mandamento}</div>}
              {e.promessa&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Promessa a reivindicar:</b> {e.promessa}</div>}
              {e.pecado&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Pecado a evitar:</b> {e.pecado}</div>}
              {e.aplicacao&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Aplicação a fazer:</b> {e.aplicacao}</div>}
              {e.novoDeus&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Algo novo sobre Deus:</b> {e.novoDeus}</div>}
              {e.quem&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Quem:</b> {e.quem}</div>}
              {e.oque&&<div><b style={{color:'rgba(255,255,255,.4)'}}>O quê:</b> {e.oque}</div>}
              {e.quando&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Quando:</b> {e.quando}</div>}
              {e.onde&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Onde:</b> {e.onde}</div>}
              {e.porque&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Por quê:</b> {e.porque}</div>}
              {e.apren&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Aprendizado:</b> {e.apren}</div>}
              {e.reflex&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Reflexão (registro antigo):</b> {e.reflex}</div>}
            </div>}
          </div>))}
        </div>}"""
s = replace_once(s, old_jsx, new_jsx, "espiritual-jsx-perguntas")

# reset das perguntas depois de salvar (o botao ja usa a funcao salvar, so falta limpar o
# formulario do dia depois de salvar, igual os outros campos)
old_setsaved = "    setEntries(n);localStorage.setItem('dos_devocionais',JSON.stringify(n))\n    setSaved(true)\n  }"
new_setsaved = "    setEntries(n);localStorage.setItem('dos_devocionais',JSON.stringify(n))\n    setSaved(true);setPerguntas(PERGUNTAS_VAZIAS)\n  }"
s = replace_once(s, old_setsaved, new_setsaved, "espiritual-reset-apos-salvar")

main_file.write_text(s)
print("OK - Espiritual atualizado:")
print(" - Campo unico 'Reflexao' virou as 10 perguntas de verdade (Faça perguntas + Pergunte:")
print("   Quem/O quê/Quando/Onde/Por quê), cada uma com seu campo, salvas por dia.")
print(" - Histórico agora mostra todos os dias (até 30 por vez) e cada dia pode ser clicado pra")
print("   abrir e ver as 10 respostas daquele dia, não só o resumo de 5 dias de antes.")
print(" - Registros antigos que só tinham o campo 'Reflexão' continuam aparecendo no histórico")
print("   (mostrados como 'Reflexão (registro antigo)') - nada se perde.")
