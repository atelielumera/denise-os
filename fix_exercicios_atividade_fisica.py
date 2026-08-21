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

# 1) Renomeia o item do menu (rota /exercicios continua igual, so o nome exibido muda).
old1 = "const navItems=[['/', 'Home','🏠'],['/agenda','Agenda','📅'],['/espiritual','Espiritual','📖'],['/saude','Saúde','❤️'],['/alimentacao','Alimentação','🍽️'],['/exercicios','Exercícios','💪'],['/familia','Família','👨‍👩‍👧'],['/trabalho','Trabalho','💼'],['/desenvolvimento','Desenvolvimento','📈'],['/casa','Casa','🏡'],['/insights','Insights','💡'],['/relatorios','Relatórios','📊'],['/assistente','Luna','🌙'],['/config','Configurações','⚙️']]"
new1 = "const navItems=[['/', 'Home','🏠'],['/agenda','Agenda','📅'],['/espiritual','Espiritual','📖'],['/saude','Saúde','❤️'],['/alimentacao','Alimentação','🍽️'],['/exercicios','Atividade física','💪'],['/familia','Família','👨‍👩‍👧'],['/trabalho','Trabalho','💼'],['/desenvolvimento','Desenvolvimento','📈'],['/casa','Casa','🏡'],['/insights','Insights','💡'],['/relatorios','Relatórios','📊'],['/assistente','Luna','🌙'],['/config','Configurações','⚙️']]"
s = replace_once(s, old1, new1, "renomeia-nav-item")

# 2) Reescreve a tela inteira de Exercicios/Atividade fisica: plano semanal editavel e
#    persistido (antes era hardcoded no frontend), sessao real com cronometro
#    pausar/retomar, exercicios estruturados, historico com detalhe e scroll, evolucao,
#    meta semanal configuravel, "nao realizado" sem apagar o planejado.
old2 = '''function Exercicios(){
  const PLANO_SEMANA:[string,string][]=[['Seg','Calistenia'],['Ter','Caminhada'],['Qua','Calistenia'],['Qui','Caminhada'],['Sex','Calistenia'],['Sáb','Mobilidade'],['Dom','Descanso']]
  const [ativo,setAtivo]=React.useState(false)
  const [inicio,setInicio]=React.useState(0)
  const [dur,setDur]=React.useState(0)
  const [saved,setSaved]=React.useState(false)
  const [tipo,setTipo]=React.useState('Calistenia')
  const [treinos,setTreinos]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})
  React.useEffect(()=>{if(!ativo)return;const t=setInterval(()=>setDur(Math.floor((Date.now()-inicio)/1000)),1000);return()=>clearInterval(t)},[ativo,inicio])
  const fmt=(s:number)=>`${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`
  function pararTreino(){
    setAtivo(false)
    const reg={data:isoBR(new Date()),tipo,duracaoMin:Math.max(1,Math.round(dur/60))}
    const n=[reg,...treinos]
    setTreinos(n);localStorage.setItem('dos_treinos',JSON.stringify(n))
    setSaved(true)
  }
  function segundaDaSemana(d:Date){const x=new Date(d);const day=x.getDay();const diff=(day===0?-6:1-day);x.setDate(x.getDate()+diff);return x}
  const seg=segundaDaSemana(new Date())
  const diasComTreino=new Set(treinos.map((t:any)=>t.data))
  const plano=PLANO_SEMANA.map(([d,t],i)=>{const dt=new Date(seg);dt.setDate(seg.getDate()+i);const iso=isoBR(dt);return [d,t,diasComTreino.has(iso)] as [string,string,boolean]})
  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Exercícios</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Plano semanal · domingo é descanso</p>
    <div style={{display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:10,marginBottom:20}}>{plano.map(([d,t,done])=>(<div key={String(d)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'12px 8px',textAlign:'center' as const}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:6}}>{d}</div><div style={{fontSize:12,fontWeight:600,marginBottom:6}}>{t}</div>{done&&<span style={{color:C.ok}}>✓</span>}</div>))}</div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Treino de hoje">
        {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Treino salvo! {fmt(dur)}</div>}
        {!ativo&&!saved&&<div style={{marginBottom:12}}><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Tipo de treino</label><select value={tipo} onChange={e=>setTipo(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}><option>Calistenia</option><option>Caminhada</option><option>Mobilidade</option></select></div>}
        {ativo&&<div style={{background:'rgba(139,92,246,.15)',border:'1px solid rgba(139,92,246,.35)',borderRadius:12,padding:'20px',textAlign:'center' as const,marginBottom:12}}><div style={{fontSize:36,fontWeight:800,fontFamily:'monospace'}}>{fmt(dur)}</div><div style={{fontSize:13,color:'rgba(255,255,255,.6)',marginTop:4}}>{tipo} em andamento…</div></div>}
        {!saved&&<button onClick={()=>{if(!ativo){setAtivo(true);setInicio(Date.now())}else{pararTreino()}}} style={{width:'100%',background:ativo?`linear-gradient(135deg,${C.ok},#15803d)`:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'14px',fontSize:15,fontWeight:700,cursor:'pointer',marginBottom:10}}>{ativo?`⏹ Parar (${fmt(dur)})`:'▶ Iniciar treino'}</button>}
      </Card>
      <Card title="Histórico">
        {treinos.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Nenhum treino registrado ainda.</div>}
        {treinos.slice(0,8).map((tk:any,i:number)=>(<div key={i} style={{display:'flex',gap:8,padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13,color:'rgba(255,255,255,.6)'}}><span style={{width:70}}>{tk.data.slice(8,10)}/{tk.data.slice(5,7)}</span><span style={{flex:1}}>{tk.tipo}</span><span>{tk.duracaoMin} min</span></div>))}
      </Card>
    </div>
  </div>)
}'''

