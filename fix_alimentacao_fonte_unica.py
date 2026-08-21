from pathlib import Path

p = Path("src/main.tsx")
s = p.read_text()
applied = []

def replace_once(s, old, new, label):
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {c}. Nada foi alterado.")
    applied.append(label)
    return s.replace(old, new, 1)

# 1) Causa raiz do valor errado: dos_prot/dos_refs nunca tinham data (diferente da
#    agua, que ja usa um mapa por dia). Substitui por dos_refs_log (mapa iso->refeicoes),
#    com proteina/calorias derivados sempre da soma das refeicoes de hoje - fonte unica
#    de verdade, usada por Alimentacao, Home, Insights e Relatorios.
old1 = "const navItems=[['/', 'Home','🏠'],['/agenda','Agenda','📅'],['/espiritual','Espiritual','📖'],['/saude','Saúde','❤️'],['/alimentacao','Alimentação','🍽️'],['/exercicios','Exercícios','💪'],['/familia','Família','👨‍👩‍👧'],['/trabalho','Trabalho','💼'],['/desenvolvimento','Desenvolvimento','📈'],['/casa','Casa','🏡'],['/insights','Insights','💡'],['/relatorios','Relatórios','📊'],['/assistente','Luna','🌙'],['/config','Configurações','⚙️']]"
new1 = '''type RefEntry={id:string,tipo:string,nome:string,prot?:number,cal?:number,carb?:number,gord?:number,hora:string,origem?:'app'|'whatsapp'}
function lerRefsLog():Record<string,RefEntry[]>{
  try{return JSON.parse(localStorage.getItem('dos_refs_log')||'{}')}catch{return {}}
}
function salvarRefsLog(log:Record<string,RefEntry[]>){
  localStorage.setItem('dos_refs_log',JSON.stringify(log))
}
function lerRefeicoesDia(iso:string):RefEntry[]{
  return lerRefsLog()[iso]||[]
}
function salvarRefeicoesDia(iso:string,lista:RefEntry[]){
  const log=lerRefsLog();log[iso]=lista;salvarRefsLog(log)
}
function totalProteinaDia(iso:string):number{
  return lerRefeicoesDia(iso).reduce((a,r)=>a+(r.prot||0),0)
}
function lerMetaProteina():number{return Number(localStorage.getItem('dos_meta_prot_g')||120)}
function lerMetaCalorias():number|null{const v=localStorage.getItem('dos_meta_kcal');return v?Number(v):null}
function lerMetaRefeicoes():number|null{const v=localStorage.getItem('dos_meta_refeicoes');return v?Number(v):null}
function novoIdRef():string{return `${Date.now()}_${Math.random().toString(36).slice(2,8)}`}
const navItems=[['/', 'Home','🏠'],['/agenda','Agenda','📅'],['/espiritual','Espiritual','📖'],['/saude','Saúde','❤️'],['/alimentacao','Alimentação','🍽️'],['/exercicios','Exercícios','💪'],['/familia','Família','👨‍👩‍👧'],['/trabalho','Trabalho','💼'],['/desenvolvimento','Desenvolvimento','📈'],['/casa','Casa','🏡'],['/insights','Insights','💡'],['/relatorios','Relatórios','📊'],['/assistente','Luna','🌙'],['/config','Configurações','⚙️']]'''
s = replace_once(s, old1, new1, "helpers-refs-log")

