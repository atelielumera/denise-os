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

old1 = "function Trabalho(){const TAREFAS_SEED=[{t:'Finalizar proposta Sala Imersiva',p:'PixelSAV',s:'pendente'},{t:'Agente Vita no WhatsApp',p:'SecaVita',s:'andamento'},{t:'Arte de embalagem',p:'Impressões da Domi',s:'pendente'},{t:'Calculadora de projetores',p:'PixelSAV',s:'andamento'},{t:'Migração SGI',p:'SecaVita',s:'concluído'},{t:'Deploy do painel',p:'Lumera',s:'concluído'}];const [tasks,setTasksRaw]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_trabalho')||'null')||TAREFAS_SEED}catch{return TAREFAS_SEED}});const setTasks=(fn:any[]|((prev:any[])=>any[]))=>{setTasksRaw((prev:any[])=>{const n=typeof fn==='function'?(fn as (prev:any[])=>any[])(prev):fn;localStorage.setItem('dos_trabalho',JSON.stringify(n));return n})};const [nova,setNova]=React.useState('');const [proj,setProj]=React.useState('PixelSAV');const cols=[['pendente','Pendente',C.warn],['andamento','Em andamento',C.acc2],['aguardando','Aguardando',C.water],['concluído','Concluído',C.ok]] as [string,string,string][];return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Trabalho</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>PixelSAV · SecaVita · Impressões da Domi · Lumera</p><div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const}}><input value={nova} onChange={e=>setNova(e.target.value)} onKeyDown={e=>e.key==='Enter'&&nova&&(setTasks(t=>[{t:nova,p:proj,s:'pendente'},...t]),setNova(''))} placeholder=\"Nova tarefa…\" style={{flex:1,minWidth:200,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14}}/><select value={proj} onChange={e=>setProj(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14,colorScheme:'dark'}}><option>PixelSAV</option><option>SecaVita</option><option>Impressões da Domi</option><option>Lumera</option></select><button onClick={()=>nova&&(setTasks(t=>[{t:nova,p:proj,s:'pendente'},...t]),setNova(''))} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar</button></div><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:12}}>{cols.map(([status,label,color])=>(<div key={status} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:12}}><div style={{fontSize:11,textTransform:'uppercase' as const,color:'rgba(255,255,255,.4)',marginBottom:10,display:'flex',justifyContent:'space-between' as const}}><span>{label}</span><span style={{color}}>{tasks.filter(t=>t.s===status).length}</span></div>{tasks.filter(t=>t.s===status).map((tk,i)=>(<div key={i} style={{background:C.s,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px',marginBottom:8}}><div style={{fontSize:13,marginBottom:6}}>{tk.t}</div><div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center'}}><span style={{fontSize:11,background:'rgba(139,92,246,.15)',color:C.acc2,padding:'2px 8px',borderRadius:20}}>{tk.p}</span><select value={tk.s} onChange={e=>{const ns=e.target.value;setTasks(ts=>ts.map(x=>x===tk?{...x,s:ns}:x))}} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.4)',fontSize:11,cursor:'pointer',colorScheme:'dark'}}>{cols.map(([s,l])=>(<option key={s} value={s}>{l}</option>))}</select></div></div>))}</div>))}</div></div>)}"