new2 = r'''type ExercicioPlano={nome:string,series?:number,reps?:string,carga?:string,descansoSeg?:number,duracaoSeg?:number,obs?:string}
type DiaPlanoTreino={tipo:string,nome:string,duracaoMin?:number,intensidade?:string,horario?:string,observacao?:string,descanso:boolean,exercicios:ExercicioPlano[]}
type ExercicioFeito={nome:string,seriesTotal:number,seriesFeitas:number,reps?:string,carga?:string,obs?:string}
type SessaoTreino={id:string,data:string,tipo:string,nome:string,duracaoMin:number,intensidade?:string,observacao?:string,status:'concluido'|'nao_realizado',horaInicio?:string,horaFim?:string,exercicios?:ExercicioFeito[],origem?:'app'|'whatsapp',passos?:number,distanciaKm?:number,freqCardiacaMedia?:number,caloriasAtivas?:number,origemDados?:'manual'|'apple_health'}
type SessaoAtiva={id:string,data:string,tipo:string,nome:string,intensidade?:string,exercicios:ExercicioFeito[],inicio:number,pausadoEm:number|null,pausadoAcumMs:number,horaInicioStr:string}
const EXERCICIOS_CALISTENIA_PADRAO:ExercicioPlano[]=[{nome:'Barra fixa',series:4,reps:'8-10',descansoSeg:90},{nome:'Flexões',series:4,reps:'12-15'},{nome:'Agachamento',series:4,reps:'15'},{nome:'Prancha',series:3,duracaoSeg:45}]
const PLANO_TREINO_PADRAO:DiaPlanoTreino[]=[
  {tipo:'Descanso',nome:'Descanso',descanso:true,exercicios:[]},
  {tipo:'Calistenia',nome:'Calistenia',duracaoMin:30,intensidade:'Moderada',descanso:false,exercicios:EXERCICIOS_CALISTENIA_PADRAO},
  {tipo:'Caminhada',nome:'Caminhada',duracaoMin:45,intensidade:'Leve',descanso:false,exercicios:[]},
  {tipo:'Calistenia',nome:'Calistenia',duracaoMin:30,intensidade:'Moderada',descanso:false,exercicios:EXERCICIOS_CALISTENIA_PADRAO},
  {tipo:'Caminhada',nome:'Caminhada',duracaoMin:45,intensidade:'Leve',descanso:false,exercicios:[]},
  {tipo:'Calistenia',nome:'Calistenia',duracaoMin:30,intensidade:'Moderada',descanso:false,exercicios:EXERCICIOS_CALISTENIA_PADRAO},
  {tipo:'Mobilidade',nome:'Mobilidade',duracaoMin:20,intensidade:'Leve',descanso:false,exercicios:[]},
]
const DIAS_SEMANA_NOME=['Dom','Seg','Ter','Qua','Qui','Sex','Sáb']
function lerPlanoTreino():DiaPlanoTreino[]{
  try{
    const v=JSON.parse(localStorage.getItem('dos_plano_treino')||'null')
    if(Array.isArray(v)&&v.length===7)return v
  }catch{}
  return PLANO_TREINO_PADRAO
}
function salvarPlanoTreino(plano:DiaPlanoTreino[]){localStorage.setItem('dos_plano_treino',JSON.stringify(plano))}
function lerTreinos():SessaoTreino[]{
  try{
    const v=JSON.parse(localStorage.getItem('dos_treinos')||'[]')
    if(!Array.isArray(v))return []
    return v.map((t:any,i:number):SessaoTreino=>({
      id:t.id||`legado_${t.data}_${i}`,
      data:t.data,
      tipo:t.tipo||'Treino',
      nome:t.nome||t.tipo||'Treino',
      duracaoMin:Number(t.duracaoMin||0),
      intensidade:t.intensidade,
      observacao:t.observacao,
      status:t.status||'concluido',
      horaInicio:t.horaInicio,
      horaFim:t.horaFim,
      exercicios:t.exercicios,
      origem:t.origem||'app',
      passos:t.passos,
      distanciaKm:t.distanciaKm,
      freqCardiacaMedia:t.freqCardiacaMedia,
      caloriasAtivas:t.caloriasAtivas,
      origemDados:t.origemDados,
    }))
  }catch{return []}
}
function salvarTreinos(treinos:SessaoTreino[]){localStorage.setItem('dos_treinos',JSON.stringify(treinos))}
function lerSessaoAtiva():SessaoAtiva|null{
  try{return JSON.parse(localStorage.getItem('dos_treino_sessao_atual')||'null')}catch{return null}
}
function salvarSessaoAtiva(s:SessaoAtiva|null){
  if(s)localStorage.setItem('dos_treino_sessao_atual',JSON.stringify(s))
  else localStorage.removeItem('dos_treino_sessao_atual')
}
function lerMetaTreinos():number{return Number(localStorage.getItem('dos_meta_treinos_semana')||6)}
function novoIdTreino():string{return `${Date.now()}_${Math.random().toString(36).slice(2,8)}`}
function segundaDaSemanaEx(d:Date):Date{const x=new Date(d);const dw=x.getDay();const diff=(dw===0?-6:1-dw);x.setDate(x.getDate()+diff);x.setHours(0,0,0,0);return x}

function Exercicios(){
  const hojeIsoEx=isoBR(new Date())
  const hojeDiaSemanaEx=new Date().getDay()
  const [tick,setTick]=React.useState(0)
  const forceRefreshEx=()=>setTick(t=>t+1)
  const [plano,setPlano]=React.useState<DiaPlanoTreino[]>(lerPlanoTreino)
  const [treinos,setTreinos]=React.useState<SessaoTreino[]>(lerTreinos)
  const [sessaoAtual,setSessaoAtual]=React.useState<SessaoAtiva|null>(lerSessaoAtiva)
  const [showEditPlano,setShowEditPlano]=React.useState(false)
  const [diaEditando,setDiaEditando]=React.useState(hojeDiaSemanaEx)
  const [showHistCompleto,setShowHistCompleto]=React.useState(false)
  const [expandido,setExpandido]=React.useState<string|null>(null)
  const [metaSemana,setMetaSemana]=React.useState(lerMetaTreinos)
  const [metaInput,setMetaInput]=React.useState('')

  React.useEffect(()=>{
    if(!sessaoAtual||sessaoAtual.pausadoEm)return
    const t=setInterval(()=>forceRefreshEx(),1000)
    return()=>clearInterval(t)
  },[sessaoAtual])

  const fmt=(s:number)=>`${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`
  const decorridoSeg=sessaoAtual?Math.max(0,Math.floor((Date.now()-sessaoAtual.inicio-sessaoAtual.pausadoAcumMs-(sessaoAtual.pausadoEm?Date.now()-sessaoAtual.pausadoEm:0))/1000)):0

  const planoHoje=plano[hojeDiaSemanaEx]
  const registroHoje=treinos.find(t=>t.data===hojeIsoEx)

  function iniciarTreino(){
    if(planoHoje.descanso||sessaoAtual)return
    const nova:SessaoAtiva={
      id:novoIdTreino(),data:hojeIsoEx,tipo:planoHoje.tipo,nome:planoHoje.nome,intensidade:planoHoje.intensidade,
      exercicios:planoHoje.exercicios.map(e=>({nome:e.nome,seriesTotal:e.series||1,seriesFeitas:0,reps:e.reps,carga:e.carga})),
      inicio:Date.now(),pausadoEm:null,pausadoAcumMs:0,
      horaInicioStr:new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}),
    }
    salvarSessaoAtiva(nova);setSessaoAtual(nova)
  }
  function pausarRetomar(){
    if(!sessaoAtual)return
    let n:SessaoAtiva
    if(sessaoAtual.pausadoEm){
      n={...sessaoAtual,pausadoAcumMs:sessaoAtual.pausadoAcumMs+(Date.now()-sessaoAtual.pausadoEm),pausadoEm:null}
    }else{
      n={...sessaoAtual,pausadoEm:Date.now()}
    }
    salvarSessaoAtiva(n);setSessaoAtual(n)
  }
  function marcarSerie(exIdx:number){
    if(!sessaoAtual)return
    const exs=sessaoAtual.exercicios.map((e,i)=>i===exIdx?{...e,seriesFeitas:e.seriesFeitas>=e.seriesTotal?0:e.seriesFeitas+1}:e)
    const n={...sessaoAtual,exercicios:exs}
    salvarSessaoAtiva(n);setSessaoAtual(n)
  }
  function finalizarTreino(){
    if(!sessaoAtual)return
    const obs=window.prompt('Como foi o treino? (opcional)','')
    const duracaoMin=Math.max(1,Math.round(decorridoSeg/60))
    const reg:SessaoTreino={
      id:sessaoAtual.id,data:sessaoAtual.data,tipo:sessaoAtual.tipo,nome:sessaoAtual.nome,duracaoMin,
      intensidade:sessaoAtual.intensidade,observacao:obs&&obs.trim()?obs.trim():undefined,status:'concluido',
      horaInicio:sessaoAtual.horaInicioStr,horaFim:new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}),
      exercicios:sessaoAtual.exercicios.length>0?sessaoAtual.exercicios:undefined,origem:'app',
    }
    const n=[reg,...treinos.filter(t=>t.id!==reg.id)]
    setTreinos(n);salvarTreinos(n)
    salvarSessaoAtiva(null);setSessaoAtual(null)
  }
  function marcarNaoRealizado(){
    if(registroHoje)return
    const reg:SessaoTreino={id:novoIdTreino(),data:hojeIsoEx,tipo:planoHoje.tipo,nome:planoHoje.nome,duracaoMin:0,status:'nao_realizado',origem:'app'}
    const n=[reg,...treinos]
    setTreinos(n);salvarTreinos(n)
  }
  function atualizarMetaSemana(){
    const v=Math.max(1,Number(metaInput)||metaSemana)
    setMetaSemana(v);localStorage.setItem('dos_meta_treinos_semana',String(v));setMetaInput('')
  }
  function salvarDia(diaIdx:number,novoDia:DiaPlanoTreino){
    const n=plano.map((d,i)=>i===diaIdx?novoDia:d)
    setPlano(n);salvarPlanoTreino(n)
  }

  const segAtualEx=segundaDaSemanaEx(new Date())
  const segIsoEx=isoBR(segAtualEx)
  const domIsoEx=(()=>{const d=new Date(segAtualEx);d.setDate(d.getDate()+6);return isoBR(d)})()
  const diasSemanaCards=Array.from({length:7},(_,i)=>{const d=new Date(segAtualEx);d.setDate(segAtualEx.getDate()+i);return d})
  const treinosConcluidosSemana=treinos.filter(t=>t.status==='concluido'&&t.data>=segIsoEx&&t.data<=domIsoEx)
  const minutosTreinadosSemana=treinosConcluidosSemana.reduce((a,t)=>a+t.duracaoMin,0)
  const treinosConcluidosTodos=treinos.filter(t=>t.status==='concluido').sort((a,b)=>b.data.localeCompare(a.data))
  const ultimoTreino=treinosConcluidosTodos[0]||null
  const proximoTreino=(()=>{
    for(let i=0;i<8;i++){
      const d=new Date();d.setDate(d.getDate()+i)
      const iso=isoBR(d)
      const diaPlano=plano[d.getDay()]
      if(diaPlano.descanso)continue
      const ja=treinos.find(t=>t.data===iso)
      if(ja)continue
      return {iso,dia:diaPlano,hoje:i===0}
    }
    return null
  })()
  const consistenciaAtual=(()=>{
    let n=0
    const d=new Date()
    for(let i=0;i<60;i++){
      const iso=isoBR(d)
      const diaPlano=plano[d.getDay()]
      if(diaPlano.descanso){d.setDate(d.getDate()-1);continue}
      const reg=treinos.find(t=>t.data===iso)
      if(reg&&reg.status==='concluido'){n++;d.setDate(d.getDate()-1);continue}
      if(iso===hojeIsoEx){d.setDate(d.getDate()-1);continue}
      break
    }
    return n
  })()
  const pctMetaSemana=Math.min(100,Math.round(treinosConcluidosSemana.length/metaSemana*100))

  const semanas4=Array.from({length:4},(_,i)=>{
    const inicioSem=new Date(segAtualEx);inicioSem.setDate(inicioSem.getDate()-(3-i)*7)
    const fimSem=new Date(inicioSem);fimSem.setDate(fimSem.getDate()+6)
    const isoIni=isoBR(inicioSem),isoFim=isoBR(fimSem)
    const doSemana=treinos.filter(t=>t.status==='concluido'&&t.data>=isoIni&&t.data<=isoFim)
    return {label:`${String(inicioSem.getDate()).padStart(2,'0')}/${String(inicioSem.getMonth()+1).padStart(2,'0')}`,qtd:doSemana.length,min:doSemana.reduce((a,t)=>a+t.duracaoMin,0)}
  })
  const maxQtdSemana=Math.max(1,...semanas4.map(s=>s.qtd))
  const duracaoMediaGeral=treinosConcluidosTodos.length>0?Math.round(treinosConcluidosTodos.reduce((a,t)=>a+t.duracaoMin,0)/treinosConcluidosTodos.length):0

  function statusDoDia(d:Date):'concluido'|'hoje'|'pendente'|'em_andamento'|'descanso'|'nao_realizado'{
    const iso=isoBR(d)
    const diaPlano=plano[d.getDay()]
    if(diaPlano.descanso)return 'descanso'
    const reg=treinos.find(t=>t.data===iso)
    if(reg)return reg.status==='concluido'?'concluido':'nao_realizado'
    if(sessaoAtual&&sessaoAtual.data===iso)return 'em_andamento'
    if(iso===hojeIsoEx)return 'hoje'
    return 'pendente'
  }
  const LABEL_STATUS:Record<string,string>={concluido:'Concluído',hoje:'Hoje',pendente:'Pendente',em_andamento:'Em andamento',descanso:'Descanso',nao_realizado:'Não realizado'}
  const COR_STATUS:Record<string,string>={concluido:C.ok,hoje:C.acc2,pendente:'rgba(255,255,255,.4)',em_andamento:C.warn,descanso:'rgba(255,255,255,.3)',nao_realizado:C.danger}

  const [diaTemp,setDiaTemp]=React.useState<DiaPlanoTreino>(plano[diaEditando])
  React.useEffect(()=>{setDiaTemp(plano[diaEditando])},[diaEditando,showEditPlano])
  function addExercicioTemp(){setDiaTemp(d=>({...d,exercicios:[...d.exercicios,{nome:'',series:3,reps:''}]}))}
  function delExercicioTemp(i:number){setDiaTemp(d=>({...d,exercicios:d.exercicios.filter((_,j)=>j!==i)}))}
  function editExercicioTemp(i:number,campo:keyof ExercicioPlano,valor:string){
    setDiaTemp(d=>({...d,exercicios:d.exercicios.map((e,j)=>j===i?{...e,[campo]:campo==='series'||campo==='descansoSeg'||campo==='duracaoSeg'?Number(valor)||undefined:valor}:e)}))
  }
  const [salvoDiaMsg,setSalvoDiaMsg]=React.useState(false)
  function salvarDiaTemp(){
    salvarDia(diaEditando,diaTemp)
    setSalvoDiaMsg(true);setTimeout(()=>setSalvoDiaMsg(false),1800)
  }

  const diasHist=(()=>{const l:string[]=[];for(let i=0;i<30;i++){const d=new Date();d.setDate(d.getDate()-i);l.push(isoBR(d))}return l})()

  void tick
  return(<div style={{padding:'24px 28px'}}>
    {showEditPlano&&<div onClick={e=>{if(e.target===e.currentTarget)setShowEditPlano(false)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:560,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Editar plano semanal</h3>
          <button onClick={()=>setShowEditPlano(false)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          <div style={{display:'flex',gap:6,marginBottom:16,flexWrap:'wrap' as const}}>
            {DIAS_SEMANA_NOME.map((dn,i)=>(<button key={dn} onClick={()=>setDiaEditando(i)} style={{background:diaEditando===i?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,color:'#fff',border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',fontSize:12,fontWeight:700,cursor:'pointer'}}>{dn}</button>))}
          </div>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'flex',alignItems:'center',gap:8,marginBottom:14,cursor:'pointer'}}>
            <input type="checkbox" checked={diaTemp.descanso} onChange={e=>setDiaTemp(d=>({...d,descanso:e.target.checked}))}/> Dia de descanso
          </label>
          {!diaTemp.descanso&&<>
            <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Tipo de treino</label>
            <input value={diaTemp.tipo} onChange={e=>setDiaTemp(d=>({...d,tipo:e.target.value,nome:d.nome===d.tipo?e.target.value:d.nome}))} placeholder="Ex: Calistenia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
            <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Nome do treino</label>
            <input value={diaTemp.nome} onChange={e=>setDiaTemp(d=>({...d,nome:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Duração prevista (min)</label><input type="number" value={diaTemp.duracaoMin||''} onChange={e=>setDiaTemp(d=>({...d,duracaoMin:Number(e.target.value)||undefined}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Horário (opcional)</label><input type="time" value={diaTemp.horario||''} onChange={e=>setDiaTemp(d=>({...d,horario:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
            </div>
            <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Intensidade</label>
            <select value={diaTemp.intensidade||'Moderada'} onChange={e=>setDiaTemp(d=>({...d,intensidade:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12,colorScheme:'dark' as const}}>
              <option>Leve</option><option>Moderada</option><option>Intensa</option>
            </select>
            <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Observação</label>
            <input value={diaTemp.observacao||''} onChange={e=>setDiaTemp(d=>({...d,observacao:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:16}}/>
            <div style={{fontSize:12,fontWeight:700,marginBottom:8,color:'rgba(255,255,255,.6)'}}>Exercícios</div>
            {diaTemp.exercicios.map((ex,i)=>(<div key={i} style={{display:'grid',gridTemplateColumns:'1.4fr .6fr .8fr .6fr auto',gap:6,marginBottom:8,alignItems:'center'}}>
              <input value={ex.nome} onChange={e=>editExercicioTemp(i,'nome',e.target.value)} placeholder="Nome" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12.5}}/>
              <input type="number" value={ex.series||''} onChange={e=>editExercicioTemp(i,'series',e.target.value)} placeholder="Séries" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12.5}}/>
              <input value={ex.reps||''} onChange={e=>editExercicioTemp(i,'reps',e.target.value)} placeholder="Reps" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12.5}}/>
              <input type="number" value={ex.descansoSeg||''} onChange={e=>editExercicioTemp(i,'descansoSeg',e.target.value)} placeholder="Desc.(s)" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12.5}}/>
              <button onClick={()=>delExercicioTemp(i)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'6px 8px',fontSize:11,cursor:'pointer'}}>✕</button>
            </div>))}
            <button onClick={addExercicioTemp} style={{background:'transparent',border:`1px dashed ${C.line}`,color:C.acc2,borderRadius:9,padding:'8px',fontSize:12,fontWeight:600,cursor:'pointer',width:'100%',marginBottom:16}}>+ Exercício</button>
          </>}
          {salvoDiaMsg&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'8px 12px',fontSize:12.5,color:C.ok,marginBottom:12}}>✓ {DIAS_SEMANA_NOME[diaEditando]} salvo</div>}
          <button onClick={salvarDiaTemp} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Salvar {DIAS_SEMANA_NOME[diaEditando]}</button>
        </div>
      </div>
    </div>}
    {showHistCompleto&&<div onClick={e=>{if(e.target===e.currentTarget)setShowHistCompleto(false)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:600,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Histórico completo · últimos 30 dias</h3>
          <button onClick={()=>setShowHistCompleto(false)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          {diasHist.filter(iso=>treinos.some(t=>t.data===iso)).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum registro nos últimos 30 dias.</div>}
          {diasHist.map(iso=>treinos.filter(t=>t.data===iso).map(t=>(
            <div key={t.id} style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
              <div style={{display:'flex',alignItems:'center',gap:10,fontSize:13,cursor:'pointer'}} onClick={()=>setExpandido(expandido===t.id?null:t.id)}>
                <span style={{width:80,flexShrink:0,color:'rgba(255,255,255,.5)'}}>{new Date(iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>
                <span style={{flex:1}}>{t.nome}{t.status==='concluido'?` · ${t.duracaoMin} min`:''}</span>
                <span style={{color:COR_STATUS[t.status],fontSize:11,fontWeight:700}}>{LABEL_STATUS[t.status]}</span>
              </div>
              {expandido===t.id&&<div style={{marginTop:8,paddingLeft:90,fontSize:12,color:'rgba(255,255,255,.5)'}}>
                {t.intensidade&&<div>Intensidade: {t.intensidade}</div>}
                {t.horaInicio&&<div>Início: {t.horaInicio}{t.horaFim?` · Fim: ${t.horaFim}`:''}</div>}
                {t.observacao&&<div>Obs: {t.observacao}</div>}
                {t.exercicios&&t.exercicios.length>0&&t.exercicios.map((e,i)=>(<div key={i}>{e.nome}: {e.seriesFeitas}/{e.seriesTotal} séries{e.reps?` · ${e.reps} reps`:''}</div>))}
                {t.origem==='whatsapp'&&<div>Registrado via WhatsApp</div>}
              </div>}
            </div>
          )))}
        </div>
      </div>
    </div>}
    <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:4,flexWrap:'wrap' as const,gap:10}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Atividade física</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Plano semanal · progresso · execução</p></div>
      <button onClick={()=>{setDiaEditando(hojeDiaSemanaEx);setShowEditPlano(true)}} style={{background:'transparent',border:`1px solid ${C.acc2}`,color:C.acc2,borderRadius:10,padding:'8px 14px',fontSize:12.5,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>✎ Editar plano</button>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:10,margin:'16px 0 20px'}}>
      {diasSemanaCards.map(d=>{
        const st=statusDoDia(d)
        const diaPlano=plano[d.getDay()]
        const ehHoje=isoBR(d)===hojeIsoEx
        return(<div key={isoBR(d)} style={{background:C.s2,border:ehHoje?`1.5px solid ${C.acc2}`:`1px solid ${C.line}`,borderRadius:12,padding:'12px 8px',textAlign:'center' as const}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:5,fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:6}}>{DIAS_SEMANA_NOME[d.getDay()]}{ehHoje&&<span style={{width:6,height:6,borderRadius:'50%',background:C.acc2}}/>}</div>
          <div style={{fontSize:12.5,fontWeight:700,marginBottom:2}}>{diaPlano.nome}</div>
          {diaPlano.duracaoMin&&!diaPlano.descanso?<div style={{fontSize:10,color:'rgba(255,255,255,.35)',marginBottom:6}}>{diaPlano.duracaoMin} min</div>:<div style={{marginBottom:6}}/>}
          <div style={{fontSize:10.5,fontWeight:700,color:COR_STATUS[st]}}>{LABEL_STATUS[st]}</div>
        </div>)
      })}
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(170px,1fr))',gap:10,marginBottom:20}}>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',alignItems:'center',gap:12}}><span style={{fontSize:20}}>🏋️</span><div><div style={{fontSize:18,fontWeight:800}}>{treinosConcluidosSemana.length} / {metaSemana}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Treinos da semana</div></div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',alignItems:'center',gap:12}}><span style={{fontSize:20}}>⏱️</span><div><div style={{fontSize:18,fontWeight:800}}>{minutosTreinadosSemana} min</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Minutos treinados</div></div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',alignItems:'center',gap:12}}><span style={{fontSize:20}}>🎯</span><div><div style={{fontSize:18,fontWeight:800}}>{pctMetaSemana}%</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Meta semanal</div></div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',alignItems:'center',gap:12}}><span style={{fontSize:20}}>📅</span><div><div style={{fontSize:14,fontWeight:800}}>{ultimoTreino?`${ultimoTreino.nome}`:'—'}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Último · {ultimoTreino?(ultimoTreino.data===hojeIsoEx?'hoje':ultimoTreino.data===isoBR(new Date(Date.now()-86400000))?'ontem':new Date(ultimoTreino.data+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})):'—'}</div></div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',alignItems:'center',gap:12}}><span style={{fontSize:20}}>⏭️</span><div><div style={{fontSize:14,fontWeight:800}}>{proximoTreino?proximoTreino.dia.nome:'—'}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Próximo · {proximoTreino?(proximoTreino.hoje?'hoje':new Date(proximoTreino.iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})):'—'}</div></div></div>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'1.3fr 1fr',gap:16,marginBottom:16}}>
      <Card title="Treino de hoje" action={!planoHoje.descanso?<span style={{background:'rgba(139,92,246,.15)',color:C.acc2,fontSize:11,fontWeight:700,padding:'3px 10px',borderRadius:20}}>{planoHoje.tipo}</span>:undefined}>
        {planoHoje.descanso?(
          <div style={{textAlign:'center' as const,padding:'30px 0'}}>
            <div style={{fontSize:32,marginBottom:10}}>😴</div>
            <div style={{fontSize:15,fontWeight:700,marginBottom:4}}>Hoje é dia de descanso.</div>
            <div style={{fontSize:12.5,color:'rgba(255,255,255,.4)'}}>Aproveite pra recuperar.</div>
          </div>
        ):registroHoje?(
          <div>
            <div style={{fontSize:15,fontWeight:700,marginBottom:4}}>{registroHoje.status==='concluido'?'✓ Treino de hoje concluído':'Treino de hoje marcado como não realizado'}</div>
            {registroHoje.status==='concluido'&&<div style={{fontSize:12.5,color:'rgba(255,255,255,.5)'}}>{registroHoje.duracaoMin} min{registroHoje.intensidade?` · ${registroHoje.intensidade}`:''}{registroHoje.observacao?` · ${registroHoje.observacao}`:''}</div>}
          </div>
        ):sessaoAtual?(
          <div>
            <div style={{background:'rgba(139,92,246,.15)',border:'1px solid rgba(139,92,246,.35)',borderRadius:12,padding:'20px',textAlign:'center' as const,marginBottom:14}}>
              <div style={{fontSize:36,fontWeight:800,fontFamily:'monospace'}}>{fmt(decorridoSeg)}</div>
              <div style={{fontSize:13,color:'rgba(255,255,255,.6)',marginTop:4}}>{sessaoAtual.nome} {sessaoAtual.pausadoEm?'· pausado':'em andamento…'}</div>
            </div>
            {sessaoAtual.exercicios.length>0&&<div style={{marginBottom:14}}>
              {sessaoAtual.exercicios.map((e,i)=>(<div key={i} onClick={()=>marcarSerie(i)} style={{display:'flex',alignItems:'center',gap:10,padding:'8px 0',borderBottom:`1px solid ${C.line}`,cursor:'pointer'}}>
                <span style={{flex:1,fontSize:13}}>{e.nome}{e.reps?` · ${e.reps} reps`:''}</span>
                <span style={{fontSize:12,fontWeight:700,color:e.seriesFeitas>=e.seriesTotal?C.ok:'rgba(255,255,255,.5)'}}>{e.seriesFeitas}/{e.seriesTotal} séries {e.seriesFeitas>=e.seriesTotal?'✓':''}</span>
              </div>))}
            </div>}
            <div style={{display:'flex',gap:10}}>
              <button onClick={pausarRetomar} style={{flex:1,background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'12px',fontSize:13,fontWeight:700,cursor:'pointer'}}>{sessaoAtual.pausadoEm?'▶ Retomar':'⏸ Pausar'}</button>
              <button onClick={finalizarTreino} style={{flex:1,background:`linear-gradient(135deg,${C.ok},#15803d)`,border:'none',color:'#fff',borderRadius:10,padding:'12px',fontSize:13,fontWeight:700,cursor:'pointer'}}>■ Finalizar</button>
            </div>
          </div>
        ):(
          <div>
            <div style={{fontSize:16,fontWeight:700,marginBottom:6}}>{planoHoje.nome}</div>
            <div style={{fontSize:12.5,color:'rgba(255,255,255,.5)',marginBottom:12}}>{planoHoje.duracaoMin?`${planoHoje.duracaoMin} min previstos · `:''}{planoHoje.intensidade||''}{planoHoje.observacao?` · ${planoHoje.observacao}`:''}</div>
            {planoHoje.exercicios.length>0&&<div style={{marginBottom:14}}>
              {planoHoje.exercicios.map((e,i)=>(<div key={i} style={{display:'flex',justifyContent:'space-between',padding:'6px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,color:'rgba(255,255,255,.6)'}}>
                <span>{e.nome}</span><span>{e.series?`${e.series} séries`:''}{e.reps?` × ${e.reps}`:''}{e.duracaoSeg?`${e.duracaoSeg}s`:''}</span>
              </div>))}
            </div>}
            <div style={{display:'flex',gap:10}}>
              <button onClick={iniciarTreino} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'14px',fontSize:15,fontWeight:700,cursor:'pointer'}}>▶ Iniciar treino</button>
              <button onClick={marcarNaoRealizado} style={{background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)',borderRadius:10,padding:'0 14px',fontSize:12.5,cursor:'pointer'}}>Não realizado</button>
            </div>
          </div>
        )}
      </Card>
      <Card title="Progresso da semana">
        <div style={{display:'flex',alignItems:'center',gap:16,marginBottom:14}}>
          <Ring pct={pctMetaSemana} color={pctMetaSemana>=100?C.ok:C.acc2} size={70}/>
          <div><div style={{fontSize:18,fontWeight:800}}>{treinosConcluidosSemana.length} de {metaSemana}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>treinos concluídos</div></div>
        </div>
        <div style={{display:'flex',gap:5,marginBottom:14}}>
          {diasSemanaCards.map(d=>{const st=statusDoDia(d);return(<div key={isoBR(d)} style={{flex:1,textAlign:'center' as const}}><div style={{fontSize:9.5,color:'rgba(255,255,255,.35)',marginBottom:4}}>{DIAS_SEMANA_NOME[d.getDay()]}</div><div style={{width:20,height:20,borderRadius:'50%',margin:'0 auto',display:'grid',placeItems:'center',fontSize:10,background:st==='concluido'?'rgba(52,211,153,.2)':'rgba(255,255,255,.06)',color:COR_STATUS[st]}}>{st==='concluido'?'✓':st==='descanso'?'·':st==='nao_realizado'?'✕':''}</div></div>)})}
        </div>
        <div style={{display:'flex',gap:6,marginBottom:10}}>
          <input type="number" value={metaInput} onChange={e=>setMetaInput(e.target.value)} placeholder={`Meta semanal (${metaSemana})`} style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12}}/>
          <button onClick={atualizarMetaSemana} style={{background:'rgba(139,92,246,.15)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'7px 12px',fontSize:11.5,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>Definir meta</button>
        </div>
        <div style={{fontSize:12.5,color:'rgba(255,255,255,.5)'}}>Sequência atual: <b style={{color:'#fff'}}>{consistenciaAtual} dia{consistenciaAtual===1?'':'s'} 🔥</b></div>
      </Card>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(300px,1fr))',gap:16}}>
      <Card title="Histórico recente" action={<button onClick={()=>setShowHistCompleto(true)} style={{fontSize:12,color:C.acc2,background:'transparent',border:'none',cursor:'pointer'}}>Ver histórico completo →</button>}>
        <div style={{maxHeight:260,overflowY:'auto' as const}}>
          {treinosConcluidosTodos.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum treino concluído ainda.</div>}
          {treinos.slice(0,10).map(t=>(<div key={t.id} onClick={()=>setExpandido(expandido===t.id?null:t.id)} style={{padding:'9px 0',borderBottom:`1px solid ${C.line}`,cursor:'pointer'}}>
            <div style={{display:'flex',alignItems:'center',gap:8,fontSize:13}}>
              <span style={{width:60,flexShrink:0,color:'rgba(255,255,255,.4)'}}>{new Date(t.data+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>
              <span style={{flex:1}}>{t.nome}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{t.status==='concluido'?`${t.duracaoMin} min`:''}</span>
              <span style={{color:COR_STATUS[t.status],fontSize:10.5,fontWeight:700}}>{LABEL_STATUS[t.status]}</span>
            </div>
            {expandido===t.id&&<div style={{marginTop:6,paddingLeft:68,fontSize:11.5,color:'rgba(255,255,255,.5)'}}>
              {t.intensidade&&<div>Intensidade: {t.intensidade}</div>}
              {t.observacao&&<div>Obs: {t.observacao}</div>}
              {t.exercicios&&t.exercicios.map((e,i)=>(<div key={i}>{e.nome}: {e.seriesFeitas}/{e.seriesTotal} séries</div>))}
            </div>}
          </div>))}
        </div>
      </Card>
      <Card title="Evolução · últimas 4 semanas">
        <div style={{display:'flex',alignItems:'flex-end' as const,gap:10,height:110,padding:'6px 0 10px'}}>
          {semanas4.map(s=>(<div key={s.label} style={{flex:1,display:'flex',flexDirection:'column' as const,alignItems:'center',gap:6}}>
            <div style={{flex:1,width:'100%',display:'flex',alignItems:'flex-end' as const}}><div style={{width:'100%',borderRadius:'5px 5px 2px 2px',background:`linear-gradient(180deg,${C.acc2},#6d28d9)`,height:`${Math.max(Math.round(s.qtd/maxQtdSemana*100),s.qtd>0?8:0)}%`}}/></div>
            <span style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>{s.label}</span>
          </div>))}
        </div>
        <div style={{display:'flex',justifyContent:'space-between',fontSize:11.5,color:'rgba(255,255,255,.5)',paddingTop:8,borderTop:`1px solid ${C.line}`}}>
          <span>Duração média: <b style={{color:'#fff'}}>{duracaoMediaGeral} min</b></span>
          <span>Total: <b style={{color:'#fff'}}>{treinosConcluidosTodos.length} treinos</b></span>
        </div>
      </Card>
      <Card title="Meta e consistência">
        <div style={{display:'flex',alignItems:'center',gap:16,marginBottom:14}}>
          <Ring pct={Math.min(100,consistenciaAtual*10)} color={C.warn} size={64} label={`${consistenciaAtual}d`}/>
          <div style={{flex:1,fontSize:12.5}}>
            <div style={{display:'flex',justifyContent:'space-between',padding:'4px 0'}}><span style={{color:'rgba(255,255,255,.5)'}}>Meta semanal</span><span style={{fontWeight:700}}>{metaSemana} treinos</span></div>
            <div style={{display:'flex',justifyContent:'space-between',padding:'4px 0'}}><span style={{color:'rgba(255,255,255,.5)'}}>Progresso</span><span style={{fontWeight:700,color:pctMetaSemana>=100?C.ok:'#fff'}}>{pctMetaSemana}%</span></div>
            <div style={{display:'flex',justifyContent:'space-between',padding:'4px 0'}}><span style={{color:'rgba(255,255,255,.5)'}}>Duração média</span><span style={{fontWeight:700}}>{duracaoMediaGeral} min</span></div>
          </div>
        </div>
        {pctMetaSemana>=100?(
          <div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:12.5,color:C.ok}}>⭐ Meta da semana batida! Mantenha o ritmo.</div>
        ):(
          <div style={{background:'rgba(139,92,246,.1)',border:'1px solid rgba(139,92,246,.25)',borderRadius:10,padding:'10px 12px',fontSize:12.5,color:C.acc2}}>Você está no caminho certo! Continue treinando com consistência.</div>
        )}
      </Card>
    </div>
  </div>)
}'''
s = replace_once(s, old2, new2, "reescreve-exercicios")