# 2) Reescreve a tela Alimentacao inteira, igual a referencia.
old2 = '''function Alimentacao(){
  type Ref={nome:string,prot:number,hora:string}
  const [wat,setWat]=React.useState(lerAguaHoje)
  const [prot,setProt]=React.useState(()=>Number(localStorage.getItem('dos_prot')||0))
  const [refs,setRefs]=React.useState<Ref[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_refs')||'[]')}catch{return []}})
  const [nomef,setNomef]=React.useState('')
  const [protf,setProtf]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const metaP=120
  const [metaW,setMetaW]=React.useState(()=>Number(localStorage.getItem('dos_meta_agua_ml')||2500))
  const [metaWInput,setMetaWInput]=React.useState('')
  function atualizarMetaAgua(){
    const n=Math.max(500,Number(metaWInput)||metaW)
    setMetaW(n);localStorage.setItem('dos_meta_agua_ml',String(n));setMetaWInput('')
  }
  const addW=(ml:number)=>{const n=Math.min(wat+ml,6000);setWat(n);salvarAguaHoje(n)}
  const addP=(g:number)=>{const n=Math.min(prot+g,300);setProt(n);localStorage.setItem('dos_prot',String(n))}
  function registrar(){
    if(!nomef)return
    const r:Ref={nome:nomef,prot:Number(protf)||0,hora:new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}
    const n=[r,...refs]
    setRefs(n);localStorage.setItem('dos_refs',JSON.stringify(n))
    if(r.prot>0)addP(r.prot)
    setSaved(true);setNomef('');setProtf('')
  }
  function delRef(i:number){const n=refs.filter((_,j)=>j!==i);setRefs(n);localStorage.setItem('dos_refs',JSON.stringify(n))}
  const pctP=Math.min(100,Math.round(prot/metaP*100))
  const pctW=Math.min(100,Math.round(wat/metaW*100))
  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Alimentação</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Registro do dia · sem lactose · proteína em foco</p>
    <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12,marginBottom:20}}>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
        <div style={{fontSize:22,fontWeight:800,color:C.ok}}>{prot} / {metaP} g</div>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2,marginBottom:8}}>Proteína hoje</div>
        <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${pctP}%`,borderRadius:4,background:C.ok,transition:'width .3s'}}/></div>
        <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}>{pctP}% da meta</div>
      </div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
        <div style={{fontSize:22,fontWeight:800,color:C.water}}>{(wat/1000).toFixed(1).replace('.',',')} / {(metaW/1000).toFixed(1).replace('.',',')} L</div>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2,marginBottom:8}}>Água hoje</div>
        <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${pctW}%`,borderRadius:4,background:C.water,transition:'width .3s'}}/></div>
        <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}>{pctW}% da meta</div>
        <div style={{display:'flex',gap:6,marginTop:8}}>
          <input type="number" value={metaWInput} onChange={e=>setMetaWInput(e.target.value)} placeholder={`Meta em ml (${metaW})`} style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'6px 8px',color:'#fff',fontSize:11.5}}/>
          <button onClick={atualizarMetaAgua} style={{background:'rgba(56,189,248,.15)',border:'1px solid rgba(56,189,248,.3)',color:C.water,borderRadius:8,padding:'6px 10px',fontSize:11,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>Definir meta</button>
        </div>
      </div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
        <div style={{fontSize:22,fontWeight:800}}>{refs.length}</div>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Refeições registradas</div>
        <div style={{marginTop:12,fontSize:12,color:'rgba(255,255,255,.5)'}}>Hoje · {new Date().toLocaleDateString('pt-BR',{weekday:'long'})}</div>
      </div>
    </div>
    <div style={{display:'flex',gap:8,marginBottom:20,flexWrap:'wrap' as const}}>
      <span style={{fontSize:12,color:'rgba(255,255,255,.4)',alignSelf:'center',marginRight:4}}>💧 Água:</span>
      {[200,300,500].map(ml=>(<button key={ml} onClick={()=>addW(ml)} style={{background:'linear-gradient(135deg,#0ea5e9,#0369a1)',color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:600,cursor:'pointer'}}>+{ml} ml</button>))}
      <span style={{fontSize:12,color:'rgba(255,255,255,.4)',alignSelf:'center',marginLeft:8,marginRight:4}}>🥩 Proteína:</span>
      {[10,20,25,30].map(g=>(<button key={g} onClick={()=>addP(g)} style={{background:'linear-gradient(135deg,#16a34a,#15803d)',color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:600,cursor:'pointer'}}>+{g}g</button>))}
    </div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Registrar refeição">
        {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Refeição registrada!</div>}
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>O que comeu?</label>
        <input value={nomef} onChange={e=>setNomef(e.target.value)} placeholder="Ex: Frango grelhado + salada + arroz" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Proteína estimada (g) — opcional</label>
        <input type="number" value={protf} onChange={e=>setProtf(e.target.value)} placeholder="Ex: 35" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <button onClick={registrar} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Registrar</button>
        <div style={{marginTop:16,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:8,color:'rgba(255,255,255,.6)'}}>Sugestões · sem lactose</div>
          {[['☕','Café · whey com água · creatina · KADE'],['🍎','Lanche · iogurte proteico ou ovo'],['🍽️','Almoço · proteína primeiro'],['🥛','Whey da tarde com água'],['🌙','Jantar · proteína + salada']].map(([i,n])=>(
            <div key={String(n)} style={{display:'flex',alignItems:'center',gap:8,padding:'6px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,color:'rgba(255,255,255,.5)'}}>
              <span>{i}</span><span>{n}</span>
            </div>
          ))}
        </div>
      </Card>
      <Card title="Histórico de hoje">
        {refs.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma refeição registrada ainda hoje.</div>}
        {refs.map((r,i)=>(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div style={{flex:1}}>
            <div style={{fontSize:13,fontWeight:600}}>{r.nome}</div>
            <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:2}}>{r.hora}{r.prot>0?` · ${r.prot}g proteína`:''}</div>
          </div>
          {r.prot>0&&<span style={{background:'rgba(52,211,153,.15)',color:C.ok,fontSize:11,padding:'2px 8px',borderRadius:20,flexShrink:0}}>{r.prot}g</span>}
          <button onClick={()=>delRef(i)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'4px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button>
        </div>))}
        {refs.length>0&&<div style={{marginTop:12,padding:'10px',background:C.s2,borderRadius:10,fontSize:13}}>
          <div style={{display:'flex',justifyContent:'space-between' as const}}>
            <span style={{color:'rgba(255,255,255,.6)'}}>Total proteína registrada</span>
            <span style={{fontWeight:700,color:C.ok}}>{refs.reduce((a,r)=>a+r.prot,0)}g</span>
          </div>
        </div>}
        {refs.length>0&&<button onClick={()=>{if(window.confirm('Limpar histórico de hoje?')){setRefs([]);setWat(0);setProt(0);localStorage.removeItem('dos_refs');salvarAguaHoje(0);localStorage.removeItem('dos_prot')}}} style={{width:'100%',background:'rgba(248,113,113,.1)',border:'1px solid rgba(248,113,113,.2)',color:C.danger,borderRadius:10,padding:'9px',fontSize:12,cursor:'pointer',marginTop:12}}>Limpar dia</button>}
      </Card>
    </div>
  </div>)}'''