new1 = r'''type ChecklistItemTrab={id:string,texto:string,feito:boolean}
type TarefaTrab={id:string,t:string,p:string,s:string,prioridade?:string,prazo?:string,horario?:string,observacoes?:string,checklist?:ChecklistItemTrab[],tags?:string[],link?:string,aguardandoQuem?:string,followUp?:string,criadaEm?:string,concluidaEm?:string,origem?:'app'|'whatsapp'}
function migrarTarefaTrab(t:any,i:number):TarefaTrab{
  return {
    id:t.id||`legado_${i}_${String(t.t||'').slice(0,12)}`,
    t:t.t||'',p:t.p||'Outros',s:t.s||'pendente',
    prioridade:t.prioridade,prazo:t.prazo,horario:t.horario,observacoes:t.observacoes,
    checklist:t.checklist,tags:t.tags,link:t.link,aguardandoQuem:t.aguardandoQuem,followUp:t.followUp,
    criadaEm:t.criadaEm,concluidaEm:t.concluidaEm,origem:t.origem||'app',
  }
}
function lerProjetosTrab():string[]{
  try{const v=JSON.parse(localStorage.getItem('dos_projetos_trabalho')||'null');if(Array.isArray(v)&&v.length>0)return v}catch{}
  return ['PixelSAV','SecaVita','Impressões da Domi','Lumera','Outros']
}
function novoIdTarefa(){return `${Date.now()}_${Math.random().toString(36).slice(2,8)}`}
function calcPrazoLabelTrab(prazo?:string):{texto:string,cor:string,atrasada:boolean}|null{
  if(!prazo)return null
  const hojeIso=isoBR(new Date())
  const dias=Math.round((new Date(prazo+'T12:00:00').getTime()-new Date(hojeIso+'T12:00:00').getTime())/86400000)
  if(dias<0)return {texto:`Atrasada ${Math.abs(dias)}d`,cor:C.danger,atrasada:true}
  if(dias===0)return {texto:'Hoje',cor:C.warn,atrasada:false}
  if(dias===1)return {texto:'Amanhã',cor:C.acc2,atrasada:false}
  if(dias<=7)return {texto:`Em ${dias}d`,cor:'rgba(255,255,255,.5)',atrasada:false}
  return {texto:`Em ${dias}d`,cor:'rgba(255,255,255,.35)',atrasada:false}
}
const PRIORIDADE_LABEL_TRAB:Record<string,string>={baixa:'Baixa',normal:'Normal',alta:'Alta',urgente:'Urgente'}
const PRIORIDADE_COR_TRAB:Record<string,string>={baixa:'rgba(255,255,255,.35)',normal:'rgba(255,255,255,.4)',alta:C.warn,urgente:C.danger}
const COLS_TRAB=[['pendente','Pendente',C.warn],['andamento','Em andamento',C.acc2],['aguardando','Aguardando',C.water],['concluído','Concluído',C.ok]] as [string,string,string][]

function Trabalho(){
  const [tasks,setTasksRaw]=React.useState<TarefaTrab[]>(()=>{
    try{
      const raw=JSON.parse(localStorage.getItem('dos_trabalho')||'null')
      if(Array.isArray(raw)&&raw.length>0)return raw.map(migrarTarefaTrab)
    }catch{}
    const seed=[{t:'Finalizar proposta Sala Imersiva',p:'PixelSAV',s:'pendente'},{t:'Agente Vita no WhatsApp',p:'SecaVita',s:'andamento'},{t:'Arte de embalagem',p:'Impressões da Domi',s:'pendente'},{t:'Calculadora de projetores',p:'PixelSAV',s:'andamento'},{t:'Migração SGI',p:'SecaVita',s:'concluído'},{t:'Deploy do painel',p:'Lumera',s:'concluído'}]
    return seed.map(migrarTarefaTrab)
  })
  const setTasks=(fn:TarefaTrab[]|((prev:TarefaTrab[])=>TarefaTrab[]))=>{
    setTasksRaw((prev:TarefaTrab[])=>{const n=typeof fn==='function'?(fn as (prev:TarefaTrab[])=>TarefaTrab[])(prev):fn;localStorage.setItem('dos_trabalho',JSON.stringify(n));return n})
  }
  const [projetos]=React.useState<string[]>(lerProjetosTrab)
  const [filtroProjeto,setFiltroProjeto]=React.useState('Todos')
  const [busca,setBusca]=React.useState('')
  const [filtroStatus,setFiltroStatus]=React.useState('')
  const [filtroPrioridade,setFiltroPrioridade]=React.useState('')
  const [filtroPrazo,setFiltroPrazo]=React.useState('')
  const [nova,setNova]=React.useState('')
  const [proj,setProj]=React.useState(projetos[0]||'Outros')
  const [taskAberta,setTaskAberta]=React.useState<TarefaTrab|null>(null)
  const [showHistorico,setShowHistorico]=React.useState(false)
  const [mostrarTodasPrio,setMostrarTodasPrio]=React.useState(false)
  const [addingCol,setAddingCol]=React.useState<string|null>(null)
  const [addingText,setAddingText]=React.useState('')
  const dragIdRef=React.useRef<string|null>(null)
  const hojeIsoTrab=isoBR(new Date())

  function atualizarTarefa(id:string,campos:Partial<TarefaTrab>){
    setTasks(ts=>ts.map(x=>x.id===id?{...x,...campos}:x))
    setTaskAberta(ta=>ta&&ta.id===id?{...ta,...campos}:ta)
  }
  function atualizarStatus(id:string,novoStatus:string){
    const t=tasks.find(x=>x.id===id)
    if(!t)return
    const campos:Partial<TarefaTrab>={s:novoStatus}
    if(novoStatus==='concluído'&&t.s!=='concluído')campos.concluidaEm=new Date().toISOString()
    if(novoStatus!=='concluído')campos.concluidaEm=undefined
    atualizarTarefa(id,campos)
    if(novoStatus==='aguardando'&&!t.aguardandoQuem){
      setTaskAberta({...t,...campos})
    }
  }
  function criarTarefa(titulo:string,projeto:string,statusInicial:string){
    if(!titulo.trim())return
    const nova:TarefaTrab={id:novoIdTarefa(),t:titulo.trim(),p:projeto,s:statusInicial,criadaEm:new Date().toISOString(),origem:'app'}
    setTasks(ts=>[nova,...ts])
    setTaskAberta(nova)
  }
  function excluirTarefa(id:string){
    if(!window.confirm('Excluir esta tarefa? Essa ação não pode ser desfeita.'))return
    setTasks(ts=>ts.filter(x=>x.id!==id))
    setTaskAberta(null)
  }
  function addChecklistItem(id:string,texto:string){
    if(!texto.trim())return
    const t=tasks.find(x=>x.id===id);if(!t)return
    const item:ChecklistItemTrab={id:novoIdTarefa(),texto:texto.trim(),feito:false}
    atualizarTarefa(id,{checklist:[...(t.checklist||[]),item]})
  }
  function toggleChecklistItem(id:string,itemId:string){
    const t=tasks.find(x=>x.id===id);if(!t)return
    atualizarTarefa(id,{checklist:(t.checklist||[]).map(c=>c.id===itemId?{...c,feito:!c.feito}:c)})
  }
  function delChecklistItem(id:string,itemId:string){
    const t=tasks.find(x=>x.id===id);if(!t)return
    atualizarTarefa(id,{checklist:(t.checklist||[]).filter(c=>c.id!==itemId)})
  }

  const tasksProjeto=filtroProjeto==='Todos'?tasks:tasks.filter(t=>t.p===filtroProjeto)
  const buscaLower=busca.trim().toLowerCase()
  const tasksFiltradas=tasksProjeto.filter(t=>{
    if(buscaLower){
      const alvo=[t.t,t.observacoes,t.p,t.aguardandoQuem,...(t.tags||[])].filter(Boolean).join(' ').toLowerCase()
      if(!alvo.includes(buscaLower))return false
    }
    if(filtroStatus&&t.s!==filtroStatus)return false
    if(filtroPrioridade&&(t.prioridade||'normal')!==filtroPrioridade)return false
    if(filtroPrazo){
      const pl=calcPrazoLabelTrab(t.prazo)
      if(filtroPrazo==='sem_prazo'&&t.prazo)return false
      if(filtroPrazo==='hoje'&&t.prazo!==hojeIsoTrab)return false
      if(filtroPrazo==='amanha'&&t.prazo!==isoBR(new Date(Date.now()+86400000)))return false
      if(filtroPrazo==='atrasadas'&&!(pl&&pl.atrasada&&t.s!=='concluído'))return false
      if(filtroPrazo==='semana'){
        if(!t.prazo)return false
        const dias=Math.round((new Date(t.prazo+'T12:00:00').getTime()-new Date(hojeIsoTrab+'T12:00:00').getTime())/86400000)
        if(dias<0||dias>7)return false
      }
    }
    return true
  })

  const segundaTrab=(()=>{const d=new Date();const dw=d.getDay();const diff=(dw===0?-6:1-dw);d.setDate(d.getDate()+diff);d.setHours(0,0,0,0);return d})()
  const segIsoTrab=isoBR(segundaTrab)
  const resumoHoje=tasksProjeto.filter(t=>t.s!=='concluído'&&t.prazo===hojeIsoTrab).length
  const resumoAtrasadas=tasksProjeto.filter(t=>{const pl=calcPrazoLabelTrab(t.prazo);return t.s!=='concluído'&&pl?.atrasada}).length
  const resumoAndamento=tasksProjeto.filter(t=>t.s==='andamento').length
  const resumoAguardando=tasksProjeto.filter(t=>t.s==='aguardando').length
  const resumoConcluidasSemana=tasksProjeto.filter(t=>t.s==='concluído'&&t.concluidaEm&&t.concluidaEm.slice(0,10)>=segIsoTrab).length

  const prioridadesHoje=tasksProjeto.filter(t=>t.s!=='concluído').map(t=>{
    const pl=calcPrazoLabelTrab(t.prazo)
    const urgente=t.prioridade==='urgente'
    const atrasada=!!pl?.atrasada
    const hoje=t.prazo===hojeIsoTrab
    const alta=t.prioridade==='alta'
    const relevante=urgente||atrasada||hoje||alta
    const peso=(urgente?3000:0)+(atrasada?2000:0)+(hoje?1000:0)+(alta?500:0)
    return {t,relevante,peso}
  }).filter(x=>x.relevante).sort((a,b)=>b.peso-a.peso).map(x=>x.t)
  const prioridadesMostradas=mostrarTodasPrio?prioridadesHoje.slice(0,10):prioridadesHoje.slice(0,5)

  function onDrop(e:React.DragEvent,status:string){
    e.preventDefault()
    const id=e.dataTransfer.getData('text/plain')||dragIdRef.current
    if(id)atualizarStatus(id,status)
    dragIdRef.current=null
  }

  function TaskCard({tk}:{tk:TarefaTrab}){
    const pl=calcPrazoLabelTrab(tk.prazo)
    const checklistTotal=(tk.checklist||[]).length
    const checklistFeitos=(tk.checklist||[]).filter(c=>c.feito).length
    return(<div draggable onDragStart={e=>{e.dataTransfer.setData('text/plain',tk.id);dragIdRef.current=tk.id}} onClick={()=>setTaskAberta(tk)} style={{background:C.s,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px',marginBottom:8,cursor:'grab'}}>
      <div style={{display:'flex',alignItems:'flex-start',gap:6,marginBottom:6}}>
        {tk.prioridade&&(tk.prioridade==='urgente'||tk.prioridade==='alta')&&<span style={{fontSize:9.5,fontWeight:700,color:'#fff',background:PRIORIDADE_COR_TRAB[tk.prioridade],padding:'2px 7px',borderRadius:20,flexShrink:0,textTransform:'uppercase' as const}}>{PRIORIDADE_LABEL_TRAB[tk.prioridade]}</span>}
        <div style={{fontSize:13,flex:1}}>{tk.t}</div>
      </div>
      {tk.s==='aguardando'&&tk.aguardandoQuem&&<div style={{fontSize:11,color:C.water,marginBottom:4}}>Aguardando {tk.aguardandoQuem}</div>}
      {checklistTotal>0&&<div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>☑ {checklistFeitos}/{checklistTotal}</div>}
      <div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',gap:6,flexWrap:'wrap' as const}}>
        <span style={{fontSize:11,background:'rgba(139,92,246,.15)',color:C.acc2,padding:'2px 8px',borderRadius:20}}>{tk.p}</span>
        {pl&&tk.s!=='concluído'&&<span style={{fontSize:10.5,color:pl.cor,fontWeight:pl.atrasada?700:500}}>{pl.atrasada?'⚠️ ':''}{pl.texto}</span>}
      </div>
    </div>)
  }

  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Trabalho</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:16}}>Organize suas tarefas e acompanhe tudo que precisa ser feito.</p>

    <div style={{display:'flex',gap:8,marginBottom:16,flexWrap:'wrap' as const}}>
      {['Todos',...projetos].map(pr=>(<button key={pr} onClick={()=>setFiltroProjeto(pr)} style={{background:filtroProjeto===pr?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,color:'#fff',border:`1px solid ${filtroProjeto===pr?'transparent':C.line}`,borderRadius:10,padding:'8px 14px',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>{pr}</button>))}
    </div>

    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))',gap:10,marginBottom:20}}>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Hoje</div><div style={{fontSize:22,fontWeight:800}}>{resumoHoje}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>tarefas</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Atrasadas</div><div style={{fontSize:22,fontWeight:800,color:resumoAtrasadas>0?C.danger:'#fff'}}>{resumoAtrasadas}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>tarefas</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Em andamento</div><div style={{fontSize:22,fontWeight:800}}>{resumoAndamento}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>tarefas</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Aguardando</div><div style={{fontSize:22,fontWeight:800}}>{resumoAguardando}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>tarefas</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Concluídas na semana</div><div style={{fontSize:22,fontWeight:800,color:C.ok}}>{resumoConcluidasSemana}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>tarefas</div></div>
    </div>

    {prioridadesHoje.length>0&&<Card title="⭐ Prioridades de hoje" action={prioridadesHoje.length>5?<button onClick={()=>setMostrarTodasPrio(v=>!v)} style={{fontSize:12,color:C.acc2,background:'transparent',border:'none',cursor:'pointer'}}>{mostrarTodasPrio?'Ver menos':'Ver todas'}</button>:undefined}>
      <p style={{fontSize:11.5,color:'rgba(255,255,255,.4)',marginTop:0,marginBottom:10}}>Tarefas que precisam da sua atenção agora.</p>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(200px,1fr))',gap:10}}>
        {prioridadesMostradas.map(tk=>{
          const pl=calcPrazoLabelTrab(tk.prazo)
          return(<div key={tk.id} onClick={()=>setTaskAberta(tk)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:12,cursor:'pointer'}}>
            {tk.prioridade&&<span style={{fontSize:9.5,fontWeight:700,color:'#fff',background:tk.prioridade==='urgente'?C.danger:tk.prioridade==='alta'?C.warn:'rgba(255,255,255,.15)',padding:'2px 7px',borderRadius:20,textTransform:'uppercase' as const}}>{PRIORIDADE_LABEL_TRAB[tk.prioridade]}</span>}
            <div style={{fontSize:13,fontWeight:600,margin:'6px 0'}}>{tk.t}</div>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><span style={{fontSize:11,color:C.acc2}}>{tk.p}</span>{pl&&<span style={{fontSize:10.5,color:pl.cor}}>{pl.texto}</span>}</div>
          </div>)
        })}
      </div>
    </Card>}

    <div style={{display:'flex',gap:10,margin:'16px 0',flexWrap:'wrap' as const}}>
      <input value={busca} onChange={e=>setBusca(e.target.value)} placeholder="🔎 Buscar tarefas…" style={{flex:1,minWidth:180,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:13}}/>
      <select value={filtroStatus} onChange={e=>setFiltroStatus(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}><option value="">Status: todos</option>{COLS_TRAB.map(([s,l])=>(<option key={s} value={s}>{l}</option>))}</select>
      <select value={filtroPrioridade} onChange={e=>setFiltroPrioridade(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}><option value="">Prioridade: todas</option>{Object.entries(PRIORIDADE_LABEL_TRAB).map(([k,l])=>(<option key={k} value={k}>{l}</option>))}</select>
      <select value={filtroPrazo} onChange={e=>setFiltroPrazo(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}><option value="">Prazo: todos</option><option value="hoje">Hoje</option><option value="amanha">Amanhã</option><option value="semana">Esta semana</option><option value="atrasadas">Atrasadas</option><option value="sem_prazo">Sem prazo</option></select>
    </div>

    <div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const}}>
      <input value={nova} onChange={e=>setNova(e.target.value)} onKeyDown={e=>e.key==='Enter'&&(criarTarefa(nova,proj,'pendente'),setNova(''))} placeholder="Nova tarefa…" style={{flex:1,minWidth:200,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14}}/>
      <select value={proj} onChange={e=>setProj(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{projetos.map(p=>(<option key={p}>{p}</option>))}</select>
      <button onClick={()=>{criarTarefa(nova,proj,'pendente');setNova('')}} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar</button>
    </div>

    <div style={{display:'flex',gap:12,overflowX:'auto' as const,paddingBottom:8}}>
      {COLS_TRAB.map(([status,label,color])=>{
        const tasksCol=tasksFiltradas.filter(t=>t.s===status)
        const listaCol=status==='concluído'?tasksCol.slice().sort((a,b)=>(b.concluidaEm||'').localeCompare(a.concluidaEm||'')).slice(0,15):tasksCol
        return(<div key={status} onDragOver={e=>e.preventDefault()} onDrop={e=>onDrop(e,status)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:12,minWidth:260,flex:'1 1 260px'}}>
          <div style={{fontSize:11,textTransform:'uppercase' as const,color:'rgba(255,255,255,.4)',marginBottom:10,display:'flex',justifyContent:'space-between' as const}}><span>{label}</span><span style={{color}}>{tasksCol.length}</span></div>
          <div style={{maxHeight:520,overflowY:'auto' as const}}>
            {listaCol.map(tk=>(<TaskCard key={tk.id} tk={tk}/>))}
          </div>
          {status==='concluído'&&tasksCol.length>15&&<button onClick={()=>setShowHistorico(true)} style={{width:'100%',background:'transparent',border:'none',color:C.acc2,fontSize:11.5,cursor:'pointer',padding:'6px 0'}}>Ver histórico de concluídas →</button>}
          {addingCol===status?(
            <div style={{display:'flex',gap:6,marginTop:8}}>
              <input autoFocus value={addingText} onChange={e=>setAddingText(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'){criarTarefa(addingText,proj,status);setAddingText('');setAddingCol(null)}if(e.key==='Escape'){setAddingText('');setAddingCol(null)}}} placeholder="Título…" style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12.5}}/>
              <button onClick={()=>{criarTarefa(addingText,proj,status);setAddingText('');setAddingCol(null)}} style={{background:C.acc,border:'none',color:'#fff',borderRadius:8,padding:'0 10px',fontSize:12,cursor:'pointer'}}>✓</button>
            </div>
          ):(
            <button onClick={()=>{setAddingCol(status);setAddingText('')}} style={{width:'100%',background:'transparent',border:'none',color:'rgba(255,255,255,.4)',fontSize:12,cursor:'pointer',padding:'8px 0',textAlign:'left' as const}}>+ Adicionar tarefa</button>
          )}
        </div>)
      })}
    </div>
    <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginTop:14}}>⚡ Dica: arraste as tarefas entre as colunas para alterar o status rapidamente.</p>

    {taskAberta&&<div onClick={e=>{if(e.target===e.currentTarget)setTaskAberta(null)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:560,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Detalhes da tarefa</h3>
          <button onClick={()=>setTaskAberta(null)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Título</label>
          <input value={taskAberta.t} onChange={e=>atualizarTarefa(taskAberta.id,{t:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:14}}/>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Projeto</label><select value={taskAberta.p} onChange={e=>atualizarTarefa(taskAberta.id,{p:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{projetos.map(p=>(<option key={p}>{p}</option>))}</select></div>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Status</label><select value={taskAberta.s} onChange={e=>atualizarStatus(taskAberta.id,e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{COLS_TRAB.map(([s,l])=>(<option key={s} value={s}>{l}</option>))}</select></div>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:10,marginBottom:14}}>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Prioridade</label><select value={taskAberta.prioridade||'normal'} onChange={e=>atualizarTarefa(taskAberta.id,{prioridade:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{Object.entries(PRIORIDADE_LABEL_TRAB).map(([k,l])=>(<option key={k} value={k}>{l}</option>))}</select></div>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Prazo</label><input type="date" value={taskAberta.prazo||''} onChange={e=>atualizarTarefa(taskAberta.id,{prazo:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Horário</label><input type="time" value={taskAberta.horario||''} onChange={e=>atualizarTarefa(taskAberta.id,{horario:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
          </div>
          {taskAberta.s==='aguardando'&&<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14,background:'rgba(56,189,248,.06)',border:'1px solid rgba(56,189,248,.2)',borderRadius:10,padding:12}}>
            <div><label style={{fontSize:12,color:C.water,display:'block',marginBottom:5}}>Aguardando quem/o quê?</label><input value={taskAberta.aguardandoQuem||''} onChange={e=>atualizarTarefa(taskAberta.id,{aguardandoQuem:e.target.value})} placeholder="Ex: Cliente, Nicolas, aprovação…" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
            <div><label style={{fontSize:12,color:C.water,display:'block',marginBottom:5}}>Revisar novamente em</label><input type="date" value={taskAberta.followUp||''} onChange={e=>atualizarTarefa(taskAberta.id,{followUp:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
          </div>}
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Observações</label>
          <textarea value={taskAberta.observacoes||''} onChange={e=>atualizarTarefa(taskAberta.id,{observacoes:e.target.value})} rows={2} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:13.5,marginBottom:14,resize:'vertical' as const,fontFamily:'inherit'}}/>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Tags (separadas por vírgula)</label><input value={(taskAberta.tags||[]).join(', ')} onChange={e=>atualizarTarefa(taskAberta.id,{tags:e.target.value.split(',').map(x=>x.trim()).filter(Boolean)})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:13.5}}/></div>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Link (opcional)</label><input value={taskAberta.link||''} onChange={e=>atualizarTarefa(taskAberta.id,{link:e.target.value})} placeholder="https://…" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:13.5}}/></div>
          </div>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:8}}>Checklist</label>
          {(taskAberta.checklist||[]).map(c=>(<div key={c.id} style={{display:'flex',alignItems:'center',gap:8,padding:'5px 0'}}>
            <input type="checkbox" checked={c.feito} onChange={()=>toggleChecklistItem(taskAberta.id,c.id)} style={{accentColor:C.acc,cursor:'pointer'}}/>
            <span style={{flex:1,fontSize:13,textDecoration:c.feito?'line-through':'none',color:c.feito?'rgba(255,255,255,.4)':'#fff'}}>{c.texto}</span>
            <button onClick={()=>delChecklistItem(taskAberta.id,c.id)} style={{background:'transparent',border:'none',color:C.danger,cursor:'pointer',fontSize:12}}>✕</button>
          </div>))}
          <ChecklistAddRow onAdd={texto=>addChecklistItem(taskAberta.id,texto)}/>
          {taskAberta.criadaEm&&<div style={{fontSize:11,color:'rgba(255,255,255,.3)',marginTop:14}}>Criada em {new Date(taskAberta.criadaEm).toLocaleDateString('pt-BR')}{taskAberta.concluidaEm?` · Concluída em ${new Date(taskAberta.concluidaEm).toLocaleString('pt-BR')}`:''}</div>}
        </div>
        <div style={{display:'flex',gap:10,padding:'14px 18px',position:'sticky',bottom:0,background:'#1c1c28'}}>
          <button onClick={()=>excluirTarefa(taskAberta.id)} style={{background:'rgba(248,113,113,.1)',border:'1px solid rgba(248,113,113,.25)',color:C.danger,borderRadius:10,padding:'11px 16px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Excluir</button>
          <button onClick={()=>atualizarStatus(taskAberta.id,taskAberta.s==='concluído'?'pendente':'concluído')} style={{flex:1,background:taskAberta.s==='concluído'?C.s2:`linear-gradient(135deg,${C.ok},#15803d)`,border:taskAberta.s==='concluído'?`1px solid ${C.line}`:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>{taskAberta.s==='concluído'?'↺ Reabrir tarefa':'✓ Marcar como concluída'}</button>
          <button onClick={()=>setTaskAberta(null)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',borderRadius:10,padding:'11px 18px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Fechar</button>
        </div>
      </div>
    </div>}

    {showHistorico&&<div onClick={e=>{if(e.target===e.currentTarget)setShowHistorico(false)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:560,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Histórico de concluídas</h3>
          <button onClick={()=>setShowHistorico(false)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          {tasksProjeto.filter(t=>t.s==='concluído').sort((a,b)=>(b.concluidaEm||'').localeCompare(a.concluidaEm||'')).map(t=>(<div key={t.id} onClick={()=>{setShowHistorico(false);setTaskAberta(t)}} style={{display:'flex',justifyContent:'space-between',padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13,cursor:'pointer'}}>
            <span>{t.t}</span>
            <span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{t.p} · {t.concluidaEm?new Date(t.concluidaEm).toLocaleDateString('pt-BR'):''}</span>
          </div>))}
        </div>
      </div>
    </div>}
  </div>)
}
function ChecklistAddRow({onAdd}:{onAdd:(texto:string)=>void}){
  const [v,setV]=React.useState('')
  return(<div style={{display:'flex',gap:6,marginTop:6}}>
    <input value={v} onChange={e=>setV(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&v.trim()){onAdd(v);setV('')}}} placeholder="+ Novo item do checklist" style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12.5}}/>
    <button onClick={()=>{if(v.trim()){onAdd(v);setV('')}}} style={{background:'rgba(139,92,246,.15)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'0 12px',fontSize:12,cursor:'pointer'}}>+</button>
  </div>)
}'''
s = replace_once(s, old1, new1, "reescreve-trabalho")

p.write_text(s)
print("TUDO OK:", applied)