# 3) Correcao de consistencia: agora que "nao realizado" existe, esses 3 lugares (Home,
#    Insights, Relatorios) nao podem mais contar qualquer entrada de dos_treinos como
#    "dia treinado" - senao um treino marcado como nao realizado contaria como feito.
old3 = "  const treinosHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]"
new3 = "  const treinosHome=(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter(t=>t.status!=='nao_realizado')}catch{return []}})() as any[]"
s = replace_once(s, old3, new3, "home-filtra-nao-realizado")

old3b = "  const diasTreinoPlanejados=6"
new3b = "  const diasTreinoPlanejados=lerMetaTreinos()"
s = replace_once(s, old3b, new3b, "home-meta-treinos-real")

old4 = "  })()},[])\n  const treinosI=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]"
new4 = "  })()},[])\n  const treinosI=(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter(t=>t.status!=='nao_realizado')}catch{return []}})() as any[]"
s = replace_once(s, old4, new4, "insights-filtra-nao-realizado")

old5 = "  const treinosR=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]"
new5 = "  const treinosR=(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter(t=>t.status!=='nao_realizado')}catch{return []}})() as any[]"
s = replace_once(s, old5, new5, "relatorios-filtra-nao-realizado")

# 4) O chat da Luna dentro do app monta o proprio contexto (montarContexto), separado
#    do contexto usado pelo WhatsApp. Faltava agua/proteina/refeicoes (Alimentacao) e
#    agora tambem faltaria treino/atividade fisica - acrescenta os dois de uma vez pra
#    nao deixar o chat do app desatualizado igual ficou o WhatsApp antes.
old6 = "  function montarContexto(){\n    const treinosI=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]"
new6 = "  function montarContexto(){\n    const treinosI=(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter(t=>t.status!=='nao_realizado')}catch{return []}})() as any[]"
s = replace_once(s, old6, new6, "montarcontexto-filtra-nao-realizado")