new2 = '''function Alimentacao(){
  const hojeIsoA=isoBR(new Date())
  const [wat,setWat]=React.useState(lerAguaHoje)
  const [refsHoje,setRefsHoje]=React.useState<RefEntry[]>(()=>lerRefeicoesDia(hojeIsoA))
  const [tick,setTick]=React.useState(0)
  const forceRefreshA=()=>setTick(t=>t+1)
  const [nomef,setNomef]=React.useState('')
  const [protf,setProtf]=React.useState('')
  const [calf,setCalf]=React.useState('')
  const [horaf,setHoraf]=React.useState(()=>new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}))
  const [tipof,setTipof]=React.useState('Almoço')
  const [saved,setSaved]=React.useState(false)
  const [mostrarOpcionais,setMostrarOpcionais]=React.useState(false)
  const [showHistCompleto,setShowHistCompleto]=React.useState(false)
  const metaP=lerMetaProteina()
  const [metaW,setMetaW]=React.useState(()=>Number(localStorage.getItem('dos_meta_agua_ml')||2500))
  const [metaWInput,setMetaWInput]=React.useState('')
  const metaKcal=lerMetaCalorias()
  const [metaKcalInput,setMetaKcalInput]=React.useState('')
  const metaRefeicoesCfg=lerMetaRefeicoes()

  function atualizarMetaAgua(){
    const n=Math.max(500,Number(metaWInput)||metaW)
    setMetaW(n);localStorage.setItem('dos_meta_agua_ml',String(n));setMetaWInput('')
  }
  function definirMetaCalorias(){
    const n=Number(metaKcalInput)
    if(!n||n<=0)return
    localStorage.setItem('dos_meta_kcal',String(n));setMetaKcalInput('');forceRefreshA()
  }
  const addW=(ml:number)=>{const n=Math.min(wat+ml,6000);setWat(n);salvarAguaHoje(n)}
  const addP=(g:number)=>{
    const nova:RefEntry={id:novoIdRef(),tipo:'Rápido',nome:'Proteína (registro rápido)',prot:g,hora:new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}),origem:'app'}
    const n=[nova,...refsHoje]
    setRefsHoje(n);salvarRefeicoesDia(hojeIsoA,n)
  }
  function registrar(){
    if(!nomef)return
    const r:RefEntry={id:novoIdRef(),tipo:tipof,nome:nomef,prot:protf?Number(protf):undefined,cal:calf?Number(calf):undefined,hora:horaf||new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}),origem:'app'}
    const n=[r,...refsHoje]
    setRefsHoje(n);salvarRefeicoesDia(hojeIsoA,n)
    setSaved(true);setNomef('');setProtf('');setCalf('');setMostrarOpcionais(false)
    setTimeout(()=>setSaved(false),2500)
  }
  function delRef(id:string){const n=refsHoje.filter(r=>r.id!==id);setRefsHoje(n);salvarRefeicoesDia(hojeIsoA,n)}
  function editarRef(r:RefEntry){
    const novoNome=window.prompt('O que comeu?',r.nome)
    if(novoNome===null)return
    const novaProtStr=window.prompt('Proteína (g)? Deixe em branco pra remover, cancelar mantém.',r.prot!=null?String(r.prot):'')
    const novaCalStr=window.prompt('Calorias (opcional)? Deixe em branco pra remover, cancelar mantém.',r.cal!=null?String(r.cal):'')
    const n=refsHoje.map(x=>{
      if(x.id!==r.id)return x
      const prot=novaProtStr===null?x.prot:(novaProtStr.trim()?Number(novaProtStr):undefined)
      const cal=novaCalStr===null?x.cal:(novaCalStr.trim()?Number(novaCalStr):undefined)
      return {...x,nome:novoNome||x.nome,prot,cal}
    })
    setRefsHoje(n);salvarRefeicoesDia(hojeIsoA,n)
  }

  const totalProt=refsHoje.reduce((a,r)=>a+(r.prot||0),0)
  const refsComCal=refsHoje.filter(r=>typeof r.cal==='number')
  const totalCal=refsComCal.length>0?refsComCal.reduce((a,r)=>a+(r.cal||0),0):null
  const refsComCarb=refsHoje.filter(r=>typeof r.carb==='number')
  const refsComGord=refsHoje.filter(r=>typeof r.gord==='number')
  const temMacros=refsComCarb.length>0||refsComGord.length>0
  const totalCarb=refsComCarb.reduce((a,r)=>a+(r.carb||0),0)
  const totalGord=refsComGord.reduce((a,r)=>a+(r.gord||0),0)
  const kcalMacroProt=totalProt*4,kcalMacroCarb=totalCarb*4,kcalMacroGord=totalGord*9
  const kcalMacroTotal=Math.max(1,kcalMacroProt+kcalMacroCarb+kcalMacroGord)
  const pctMacroProt=Math.round(kcalMacroProt/kcalMacroTotal*100)
  const pctMacroCarbAcumulado=pctMacroProt+Math.round(kcalMacroCarb/kcalMacroTotal*100)

  const pctP=Math.min(100,Math.round(totalProt/metaP*100))
  const pctW=Math.min(100,Math.round(wat/metaW*100))
  const pctCal=metaKcal?Math.min(100,Math.round((totalCal||0)/metaKcal*100)):null
  const metasAtivas:number[]=[pctP,pctW]
  if(metaRefeicoesCfg)metasAtivas.push(Math.min(100,Math.round(refsHoje.length/metaRefeicoesCfg*100)))
  if(pctCal!==null)metasAtivas.push(pctCal)
  const pctGeral=Math.round(metasAtivas.reduce((a,b)=>a+b,0)/metasAtivas.length)

  const rotinaItensA=(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'null')}catch{return null}})() as {t:string,n:string,cat:string,dias?:number[]}[]|null
  const ROTINA_DEF_A:{t:string,n:string,cat:string,dias?:number[]}[]=[{t:'06:30',n:'Café · whey · creatina',cat:'Alimentação'},{t:'09:30',n:'Lanche da manhã',cat:'Alimentação'},{t:'15:30',n:'Whey da tarde',cat:'Alimentação'},{t:'19:00',n:'Jantar',cat:'Alimentação'}]
  const rotinaAlim=(rotinaItensA||ROTINA_DEF_A).map((it,i)=>({it,i})).filter(({it})=>it.cat==='Alimentação')
  const doneHojeA=new Set<number>((()=>{try{return JSON.parse(localStorage.getItem(`dos_rotina_done_${hojeIsoA}`)||'[]')}catch{return []}})())
  const toggleLembreteA=(i:number)=>{
    const chave=`dos_rotina_done_${hojeIsoA}`
    const atual=new Set<number>((()=>{try{return JSON.parse(localStorage.getItem(chave)||'[]')}catch{return []}})())
    if(atual.has(i))atual.delete(i);else atual.add(i)
    localStorage.setItem(chave,JSON.stringify([...atual]))
    forceRefreshA()
  }

  const faltamProt=Math.max(0,metaP-totalProt)
  const SUGESTOES:[string,string][]=[['☕','Café · whey com água · creatina'],['🍎','Lanche · iogurte proteico ou ovo'],['🍽️','Almoço · proteína primeiro'],['🥛','Whey da tarde com água'],['🌙','Jantar · proteína + salada']]

  const [periodoHist,setPeriodoHist]=React.useState<7|30>(7)
  const diasHist=(()=>{const dias:string[]=[];for(let i=0;i<periodoHist;i++){const d=new Date();d.setDate(d.getDate()-i);dias.push(isoBR(d))}return dias})()
  const aguaLogHist=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
  const refsLogHist=lerRefsLog()

  void tick
  return(<div style={{padding:'24px 28px'}}>
    {showHistCompleto&&<div onClick={e=>{if(e.target===e.currentTarget)setShowHistCompleto(false)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:640,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Histórico completo</h3>
          <button onClick={()=>setShowHistCompleto(false)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          <div style={{display:'flex',gap:8,marginBottom:14}}>
            {([[7,'7 dias'],[30,'30 dias']] as [7|30,string][]).map(([v,l])=>(<button key={v} onClick={()=>setPeriodoHist(v)} style={{background:periodoHist===v?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,color:'#fff',border:`1px solid ${C.line}`,borderRadius:20,padding:'6px 14px',fontSize:12,fontWeight:600,cursor:'pointer'}}>{l}</button>))}
          </div>
          {diasHist.map(iso=>{
            const aguaDia=Number(aguaLogHist[iso]||0)
            const refsDia=refsLogHist[iso]||[]
            const protDia=refsDia.reduce((a,r)=>a+(r.prot||0),0)
            const refsComCalDia=refsDia.filter(r=>typeof r.cal==='number')
            const calDia=refsComCalDia.length>0?refsComCalDia.reduce((a,r)=>a+(r.cal||0),0):null
            if(aguaDia===0&&refsDia.length===0)return null
            return(<div key={iso} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}>
              <span style={{width:70,flexShrink:0,color:'rgba(255,255,255,.5)'}}>{new Date(iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>
              <span style={{flex:1}}>💧 {(aguaDia/1000).toFixed(1).replace('.',',')}L · 🥩 {protDia}g · 🍽️ {refsDia.length}{calDia!==null?` · 🔥 ${calDia}kcal`:''}</span>
            </div>)
          })}
          {diasHist.every(iso=>Number(aguaLogHist[iso]||0)===0&&(refsLogHist[iso]||[]).length===0)&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum registro no período.</div>}
        </div>
      </div>
    </div>}
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Alimentação</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Registro do dia · sem lactose · proteína em foco</p>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(190px,1fr))',gap:12,marginBottom:20}}>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
        <div style={{fontSize:22,fontWeight:800,color:C.ok}}>{totalProt} / {metaP} g</div>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2,marginBottom:8}}>Proteína hoje</div>
        <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${pctP}%`,borderRadius:4,background:C.ok,transition:'width .3s'}}/></div>
        <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}><span>{pctP}% da meta</span><span>{faltamProt>0?`+${faltamProt}g restantes`:'Meta batida ✓'}</span></div>
      </div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
        <div style={{fontSize:22,fontWeight:800,color:C.water}}>{(wat/1000).toFixed(1).replace('.',',')} / {(metaW/1000).toFixed(1).replace('.',',')} L</div>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2,marginBottom:8}}>Água hoje</div>
        <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${pctW}%`,borderRadius:4,background:C.water,transition:'width .3s'}}/></div>
        <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}><span>{pctW}% da meta</span><span>{wat<metaW?`+${((metaW-wat)/1000).toFixed(1).replace('.',',')}L restantes`:'Meta batida ✓'}</span></div>
        <div style={{display:'flex',gap:6,marginTop:8}}>
          <input type="number" value={metaWInput} onChange={e=>setMetaWInput(e.target.value)} placeholder={`Meta em ml (${metaW})`} style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'6px 8px',color:'#fff',fontSize:11.5}}/>
          <button onClick={atualizarMetaAgua} style={{background:'rgba(56,189,248,.15)',border:'1px solid rgba(56,189,248,.3)',color:C.water,borderRadius:8,padding:'6px 10px',fontSize:11,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>Definir meta</button>
        </div>
      </div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
        <div style={{fontSize:22,fontWeight:800}}>{refsHoje.length}{metaRefeicoesCfg?` / ${metaRefeicoesCfg}`:''}</div>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Refeições{metaRefeicoesCfg?'':' registradas'}</div>
        <div style={{marginTop:12,fontSize:12,color:'rgba(255,255,255,.5)'}}>Hoje · {new Date().toLocaleDateString('pt-BR',{weekday:'long'})}</div>
      </div>
      {metaKcal!==null?(
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
          <div style={{fontSize:22,fontWeight:800,color:C.warn}}>{totalCal||0} / {metaKcal} kcal</div>
          <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2,marginBottom:8}}>Calorias</div>
          <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${pctCal}%`,borderRadius:4,background:C.warn,transition:'width .3s'}}/></div>
          <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}>Restam {Math.max(0,metaKcal-(totalCal||0))} kcal</div>
        </div>
      ):(
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
          <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:8}}>Calorias (opcional)</div>
          <div style={{display:'flex',gap:6}}>
            <input type="number" value={metaKcalInput} onChange={e=>setMetaKcalInput(e.target.value)} placeholder="Meta em kcal" style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'6px 8px',color:'#fff',fontSize:11.5}}/>
            <button onClick={definirMetaCalorias} style={{background:'rgba(251,191,36,.15)',border:'1px solid rgba(251,191,36,.3)',color:C.warn,borderRadius:8,padding:'6px 10px',fontSize:11,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>Ativar</button>
          </div>
        </div>
      )}
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:6}}>Meta do dia</div>
        <div style={{display:'flex',alignItems:'center',gap:12}}>
          <Ring pct={pctGeral} color={pctGeral>=70?C.ok:C.acc2} size={56}/>
          <div><div style={{fontSize:13,fontWeight:700,color:pctGeral>=70?C.ok:'rgba(255,255,255,.7)'}}>{pctGeral>=70?'Muito bem!':'Continue assim'}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Média das metas configuradas hoje</div></div>
        </div>
      </div>
    </div>
    <div style={{display:'flex',gap:8,marginBottom:20,flexWrap:'wrap' as const}}>
      <span style={{fontSize:12,color:'rgba(255,255,255,.4)',alignSelf:'center',marginRight:4}}>💧 Água:</span>
      {[200,300,500].map(ml=>(<button key={ml} onClick={()=>addW(ml)} style={{background:'linear-gradient(135deg,#0ea5e9,#0369a1)',color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:600,cursor:'pointer'}}>+{ml} ml</button>))}
      <button onClick={()=>addW(1000)} style={{background:'linear-gradient(135deg,#0ea5e9,#0369a1)',color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:600,cursor:'pointer'}}>+1 L</button>
      <span style={{fontSize:12,color:'rgba(255,255,255,.4)',alignSelf:'center',marginLeft:8,marginRight:4}}>🥩 Proteína:</span>
      {[10,20,25,30].map(g=>(<button key={g} onClick={()=>addP(g)} style={{background:'linear-gradient(135deg,#16a34a,#15803d)',color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:600,cursor:'pointer'}}>+{g}g</button>))}
    </div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Registrar refeição">
        {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Refeição registrada!</div>}
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>O que comeu?</label>
        <input value={nomef} onChange={e=>setNomef(e.target.value)} placeholder="Ex: Frango grelhado + salada + arroz" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Proteína estimada (g) — opcional</label>
        <input type="number" value={protf} onChange={e=>setProtf(e.target.value)} placeholder="Ex: 35" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        {!mostrarOpcionais?(
          <button onClick={()=>setMostrarOpcionais(true)} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:0,marginBottom:12}}>+ Calorias, horário e tipo (opcional)</button>
        ):(<>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
            <div>
              <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Calorias (opcional)</label>
              <input type="number" value={calf} onChange={e=>setCalf(e.target.value)} placeholder="Ex: 350" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/>
            </div>
            <div>
              <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Horário</label>
              <input type="time" value={horaf} onChange={e=>setHoraf(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/>
            </div>
          </div>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Tipo de refeição</label>
          <select value={tipof} onChange={e=>setTipof(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12,colorScheme:'dark' as const}}>
            {['Café da manhã','Lanche','Almoço','Lanche da tarde','Jantar','Ceia','Outro'].map(t=>(<option key={t}>{t}</option>))}
          </select>
        </>)}
        <button onClick={registrar} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Registrar</button>
        <div style={{marginTop:16,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:4,color:'rgba(255,255,255,.6)'}}>Sugestões · sem lactose</div>
          {faltamProt>0&&<div style={{fontSize:11.5,color:C.warn,marginBottom:8}}>Ainda faltam {faltamProt}g de proteína hoje.</div>}
          {SUGESTOES.map(([i,n])=>(
            <div key={n} style={{display:'flex',alignItems:'center',gap:8,padding:'6px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,color:'rgba(255,255,255,.5)'}}>
              <span>{i}</span><span>{n}</span>
            </div>
          ))}
        </div>
      </Card>
      <Card title="Histórico de hoje">
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {refsHoje.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma refeição registrada ainda hoje.</div>}
          {refsHoje.map(r=>(<div key={r.id} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
            <div style={{flex:1}}>
              <div style={{fontSize:13,fontWeight:600}}>{r.tipo!=='Rápido'?`${r.tipo} — `:''}{r.hora}</div>
              <div style={{fontSize:12.5,marginTop:2}}>{r.nome}</div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:2}}>{r.prot?`${r.prot}g proteína`:''}{r.prot&&r.cal!=null?' · ':''}{r.cal!=null?`${r.cal} kcal`:''}{r.origem==='whatsapp'?' · via WhatsApp':''}</div>
            </div>
            <button onClick={()=>editarRef(r)} style={{background:'rgba(139,92,246,.1)',border:'none',color:C.acc2,borderRadius:6,padding:'4px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✎</button>
            <button onClick={()=>delRef(r.id)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'4px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button>
          </div>))}
        </div>
        {refsHoje.length>0&&<div style={{marginTop:12,padding:'10px',background:C.s2,borderRadius:10,fontSize:13}}>
          <div style={{display:'flex',justifyContent:'space-between' as const}}>
            <span style={{color:'rgba(255,255,255,.6)'}}>Total proteína registrada</span>
            <span style={{fontWeight:700,color:C.ok}}>{totalProt}g</span>
          </div>
        </div>}
        {temMacros&&<div style={{marginTop:16,borderTop:`1px solid ${C.line}`,paddingTop:14}}>
          <div style={{fontSize:12,fontWeight:700,marginBottom:10,color:'rgba(255,255,255,.6)'}}>Macros do dia</div>
          <div style={{display:'flex',alignItems:'center',gap:16}}>
            <div style={{width:70,height:70,borderRadius:'50%',background:`conic-gradient(${C.ok} 0% ${pctMacroProt}%, ${C.warn} ${pctMacroProt}% ${pctMacroCarbAcumulado}%, #fb923c ${pctMacroCarbAcumulado}% 100%)`,flexShrink:0}}/>
            <div style={{flex:1,fontSize:12}}>
              <div style={{display:'flex',justifyContent:'space-between',padding:'3px 0'}}><span style={{color:C.ok}}>● Proteínas</span><span>{totalProt}g</span></div>
              <div style={{display:'flex',justifyContent:'space-between',padding:'3px 0'}}><span style={{color:C.warn}}>● Carboidratos</span><span>{totalCarb}g</span></div>
              <div style={{display:'flex',justifyContent:'space-between',padding:'3px 0'}}><span style={{color:'#fb923c'}}>● Gorduras</span><span>{totalGord}g</span></div>
            </div>
          </div>
        </div>}
      </Card>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(280px,1fr))',gap:16,marginTop:16}}>
      <Card title="Plano do dia">
        <div style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{flex:1}}>💧 Água</span><span style={{color:'rgba(255,255,255,.5)'}}>{(wat/1000).toFixed(1).replace('.',',')} / {(metaW/1000).toFixed(1).replace('.',',')} L</span><span style={{width:38,textAlign:'right' as const,fontWeight:700,color:pctW>=100?C.ok:'rgba(255,255,255,.6)'}}>{pctW}%</span></div>
        <div style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{flex:1}}>🥩 Proteína</span><span style={{color:'rgba(255,255,255,.5)'}}>{totalProt} / {metaP} g</span><span style={{width:38,textAlign:'right' as const,fontWeight:700,color:pctP>=100?C.ok:'rgba(255,255,255,.6)'}}>{pctP}%</span></div>
        <div style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:metaKcal!==null?`1px solid ${C.line}`:'none',fontSize:13}}><span style={{flex:1}}>🍽️ Refeições</span><span style={{color:'rgba(255,255,255,.5)'}}>{refsHoje.length}{metaRefeicoesCfg?` / ${metaRefeicoesCfg}`:''}</span>{metaRefeicoesCfg?<span style={{width:38,textAlign:'right' as const,fontWeight:700,color:'rgba(255,255,255,.6)'}}>{Math.min(100,Math.round(refsHoje.length/metaRefeicoesCfg*100))}%</span>:null}</div>
        {metaKcal!==null&&<div style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',fontSize:13}}><span style={{flex:1}}>🔥 Calorias</span><span style={{color:'rgba(255,255,255,.5)'}}>{totalCal||0} / {metaKcal}</span><span style={{width:38,textAlign:'right' as const,fontWeight:700,color:(pctCal||0)>=100?C.ok:'rgba(255,255,255,.6)'}}>{pctCal}%</span></div>}
      </Card>
      <Card title="Lembretes">
        {rotinaAlim.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum lembrete de alimentação configurado na Rotina.</div>}
        {rotinaAlim.map(({it,i})=>{
          const feito=doneHojeA.has(i)
          return(<div key={i} onClick={()=>toggleLembreteA(i)} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,cursor:'pointer'}}>
            <span style={{width:22,height:22,borderRadius:'50%',display:'grid',placeItems:'center',background:feito?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:feito?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>{feito?'✓':'○'}</span>
            <span style={{width:42,fontSize:11.5,color:'rgba(255,255,255,.4)',flexShrink:0}}>{it.t}</span>
            <span style={{flex:1,fontSize:13,textDecoration:feito?'line-through':'none',color:feito?'rgba(255,255,255,.4)':'#f3f3f8'}}>{it.n}</span>
          </div>)
        })}
        {wat<metaW&&<div style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',fontSize:13,color:'rgba(255,255,255,.6)'}}><span>💧</span><span style={{flex:1}}>Beber mais água</span><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{((metaW-wat)/1000).toFixed(1).replace('.',',')}L restantes</span></div>}
      </Card>
      <Card title="Últimas refeições" action={<button onClick={()=>setShowHistCompleto(true)} style={{fontSize:12,color:C.acc2,background:'transparent',border:'none',cursor:'pointer'}}>Ver histórico completo →</button>}>
        <div style={{maxHeight:220,overflowY:'auto' as const}}>
          {refsHoje.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nada registrado ainda hoje.</div>}
          {refsHoje.slice(0,6).map(r=>(<div key={r.id} style={{display:'flex',justifyContent:'space-between',padding:'7px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5}}>
            <span style={{color:'rgba(255,255,255,.6)'}}>{r.hora} · {r.nome}</span>
            {r.prot?<span style={{color:C.ok,flexShrink:0,marginLeft:8}}>{r.prot}g</span>:null}
          </div>))}
        </div>
      </Card>
    </div>
  </div>)}'''