old7 = '''    return {
      data_hoje:hojeIso,
      tirzepatida:Object.keys(tzSched).length>0?{estoque_atual_mg:tzBalance,denise:tzSched.denise||null,flavio:tzSched.flavio||null}:null,
      sequencia_treinos_dias:sequencia(diasUnicos(treinosI)),'''
new7 = '''    const aguaLogCtx=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
    const refsLogCtx=lerRefsLog()
    const refeicoesHojeCtx=refsLogCtx[hojeIso]||[]
    const planoCtx=lerPlanoTreino()
    const treinosBrutosCtx=lerTreinos()
    const diaSemanaCtx=new Date().getDay()
    const planoHojeCtx=planoCtx[diaSemanaCtx]
    const registroHojeCtx=treinosBrutosCtx.find(t=>t.data===hojeIso)
    const sessaoAtivaCtx=lerSessaoAtiva()
    const ultimoTreinoCtx=treinosBrutosCtx.filter(t=>t.status==='concluido').sort((a,b)=>b.data.localeCompare(a.data))[0]||null
    return {
      data_hoje:hojeIso,
      tirzepatida:Object.keys(tzSched).length>0?{estoque_atual_mg:tzBalance,denise:tzSched.denise||null,flavio:tzSched.flavio||null}:null,
      agua_hoje_ml:Number(aguaLogCtx[hojeIso]||0),
      meta_agua_ml:Number(localStorage.getItem('dos_meta_agua_ml')||2500),
      proteina_hoje_g:totalProteinaDia(hojeIso),
      meta_proteina_g:lerMetaProteina(),
      refeicoes_hoje:refeicoesHojeCtx.map(r=>({tipo:r.tipo,nome:r.nome,hora:r.hora,proteina_g:r.prot??null,calorias:r.cal??null})),
      treino_hoje:planoHojeCtx.descanso?{descanso:true}:{descanso:false,tipo:planoHojeCtx.tipo,nome:planoHojeCtx.nome,duracao_prevista_min:planoHojeCtx.duracaoMin??null,status:registroHojeCtx?registroHojeCtx.status:(sessaoAtivaCtx?'em_andamento':'pendente')},
      treinos_semana_concluidos:treinosBrutosCtx.filter(t=>t.status==='concluido'&&t.data>=isoBR(segundaDaSemanaEx(new Date()))).length,
      meta_treinos_semana:lerMetaTreinos(),
      minutos_treinados_semana:treinosBrutosCtx.filter(t=>t.status==='concluido'&&t.data>=isoBR(segundaDaSemanaEx(new Date()))).reduce((a,t)=>a+t.duracaoMin,0),
      ultimo_treino:ultimoTreinoCtx?{data:ultimoTreinoCtx.data,nome:ultimoTreinoCtx.nome,duracao_min:ultimoTreinoCtx.duracaoMin}:null,
      sequencia_treinos_dias:sequencia(diasUnicos(treinosI)),'''
s = replace_once(s, old7, new7, "montarcontexto-alimentacao-treino")

p.write_text(s)
print("TUDO OK:", applied)