s = replace_once(s, old2, new2, "reescreve-alimentacao")

# 3) Home: card "Visao rapida" ganha o mesmo dado de proteina que a tela de
#    Alimentacao (mesma fonte - totalProteinaDia/lerMetaProteina), corrigindo o
#    valor que a Home podia mostrar sem registro correspondente.
old3 = '''      <div style={{gridColumn:'span 3'}}><Card title="Visão rápida"><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>💧</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{(wat/1000).toFixed(1).replace('.',',')} L</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Água hoje / {(metaAguaHome/1000).toFixed(1).replace('.',',')} L</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>🔥</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{treinosSemana.length} / {diasTreinoPlanejados}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Treinos esta semana</div></div>'''
new3 = '''      <div style={{gridColumn:'span 3'}}><Card title="Visão rápida"><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>💧</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{(wat/1000).toFixed(1).replace('.',',')} L</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Água hoje / {(metaAguaHome/1000).toFixed(1).replace('.',',')} L</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>🥩</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{totalProteinaDia(hojeIsoHome)} / {lerMetaProteina()} g</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Proteína hoje</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>🔥</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{treinosSemana.length} / {diasTreinoPlanejados}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Treinos esta semana</div></div>'''
s = replace_once(s, old3, new3, "home-tile-proteina")

# 4) Insights: acrescenta insights reais de proteina/agua (so aparecem se houver
#    dados suficientes - nada de inventar correlacao).
old4 = '''  if(pessoasSchedI.length>0)insights.push({t:tzAutonomyI<=14?`Estoque de tirzepatida baixo: ~${tzAutonomyI} dias`:`Estoque de tirzepatida: ~${tzAutonomyI} dias de autonomia`,d:tzAutonomyI<=14?'Vale considerar reposição em breve.':'Autonomia tranquila por enquanto.',p:'agora',c:tzAutonomyI<=14?'atenção':'associação'})
  return(<div style={{padding:'24px 28px'}}>'''
new4 = '''  if(pessoasSchedI.length>0)insights.push({t:tzAutonomyI<=14?`Estoque de tirzepatida baixo: ~${tzAutonomyI} dias`:`Estoque de tirzepatida: ~${tzAutonomyI} dias de autonomia`,d:tzAutonomyI<=14?'Vale considerar reposição em breve.':'Autonomia tranquila por enquanto.',p:'agora',c:tzAutonomyI<=14?'atenção':'associação'})
  const refsLogIns=lerRefsLog()
  const aguaLogIns=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
  const diasPeriodoIns=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-i);return isoBR(d)})
  const diasComRegistroAlimIns=diasPeriodoIns.filter(iso=>(refsLogIns[iso]||[]).length>0||Number(aguaLogIns[iso]||0)>0).length
  const diasComMetaProtIns=diasPeriodoIns.filter(iso=>{const refs=refsLogIns[iso]||[];return refs.reduce((a,r)=>a+(r.prot||0),0)>=lerMetaProteina()}).length
  if(diasComRegistroAlimIns>=3){
    insights.push({t:`Proteína: meta batida em ${diasComMetaProtIns} de 7 dias`,d:diasComMetaProtIns>=5?'Consistência ótima com a meta de proteína.':diasComMetaProtIns>=3?'Boa parte da semana com a meta batida.':'Poucos dias bateram a meta de proteína essa semana.',p:'últimos 7 dias',c:diasComMetaProtIns>=5?'conquista':diasComMetaProtIns>=3?'associação':'atenção'})
  }
  const aguaPorDiaSemanaIns:Record<number,number[]>={}
  Object.keys(aguaLogIns).forEach(iso=>{
    const v=Number(aguaLogIns[iso]||0)
    if(v<=0)return
    const dw=new Date(iso+'T12:00:00-03:00').getDay()
    if(!aguaPorDiaSemanaIns[dw])aguaPorDiaSemanaIns[dw]=[]
    aguaPorDiaSemanaIns[dw].push(v)
  })
  const mediasPorDiaIns=Object.entries(aguaPorDiaSemanaIns).filter(([,vs])=>vs.length>=2).map(([dw,vs])=>({dw:Number(dw),media:vs.reduce((a,b)=>a+b,0)/vs.length,n:vs.length}))
  if(mediasPorDiaIns.length>=2){
    const mediaGeralIns=mediasPorDiaIns.reduce((a,m)=>a+m.media,0)/mediasPorDiaIns.length
    const piorDiaIns=mediasPorDiaIns.reduce((pior,m)=>m.media<pior.media?m:pior)
    if(piorDiaIns.media<mediaGeralIns*0.85){
      const DIAS_NOME_INS=['domingo','segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado']
      insights.push({t:`Sua ingestão de água costuma ser menor às ${DIAS_NOME_INS[piorDiaIns.dw]}s`,d:`Média de ${(piorDiaIns.media/1000).toFixed(1).replace('.',',')}L nesse dia, contra ${(mediaGeralIns/1000).toFixed(1).replace('.',',')}L nos demais dias com registro.`,p:`baseado em ${piorDiaIns.n} registros`,c:'atenção'})
    }
  }
  return(<div style={{padding:'24px 28px'}}>'''
s = replace_once(s, old4, new4, "insights-alimentacao")

# 5) Relatorios: protR/hidPctR paravam de usar dados corretos (dos_prot sem data,
#    meta de agua fixa em 2500). Agora usam a mesma fonte da Alimentacao/Home, e
#    ganham 2 linhas novas no resumo (refeicoes/dia e % de dias com meta batida).
old5 = '''  const watR=lerAguaHoje()
  const protR=Number(localStorage.getItem('dos_prot')||0)
  const hidPctR=Math.min(100,Math.round(watR/2500*100))
  const aliPctR=Math.min(100,Math.round(protR/120*100))
  const hojeIsoR=isoBR(new Date())
  const pessoasSchedR=Object.keys(tzSched)
  const emDiaR=pessoasSchedR.filter(pid=>{const nd=tzSched[pid].next_application_date;return nd&&nd>=hojeIsoR}).length
  const tzPctR=pessoasSchedR.length>0?Math.round(emDiaR/pessoasSchedR.length*100):0
  const resumoPeriodo:[string,string,string][]=[
    ['Espiritual',`${espPctR}%`,C.acc2],
    ['Exercícios',`${exPctR}%`,C.ok],
    ['Alimentação (hoje)',`${aliPctR}%`,C.warn],
    ['Hidratação (hoje)',`${hidPctR}%`,C.warn],
    ['Tirzepatida',pessoasSchedR.length>0?`${tzPctR}%`:'—',C.ok],
  ]'''
new5 = '''  const hojeIsoR=isoBR(new Date())
  const watR=lerAguaHoje()
  const protR=totalProteinaDia(hojeIsoR)
  const hidPctR=Math.min(100,Math.round(watR/Number(localStorage.getItem('dos_meta_agua_ml')||2500)*100))
  const aliPctR=Math.min(100,Math.round(protR/lerMetaProteina()*100))
  const pessoasSchedR=Object.keys(tzSched)
  const emDiaR=pessoasSchedR.filter(pid=>{const nd=tzSched[pid].next_application_date;return nd&&nd>=hojeIsoR}).length
  const tzPctR=pessoasSchedR.length>0?Math.round(emDiaR/pessoasSchedR.length*100):0
  const refsLogR=lerRefsLog()
  const diasPeriodoR=Array.from({length:periodoDias},(_,i)=>{const d=new Date();d.setDate(d.getDate()-i);return isoBR(d)})
  const diasComMetaProtR=diasPeriodoR.filter(iso=>{const refs=refsLogR[iso]||[];return refs.reduce((a,r)=>a+(r.prot||0),0)>=lerMetaProteina()}).length
  const pctMetaProtR=Math.round(diasComMetaProtR/periodoDias*100)
  const mediaRefeicoesR=(diasPeriodoR.reduce((a,iso)=>a+((refsLogR[iso]||[]).length),0)/periodoDias).toFixed(1)
  const resumoPeriodo:[string,string,string][]=[
    ['Espiritual',`${espPctR}%`,C.acc2],
    ['Exercícios',`${exPctR}%`,C.ok],
    ['Alimentação (hoje)',`${aliPctR}%`,C.warn],
    ['Hidratação (hoje)',`${hidPctR}%`,C.warn],
    ['Refeições/dia (média)',mediaRefeicoesR,C.warn],
    ['Meta de proteína batida',`${pctMetaProtR}%`,C.ok],
    ['Tirzepatida',pessoasSchedR.length>0?`${tzPctR}%`:'—',C.ok],
  ]'''
s = replace_once(s, old5, new5, "relatorios-fonte-unica")

p.write_text(s)
print("TUDO OK:", applied)
