import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, NavLink, Outlet, Navigate, useNavigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import { supabase } from './lib/supabase'

const qc=new QueryClient()
const C={bg:'#0a0a0f',s:'#16161f',s2:'#1c1c28',s3:'#22222f',line:'rgba(255,255,255,.07)',acc:'#8b5cf6',acc2:'#a78bfa',ok:'#34d399',water:'#38bdf8',warn:'#fbbf24',danger:'#f87171',pink:'#f472b6',teal:'#2dd4bf'}
const navItems=[['/', 'Home','🏠'],['/rotina','Minha Rotina','📋'],['/agenda','Agenda','📅'],['/espiritual','Espiritual','📖'],['/saude','Saúde','❤️'],['/alimentacao','Alimentação','🍽️'],['/exercicios','Exercícios','💪'],['/tirzepatida','Tirzepatida','💉'],['/familia','Família','👨‍👩‍👧'],['/trabalho','Trabalho','💼'],['/desenvolvimento','Desenvolvimento','📈'],['/casa','Casa','🏡'],['/insights','Insights','💡'],['/relatorios','Relatórios','📊'],['/assistente','Assistente IA','✨'],['/config','Configurações','⚙️']]

function AuthScreen(){
  const [email,setEmail]=React.useState('')
  const [password,setPassword]=React.useState('')
  const [error,setError]=React.useState('')
  const [loading,setLoading]=React.useState(false)

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setError('');setLoading(true)
    try{
      const {error}=await supabase.auth.signInWithPassword({email,password})
      if(error) throw error
    }catch(err:any){
      setError(err?.message||'Erro ao autenticar.')
    }
    setLoading(false)
  }

  return (<div style={{minHeight:'100vh',display:'grid',placeItems:'center',background:C.bg,color:'#f3f3f8',padding:20}}>
    <div style={{width:'100%',maxWidth:380}}>
      <div style={{display:'flex',flexDirection:'column' as const,alignItems:'center',marginBottom:24}}>
        <div style={{width:48,height:48,borderRadius:14,background:'linear-gradient(145deg,#8b5cf6,#6d28d9)',display:'grid',placeItems:'center',fontSize:22,marginBottom:12}}>💜</div>
        <div style={{fontWeight:800,fontSize:18}}>Denise OS</div>
        <div style={{fontSize:12,color:'#7d7d90'}}>Seu sistema operacional de vida</div>
      </div>
      <form onSubmit={submit} style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:24}}>
        <h2 style={{fontSize:16,fontWeight:700,margin:'0 0 4px'}}>Entrar</h2>
        <p style={{fontSize:12,color:'rgba(255,255,255,.4)',margin:'0 0 18px'}}>Acesse o seu painel pessoal.</p>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>E-mail</label>
        <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Senha</label>
        <input type="password" required minLength={6} value={password} onChange={e=>setPassword(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:16}}/>
        {error&&<div style={{background:'rgba(248,113,113,.1)',border:'1px solid rgba(248,113,113,.3)',borderRadius:10,padding:'8px 12px',fontSize:12.5,color:C.danger,marginBottom:12}}>{error}</div>}
        <button type="submit" disabled={loading} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>{loading?'Aguarde...':'Entrar'}</button>
      </form>
    </div>
  </div>)
}

function AuthGate({children}:{children:React.ReactNode}){
  const [session,setSession]=React.useState<any>(undefined)

  React.useEffect(()=>{
    supabase.auth.getSession().then(({data}:any)=>setSession(data.session))
    const {data:sub}=supabase.auth.onAuthStateChange((_event:any,s:any)=>setSession(s))
    return ()=>sub.subscription.unsubscribe()
  },[])

  if(session===undefined) return <div style={{minHeight:'100vh',display:'grid',placeItems:'center',background:C.bg,color:'rgba(255,255,255,.5)'}}>Carregando…</div>
  if(!session) return <AuthScreen/>
  return <>{children}</>
}

const PhotoCtx=React.createContext<{photos:Record<string,string>,setPhoto:(k:string,v:string)=>void}>({photos:{},setPhoto:()=>{}})
function PhotoProvider({children}:{children:React.ReactNode}){const [photos,setPhotos]=React.useState<Record<string,string>>(()=>{try{return JSON.parse(localStorage.getItem('dos_photos')||'{}')}catch{return {}}});const setPhoto=(k:string,v:string)=>setPhotos(p=>{const n={...p,[k]:v};localStorage.setItem('dos_photos',JSON.stringify(n));return n});return <PhotoCtx.Provider value={{photos,setPhoto}}>{children}</PhotoCtx.Provider>}
function Avatar({id,label,size=40,radius=12}:{id:string,label:string,size?:number,radius?:number}){const {photos,setPhoto}=React.useContext(PhotoCtx);const ref=React.useRef<HTMLInputElement>(null);return(<><div onClick={()=>ref.current?.click()} style={{width:size,height:size,borderRadius:radius,background:photos[id]?'transparent':'linear-gradient(145deg,#f0abfc,#8b5cf6)',backgroundImage:photos[id]?`url(${photos[id]})`:'',backgroundSize:'cover',backgroundPosition:'center',display:'grid',placeItems:'center',fontWeight:800,color:'#fff',fontSize:size*0.38,cursor:'pointer',flexShrink:0}}>{!photos[id]&&label}</div><input ref={ref} type="file" accept="image/*" style={{display:'none'}} onChange={e=>{const f=e.target.files?.[0];if(!f)return;const r=new FileReader();r.onload=()=>setPhoto(id,r.result as string);r.readAsDataURL(f);e.target.value=''}}/></>)}
type FamData={dropOff:string,pk:{[k:number]:string}}
const defaultFam:Record<string,FamData>={domi:{dropOff:'07:00',pk:{1:'12:50',2:'11:40',3:'12:50',4:'11:40',5:'13:00'}},derick:{dropOff:'07:00',pk:{1:'17:00',2:'17:00',3:'17:00',4:'17:00',5:'17:00'}}}
const FamCtx=React.createContext<{fam:typeof defaultFam,setFam:(f:typeof defaultFam)=>void}>({fam:defaultFam,setFam:()=>{}})
function FamProvider({children}:{children:React.ReactNode}){const [fam,setFamState]=React.useState<typeof defaultFam>(()=>{try{return JSON.parse(localStorage.getItem('dos_fam')||'null')||defaultFam}catch{return defaultFam}});const setFam=(f:typeof defaultFam)=>{setFamState(f);localStorage.setItem('dos_fam',JSON.stringify(f))};return <FamCtx.Provider value={{fam,setFam}}>{children}</FamCtx.Provider>}
function Ring({pct,color,size=72,label}:{pct:number,color:string,size?:number,label?:string}){const r=32,ci=2*Math.PI*r,off=ci-ci*pct/100;return(<div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:6,flex:1,minWidth:58}}><div style={{position:'relative',width:size,height:size}}><svg viewBox="0 0 72 72" width={size} height={size} style={{transform:'rotate(-90deg)'}}><circle cx="36" cy="36" r={r} fill="none" strokeWidth={7} stroke="rgba(255,255,255,.07)"/><circle cx="36" cy="36" r={r} fill="none" strokeWidth={7} strokeLinecap="round" stroke={color} strokeDasharray={ci} strokeDashoffset={off}/></svg><span style={{position:'absolute',inset:0,display:'grid',placeItems:'center',fontWeight:800,fontSize:13}}>{pct}%</span></div>{label&&<span style={{fontSize:11,color:'rgba(255,255,255,.7)',textAlign:'center'}}>{label}</span>}</div>)}
function Card({title,action,children}:{title:string,action?:React.ReactNode,children:React.ReactNode}){return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,minWidth:0}}><div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:14}}><h3 style={{fontSize:15,fontWeight:700,margin:0}}>{title}</h3>{action}</div>{children}</div>)}
function Lrow({icon,name,val,ok,color}:{icon:string,name:string,val:string,ok?:boolean,color?:string}){return(<div style={{display:'flex',alignItems:'center',gap:10,padding:'7px 2px',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{width:26,height:26,borderRadius:8,background:C.s2,display:'grid',placeItems:'center',color:color||'rgba(255,255,255,.6)',fontSize:14}}>{icon}</span><span style={{flex:1}}>{name}</span><span style={{color:ok?C.ok:'rgba(255,255,255,.6)',fontSize:12.5}}>{val}{ok&&' ✓'}</span></div>)}
function ModalFam({onClose}:{onClose:()=>void}){const {fam,setFam}=React.useContext(FamCtx);const [local,setLocal]=React.useState(JSON.parse(JSON.stringify(fam)));const days:[number,string][]=[[1,'Seg'],[2,'Ter'],[3,'Qua'],[4,'Qui'],[5,'Sex']];return(<div onClick={e=>{if(e.target===e.currentTarget)onClose()}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}><div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:480,maxHeight:'88vh',overflow:'auto'}}><div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}><h3 style={{margin:0,fontSize:16}}>Rotina das crianças</h3><button onClick={onClose} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button></div>{(['domi','derick'] as const).map(key=>{const nome=key==='domi'?'Domi':'Derick';return(<div key={key} style={{padding:'18px',borderBottom:`1px solid ${C.line}`}}><div style={{display:'flex',alignItems:'center',gap:12,marginBottom:14}}><Avatar id={key} label={nome[0]} size={52} radius={13}/><div><div style={{fontWeight:700,fontSize:15}}>{nome}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Toque na foto para alterar</div></div></div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:5}}>Ida</label><input type="time" value={local[key].dropOff} onChange={e=>setLocal((p:typeof fam)=>({...p,[key]:{...p[key],dropOff:e.target.value}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:15,marginBottom:14,colorScheme:'dark'}}/><label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:8}}>Busca por dia</label><div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:6}}>{days.map(([d,dn])=>(<div key={d}><div style={{fontSize:10.5,color:'rgba(255,255,255,.6)',textAlign:'center' as const,fontWeight:700,marginBottom:4}}>{dn}</div><input type="time" value={local[key].pk[d]||''} onChange={e=>setLocal((p:typeof fam)=>({...p,[key]:{...p[key],pk:{...p[key].pk,[d]:e.target.value}}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'7px 2px',color:'#fff',fontSize:11,textAlign:'center' as const,colorScheme:'dark'}}/></div>))}</div></div>)})}<div style={{display:'flex',gap:10,padding:'14px 18px',position:'sticky',bottom:0,background:'#1c1c28'}}><button onClick={onClose} style={{flex:1,background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Cancelar</button><button onClick={()=>{setFam(local);onClose()}} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>✓ Salvar</button></div></div></div>)}
function Shell(){return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}><aside style={{width:240,flexShrink:0,background:'linear-gradient(180deg,#101018,#0c0c12)',borderRight:`1px solid ${C.line}`,padding:'16px 12px',display:'flex',flexDirection:'column',gap:2,position:'sticky',top:0,height:'100vh',overflowY:'auto'}}><div style={{display:'flex',alignItems:'center',gap:10,padding:'4px 6px 14px'}}><div style={{width:38,height:38,borderRadius:11,background:'linear-gradient(145deg,#8b5cf6,#6d28d9)',display:'grid',placeItems:'center',fontSize:18}}>💜</div><div><div style={{fontWeight:800,fontSize:16}}>Denise OS</div><div style={{fontSize:10,color:'#7d7d90'}}>Seu sistema operacional de vida</div></div></div><nav style={{display:'flex',flexDirection:'column',gap:2}}>{navItems.map(([to,label,icon])=>(<NavLink key={to} to={to} end={to==='/'} style={({isActive})=>({display:'flex',alignItems:'center',gap:9,padding:'9px 10px',borderRadius:10,fontSize:13.5,fontWeight:500,color:isActive?'#fff':'rgba(255,255,255,.6)',background:isActive?'rgba(139,92,246,.15)':'transparent',textDecoration:'none',position:'relative'})}>{({isActive})=><>{isActive&&<span style={{position:'absolute',left:-12,top:8,bottom:8,width:3,borderRadius:'0 3px 3px 0',background:C.acc}}/>}<span style={{fontSize:14}}>{icon}</span>{label}</>}</NavLink>))}</nav><div style={{marginTop:14,background:C.s,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'#7d7d90',textTransform:'uppercase' as const,letterSpacing:'.6px',marginBottom:8}}>Score da semana</div><div style={{display:'flex',alignItems:'baseline',gap:8}}><span style={{fontSize:28,fontWeight:800}}>92%</span><span style={{fontSize:11,color:C.ok,fontWeight:700}}>▲ 8%</span></div><div style={{display:'flex',gap:4,alignItems:'flex-end',height:40,marginTop:10}}>{[60,80,70,90,75,85,40].map((h,i)=><span key={i} style={{flex:1,borderRadius:'3px 3px 2px 2px',height:`${h}%`,background:i<3?`linear-gradient(180deg,${C.ok},#15803d)`:`linear-gradient(180deg,${C.acc2},#6d28d9)`}}/>)}</div></div><div style={{marginTop:10,background:C.s,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'#7d7d90',textTransform:'uppercase' as const,letterSpacing:'.6px',marginBottom:12}}>Sequência atual</div><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:6}}>{[{n:12,l:'Espiritual',c:C.pink},{n:8,l:'Treino',c:C.ok},{n:10,l:'Leitura',c:C.warn},{n:7,l:'Água',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}</div></div><button onClick={()=>supabase.auth.signOut()} style={{marginTop:10,width:'100%',background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)',borderRadius:10,padding:'9px',fontSize:12.5,cursor:'pointer'}}>Sair</button></aside><div style={{flex:1,minWidth:0}}><Outlet/></div></div>)}
function Home(){const navigate=useNavigate();
  const [tzSched,setTzSched]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [tzBalance,setTzBalance]=React.useState(0)
  const [tzApps,setTzApps]=React.useState<any[]>([])
  const [climaTemp,setClimaTemp]=React.useState<number|null>(null)
  React.useEffect(()=>{
    fetch('https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current=temperature_2m&timezone=America%2FSao_Paulo')
      .then(r=>r.json())
      .then(d=>{const t=d?.current?.temperature_2m;if(typeof t==='number')setClimaTemp(Math.round(t))})
      .catch(()=>{})
  },[])
  React.useEffect(()=>{(async()=>{
    const [{data:sched},{data:bal},{data:apps}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
      supabase.from('tirzepatida_applications').select('*').order('applied_at',{ascending:false}),
    ])
    const map:Record<string,any>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={planned_dose_mg:Number(row.planned_dose_mg),interval_days:row.interval_days,next_application_date:row.next_application_date}})
    setTzSched(map)
    setTzBalance(Number(bal?.current_balance_mg??0))
    setTzApps(apps||[])
  })()},[])
  function fmtIsoH(iso:string|null|undefined){if(!iso)return '—';return new Date(iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}
  const tzAutonomy=(()=>{const dDen=tzSched.denise?.planned_dose_mg||5;const dFla=tzSched.flavio?.planned_dose_mg||2.5;const iDen=tzSched.denise?.interval_days||5;const iFla=tzSched.flavio?.interval_days||7;const mgDay=dDen/iDen+dFla/iFla;return mgDay>0?Math.floor(tzBalance/mgDay):0})()
  const tzUltimaDenise=tzApps.find((a:any)=>a.person==='denise')
  const h=new Date().getHours(),g=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite';const today=new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long',year:'numeric'});const [wat,setWat]=React.useState(()=>Number(localStorage.getItem('dos_wat')||1800));const [prot,setProt]=React.useState(()=>Number(localStorage.getItem('dos_prot')||76));const [showFam,setShowFam]=React.useState(false);const {fam}=React.useContext(FamCtx);const day=new Date().getDay(),sd=(day>=1&&day<=5)?day:1;const addW=(ml:number)=>{const n=Math.min(wat+ml,4000);setWat(n);localStorage.setItem('dos_wat',String(n))};const addP=(gp:number)=>{const n=Math.min(prot+gp,200);setProt(n);localStorage.setItem('dos_prot',String(n))};
  const extrasSaude=(()=>{try{return JSON.parse(localStorage.getItem('dos_saude_extra')||'[]')}catch{return []}})() as any[]
  const ultimoSaude=extrasSaude[0]
  const ROTINA_DEF_HOME=[{t:'05:30',n:'Devocional',cat:'Espiritual'},{t:'06:00',n:'Acordar · água · humor',cat:'Saúde'},{t:'06:30',n:'Café · whey · creatina',cat:'Alimentação'},{t:'07:00',n:'Levar crianças à escola',cat:'Família'},{t:'07:30',n:'Calistenia',cat:'Exercícios'},{t:'08:20',n:'Banho · skincare',cat:'Casa'},{t:'08:45',n:'Planejar o dia · prioridades',cat:'Trabalho'},{t:'09:30',n:'Lanche da manhã',cat:'Alimentação'},{t:'12:50',n:'Buscar Domi',cat:'Família'},{t:'15:30',n:'Whey da tarde',cat:'Alimentação'},{t:'17:00',n:'Buscar Derick',cat:'Família'},{t:'19:00',n:'Jantar',cat:'Alimentação'},{t:'20:00',n:'Célula (Qua) / Aula (Sex)',cat:'Compromisso'},{t:'21:30',n:'Probióticos',cat:'Saúde'},{t:'22:00',n:'Leitura · 20 min',cat:'Desenvolvimento'}]
  const rotinaItens=(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'null')||ROTINA_DEF_HOME}catch{return ROTINA_DEF_HOME}})() as any[]
  const hojeIsoHome=new Date().toISOString().slice(0,10)
  const rotinaDiaKeyHome=`dos_rotina_done_${hojeIsoHome}`
  const rotinaDoneIdx=new Set<number>((()=>{try{return JSON.parse(localStorage.getItem(rotinaDiaKeyHome)||'[]')}catch{return []}})())
  const rotinaOrdenada=rotinaItens.map((it:any,idx:number)=>({...it,idx})).sort((a:any,b:any)=>String(a.t).localeCompare(String(b.t)))
  let nowMarcadoHome=false
  const rotinaTimeline=rotinaOrdenada.map((it:any)=>{let st='wait';if(rotinaDoneIdx.has(it.idx))st='done';else if(!nowMarcadoHome){st='now';nowMarcadoHome=true};return [it.t,it.n,st] as [string,string,string]})
  const rotinaProximo=rotinaTimeline.find(([,,st])=>st==='now')
  const rotinaFeitos=rotinaDoneIdx.size
  const rotinaTotal=rotinaItens.length
  const devEntries=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  const devHoje=devEntries.some((e:any)=>e.data===hojeIsoHome)
  const devDiasSet=new Set(devEntries.map((e:any)=>e.data))
  let devSequencia=0
  const devDcursor=new Date()
  if(!devDiasSet.has(hojeIsoHome))devDcursor.setDate(devDcursor.getDate()-1)
  while(devDiasSet.has(devDcursor.toISOString().slice(0,10))){devSequencia++;devDcursor.setDate(devDcursor.getDate()-1)}
  const treinosHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]
  function segundaDaSemanaHome(d:Date){const x=new Date(d);const day=x.getDay();const diff=(day===0?-6:1-day);x.setDate(x.getDate()+diff);return x}
  const segIsoHome=segundaDaSemanaHome(new Date()).toISOString().slice(0,10)
  const treinosSemana=treinosHome.filter((t:any)=>t.data>=segIsoHome)
  const diasTreinoPlanejados=6
  const exPct=Math.min(100,Math.round(treinosSemana.length/diasTreinoPlanejados*100))
  const tasksHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_trabalho')||'[]')}catch{return []}})() as any[]
  const tasksConcluidas=tasksHome.filter((t:any)=>t.s==='concluído').length
  const trabPct=tasksHome.length>0?Math.round(tasksConcluidas/tasksHome.length*100):0
  const saudePct=ultimoSaude?100:0
  const hidPct=Math.min(100,Math.round(wat/2500*100))
  const espPct=devHoje?100:0
  const resumoMedia=Math.round((saudePct+exPct+Math.min(100,Math.round(prot/120*100))+hidPct+espPct+trabPct)/6)
  const leiturasHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  const leituraHoje=leiturasHome.some((l:any)=>l.data===hojeIsoHome)
  const lembretes:[string,string,string][]=[]
  if(wat<2500)lembretes.push(['💧','Beber mais água',`${((2500-wat)/1000).toFixed(1).replace('.',',')} L restantes`])
  if(tzSched.denise?.next_application_date)lembretes.push(['💉','Tirzepatida · você',fmtIsoH(tzSched.denise.next_application_date)])
  if(tzSched.flavio?.next_application_date)lembretes.push(['💉','Tirzepatida · Flávio',fmtIsoH(tzSched.flavio.next_application_date)])
  if(!leituraHoje)lembretes.push(['📖','Leitura','Pendente hoje'])
  return(<div style={{padding:'20px 22px 110px'}}>{showFam&&<ModalFam onClose={()=>setShowFam(false)}/>}<div style={{display:'flex',flexWrap:'wrap',gap:14,alignItems:'flex-start',marginBottom:18}}><div><h1 style={{fontSize:25,fontWeight:800,margin:0}}>{g}, Denise! ☀️</h1><div style={{color:'rgba(255,255,255,.6)',fontSize:13,marginTop:5,display:'flex',gap:9,flexWrap:'wrap'}}><span style={{textTransform:'capitalize' as const}}>{today}</span><span style={{background:C.s,border:`1px solid ${C.line}`,padding:'3px 10px',borderRadius:20,fontSize:12}}>📍 São Paulo{climaTemp!==null?`, ${climaTemp}°C`:''}</span></div></div><div style={{marginLeft:'auto',background:`linear-gradient(135deg,${C.s2},${C.s})`,border:`1px solid ${C.line}`,borderRadius:16,padding:'13px 16px',maxWidth:360,display:'flex',gap:11}}><span style={{fontSize:22,color:C.acc2}}>"</span><div><p style={{fontSize:13,fontStyle:'italic',margin:0}}>Tudo posso naquele que me fortalece.</p><span style={{fontSize:11,color:'#7d7d90'}}>Filipenses 4:13</span></div></div><div style={{display:'flex',gap:9,alignItems:'center'}}><button style={{width:40,height:40,borderRadius:11,background:C.s,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:17}}>🔔</button><button style={{display:'inline-flex',alignItems:'center',gap:7,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',fontWeight:700,fontSize:13,padding:'10px 14px',borderRadius:11,border:'none',cursor:'pointer'}}>⚡ Ação rápida</button><Avatar id="denise" label="D" size={40} radius={12}/></div></div><div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14}}><div style={{gridColumn:'span 4'}}><Card title="Seu dia de hoje" action={<NavLink to="/agenda" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver agenda</NavLink>}>{rotinaTimeline.slice(0,6).map(([t,n,st])=>(<div key={t} style={{display:'flex',alignItems:'center',gap:10,padding:'8px 9px',borderRadius:10,marginBottom:2,background:st==='now'?'rgba(139,92,246,.15)':'transparent',border:st==='now'?'1px solid rgba(139,92,246,.35)':'1px solid transparent'}}><span style={{width:38,fontSize:12,color:st==='now'?'#fff':'rgba(255,255,255,.4)',flexShrink:0}}>{t}</span><span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:st==='done'?'rgba(52,211,153,.16)':st==='now'?C.acc:'rgba(255,255,255,.07)',color:st==='done'?C.ok:st==='now'?'#fff':'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>{st==='done'?'✓':st==='now'?'▶':'○'}</span><span style={{fontSize:13.5,flex:1,color:st==='now'?'#fff':st==='done'?'rgba(255,255,255,.5)':'#f3f3f8'}}>{n}</span>{st==='now'&&<span style={{background:C.acc,color:'#fff',fontSize:10,fontWeight:700,padding:'3px 8px',borderRadius:6}}>Atual</span>}</div>))}{rotinaProximo&&<div style={{marginTop:10,background:C.s2,border:'1px dashed rgba(255,255,255,.1)',borderRadius:10,padding:'10px 12px',display:'flex',alignItems:'center',gap:8,fontSize:13}}><span style={{color:C.acc2}}>▶</span>Próximo:<b style={{color:C.acc2}}>{rotinaProximo[1]}</b><span style={{marginLeft:'auto',color:'rgba(255,255,255,.4)',fontSize:12}}>{rotinaProximo[0]}</span></div>}</Card></div><div style={{gridColumn:'span 5'}}><Card title="Resumo do dia"><div style={{display:'flex',justifyContent:'space-between',gap:4,flexWrap:'wrap'}}><Ring pct={saudePct} color={C.ok} label="Saúde"/><Ring pct={exPct} color={C.teal} label="Exercícios"/><Ring pct={Math.min(100,Math.round(prot/120*100))} color={C.warn} label="Alimentação"/><Ring pct={hidPct} color={C.water} label="Hidratação"/><Ring pct={espPct} color={C.acc2} label="Espiritual"/><Ring pct={trabPct} color={C.pink} label="Trabalho"/></div><div style={{marginTop:13,background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'13px 15px',display:'flex',alignItems:'center',gap:12}}><span style={{fontSize:20}}>🔥</span><div><div style={{fontWeight:700,fontSize:14}}>{resumoMedia>=70?'Você está arrasando!':resumoMedia>=40?'Bom progresso hoje!':'Vamos começar o dia!'}</div><div style={{fontSize:12.5,color:'rgba(255,255,255,.6)'}}>Rotina: <b>{rotinaFeitos}</b> de {rotinaTotal} itens feitos hoje.</div></div><div style={{marginLeft:'auto',fontSize:26,fontWeight:800}}>{resumoMedia}%</div></div><div style={{height:9,borderRadius:6,background:C.s3,overflow:'hidden',marginTop:8}}><div style={{height:'100%',width:`${resumoMedia}%`,borderRadius:6,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div></Card></div><div style={{gridColumn:'span 3'}}><Card title="Tirzepatida" action={<NavLink to="/tirzepatida" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Gerenciar</NavLink>}><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,fontSize:13,marginBottom:11}}><div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Última</div><div style={{fontWeight:800}}>{tzUltimaDenise?new Date(tzUltimaDenise.applied_at).toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric'}):'—'}</div><div style={{fontSize:11,color:C.ok}}>{tzUltimaDenise?`${tzUltimaDenise.dose_mg} mg`:''}</div></div><div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Próxima</div><div style={{fontWeight:800}}>{fmtIsoH(tzSched.denise?.next_application_date)}</div><div style={{fontSize:11,color:C.acc2}}>{tzSched.denise?.next_application_date?(()=>{const dias=Math.ceil((new Date(tzSched.denise.next_application_date+'T12:00:00').getTime()-Date.now())/86400000);return dias>0?`Em ${dias} dia${dias===1?'':'s'}`:dias===0?'Hoje':'Atrasada'})():''}</div></div></div><div style={{display:'flex',alignItems:'center',gap:11,background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'11px 13px',marginBottom:11}}><div style={{width:36,height:36,borderRadius:10,background:'rgba(139,92,246,.14)',display:'grid',placeItems:'center',fontSize:17}}>💉</div><div><div style={{fontSize:21,fontWeight:800}}>{tzBalance} <small style={{fontSize:13}}>mg</small></div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Estoque atual</div></div><div style={{marginLeft:'auto',textAlign:'right'}}><div style={{fontWeight:800,fontSize:14}}>~{tzAutonomy} dias</div></div></div><NavLink to="/tirzepatida" style={{display:'flex',alignItems:'center',justifyContent:'center',gap:6,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,textDecoration:'none'}}>+ Registrar aplicação</NavLink><p style={{fontSize:10.5,color:'rgba(255,255,255,.4)',marginTop:10,borderTop:`1px solid ${C.line}`,paddingTop:9,lineHeight:1.4}}>Não substitui orientação médica.</p></Card></div><div style={{gridColumn:'span 3'}}><Card title="Alimentação" action={<NavLink to="/alimentacao" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver mais</NavLink>}><div style={{display:'flex',alignItems:'center',gap:12,marginBottom:11}}><Ring pct={Math.min(100,Math.round(prot/120*100))} color={C.ok} size={64}/><div><div style={{fontSize:21,fontWeight:800}}>{prot} g</div><small style={{fontSize:12,color:'rgba(255,255,255,.4)'}}>de 120 g</small></div></div><div style={{marginTop:10,display:'flex',justifyContent:'space-between',fontSize:12.5,color:'rgba(255,255,255,.6)'}}><span>Água</span><span>{(wat/1000).toFixed(1).replace('.',',')} / 2,5 L</span></div><div style={{height:9,borderRadius:6,background:C.s3,overflow:'hidden',marginTop:6}}><div style={{height:'100%',width:`${Math.min(100,wat/2500*100)}%`,borderRadius:6,background:`linear-gradient(90deg,${C.water},#0284c7)`}}/></div></Card></div><div style={{gridColumn:'span 3'}}><Card title="Saúde" action={<NavLink to="/saude" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver mais</NavLink>}>{ultimoSaude?<>
  <Lrow icon="⚖️" name="Peso" val={ultimoSaude.peso?`${String(ultimoSaude.peso).replace('.',',')} kg`:'—'}/>
  <Lrow icon="🌙" name="Sono" val={ultimoSaude.sono?`${String(ultimoSaude.sono).replace('.',',')} h`:'—'} ok={!!ultimoSaude.sono&&ultimoSaude.sono>=7}/>
  <Lrow icon="📊" name="Intestino" val={ultimoSaude.intestino||'—'} ok={ultimoSaude.intestino==='Regular'}/>
  <Lrow icon="😊" name="Humor" val={ultimoSaude.humor?`${ultimoSaude.humor}/10`:'—'}/>
  <Lrow icon="⚡" name="Energia" val={ultimoSaude.energia?`${ultimoSaude.energia}/10`:'—'}/>
</>:<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Nenhum registro hoje ainda.</div>}</Card></div><div style={{gridColumn:'span 3'}}><Card title="Exercícios" action={<NavLink to="/exercicios" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver mais</NavLink>}><div style={{display:'flex',alignItems:'center',gap:12,marginBottom:11}}><Ring pct={exPct} color={C.teal} size={64}/><div><div style={{fontSize:21,fontWeight:800}}>{treinosSemana.length} / {diasTreinoPlanejados}</div><small style={{fontSize:12,color:'rgba(255,255,255,.4)'}}>treinos esta semana</small></div></div><button onClick={()=>navigate('/exercicios')} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>▶ Iniciar treino</button></Card></div><div style={{gridColumn:'span 3'}}><Card title="Família" action={<button onClick={()=>setShowFam(true)} style={{fontSize:12,color:C.acc2,background:'rgba(139,92,246,.1)',border:'1px solid rgba(139,92,246,.2)',padding:'5px 9px',borderRadius:9,cursor:'pointer'}}>✏️ Editar rotina</button>}>{(['domi','derick'] as const).map(k=>{const nome=k==='domi'?'Domi':'Derick';const pk=fam[k].pk[sd]||'—';return(<div key={k} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 2px',borderBottom:`1px solid ${C.line}`}}><Avatar id={k} label={nome[0]} size={40} radius={11}/><div><div style={{fontWeight:700,fontSize:13.5}}>{nome}</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)'}}>Buscar · {pk}</div></div></div>)})}</Card></div><div style={{gridColumn:'span 3'}}><Card title="Espiritual" action={<NavLink to="/espiritual" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver mais</NavLink>}><Lrow icon="☀️" name="Devocional" val={devHoje?'Concluído':'Pendente'} ok={devHoje}/><Lrow icon="📖" name="Registros" val={`${devEntries.length} no total`}/><div style={{display:'flex',alignItems:'center',gap:6,marginTop:11,fontSize:12.5,color:C.warn}}>🔥 Sequência: {devSequencia} dia{devSequencia===1?'':'s'}</div></Card></div><div style={{gridColumn:'span 3'}}><Card title="Desenvolvimento" action={<NavLink to="/desenvolvimento" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver mais</NavLink>}><div style={{fontWeight:700,fontSize:14,marginBottom:4}}>Hábitos Atômicos</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:10}}>James Clear · 45%</div><div style={{height:9,borderRadius:6,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:'45%',borderRadius:6,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div></Card></div><div style={{gridColumn:'span 3'}}><Card title="Lembretes">{lembretes.length>0?lembretes.map(([icon,name,val],i)=>(<Lrow key={i} icon={icon} name={name} val={val}/>)):<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Nenhum lembrete pendente 🎉</div>}</Card></div><div style={{gridColumn:'span 3'}}><Card title="IA Assistente"><div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'12px 13px',fontSize:13,color:'rgba(255,255,255,.7)',lineHeight:1.5,marginBottom:11}}>{g}, Denise! ☀️ Estoque tirzepatida: {tzBalance} mg. Próxima: {fmtIsoH(tzSched.denise?.next_application_date)}. Vamos juntas? 💜</div><NavLink to="/assistente" style={{display:'flex',alignItems:'center',justifyContent:'center',gap:6,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,textDecoration:'none'}}>Abrir assistente</NavLink></Card></div></div><div style={{position:'fixed',bottom:0,left:240,right:0,background:'rgba(12,12,18,.92)',backdropFilter:'blur(12px)',borderTop:`1px solid ${C.line}`,padding:'11px 22px',display:'flex',gap:8,alignItems:'center',overflowX:'auto',zIndex:40}}><span style={{fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,marginRight:4}}>⚡ Ações rápidas</span><button onClick={()=>addW(250)} style={{flexShrink:0,display:'inline-flex',alignItems:'center',gap:7,padding:'9px 13px',borderRadius:11,border:'none',background:'linear-gradient(135deg,#0ea5e9,#0369a1)',color:'#fff',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>💧 +250 ml Água</button><button onClick={()=>addP(20)} style={{flexShrink:0,display:'inline-flex',alignItems:'center',gap:7,padding:'9px 13px',borderRadius:11,border:'none',background:'linear-gradient(135deg,#16a34a,#15803d)',color:'#fff',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>🥩 +20 g Proteína</button>{[['⚖️ Peso','/saude'],['😊 Humor','/saude'],['📊 Intestino','/saude'],['💪 Treino','/exercicios'],['🍽️ Refeição','/alimentacao'],['💉 Aplicação','/tirzepatida']].map(([l,rota])=>(<button key={l} onClick={()=>navigate(rota)} style={{flexShrink:0,display:'inline-flex',alignItems:'center',gap:7,padding:'9px 13px',borderRadius:11,border:`1px solid ${C.line}`,background:C.s,color:'#fff',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>{l}</button>))}</div></div>)}
function Rotina(){
  type RItem={t:string,n:string,cat:string}
  const DEF:RItem[]=[{t:'05:30',n:'Devocional',cat:'Espiritual'},{t:'06:00',n:'Acordar · água · humor',cat:'Saúde'},{t:'06:30',n:'Café · whey · creatina',cat:'Alimentação'},{t:'07:00',n:'Levar crianças à escola',cat:'Família'},{t:'07:30',n:'Calistenia',cat:'Exercícios'},{t:'08:20',n:'Banho · skincare',cat:'Casa'},{t:'08:45',n:'Planejar o dia · prioridades',cat:'Trabalho'},{t:'09:30',n:'Lanche da manhã',cat:'Alimentação'},{t:'12:50',n:'Buscar Domi',cat:'Família'},{t:'15:30',n:'Whey da tarde',cat:'Alimentação'},{t:'17:00',n:'Buscar Derick',cat:'Família'},{t:'19:00',n:'Jantar',cat:'Alimentação'},{t:'20:00',n:'Célula (Qua) / Aula (Sex)',cat:'Compromisso'},{t:'21:30',n:'Probióticos',cat:'Saúde'},{t:'22:00',n:'Leitura · 20 min',cat:'Desenvolvimento'}]
  const [items,setItems]=React.useState<RItem[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'null')||DEF}catch{return DEF}})
  const rotinaDiaKey=`dos_rotina_done_${new Date().toISOString().slice(0,10)}`
  const [done,setDoneRaw]=React.useState<number[]>(()=>{try{return JSON.parse(localStorage.getItem(rotinaDiaKey)||'[]')}catch{return []}})
  const setDone=(fn:number[]|((prev:number[])=>number[]))=>{setDoneRaw((prev:number[])=>{const n=typeof fn==='function'?(fn as (prev:number[])=>number[])(prev):fn;localStorage.setItem(rotinaDiaKey,JSON.stringify(n));return n})}
  const [editIdx,setEditIdx]=React.useState<number|null>(null)
  const [editItem,setEditItem]=React.useState<RItem>({t:'',n:'',cat:''})
  const [adding,setAdding]=React.useState(false)
  const [newItem,setNewItem]=React.useState<RItem>({t:'',n:'',cat:'Saúde'})
  const cats=['Espiritual','Saúde','Alimentação','Família','Exercícios','Casa','Trabalho','Compromisso','Desenvolvimento']
  const save=(it:RItem[])=>{setItems(it);localStorage.setItem('dos_rotina',JSON.stringify(it))}
  const openEdit=(i:number)=>{setEditIdx(i);setEditItem({...items[i]})}
  const saveEdit=()=>{if(editIdx===null)return;const n=[...items];n[editIdx]=editItem;save(n);setEditIdx(null)}
  const del=(i:number)=>{save(items.filter((_,idx)=>idx!==i));setDone(d=>d.filter(x=>x!==i).map(x=>x>i?x-1:x))}
  const addItem=()=>{if(!newItem.n||!newItem.t)return;save([...items,newItem]);setAdding(false);setNewItem({t:'',n:'',cat:'Saúde'})}
  return(<div style={{padding:'24px 28px'}}>
    {editIdx!==null&&<div onClick={e=>{if(e.target===e.currentTarget)setEditIdx(null)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:420,padding:20}}>
        <h3 style={{margin:'0 0 16px',fontSize:16}}>Editar item</h3>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Horário</label>
        <input type="time" value={editItem.t} onChange={e=>setEditItem(p=>({...p,t:e.target.value}))} style={{width:'100%',background:'#0a0a0f',border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12,colorScheme:'dark'}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Nome</label>
        <input value={editItem.n} onChange={e=>setEditItem(p=>({...p,n:e.target.value}))} style={{width:'100%',background:'#0a0a0f',border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Categoria</label>
        <select value={editItem.cat} onChange={e=>setEditItem(p=>({...p,cat:e.target.value}))} style={{width:'100%',background:'#0a0a0f',border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:16,colorScheme:'dark'}}>{cats.map(c=><option key={c}>{c}</option>)}</select>
        <div style={{display:'flex',gap:10}}><button onClick={()=>setEditIdx(null)} style={{flex:1,background:'#1c1c28',border:'1px solid rgba(255,255,255,.07)',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Cancelar</button><button onClick={saveEdit} style={{flex:1,background:'linear-gradient(135deg,#8b5cf6,#7c3aed)',border:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>✓ Salvar</button></div>
      </div>
    </div>}
    {adding&&<div onClick={e=>{if(e.target===e.currentTarget)setAdding(false)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:420,padding:20}}>
        <h3 style={{margin:'0 0 16px',fontSize:16}}>Novo item</h3>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Horário</label>
        <input type="time" value={newItem.t} onChange={e=>setNewItem(p=>({...p,t:e.target.value}))} style={{width:'100%',background:'#0a0a0f',border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12,colorScheme:'dark'}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Nome</label>
        <input value={newItem.n} onChange={e=>setNewItem(p=>({...p,n:e.target.value}))} placeholder="Ex: Vitamina D" style={{width:'100%',background:'#0a0a0f',border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Categoria</label>
        <select value={newItem.cat} onChange={e=>setNewItem(p=>({...p,cat:e.target.value}))} style={{width:'100%',background:'#0a0a0f',border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:16,colorScheme:'dark'}}>{cats.map(c=><option key={c}>{c}</option>)}</select>
        <div style={{display:'flex',gap:10}}><button onClick={()=>setAdding(false)} style={{flex:1,background:'#1c1c28',border:'1px solid rgba(255,255,255,.07)',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Cancelar</button><button onClick={addItem} style={{flex:1,background:'linear-gradient(135deg,#8b5cf6,#7c3aed)',border:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar</button></div>
      </div>
    </div>}
    <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:20}}>
      <div><h1 style={{fontSize:24,fontWeight:800,margin:0}}>Minha Rotina</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginTop:4}}>Toque para marcar · ✏️ para editar · salva automaticamente</p></div>
      <button onClick={()=>setAdding(true)} style={{background:'linear-gradient(135deg,#8b5cf6,#7c3aed)',color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Novo item</button>
    </div>
    <Card title={`Hoje — ${done.length} / ${items.length} concluídos (${Math.round(done.length/items.length*100)}%)`}>
      <>{items.map((item,i)=>(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 9px',borderRadius:10,marginBottom:2,background:done.includes(i)?'rgba(52,211,153,.06)':'transparent',border:done.includes(i)?'1px solid rgba(52,211,153,.15)':'1px solid transparent'}}>
        <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:done.includes(i)?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:done.includes(i)?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>{done.includes(i)?'✓':'○'}</span>
        <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,cursor:'pointer'}}>{item.t}</span>
        <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{flex:1,fontSize:13.5,color:done.includes(i)?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:done.includes(i)?'line-through':'none',cursor:'pointer'}}>{item.n}</span>
        <span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:'rgba(139,92,246,.15)',color:C.acc2,flexShrink:0}}>{item.cat}</span>
        <button onClick={()=>openEdit(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:13,flexShrink:0}}>✏️</button>
        <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
      </div>))}</>
    </Card>
  </div>)}
function Agenda(){
  const GOOGLE_CLIENT_ID='386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'
  const GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar.events'
  const [eventos,setEventos]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_agenda')||'[]')}catch{return []}})
  const [novo,setNovo]=React.useState({data:'',hora:'',nome:'',cor:'#38bdf8'})
  const [schedules,setSchedules]=React.useState<any>({})
  const [saved,setSaved]=React.useState(false)
  const [gToken,setGToken]=React.useState<string>(()=>{
    try{
      const raw=JSON.parse(localStorage.getItem('dos_google_token')||'null')
      if(raw&&raw.token&&raw.expiresAt>Date.now())return raw.token
    }catch{}
    return ''
  })
  const [gEventos,setGEventos]=React.useState<any[]>([])
  const [gLoading,setGLoading]=React.useState(false)
  const [gErro,setGErro]=React.useState('')
  const [view,setView]=React.useState<'dia'|'semana'|'mes'|'ano'>('mes')
  const [cursor,setCursor]=React.useState(new Date())
  const [medicamentosAg,setMedicamentosAg]=React.useState<Record<string,any[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_medicamentos')||'{}')}catch{return {}}})

  React.useEffect(()=>{
    function refrescarMedicamentos(){
      try{setMedicamentosAg(JSON.parse(localStorage.getItem('dos_medicamentos')||'{}'))}catch{}
    }
    window.addEventListener('focus',refrescarMedicamentos)
    window.addEventListener('storage',refrescarMedicamentos)
    return ()=>{
      window.removeEventListener('focus',refrescarMedicamentos)
      window.removeEventListener('storage',refrescarMedicamentos)
    }
  },[])

  React.useEffect(()=>{
    supabase.from('tirzepatida_schedule').select('*').then(({data}:any)=>{
      const m:any={}
      ;(data||[]).forEach((r:any)=>{m[r.person]=r})
      setSchedules(m)
    })
  },[])

  React.useEffect(()=>{
    if(gToken)buscarEventosGoogle(gToken)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  function buscarEventosGoogle(token:string){
    setGLoading(true);setGErro('')
    const hoje=new Date()
    const timeMin=new Date(hoje.getFullYear(),hoje.getMonth()-2,1).toISOString()
    const timeMax=new Date(hoje.getFullYear(),hoje.getMonth()+10,1).toISOString()
    fetch(`https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&maxResults=250&singleEvents=true&orderBy=startTime`,{headers:{Authorization:`Bearer ${token}`}})
      .then(r=>r.json())
      .then(data=>{setGEventos(data.items||[]);setGLoading(false)})
      .catch(()=>{setGErro('Erro ao buscar eventos do Google.');setGLoading(false)})
  }

  function conectarGoogle(){
    const g=(window as any).google
    if(!g||!g.accounts||!g.accounts.oauth2){setGErro('Google ainda carregando, tenta de novo em alguns segundos.');return}
    const tokenClient=g.accounts.oauth2.initTokenClient({
      client_id:GOOGLE_CLIENT_ID,
      scope:GOOGLE_SCOPE,
      callback:(resp:any)=>{
        if(resp&&resp.access_token){
          setGToken(resp.access_token)
          const expiresAt=Date.now()+((resp.expires_in||3600)*1000)
          try{localStorage.setItem('dos_google_token',JSON.stringify({token:resp.access_token,expiresAt}))}catch{}
          buscarEventosGoogle(resp.access_token)
        }else{setGErro('Nao foi possivel conectar ao Google.')}
      }
    })
    tokenClient.requestAccessToken()
  }

  function addHora(hhmm:string){
    const partes=hhmm.split(':').map(Number)
    const hh=partes[0]||0,mm=partes[1]||0
    const d=new Date();d.setHours(hh+1,mm,0,0)
    return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  }

  function addEvento(){
    if(!novo.data||!novo.nome)return
    const n=[...eventos,{...novo}].sort((a,b)=>(a.data+a.hora).localeCompare(b.data+b.hora))
    setEventos(n);localStorage.setItem('dos_agenda',JSON.stringify(n))
    if(gToken){
      const body:any={summary:novo.nome}
      if(novo.hora){
        body.start={dateTime:`${novo.data}T${novo.hora}:00`,timeZone:'America/Sao_Paulo'}
        body.end={dateTime:`${novo.data}T${addHora(novo.hora)}:00`,timeZone:'America/Sao_Paulo'}
      }else{
        body.start={date:novo.data}
        body.end={date:novo.data}
      }
      fetch('https://www.googleapis.com/calendar/v3/calendars/primary/events',{
        method:'POST',
        headers:{Authorization:`Bearer ${gToken}`,'Content-Type':'application/json'},
        body:JSON.stringify(body)
      }).then(()=>buscarEventosGoogle(gToken)).catch(()=>{})
    }
    setNovo({data:'',hora:'',nome:'',cor:'#38bdf8'});setSaved(true)
  }
  function delEvento(idx:number){
    const n=eventos.filter((_e:any,i:number)=>i!==idx)
    setEventos(n);localStorage.setItem('dos_agenda',JSON.stringify(n))
  }

  function pad2(n:number){return String(n).padStart(2,'0')}
  function toISO(d:Date){return `${d.getFullYear()}-${pad2(d.getMonth()+1)}-${pad2(d.getDate())}`}
  function startOfWeek(d:Date){
    const dt=new Date(d);const day=dt.getDay();const diff=(day===0?-6:1-day)
    dt.setDate(dt.getDate()+diff);dt.setHours(0,0,0,0);return dt
  }
  function nav(delta:number){
    const d=new Date(cursor)
    if(view==='dia')d.setDate(d.getDate()+delta)
    else if(view==='semana')d.setDate(d.getDate()+delta*7)
    else if(view==='mes')d.setMonth(d.getMonth()+delta)
    else d.setFullYear(d.getFullYear()+delta)
    setCursor(d)
  }
  function irHoje(){setCursor(new Date())}
  function atualizarAgenda(){
    try{setEventos(JSON.parse(localStorage.getItem('dos_agenda')||'[]'))}catch{}
    try{setMedicamentosAg(JSON.parse(localStorage.getItem('dos_medicamentos')||'{}'))}catch{}
    supabase.from('tirzepatida_schedule').select('*').then(({data}:any)=>{
      const m:any={}
      ;(data||[]).forEach((r:any)=>{m[r.person]=r})
      setSchedules(m)
    })
    if(gToken)buscarEventosGoogle(gToken)
  }

  const localEvs=eventos.map((e:any)=>({date:e.data,time:e.hora,title:e.nome,color:e.cor,source:'local'}))
  const googleEvs=gEventos.map((ev:any)=>{
    const inicio=ev.start?.dateTime||ev.start?.date
    const isDate=!!ev.start?.date
    const d=new Date(inicio)
    return {date:toISO(d),time:isDate?'':`${pad2(d.getHours())}:${pad2(d.getMinutes())}`,title:ev.summary||'(Sem titulo)',color:'#4285F4',source:'google'}
  })
  const medEvs:any[]=[]
  const medKids:Record<string,{nome:string,cor:string}>={domi:{nome:'Domi',cor:C.pink},derick:{nome:'Derick',cor:C.ok}}
  Object.keys(medicamentosAg).forEach(kid=>{
    const info=medKids[kid]
    if(!info)return
    ;(medicamentosAg[kid]||[]).forEach((m:any)=>{
      const horarios=(m.horarios||'').split(',').map((h:string)=>h.trim()).filter((h:string)=>/^\d{1,2}:\d{2}$/.test(h))
      if(horarios.length===0)return
      for(let off=-7;off<=60;off++){
        const d=new Date();d.setDate(d.getDate()+off)
        const iso=toISO(d)
        horarios.forEach((h:string)=>{
          medEvs.push({date:iso,time:h,title:`${m.nome} - ${info.nome}`,color:info.cor,source:'medicamento'})
        })
      }
    })
  })
  const tirzoEvs:any[]=[]
  if(schedules.denise?.next_application_date)tirzoEvs.push({date:schedules.denise.next_application_date,time:'',title:'Tirzepatida - Denise',color:C.acc2,source:'tirzo'})
  if(schedules.flavio?.next_application_date)tirzoEvs.push({date:schedules.flavio.next_application_date,time:'',title:'Tirzepatida - Flavio',color:C.water,source:'tirzo'})
  const allEvs=[...localEvs,...googleEvs,...tirzoEvs,...medEvs]
  const evsByDate:Record<string,any[]>={}
  allEvs.forEach((e:any)=>{(evsByDate[e.date]=evsByDate[e.date]||[]).push(e)})
  Object.values(evsByDate).forEach((arr:any)=>arr.sort((a:any,b:any)=>(a.time||'').localeCompare(b.time||'')))

  function fmtDiaLong(d:Date){return d.toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long',year:'numeric'})}
  function fmtMesAno(d:Date){const s2=d.toLocaleDateString('pt-BR',{month:'long',year:'numeric'});return s2.charAt(0).toUpperCase()+s2.slice(1)}
  function fmtDiaCurto(d:Date){return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}

  function excluirEventoUnificado(ev:any){
    if(ev.source!=='local')return
    const idx=eventos.findIndex((e:any)=>e.data===ev.date&&e.hora===ev.time&&e.nome===ev.title)
    if(idx>=0)delEvento(idx)
  }

  function renderDia(){
    const diaISO=toISO(cursor)
    const evs=evsByDate[diaISO]||[]
    return(<Card title={fmtDiaLong(cursor)}>
      {evs.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum evento neste dia.</div>}
      {evs.map((e:any,i:number)=>(<div key={i} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:`1px solid ${C.line}`,alignItems:'center'}}>
        <span style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.time}</span>
        <span style={{width:4,height:20,borderRadius:2,background:e.color,flexShrink:0}}/>
        <span style={{fontSize:13.5,flex:1}}>{e.title}</span>
        {e.source==='local'&&<button onClick={()=>excluirEventoUnificado(e)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button>}
      </div>))}
    </Card>)
  }

  function renderSemana(){
    const inicio=startOfWeek(cursor)
    const dias=[...Array(7)].map((_,i)=>{const d=new Date(inicio);d.setDate(d.getDate()+i);return d})
    return(<Card title={`Semana de ${fmtDiaCurto(dias[0])} a ${fmtDiaCurto(dias[6])}`}>
      <div style={{display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:8}}>
        {dias.map((d,i)=>{
          const iso=toISO(d)
          const evs=evsByDate[iso]||[]
          const hoje=iso===toISO(new Date())
          return(<div key={i} onClick={()=>{setCursor(d);setView('dia')}} style={{background:hoje?'rgba(139,92,246,.12)':C.s2,border:`1px solid ${hoje?C.acc2:C.line}`,borderRadius:10,padding:8,minHeight:120,cursor:'pointer'}}>
            <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>{d.toLocaleDateString('pt-BR',{weekday:'short'})}</div>
            <div style={{fontSize:14,fontWeight:700,marginBottom:6}}>{d.getDate()}</div>
            {evs.slice(0,4).map((e:any,j:number)=>(<div key={j} style={{fontSize:10.5,padding:'2px 4px',borderRadius:4,background:`${e.color}22`,color:e.color,marginBottom:2,overflow:'hidden',whiteSpace:'nowrap' as const,textOverflow:'ellipsis'}}>{e.title}</div>))}
            {evs.length>4&&<div style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>+{evs.length-4}</div>}
          </div>)
        })}
      </div>
    </Card>)
  }

  function renderMes(){
    const mesInicio=new Date(cursor.getFullYear(),cursor.getMonth(),1)
    const gridStart=startOfWeek(mesInicio)
    const cells=[...Array(42)].map((_,i)=>{const d=new Date(gridStart);d.setDate(d.getDate()+i);return d})
    const hojeISO=toISO(new Date())
    return(<Card title={fmtMesAno(cursor)}>
      <div style={{display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:4,marginBottom:6}}>
        {['Seg','Ter','Qua','Qui','Sex','Sab','Dom'].map(d=>(<div key={d} style={{fontSize:11,color:'rgba(255,255,255,.4)',textAlign:'center' as const,padding:'4px 0'}}>{d}</div>))}
      </div>
      <div style={{display:'grid',gridTemplateColumns:'repeat(7,1fr)',gap:4}}>
        {cells.map((d,i)=>{
          const iso=toISO(d)
          const evs=evsByDate[iso]||[]
          const foraDoMes=d.getMonth()!==cursor.getMonth()
          const hoje=iso===hojeISO
          return(<div key={i} onClick={()=>{setCursor(d);setView('dia')}} style={{background:hoje?'rgba(139,92,246,.12)':C.s2,border:`1px solid ${hoje?C.acc2:C.line}`,borderRadius:8,padding:5,minHeight:68,opacity:foraDoMes?0.35:1,cursor:'pointer'}}>
            <div style={{fontSize:11.5,fontWeight:hoje?800:600,marginBottom:3}}>{d.getDate()}</div>
            {evs.slice(0,2).map((e:any,j:number)=>(<div key={j} style={{fontSize:9.5,padding:'1px 3px',borderRadius:3,background:`${e.color}22`,color:e.color,marginBottom:1,overflow:'hidden',whiteSpace:'nowrap' as const,textOverflow:'ellipsis'}}>{e.title}</div>))}
            {evs.length>2&&<div style={{fontSize:9,color:'rgba(255,255,255,.4)'}}>+{evs.length-2}</div>}
          </div>)
        })}
      </div>
    </Card>)
  }

  function renderAno(){
    const meses=[...Array(12)].map((_,i)=>new Date(cursor.getFullYear(),i,1))
    return(<Card title={String(cursor.getFullYear())}>
      <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:12}}>
        {meses.map((m,i)=>{
          const count=allEvs.filter((e:any)=>{const ed=new Date(e.date+'T12:00:00');return ed.getFullYear()===m.getFullYear()&&ed.getMonth()===m.getMonth()}).length
          const nomeMes=m.toLocaleDateString('pt-BR',{month:'long'})
          return(<div key={i} onClick={()=>{setCursor(m);setView('mes')}} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:12,cursor:'pointer'}}>
            <div style={{fontSize:13,fontWeight:700,marginBottom:4,textTransform:'capitalize' as const}}>{nomeMes}</div>
            <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{count} evento{count===1?'':'s'}</div>
          </div>)
        })}
      </div>
    </Card>)
  }

  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'flex-start',marginBottom:16,flexWrap:'wrap' as const,gap:10}}>
      <div>
        <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Agenda</h1>
        <p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>{new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long'})}</p>
      </div>
      {!gToken?
        <button onClick={conectarGoogle} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'9px 14px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>Conectar Google Calendar</button>
        :<div style={{fontSize:12,color:C.ok,fontWeight:700,padding:'9px 14px'}}>Google Calendar conectado</div>
      }
    </div>
    {gErro&&<div style={{background:'rgba(248,113,113,.1)',border:'1px solid rgba(248,113,113,.3)',borderRadius:10,padding:'8px 12px',fontSize:12.5,color:C.danger,marginBottom:12}}>{gErro}</div>}
    <div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',marginBottom:16,flexWrap:'wrap' as const,gap:10}}>
      <div style={{display:'flex',gap:6}}>
        {(['dia','semana','mes','ano'] as const).map(v=>(<button key={v} onClick={()=>setView(v)} style={{background:view===v?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,border:`1px solid ${view===v?'transparent':C.line}`,color:'#fff',borderRadius:9,padding:'8px 16px',fontSize:12.5,fontWeight:700,cursor:'pointer',textTransform:'capitalize' as const}}>{v}</button>))}
      </div>
      <div style={{display:'flex',gap:6,alignItems:'center'}}>
        <button onClick={()=>nav(-1)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:8,padding:'7px 12px',fontSize:13,cursor:'pointer'}}>&larr;</button>
        <button onClick={irHoje} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:8,padding:'7px 12px',fontSize:12.5,cursor:'pointer'}}>Hoje</button>
        <button onClick={()=>nav(1)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:8,padding:'7px 12px',fontSize:13,cursor:'pointer'}}>&rarr;</button>
        <button onClick={atualizarAgenda} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:8,padding:'7px 12px',fontSize:12.5,cursor:'pointer',marginLeft:4}}>&#8635; Atualizar</button>
      </div>
    </div>
    {gLoading&&<div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:10}}>Carregando eventos do Google...</div>}
    <div style={{marginBottom:16}}>
      {view==='dia'&&renderDia()}
      {view==='semana'&&renderSemana()}
      {view==='mes'&&renderMes()}
      {view==='ano'&&renderAno()}
    </div>
    <Card title="Adicionar evento">
      {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>Salvo!{gToken?' (e enviado ao Google Calendar)':''}</div>}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 2fr 1fr',gap:8,marginBottom:10}}>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novo.data} onChange={e=>setNovo(p=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Hora</label><input type="time" value={novo.hora} onChange={e=>setNovo(p=>({...p,hora:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Evento</label><input value={novo.nome} onChange={e=>setNovo(p=>({...p,nome:e.target.value}))} placeholder="Ex: Celula" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Cor</label><input type="color" value={novo.cor} onChange={e=>setNovo(p=>({...p,cor:e.target.value}))} style={{width:'100%',height:36,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:2,cursor:'pointer'}}/></div>
      </div>
      <button onClick={addEvento} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar evento</button>
    </Card>
  </div>)
}
function Espiritual(){
  const [ref,setRef]=React.useState('')
  const [reflex,setReflex]=React.useState('')
  const [grat,setGrat]=React.useState('')
  const [apren,setApren]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const [entries,setEntries]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})
  function isoHoje(){return new Date().toISOString().slice(0,10)}
  function salvar(){
    const hoje=isoHoje()
    const reg={data:hoje,ref,reflex,grat,apren}
    const outros=entries.filter((e:any)=>e.data!==hoje)
    const n=[reg,...outros].sort((a:any,b:any)=>b.data.localeCompare(a.data))
    setEntries(n);localStorage.setItem('dos_devocionais',JSON.stringify(n))
    setSaved(true)
  }
  const diasComEntrada=new Set(entries.map((e:any)=>e.data))
  let sequencia=0
  const dcursor=new Date()
  if(!diasComEntrada.has(isoHoje()))dcursor.setDate(dcursor.getDate()-1)
  while(diasComEntrada.has(dcursor.toISOString().slice(0,10))){sequencia++;dcursor.setDate(dcursor.getDate()-1)}
  const anoAtual=String(new Date().getFullYear())
  const diasNoAno=entries.filter((e:any)=>e.data.startsWith(anoAtual)).length
  const pctAno=Math.min(100,Math.round(diasNoAno/365*100))
  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Espiritual</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Devocional diário · 🔥 Sequência de {sequencia} dia{sequencia===1?'':'s'}</p>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Devocional de hoje">
        {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Devocional salvo!</div>}
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Referência bíblica</label>
        <input value={ref} onChange={e=>setRef(e.target.value)} placeholder="Ex: Salmos 143:10" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Reflexão</label>
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
        </div>}
      </Card>
      <div>
        <Card title="Plano de leitura">
          <div style={{display:'flex',justifyContent:'space-between',fontSize:12.5,color:'rgba(255,255,255,.6)'}}><span>Dias com devocional em {anoAtual}</span><span>{diasNoAno} / 365</span></div>
          <div style={{height:9,borderRadius:6,background:C.s3,overflow:'hidden',marginTop:8,marginBottom:14}}><div style={{height:'100%',width:`${pctAno}%`,borderRadius:6,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div>
          <div style={{fontSize:13,color:C.warn}}>🔥 Sequência: {sequencia} dia{sequencia===1?'':'s'}</div>
        </Card>
        <div style={{marginTop:16}}><Card title="Versículo do dia"><p style={{fontSize:13,fontStyle:'italic',lineHeight:1.6}}>"Ensina-me a fazer a tua vontade, pois tu és o meu Deus."</p><span style={{fontSize:12,color:C.acc2}}>Salmos 143:10</span></Card></div>
      </div>
    </div>
  </div>)
}
function Saude(){
  type SReg={data:string,peso:number,imc:number,gordura:number,humor:number,energia:number,intestino:string,sint:string,sono?:number}
  type MReg={data:string,cintura:number,quadril:number,peito:number,coxaE:number,coxaD:number,bracE:number,bracD:number,abdSup:number,abdInf:number}
  type ConsReg={data:string,tipo:string,obs:string,proximo:string}
  type CriancaReg={data:string,peso:number,altura:number,obs:string}
  const OKOK:SReg[]=[
    {data:"10/12",peso:75.70,imc:28.5,gordura:39.1,humor:0,energia:0,intestino:"",sint:""},{data:"12/12",peso:74.75,imc:28.1,gordura:38.6,humor:0,energia:0,intestino:"",sint:""},{data:"15/12",peso:74.10,imc:27.9,gordura:38.3,humor:0,energia:0,intestino:"",sint:""},{data:"19/12",peso:73.05,imc:27.5,gordura:37.8,humor:0,energia:0,intestino:"",sint:""},{data:"24/12",peso:72.95,imc:27.5,gordura:37.7,humor:0,energia:0,intestino:"",sint:""},{data:"31/12",peso:72.30,imc:27.2,gordura:37.4,humor:0,energia:0,intestino:"",sint:""},
    {data:"03/01",peso:72.00,imc:27.1,gordura:37.3,humor:0,energia:0,intestino:"",sint:""},{data:"08/01",peso:71.10,imc:26.8,gordura:36.8,humor:0,energia:0,intestino:"",sint:""},{data:"11/01",peso:69.55,imc:26.2,gordura:35.9,humor:0,energia:0,intestino:"",sint:""},{data:"18/01",peso:71.00,imc:26.7,gordura:37.8,humor:0,energia:0,intestino:"",sint:""},{data:"22/01",peso:69.75,imc:26.3,gordura:37.1,humor:0,energia:0,intestino:"",sint:""},{data:"30/01",peso:67.30,imc:25.3,gordura:35.7,humor:0,energia:0,intestino:"",sint:""},
    {data:"04/02",peso:68.10,imc:25.6,gordura:36.2,humor:0,energia:0,intestino:"",sint:""},{data:"10/02",peso:65.95,imc:24.8,gordura:34.9,humor:0,energia:0,intestino:"",sint:""},{data:"12/02",peso:66.85,imc:25.2,gordura:35.4,humor:0,energia:0,intestino:"",sint:""},{data:"16/02",peso:65.80,imc:24.8,gordura:34.8,humor:0,energia:0,intestino:"",sint:""},{data:"22/02",peso:64.90,imc:24.4,gordura:34.3,humor:0,energia:0,intestino:"",sint:""},{data:"28/02",peso:62.70,imc:23.6,gordura:32.8,humor:0,energia:0,intestino:"",sint:""},
    {data:"04/03",peso:63.35,imc:23.8,gordura:33.2,humor:0,energia:0,intestino:"",sint:""},{data:"09/03",peso:62.55,imc:23.5,gordura:32.7,humor:0,energia:0,intestino:"",sint:""},{data:"14/03",peso:62.15,imc:23.4,gordura:32.4,humor:0,energia:0,intestino:"",sint:""},{data:"21/03",peso:61.60,imc:23.2,gordura:32.1,humor:0,energia:0,intestino:"",sint:""},{data:"25/03",peso:62.80,imc:23.6,gordura:32.9,humor:0,energia:0,intestino:"",sint:""},
    {data:"03/04",peso:61.95,imc:23.3,gordura:32.3,humor:0,energia:0,intestino:"",sint:""},{data:"09/04",peso:62.95,imc:23.7,gordura:33.0,humor:0,energia:0,intestino:"",sint:""},{data:"14/04",peso:63.00,imc:23.7,gordura:33.0,humor:0,energia:0,intestino:"",sint:""},{data:"18/04",peso:60.55,imc:22.8,gordura:31.3,humor:0,energia:0,intestino:"",sint:""},{data:"21/04",peso:61.25,imc:23.1,gordura:31.8,humor:0,energia:0,intestino:"",sint:""},{data:"29/04",peso:63.00,imc:23.7,gordura:33.0,humor:0,energia:0,intestino:"",sint:""},
    {data:"18/05",peso:63.75,imc:24.0,gordura:33.5,humor:0,energia:0,intestino:"",sint:""},{data:"23/05",peso:63.80,imc:24.0,gordura:33.5,humor:0,energia:0,intestino:"",sint:""},{data:"28/05",peso:63.85,imc:24.0,gordura:33.6,humor:0,energia:0,intestino:"",sint:""},
    {data:"01/06",peso:63.95,imc:24.1,gordura:33.6,humor:0,energia:0,intestino:"",sint:""},{data:"08/06",peso:63.95,imc:24.1,gordura:33.6,humor:0,energia:0,intestino:"",sint:""},{data:"15/06",peso:63.65,imc:24.0,gordura:33.4,humor:0,energia:0,intestino:"",sint:""},{data:"21/06",peso:62.45,imc:23.5,gordura:32.6,humor:0,energia:0,intestino:"",sint:""},{data:"27/06",peso:61.95,imc:23.3,gordura:32.3,humor:0,energia:0,intestino:"",sint:""},
    {data:"01/07",peso:61.45,imc:23.1,gordura:32.0,humor:0,energia:0,intestino:"",sint:""},{data:"06/07",peso:61.85,imc:23.3,gordura:32.2,humor:0,energia:0,intestino:"",sint:""},{data:"11/07",peso:61.15,imc:23.0,gordura:31.7,humor:0,energia:0,intestino:"",sint:""},{data:"18/07",peso:62.35,imc:23.5,gordura:32.6,humor:0,energia:0,intestino:"",sint:""},{data:"23/07",peso:63.55,imc:23.9,gordura:33.4,humor:0,energia:0,intestino:"",sint:""},
  ]
  const MEDIDAS:MReg[]=[
    {data:"11/02",cintura:76,quadril:97,peito:98,coxaE:53,coxaD:54,bracE:27,bracD:28,abdSup:80,abdInf:83},{data:"18/02",cintura:77,quadril:97,peito:97,coxaE:51,coxaD:52,bracE:26,bracD:27,abdSup:82,abdInf:82},{data:"25/02",cintura:73,quadril:93,peito:95,coxaE:50,coxaD:51,bracE:27,bracD:27,abdSup:79,abdInf:81},{data:"04/03",cintura:74,quadril:92.5,peito:92,coxaE:48,coxaD:50,bracE:27,bracD:27,abdSup:78,abdInf:82},{data:"11/03",cintura:73,quadril:91,peito:92,coxaE:51,coxaD:50,bracE:27,bracD:27,abdSup:79,abdInf:82},{data:"18/03",cintura:73,quadril:93,peito:92,coxaE:49,coxaD:49,bracE:24,bracD:24,abdSup:76,abdInf:82},{data:"25/03",cintura:71,quadril:91,peito:92,coxaE:48,coxaD:49.5,bracE:24,bracD:24,abdSup:78,abdInf:80},{data:"29/07",cintura:73,quadril:91.5,peito:91,coxaE:48,coxaD:49,bracE:25,bracD:25.5,abdSup:78,abdInf:81},
  ]
  const [extras,setExtras]=React.useState<SReg[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_saude_extra')||'[]')}catch{return []}})
  const [peso,setPeso]=React.useState('')
  const [humor,setHumor]=React.useState('')
  const [energia,setEnergia]=React.useState('')
  const [intestino,setIntestino]=React.useState('')
  const [sint,setSint]=React.useState('')
  const [sono,setSono]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const [aba,setAba]=React.useState<'denise'|'flavio'|'domi'|'derick'>('denise')
  const [consuls,setConsuls]=React.useState<Record<string,ConsReg[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_consuls')||'{}')}catch{return {}}})
  const [criancas,setCriancas]=React.useState<Record<string,CriancaReg[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_criancas')||'{}')}catch{return {}}})
  const [tamanhos,setTamanhos]=React.useState<Record<string,Record<string,string>>>(()=>{try{return JSON.parse(localStorage.getItem('dos_tamanhos')||'{}')}catch{return {}}})
  const [novaConsulta,setNovaConsulta]=React.useState({tipo:'',data:'',obs:'',proximo:''})
  const [novaCrianca,setNovaCrianca]=React.useState({peso:'',altura:'',obs:''})
  const [savedC,setSavedC]=React.useState(false)
  const [extrasF,setExtrasF]=React.useState<SReg[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_saude_extra_flavio')||'null');return v||[{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}catch{return [{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}})
  const [pesoF,setPesoF]=React.useState('')
  const [savedF,setSavedF]=React.useState(false)
  const [humorF,setHumorF]=React.useState('')
  const [energiaF,setEnergiaF]=React.useState('')
  const [intestinoF,setIntestinoF]=React.useState('')
  const [sintF,setSintF]=React.useState('')
  const [medD,setMedD]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_denise')||'null');return v||[{data:'04/06',pescoco:0,ombro:37,peito:91,cintura:73,bracE:25,bracD:25.5,antebracoE:19.5,antebracoD:19,abdSup:78,abdInf:81,coxaE:48,coxaD:49,panturE:31,panturD:33,quadril:91.5}]}catch{return []}})
  const [medF,setMedF]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_flavio')||'null');return v||[{data:'29/07',pescoco:41,ombro:42,peito:99,cintura:100,bracE:33,bracD:33,antebracoE:28,antebracoD:29,abdSup:96,abdInf:103,coxaE:56,coxaD:55,panturE:42,panturD:42,quadril:108}]}catch{return []}})
  const [novaMedD,setNovaMedD]=React.useState({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})
  const [novaMedF,setNovaMedF]=React.useState({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})
  const [savedMedD,setSavedMedD]=React.useState(false)
  const [savedMedF,setSavedMedF]=React.useState(false)
  const displayList=[...[...OKOK].reverse(),...extras]
  const atual=displayList[0]
  const pesoAtual=atual.peso
  const pesoInicial=OKOK[0].peso
  const perdeu=Math.round((pesoInicial-pesoAtual)*100)/100
  const gordAtual=atual.gordura
  const ultimaMedida=MEDIDAS[MEDIDAS.length-1]
  const pesoAtualF=extrasF[0].peso
  const pesoInicialF=extrasF[extrasF.length-1].peso
  const perdeuF=Math.round((pesoInicialF-pesoAtualF)*100)/100
  function salvar(){
    if(!peso&&!humor&&!intestino)return
    const reg:SReg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),peso:Number(peso)||0,imc:Number((Number(peso)/(1.63**2)).toFixed(1))||0,gordura:0,humor:Number(humor)||0,energia:Number(energia)||0,intestino,sint,sono:Number(sono)||0}
    const n=[reg,...extras];setExtras(n);localStorage.setItem('dos_saude_extra',JSON.stringify(n))
    setSaved(true);setPeso('');setHumor('');setEnergia('');setIntestino('');setSint('');setSono('')
  }
  function salvarFlavio(){
    if(!pesoF)return
    const reg:SReg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),peso:Number(pesoF)||0,imc:0,gordura:0,humor:Number(humorF)||0,energia:Number(energiaF)||0,intestino:intestinoF,sint:sintF}
    const n=[reg,...extrasF];setExtrasF(n);localStorage.setItem('dos_saude_extra_flavio',JSON.stringify(n))
    setSavedF(true);setPesoF('');setHumorF('');setEnergiaF('');setIntestinoF('');setSintF('')
  }
  function addMedD(){
    const has=Object.values(novaMedD).some(v=>v!=='')
    if(!has)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),pescoco:Number(novaMedD.pescoco)||0,ombro:Number(novaMedD.ombro)||0,peito:Number(novaMedD.peito)||0,cintura:Number(novaMedD.cintura)||0,bracE:Number(novaMedD.bracE)||0,bracD:Number(novaMedD.bracD)||0,antebracoE:Number(novaMedD.antebracoE)||0,antebracoD:Number(novaMedD.antebracoD)||0,abdSup:Number(novaMedD.abdSup)||0,abdInf:Number(novaMedD.abdInf)||0,coxaE:Number(novaMedD.coxaE)||0,coxaD:Number(novaMedD.coxaD)||0,panturE:Number(novaMedD.panturE)||0,panturD:Number(novaMedD.panturD)||0,quadril:Number(novaMedD.quadril)||0}
    const n=[reg,...medD];setMedD(n);localStorage.setItem('dos_medidas_denise',JSON.stringify(n))
    setSavedMedD(true);setNovaMedD({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})
  }
  function addMedF(){
    const has=Object.values(novaMedF).some(v=>v!=='')
    if(!has)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),pescoco:Number(novaMedF.pescoco)||0,ombro:Number(novaMedF.ombro)||0,peito:Number(novaMedF.peito)||0,cintura:Number(novaMedF.cintura)||0,bracE:Number(novaMedF.bracE)||0,bracD:Number(novaMedF.bracD)||0,antebracoE:Number(novaMedF.antebracoE)||0,antebracoD:Number(novaMedF.antebracoD)||0,abdSup:Number(novaMedF.abdSup)||0,abdInf:Number(novaMedF.abdInf)||0,coxaE:Number(novaMedF.coxaE)||0,coxaD:Number(novaMedF.coxaD)||0,panturE:Number(novaMedF.panturE)||0,panturD:Number(novaMedF.panturD)||0,quadril:Number(novaMedF.quadril)||0}
    const n=[reg,...medF];setMedF(n);localStorage.setItem('dos_medidas_flavio',JSON.stringify(n))
    setSavedMedF(true);setNovaMedF({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})
  }
  const [medicamentos,setMedicamentos]=React.useState<Record<string,any[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_medicamentos')||'{}')}catch{return {}}})
  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:''})
  const [savedMed,setSavedMed]=React.useState(false)
  function addMedicamento(kid:string){
    if(!novoMed.nome||!novoMed.dosagem)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),nome:novoMed.nome,dosagem:novoMed.dosagem,frequencia:novoMed.frequencia,horarios:novoMed.horarios}
    const n={...medicamentos,[kid]:[reg,...(medicamentos[kid]||[])]}
    setMedicamentos(n);localStorage.setItem('dos_medicamentos',JSON.stringify(n))
    setNovoMed({nome:'',dosagem:'',frequencia:'',horarios:''});setSavedMed(true)
  }
  function delMedicamento(kid:string,idx:number){
    const n={...medicamentos,[kid]:(medicamentos[kid]||[]).filter((_c:any,i:number)=>i!==idx)}
    setMedicamentos(n);localStorage.setItem('dos_medicamentos',JSON.stringify(n))
  }
  function addConsulta(kid:string){
    if(!novaConsulta.tipo||!novaConsulta.data)return
    const n={...consuls,[kid]:[{...novaConsulta},...(consuls[kid]||[])]}
    setConsuls(n);localStorage.setItem('dos_consuls',JSON.stringify(n))
    setNovaConsulta({tipo:'',data:'',obs:'',proximo:''});setSavedC(true)
  }
  function delConsulta(kid:string,idx:number){
    const n={...consuls,[kid]:(consuls[kid]||[]).filter((_c:any,i:number)=>i!==idx)}
    setConsuls(n);localStorage.setItem('dos_consuls',JSON.stringify(n))
  }
  function addCrianca(kid:string){
    if(!novaCrianca.peso&&!novaCrianca.altura)return
    const reg:CriancaReg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),peso:Number(novaCrianca.peso)||0,altura:Number(novaCrianca.altura)||0,obs:novaCrianca.obs}
    const n={...criancas,[kid]:[reg,...(criancas[kid]||[])]}
    setCriancas(n);localStorage.setItem('dos_criancas',JSON.stringify(n))
    setNovaCrianca({peso:'',altura:'',obs:''});setSavedC(true)
  }
  function setTamanho(kid:string,campo:string,valor:string){
    const n={...tamanhos,[kid]:{...(tamanhos[kid]||{}),[campo]:valor}}
    setTamanhos(n);localStorage.setItem('dos_tamanhos',JSON.stringify(n))
  }
  const chartPeso=OKOK
  const minP=Math.min(...chartPeso.map(d=>d.peso))-0.5
  const maxP=Math.max(...chartPeso.map(d=>d.peso))+0.5
  const membros=[
    {id:'denise',nome:'Denise',label:'Você',cor:C.acc2},
    {id:'flavio',nome:'Flávio',label:'Flávio',cor:C.water},
    {id:'domi',nome:'Domi',label:'Domi',cor:C.pink},
    {id:'derick',nome:'Derick',label:'Derick',cor:C.ok},
  ]
  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Saúde da Família</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Acompanhamento individual · registros · consultas</p>
    <div style={{display:'flex',gap:10,marginBottom:20}}>
      {membros.map(m=>(<button key={m.id} onClick={()=>setAba(m.id as typeof aba)} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 16px',borderRadius:12,border:`2px solid ${aba===m.id?m.cor:'rgba(255,255,255,.1)'}`,background:aba===m.id?`rgba(${m.cor==='#a78bfa'?'167,139,250':m.cor==='#38bdf8'?'56,189,248':m.cor==='#f472b6'?'244,114,182':'52,211,153'},.1)`:'transparent',cursor:'pointer',color:'#fff'}}>
        <Avatar id={m.id} label={m.nome[0]} size={32} radius={8}/>
        <span style={{fontWeight:600,fontSize:14}}>{m.nome}</span>
      </button>))}
    </div>

    {aba==='denise'&&<div>
      <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:12,marginBottom:16}}>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:C.ok}}>{pesoAtual} kg</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Peso atual</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:C.ok}}>-{perdeu} kg</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Perdidos</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800}}>{gordAtual}%</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Gordura</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:C.acc2}}>{ultimaMedida.cintura} cm</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Cintura</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:C.acc2}}>{ultimaMedida.quadril} cm</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Quadril</div></div>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'2fr 1fr',gap:16}}>
        <Card title="Evolução do peso — dez/25 a jul/26">
          <div style={{height:140,display:'flex',alignItems:'flex-end',gap:2,marginBottom:8}}>
            {chartPeso.map((d,i)=>{
              const barH=Math.max(Math.round(((d.peso-minP)/(maxP-minP))*135),3)
              const isMin=d.peso===Math.min(...chartPeso.map(x=>x.peso))
              const isMax=d.peso===Math.max(...chartPeso.map(x=>x.peso))
              return(<div key={i} title={`${d.data}: ${d.peso}kg`} style={{flex:1,borderRadius:'2px 2px 1px 1px',background:isMin?`linear-gradient(180deg,${C.ok},#15803d)`:isMax?`linear-gradient(180deg,${C.danger},#991b1b)`:`linear-gradient(180deg,${C.acc2},#6d28d9)`,height:barH,alignSelf:'flex-end'}}/>)
            })}
          </div>
          <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)'}}>
            <span>dez/25: 75,7kg</span><span>🟢 mín: 60,55kg</span><span>atual: {pesoAtual}kg</span>
          </div>
          <div style={{height:60,display:'flex',alignItems:'flex-end',gap:2,marginTop:12}}>
            {OKOK.map((d,i)=>{if(!d.gordura)return null;const mn=31.3,mx=39.1,h=Math.max(Math.round(((d.gordura-mn)/(mx-mn))*55),3);return(<div key={i} title={`${d.data}: ${d.gordura}%`} style={{flex:1,borderRadius:'2px 2px 1px 1px',background:`linear-gradient(180deg,${C.pink},#9d174d)`,height:h,alignSelf:'flex-end'}}/>)})}
          </div>
          <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}><span>Gordura: 39,1%</span><span>mín: 31,3%</span><span>atual: 33,4%</span></div>
        </Card>
        <Card title="Registrar hoje">
          {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Salvo!</div>}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Peso (kg)</label><input type="number" step="0.1" value={peso} onChange={e=>setPeso(e.target.value)} placeholder="63,5" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Humor (1–10)</label><input type="number" min="1" max="10" value={humor} onChange={e=>setHumor(e.target.value)} placeholder="8" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Energia (1–10)</label><input type="number" min="1" max="10" value={energia} onChange={e=>setEnergia(e.target.value)} placeholder="7" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Intestino</label><select value={intestino} onChange={e=>setIntestino(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}><option value="">—</option><option>Regular</option><option>Preso</option><option>Solto</option></select></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Sono (horas)</label><input type="number" step="0.5" min="0" max="24" value={sono} onChange={e=>setSono(e.target.value)} placeholder="7" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
          </div>
          <input value={sint} onChange={e=>setSint(e.target.value)} placeholder="Sintomas" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
          <button onClick={salvar} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>✓ Salvar</button>
          <div style={{marginTop:14,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
            <div style={{fontSize:12,fontWeight:700,marginBottom:8}}>Medidas (29/07)</div>
            {[['Cintura','73 cm'],['Quadril','91,5 cm'],['Peito','91 cm'],['Coxa E/D','48/49 cm'],['Abd Sup/Inf','78/81 cm']].map(([k,v])=>(<div key={k} style={{display:'flex',justifyContent:'space-between' as const,fontSize:12,padding:'4px 0',borderBottom:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)'}}><span>{k}</span><span style={{color:C.acc2}}>{v}</span></div>))}
          </div>
        </Card>
      </div>
      <Card title="Medidas completas - Denise (04/06/2026)">
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:10}}>
          {[['Ombro','37'],['Peito','91'],['Cintura','73'],['Braco E/D','25/25,5'],['Antebraco E/D','19,5/19'],['Abd Superior','78'],['Abd Inferior','81'],['Coxa E/D','48/49'],['Panturrilha E/D','31/33'],['Quadril','91,5']].map(([k,v])=>(<div key={k} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px',textAlign:'center' as const}}><div style={{fontSize:16,fontWeight:800,color:C.acc2}}>{v} cm</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:2}}>{k}</div></div>))}
        </div>
        <p style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:12}}>Registros do app da balanca SecaVita.</p>
      </Card>
      <Card title="Registrar novas medidas - Denise">
        {savedMedD&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>Salvo!</div>}
        <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:8,marginBottom:10}}>
          {[['pescoco','Pescoco'],['ombro','Ombro'],['peito','Peito'],['cintura','Cintura'],['bracE','Braco E'],['bracD','Braco D'],['antebracoE','Antebraco E'],['antebracoD','Antebraco D'],['abdSup','Abd Sup'],['abdInf','Abd Inf'],['coxaE','Coxa E'],['coxaD','Coxa D'],['panturE','Panturr E'],['panturD','Panturr D'],['quadril','Quadril']].map(([f,l])=>(<div key={f}><label style={{fontSize:10,color:'rgba(255,255,255,.4)',display:'block',marginBottom:3}}>{l}</label><input type="number" step="0.5" value={(novaMedD as any)[f]} onChange={e=>setNovaMedD(p=>({...p,[f]:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'6px 7px',color:'#fff',fontSize:11}}/></div>))}
        </div>
        <button onClick={addMedD} style={{width:'100%',background:`linear-gradient(135deg,${C.acc2},#0369a1)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Salvar medidas</button>
      </Card>
      <Card title="Evolucao da cintura - Denise">
        <div style={{height:100,display:'flex',alignItems:'flex-end',gap:2,marginBottom:8}}>
          {[...medD].reverse().map((d,i)=>{
            const vals=medD.map(x=>x.cintura)
            const mn=Math.min(...vals)-1,mx=Math.max(...vals)+1
            const barH=Math.max(Math.round(((d.cintura-mn)/(mx-mn))*95),3)
            return(<div key={i} title={`${d.data}: ${d.cintura}cm`} style={{width:24,flexShrink:0,borderRadius:'2px 2px 1px 1px',background:`linear-gradient(180deg,${C.acc2},#0369a1)`,height:barH,alignSelf:'flex-end'}}/>)
          })}
        </div>
        <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)'}}>
          <span>{medD[medD.length-1].data}: {medD[medD.length-1].cintura}cm</span><span>atual: {medD[0].cintura}cm</span>
        </div>
      </Card>
    </div>}

    {aba==='flavio'&&<div>
      <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:12,marginBottom:16}}>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:C.water}}>{pesoAtualF} kg</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Peso atual</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:perdeuF>=0?C.ok:C.danger}}>{perdeuF>=0?'-':'+'}{Math.abs(perdeuF)} kg</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Variacao</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:C.acc2}}>100 cm</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Cintura</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800,color:C.acc2}}>108 cm</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Quadril</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800}}>99 cm</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>Peito</div></div>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'2fr 1fr',gap:16}}>
        <Card title="Evolucao do peso - Flavio">
          <div style={{height:140,display:'flex',alignItems:'flex-end',gap:2,marginBottom:8}}>
            {[...extrasF].reverse().map((d,i)=>{
              const vals=extrasF.map(x=>x.peso)
              const mn=Math.min(...vals)-0.5,mx=Math.max(...vals)+0.5
              const barH=Math.max(Math.round(((d.peso-mn)/(mx-mn))*135),3)
              const isMin=d.peso===Math.min(...vals)
              const isMax=d.peso===Math.max(...vals)
              return(<div key={i} title={`${d.data}: ${d.peso}kg`} style={{width:28,flexShrink:0,borderRadius:'2px 2px 1px 1px',background:isMin?`linear-gradient(180deg,${C.ok},#15803d)`:isMax?`linear-gradient(180deg,${C.danger},#991b1b)`:`linear-gradient(180deg,${C.water},#0369a1)`,height:barH,alignSelf:'flex-end'}}/>)
            })}
          </div>
          <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)'}}>
            <span>{extrasF[extrasF.length-1].data}: {pesoInicialF}kg</span><span>atual: {pesoAtualF}kg</span>
          </div>
        </Card>
        <Card title="Registrar hoje - Flavio">
          {savedF&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>Salvo!</div>}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Peso (kg)</label><input type="number" step="0.1" value={pesoF} onChange={e=>setPesoF(e.target.value)} placeholder="95,2" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Humor (1-10)</label><input type="number" min="1" max="10" value={humorF} onChange={e=>setHumorF(e.target.value)} placeholder="8" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Energia (1-10)</label><input type="number" min="1" max="10" value={energiaF} onChange={e=>setEnergiaF(e.target.value)} placeholder="7" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Intestino</label><select value={intestinoF} onChange={e=>setIntestinoF(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}><option value="">-</option><option>Regular</option><option>Preso</option><option>Solto</option></select></div>
          </div>
          <input value={sintF} onChange={e=>setSintF(e.target.value)} placeholder="Sintomas" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
          <button onClick={salvarFlavio} style={{width:'100%',background:`linear-gradient(135deg,${C.water},#0369a1)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Salvar</button>
          <div style={{marginTop:14,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
            <div style={{fontSize:12,fontWeight:700,marginBottom:8}}>Medidas (29/07)</div>
            {[['Cintura','100 cm'],['Quadril','108 cm'],['Peito','99 cm'],['Coxa E/D','56/55 cm'],['Abd Sup/Inf','96/103 cm']].map(([k,v])=>(<div key={k} style={{display:'flex',justifyContent:'space-between' as const,fontSize:12,padding:'4px 0',borderBottom:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)'}}><span>{k}</span><span style={{color:C.acc2}}>{v}</span></div>))}
          </div>
        </Card>
      </div>
      <Card title="Medidas iniciais completas - Flavio Dantas (29/07/2026)">
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:10}}>
          {[['Pescoco','41'],['Ombro','42'],['Peito','99'],['Cintura','100'],['Braco E/D','33/33'],['Antebraco E/D','28/29'],['Abd Superior','96'],['Abd Inferior','103'],['Coxa E/D','56/55'],['Panturrilha','42/42'],['Quadril','108']].map(([k,v])=>(<div key={k} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px',textAlign:'center' as const}}><div style={{fontSize:16,fontWeight:800,color:C.water}}>{v} cm</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:2}}>{k}</div></div>))}
        </div>
        <p style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:12}}>Registros iniciais SecaVita.</p>
      </Card>
      <Card title="Registrar novas medidas - Flavio">
        {savedMedF&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>Salvo!</div>}
        <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:8,marginBottom:10}}>
          {[['pescoco','Pescoco'],['ombro','Ombro'],['peito','Peito'],['cintura','Cintura'],['bracE','Braco E'],['bracD','Braco D'],['antebracoE','Antebraco E'],['antebracoD','Antebraco D'],['abdSup','Abd Sup'],['abdInf','Abd Inf'],['coxaE','Coxa E'],['coxaD','Coxa D'],['panturE','Panturr E'],['panturD','Panturr D'],['quadril','Quadril']].map(([f,l])=>(<div key={f}><label style={{fontSize:10,color:'rgba(255,255,255,.4)',display:'block',marginBottom:3}}>{l}</label><input type="number" step="0.5" value={(novaMedF as any)[f]} onChange={e=>setNovaMedF(p=>({...p,[f]:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'6px 7px',color:'#fff',fontSize:11}}/></div>))}
        </div>
        <button onClick={addMedF} style={{width:'100%',background:`linear-gradient(135deg,${C.water},#0369a1)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Salvar medidas</button>
      </Card>
      <Card title="Evolucao da cintura - Flavio">
        <div style={{height:100,display:'flex',alignItems:'flex-end',gap:2,marginBottom:8}}>
          {[...medF].reverse().map((d,i)=>{
            const vals=medF.map(x=>x.cintura)
            const mn=Math.min(...vals)-1,mx=Math.max(...vals)+1
            const barH=Math.max(Math.round(((d.cintura-mn)/(mx-mn))*95),3)
            return(<div key={i} title={`${d.data}: ${d.cintura}cm`} style={{width:24,flexShrink:0,borderRadius:'2px 2px 1px 1px',background:`linear-gradient(180deg,${C.water},#0369a1)`,height:barH,alignSelf:'flex-end'}}/>)
          })}
        </div>
        <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)'}}>
          <span>{medF[medF.length-1].data}: {medF[medF.length-1].cintura}cm</span><span>atual: {medF[0].cintura}cm</span>
        </div>
      </Card>
    </div>}

    {(aba==='domi'||aba==='derick')&&<div>
      {(()=>{
        const kid=aba
        const nome=kid==='domi'?'Domi':'Derick'
        const cor=kid==='domi'?C.pink:C.ok
          const kidConsuls=consuls[kid]||[]
        const kidCrianca=criancas[kid]||[]
        return(<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
          <div>
            <Card title={`Crescimento — ${nome}`}>
              {savedC&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Salvo!</div>}
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Peso (kg)</label><input type="number" step="0.1" value={novaCrianca.peso} onChange={e=>setNovaCrianca(p=>({...p,peso:e.target.value}))} placeholder="35" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Altura (cm)</label><input type="number" step="0.5" value={novaCrianca.altura} onChange={e=>setNovaCrianca(p=>({...p,altura:e.target.value}))} placeholder="140" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
              </div>
              <input value={novaCrianca.obs} onChange={e=>setNovaCrianca(p=>({...p,obs:e.target.value}))} placeholder="Observações" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
              <button onClick={()=>addCrianca(kid)} style={{width:'100%',background:`linear-gradient(135deg,${cor},${kid==='domi'?'#9d174d':'#15803d'})`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar medida</button>
              {kidCrianca.length>0&&<div style={{marginTop:12}}>
                <div style={{display:'flex',gap:6,fontSize:11,color:'rgba(255,255,255,.4)',borderBottom:`1px solid ${C.line}`,paddingBottom:6,marginBottom:4}}><span style={{width:40}}>Data</span><span style={{width:50}}>Peso</span><span>Altura</span></div>
                {kidCrianca.map((r,i)=>(<div key={i} style={{display:'flex',gap:6,padding:'6px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,color:'rgba(255,255,255,.6)'}}><span style={{width:40}}>{r.data}</span><span style={{width:50,color:cor}}>{r.peso}kg</span><span>{r.altura?`${r.altura}cm`:'—'}</span></div>))}
              </div>}
              <div style={{marginTop:16,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
                <div style={{fontSize:12,fontWeight:700,marginBottom:8,color:'rgba(255,255,255,.6)'}}>Tamanhos (atualizar quando mudar)</div>
                <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
                  {[['roupa','Roupa'],['calcado','Calçado'],['camiseta','Camiseta'],['calca','Calça']].map(([campo,label])=>(<div key={campo}><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:3}}>{label}</label><input value={(tamanhos[kid]||{})[campo]||''} onChange={e=>setTamanho(kid,campo,e.target.value)} placeholder="Ex: 12 anos / 34" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'8px 10px',color:'#fff',fontSize:12}}/></div>))}
                </div>
              </div>
            </Card>
          </div>
          <div>
            <Card title={`Consultas — ${nome}`}>
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Tipo</label>
                <select value={novaConsulta.tipo} onChange={e=>setNovaConsulta(p=>({...p,tipo:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}>
                  <option value="">Selecionar</option><option>Pediatria</option><option>Dentista</option><option>Vacina</option><option>Oftalmologia</option><option>Ortopedia</option><option>Outro</option>
                </select></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novaConsulta.data} onChange={e=>setNovaConsulta(p=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
              </div>
              <input value={novaConsulta.obs} onChange={e=>setNovaConsulta(p=>({...p,obs:e.target.value}))} placeholder="Observações / diagnóstico" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:8}}/>
              <input value={novaConsulta.proximo} onChange={e=>setNovaConsulta(p=>({...p,proximo:e.target.value}))} placeholder="Próxima consulta" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
              <button onClick={()=>addConsulta(kid)} style={{width:'100%',background:`linear-gradient(135deg,${cor},${kid==='domi'?'#9d174d':'#15803d'})`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar consulta</button>
              {kidConsuls.length>0&&<div style={{marginTop:12}}>
                {kidConsuls.map((c,i)=>(<div key={i} style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                  <div style={{display:'flex',justifyContent:'space-between' as const,marginBottom:3}}><span style={{fontWeight:700,fontSize:13,color:cor}}>{c.tipo}</span><span style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'flex',alignItems:'center',gap:8}}>{c.data}<button onClick={()=>delConsulta(kid,i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></span></div>
                  {c.obs&&<div style={{fontSize:12,color:'rgba(255,255,255,.6)'}}>{c.obs}</div>}
                  {c.proximo&&<div style={{fontSize:11,color:C.warn,marginTop:3}}>📅 Próxima: {c.proximo}</div>}
                </div>))}
              </div>}
              {kidConsuls.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma consulta registrada.</div>}
            </Card>
          </div>
          <div style={{gridColumn:'1 / -1'}}>
            <Card title={`Medicamentos - ${nome}`}>
              {savedMed&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>Salvo!</div>}
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr 1fr',gap:8,marginBottom:10}}>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Medicamento</label><input value={novoMed.nome} onChange={e=>setNovoMed(p=>({...p,nome:e.target.value}))} placeholder="Ex: Amoxicilina" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Dosagem</label><input value={novoMed.dosagem} onChange={e=>setNovoMed(p=>({...p,dosagem:e.target.value}))} placeholder="Ex: 5ml" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Frequencia</label><input value={novoMed.frequencia} onChange={e=>setNovoMed(p=>({...p,frequencia:e.target.value}))} placeholder="Ex: 2x ao dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Horarios</label><input value={novoMed.horarios} onChange={e=>setNovoMed(p=>({...p,horarios:e.target.value}))} placeholder="Ex: 08:00, 20:00" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
              </div>
              <p style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginBottom:10}}>Preenchendo os horarios, o medicamento aparece todo dia na Agenda automaticamente.</p>
              <button onClick={()=>addMedicamento(kid)} style={{width:'100%',background:`linear-gradient(135deg,${cor},${kid==='domi'?'#9d174d':'#15803d'})`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar medicamento</button>
              {(medicamentos[kid]||[]).length>0&&<div style={{marginTop:12}}>
                {(medicamentos[kid]||[]).map((m:any,i:number)=>(<div key={i} style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
                  <div><span style={{fontWeight:700,fontSize:13,color:cor}}>{m.nome}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)',marginLeft:8}}>{m.dosagem}{m.frequencia?` - ${m.frequencia}`:''}{m.horarios?` - ${m.horarios}`:''}</span></div>
                  <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{m.data}</span><button onClick={()=>delMedicamento(kid,i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></div>
                </div>))}
              </div>}
              {(medicamentos[kid]||[]).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum medicamento registrado.</div>}
            </Card>
          </div>
        </div>)
      })()}
    </div>}
  </div>)}

function Alimentacao(){
  type Ref={nome:string,prot:number,hora:string}
  const [wat,setWat]=React.useState(()=>Number(localStorage.getItem('dos_wat')||0))
  const [prot,setProt]=React.useState(()=>Number(localStorage.getItem('dos_prot')||0))
  const [refs,setRefs]=React.useState<Ref[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_refs')||'[]')}catch{return []}})
  const [nomef,setNomef]=React.useState('')
  const [protf,setProtf]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const metaP=120,metaW=2500
  const addW=(ml:number)=>{const n=Math.min(wat+ml,6000);setWat(n);localStorage.setItem('dos_wat',String(n))}
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
        <div style={{fontSize:22,fontWeight:800,color:C.water}}>{(wat/1000).toFixed(1).replace('.',',')} / 2,5 L</div>
        <div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2,marginBottom:8}}>Água hoje</div>
        <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${pctW}%`,borderRadius:4,background:C.water,transition:'width .3s'}}/></div>
        <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}>{pctW}% da meta</div>
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
        {refs.length>0&&<button onClick={()=>{if(window.confirm('Limpar histórico de hoje?')){setRefs([]);setWat(0);setProt(0);localStorage.removeItem('dos_refs');localStorage.removeItem('dos_wat');localStorage.removeItem('dos_prot')}}} style={{width:'100%',background:'rgba(248,113,113,.1)',border:'1px solid rgba(248,113,113,.2)',color:C.danger,borderRadius:10,padding:'9px',fontSize:12,cursor:'pointer',marginTop:12}}>Limpar dia</button>}
      </Card>
    </div>
  </div>)}

function Exercicios(){
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
    const reg={data:new Date().toISOString().slice(0,10),tipo,duracaoMin:Math.max(1,Math.round(dur/60))}
    const n=[reg,...treinos]
    setTreinos(n);localStorage.setItem('dos_treinos',JSON.stringify(n))
    setSaved(true)
  }
  function segundaDaSemana(d:Date){const x=new Date(d);const day=x.getDay();const diff=(day===0?-6:1-day);x.setDate(x.getDate()+diff);return x}
  const seg=segundaDaSemana(new Date())
  const diasComTreino=new Set(treinos.map((t:any)=>t.data))
  const plano=PLANO_SEMANA.map(([d,t],i)=>{const dt=new Date(seg);dt.setDate(seg.getDate()+i);const iso=dt.toISOString().slice(0,10);return [d,t,diasComTreino.has(iso)] as [string,string,boolean]})
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
}
function TirzepatidaPage(){
  const [loading,setLoading]=React.useState(true)
  const [schedules,setSchedules]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [balance,setBalance]=React.useState(0)
  const [applications,setApplications]=React.useState<any[]>([])
  const [person,setPerson]=React.useState<'denise'|'flavio'>('denise')
  const [dose,setDose]=React.useState('5')
  const [date,setDate]=React.useState(new Date().toISOString().slice(0,10))
  const [msg,setMsg]=React.useState('')
  const [filtro,setFiltro]=React.useState<'todos'|'denise'|'flavio'>('todos')
  const [seeding,setSeeding]=React.useState(false)

  function fmtIso(iso:string|null|undefined){if(!iso)return '—';return new Date(iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}
  function addDaysIso(iso:string,n:number){const d=new Date(iso);d.setDate(d.getDate()+n);return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}

  async function load(){
    setLoading(true)
    const [{data:sched},{data:bal},{data:apps}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
      supabase.from('tirzepatida_applications').select('*').order('applied_at',{ascending:false}),
    ])
    const map:Record<string,any>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={planned_dose_mg:Number(row.planned_dose_mg),interval_days:row.interval_days,next_application_date:row.next_application_date}})
    setSchedules(map)
    setBalance(Number(bal?.current_balance_mg??0))
    setApplications(apps||[])
    setLoading(false)
  }

  React.useEffect(()=>{load()},[])

  async function seed(){
    setSeeding(true);setMsg('')
    try{
      const {data:existing}=await supabase.from('tirzepatida_schedule').select('person')
      if(existing&&existing.length>0){setMsg('Dados já inicializados.');setSeeding(false);return}

      const {error:e1}=await supabase.from('tirzepatida_schedule').insert([
        {person:'denise',planned_dose_mg:5,interval_days:5},
        {person:'flavio',planned_dose_mg:2.5,interval_days:7},
      ])
      if(e1) throw e1

      const hist=[
        {person:'denise',applied_at:'2026-06-30T08:00:00',dose_mg:7.5},
        {person:'denise',applied_at:'2026-07-05T08:00:00',dose_mg:7.5},
        {person:'denise',applied_at:'2026-07-08T08:00:00',dose_mg:7.5},
        {person:'denise',applied_at:'2026-07-13T08:00:00',dose_mg:7.5},
        {person:'denise',applied_at:'2026-07-18T08:00:00',dose_mg:10},
      ]
      const {error:e2}=await supabase.from('tirzepatida_applications').insert(hist.map(h=>({...h,counted_in_stock:false})))
      if(e2) throw e2

      const {error:e3}=await supabase.rpc('tirze_register_movement',{p_type:'entrada',p_amount_mg:120,p_notes:'Saldo inicial oficial'})
      if(e3) throw e3

      setMsg('✓ Dados inicializados: estoque 120 mg, histórico importado.')
      await load()
    }catch(e:any){
      setMsg('❌ Erro ao inicializar: '+(e?.message||String(e)))
    }
    setSeeding(false)
  }

  async function register(){
    const d=parseFloat(dose.replace(',','.'))
    if(!d||d<=0){setMsg('❌ Dose inválida.');return}
    if(d>balance){setMsg('❌ Estoque insuficiente.');return}
    try{
      const appliedAt=new Date(date+'T'+new Date().toTimeString().slice(0,8)).toISOString()
      const {error}=await supabase.rpc('tirze_apply_dose',{p_person:person,p_applied_at:appliedAt,p_dose_mg:d})
      if(error) throw error
      setMsg('✓ Aplicação registrada.')
      await load()
    }catch(e:any){
      setMsg('❌ '+(e?.message||String(e)))
    }
  }

  async function excluir(app:any){
    if(app.counted_in_stock){
      await supabase.rpc('tirze_register_movement',{p_type:'correcao',p_amount_mg:Number(app.dose_mg),p_person:app.person,p_notes:'Estorno de exclusão de aplicação'})
    }
    await supabase.from('tirzepatida_applications').delete().eq('id',app.id)
    setMsg('Registro excluído (com estorno de estoque, se aplicável).')
    await load()
  }

  const autonomy=(()=>{
    const dDen=schedules.denise?.planned_dose_mg||5
    const dFla=schedules.flavio?.planned_dose_mg||2.5
    const iDen=schedules.denise?.interval_days||5
    const iFla=schedules.flavio?.interval_days||7
    const mgDay=dDen/iDen+dFla/iFla
    return mgDay>0?Math.floor(balance/mgDay):0
  })()

  const hf=filtro==='todos'?applications:applications.filter(a=>a.person===filtro)
  const notInitialized=Object.keys(schedules).length===0

  if(loading) return <div style={{padding:'24px 28px',color:'rgba(255,255,255,.5)'}}>Carregando…</div>

  return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Tirzepatida <span style={{fontSize:12,background:'rgba(139,92,246,.15)',color:C.acc2,padding:'3px 9px',borderRadius:20}}>estoque compartilhado</span></h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Acompanhamento pessoal — não substitui orientação médica.</p>
  {notInitialized?(<div style={{background:'rgba(139,92,246,.1)',border:'1px solid rgba(139,92,246,.3)',borderRadius:14,padding:20,marginBottom:20}}><p style={{margin:'0 0 10px',fontSize:14}}>Nenhum dado cadastrado ainda para Denise e Flávio.</p>{msg&&<div style={{fontSize:12.5,color:msg.startsWith('✓')?C.ok:C.danger,marginBottom:10}}>{msg}</div>}<button onClick={seed} disabled={seeding} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 18px',fontSize:14,fontWeight:700,cursor:'pointer'}}>{seeding?'Inicializando…':'Inicializar dados'}</button></div>):(<>
  <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:12,marginBottom:20}}>{[['Estoque',`${balance} mg`],['Autonomia',`~${autonomy} dias`],['Sua próxima',`${fmtIso(schedules.denise?.next_application_date)} · ${schedules.denise?.planned_dose_mg??5}mg`],['Flávio',`${fmtIso(schedules.flavio?.next_application_date)} · ${schedules.flavio?.planned_dose_mg??2.5}mg`]].map(([l,v])=>(<div key={l} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:20,fontWeight:800}}>{v}</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:2}}>{l}</div></div>))}</div>
  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
    <Card title="Registrar aplicação">
      <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Pessoa</label>
      <select value={person} onChange={e=>{const p=e.target.value as 'denise'|'flavio';setPerson(p);setDose(String(schedules[p]?.planned_dose_mg??(p==='denise'?5:2.5)))}} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12,colorScheme:'dark' as const}}>
        <option value="denise">Você — {schedules.denise?.planned_dose_mg??5} mg / a cada {schedules.denise?.interval_days??5} dias</option>
        <option value="flavio">Flávio — {schedules.flavio?.planned_dose_mg??2.5} mg / a cada {schedules.flavio?.interval_days??7} dias</option>
      </select>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
        <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Data</label><input type="date" value={date} onChange={e=>setDate(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
        <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Dose (mg)</label><input type="number" step="0.5" value={dose} onChange={e=>setDose(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
      </div>
      {msg&&<div style={{background:msg.startsWith('✓')?'rgba(52,211,153,.1)':'rgba(248,113,113,.1)',border:`1px solid ${msg.startsWith('✓')?'rgba(52,211,153,.3)':'rgba(248,113,113,.3)'}`,borderRadius:10,padding:'10px 12px',fontSize:13,color:msg.startsWith('✓')?C.ok:C.danger,marginBottom:12}}>{msg}</div>}
      <button onClick={register} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>Registrar aplicação</button>
    </Card>
    <Card title="Histórico">
      <div style={{display:'flex',gap:8,marginBottom:12}}>{[['todos','Todos'],['denise','Você'],['flavio','Flávio']].map(([v,l])=>(<button key={v} onClick={()=>setFiltro(v as any)} style={{padding:'6px 14px',borderRadius:20,border:'none',background:filtro===v?C.acc:C.s2,color:filtro===v?'#fff':'rgba(255,255,255,.6)',fontSize:12,fontWeight:600,cursor:'pointer'}}>{l}</button>))}</div>
      {hf.map(a=>(<div key={a.id} style={{display:'flex',gap:8,padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,color:'rgba(255,255,255,.6)',alignItems:'center'}}>
        <span style={{width:38}}>{fmtIso(a.applied_at?.slice(0,10))}</span>
        <span style={{width:60}}>{a.person==='denise'?'Você':'Flávio'}</span>
        <span style={{width:52}}>{Number(a.dose_mg)} mg</span>
        <span style={{flex:1}}>{a.counted_in_stock?addDaysIso(a.applied_at.slice(0,10),schedules[a.person]?.interval_days||(a.person==='denise'?5:7)):'histórico'}</span>
        <span style={{background:a.counted_in_stock?'rgba(52,211,153,.15)':C.s3,color:a.counted_in_stock?C.ok:'rgba(255,255,255,.4)',padding:'2px 7px',borderRadius:20,fontSize:11}}>{a.counted_in_stock?'✓':'histórico'}</span>
        {a.counted_in_stock&&<button onClick={()=>excluir(a)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'3px 8px',fontSize:11,cursor:'pointer'}}>✕</button>}
      </div>))}
    </Card>
  </div>
  </>)}
  </div>)
}
function Familia(){
  const {fam,setFam}=React.useContext(FamCtx)
  const [showEdit,setShowEdit]=React.useState(false)
  const [editKey,setEditKey]=React.useState<'domi'|'derick'|null>(null)
  const [local,setLocal]=React.useState(JSON.parse(JSON.stringify(fam)))
  const days:[number,string][]=[[1,'Seg'],[2,'Ter'],[3,'Qua'],[4,'Qui'],[5,'Sex']]
  const membros=[{id:'denise',nome:'Denise',papel:'Você · mãe',cor:'#8b5cf6'},{id:'flavio',nome:'Flávio',papel:'Pai',cor:'#38bdf8'},{id:'domi',nome:'Domi',papel:'Filha · escola',cor:'#f472b6'},{id:'derick',nome:'Derick',papel:'Filho · escola',cor:'#34d399'}]
  type Aval={data:string,tipo:string,obs:string,feito:boolean}
  const [avals,setAvals]=React.useState<Record<string,Aval[]>>(()=>{
    try{
      const stored=JSON.parse(localStorage.getItem('dos_avals')||'{}')
      if(!stored.domi||stored.domi.length===0){
        stored.domi=[
          {data:'11/08',tipo:'📝 Prod. Textual AV1',obs:'Poema de Cordel · peso 10',feito:false},
          {data:'12/08',tipo:'🔬 Ciências AV1',obs:'Mapa mental Sistema Urinário · peso 10',feito:false},
          {data:'14/08',tipo:'🔢 Matemática AV1',obs:'Números decimais · peso 10',feito:false},
          {data:'17/08',tipo:'📖 Português AV1',obs:'Caps 8 e 9 · peso 10',feito:false},
          {data:'17/08',tipo:'🎵 Música AV1',obs:'Parâmetros sonoros · págs 57-60 · peso 10',feito:false},
          {data:'17/08',tipo:'⚽ Ed. Física AV1',obs:'Importância da Atividade Física · peso 10',feito:false},
          {data:'18/08',tipo:'🇬🇧 Inglês AV1',obs:'Routine págs 44-48 · peso 10',feito:false},
          {data:'18/08',tipo:'🎨 Arte AV1',obs:'Colagem figuras geométricas · peso 10',feito:false},
          {data:'19/08',tipo:'📜 História AV1',obs:'Símbolos nacionais · Agência Publicidade · peso 10',feito:false},
          {data:'01/09',tipo:'🔢 Matemática AV3',obs:'Números decimais · lista exercícios · peso 10',feito:false},
          {data:'02/09',tipo:'📖 Português AV3',obs:'Notícia do dia que nasceu · apresentação · peso 10',feito:false},
          {data:'11/09',tipo:'📝 Prod. Textual AV2',obs:'Nossa Turma em Cordel · poema · peso 10',feito:false},
          {data:'14/09',tipo:'📜 História AV2',obs:'Caps 8 e 9 · apostila págs 78-92 · peso 10',feito:false},
          {data:'16/09',tipo:'🔬 Ciências AV2',obs:'Sistema Urinário + Nervoso · págs 129-148 · peso 10',feito:false},
          {data:'17/09',tipo:'📖 Português AV2',obs:'Cordel, rimas, parônimas, conjunções · peso 10',feito:false},
          {data:'18/09',tipo:'🌍 Geografia AV2',obs:'Indústria e Trabalho · caps 8 e 9 · peso 10',feito:false},
          {data:'21/09',tipo:'🔄 Recuperação Prod. Textual',obs:'',feito:false},
          {data:'22/09',tipo:'🔄 Recuperação Português',obs:'',feito:false},
          {data:'28/09',tipo:'🔄 Recuperação Matemática',obs:'',feito:false},
          {data:'29/09',tipo:'🔄 Recuperação Ciências',obs:'',feito:false},
          {data:'30/09',tipo:'🔄 Recuperação História/Geografia',obs:'',feito:false},
        ]
      }
      return stored
    }catch{return {domi:[],derick:[]}}
  })
  const [abaKid,setAbaKid]=React.useState<'domi'|'derick'>('domi')
  const [novaAval,setNovaAval]=React.useState<Aval>({data:'',tipo:'',obs:'',feito:false})
  const [loading,setLoading]=React.useState(false)
  const [msg,setMsg]=React.useState('')
  const pdfRef=React.useRef<HTMLInputElement>(null)
  function saveAvals(kid:string, list:Aval[]){
    const n={...avals,[kid]:list}
    setAvals(n);localStorage.setItem('dos_avals',JSON.stringify(n))
  }
  function addAval(kid:string){
    if(!novaAval.data||!novaAval.tipo)return
    saveAvals(kid,[...(avals[kid]||[]),{...novaAval}].sort((a,b)=>a.data.localeCompare(b.data)))
    setNovaAval({data:'',tipo:'',obs:'',feito:false})
    setMsg('✓ Avaliação adicionada!')
    setTimeout(()=>setMsg(''),3000)
  }
  function delAval(kid:string,i:number){saveAvals(kid,(avals[kid]||[]).filter((_,j)=>j!==i))}
  function toggleAval(kid:string,i:number){
    const list=[...(avals[kid]||[])]
    list[i]={...list[i],feito:!list[i].feito}
    saveAvals(kid,list)
  }
  async function uploadPDF(kid:string, file:File){
    setLoading(true);setMsg('Lendo calendário com IA...')
    try{
      const base64=await new Promise<string>((res,rej)=>{
        const r=new FileReader();r.onload=()=>res((r.result as string).split(',')[1]);r.onerror=rej;r.readAsDataURL(file)
      })
      const resp=await fetch('https://api.anthropic.com/v1/messages',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          model:'claude-sonnet-4-6',
          max_tokens:2000,
          messages:[{role:'user',content:[
            {type:'document',source:{type:'base64',media_type:'application/pdf',data:base64}},
            {type:'text',text:'Extraia todas as avaliações, provas e trabalhos deste calendário escolar. Retorne APENAS um JSON array com objetos: {"data":"DD/MM","tipo":"emoji + nome da matéria + tipo (AV1/AV2/etc)","obs":"conteúdo resumido","feito":false}. Ordene por data. Sem texto extra, sem markdown, apenas o JSON array.'}
          ]}]
        })
      })
      const data=await resp.json()
      const text=data.content[0].text.replace(/```json|```/g,'').trim()
      const extracted:Aval[]=JSON.parse(text)
      saveAvals(kid,[...(avals[kid]||[]),...extracted].sort((a,b)=>a.data.localeCompare(b.data)))
      setMsg(`✓ ${extracted.length} avaliações importadas!`)
    }catch(e){setMsg('❌ Erro ao ler PDF. Tente novamente.')}
    setLoading(false);setTimeout(()=>setMsg(''),5000)
  }
  function openEdit(key:'domi'|'derick'){setLocal(JSON.parse(JSON.stringify(fam)));setEditKey(key);setShowEdit(true)}
  function saveEdit(){if(!editKey)return;setFam(local);setShowEdit(false)}
  const day=new Date().getDay(),sd=(day>=1&&day<=5)?day:1
  return(<div style={{padding:'24px 28px'}}>
    {showEdit&&editKey&&<div onClick={e=>{if(e.target===e.currentTarget)setShowEdit(false)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:480,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Rotina de {editKey==='domi'?'Domi':'Derick'}</h3>
          <button onClick={()=>setShowEdit(false)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:16}}>
            <Avatar id={editKey} label={editKey==='domi'?'D':'De'} size={52} radius={13}/>
            <div><div style={{fontWeight:700,fontSize:15}}>{editKey==='domi'?'Domi':'Derick'}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Toque na foto para alterar</div></div>
          </div>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:5}}>Horário de ida</label>
          <input type="time" value={local[editKey].dropOff} onChange={e=>setLocal((p:typeof fam)=>({...p,[editKey]:{...p[editKey],dropOff:e.target.value}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:15,marginBottom:16,colorScheme:'dark'}}/>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:8}}>Busca por dia</label>
          <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:8}}>
            {days.map(([d,dn])=>(<div key={d}><div style={{fontSize:11,color:'rgba(255,255,255,.6)',textAlign:'center' as const,fontWeight:700,marginBottom:4}}>{dn}</div><input type="time" value={local[editKey].pk[d]||''} onChange={e=>setLocal((p:typeof fam)=>({...p,[editKey]:{...p[editKey],pk:{...p[editKey].pk,[d]:e.target.value}}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 4px',color:'#fff',fontSize:12,textAlign:'center' as const,colorScheme:'dark'}}/></div>))}
          </div>
        </div>
        <div style={{display:'flex',gap:10,padding:'14px 18px',position:'sticky',bottom:0,background:'#1c1c28'}}>
          <button onClick={()=>setShowEdit(false)} style={{flex:1,background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Cancelar</button>
          <button onClick={saveEdit} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>✓ Salvar</button>
        </div>
      </div>
    </div>}
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Família</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Membros · horários · calendário escolar</p>
    <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:14,marginBottom:20}}>
      {membros.map(m=>(<div key={m.id} style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,textAlign:'center' as const}}>
        <div style={{display:'flex',justifyContent:'center' as const,marginBottom:10}}><Avatar id={m.id} label={m.nome[0]} size={64} radius={16}/></div>
        <div style={{fontWeight:700,fontSize:14}}>{m.nome}</div>
        <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:3}}>{m.papel}</div>
        {(m.id==='domi'||m.id==='derick')&&(<button onClick={()=>openEdit(m.id as 'domi'|'derick')} style={{marginTop:10,background:'rgba(139,92,246,.15)',border:'1px solid rgba(139,92,246,.25)',color:C.acc2,borderRadius:8,padding:'6px 12px',fontSize:11,cursor:'pointer',fontWeight:600}}>✏️ Editar rotina</button>)}
      </div>))}
    </div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginBottom:16}}>
      <Card title="Rotina escolar hoje">
        <div style={{fontSize:11,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,marginBottom:12}}>{['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'][new Date().getDay()]} · {new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</div>
        {(['domi','derick'] as const).map(k=>{const nome=k==='domi'?'Domi':'Derick';const cor=k==='domi'?C.pink:C.ok;const pk=fam[k].pk[sd]||'—';return(<div key={k} style={{display:'flex',alignItems:'center',gap:12,padding:'12px 0',borderBottom:`1px solid ${C.line}`}}><Avatar id={k} label={nome[0]} size={40} radius={11}/><div style={{flex:1}}><div style={{fontWeight:700,fontSize:14}}>{nome}</div><div style={{fontSize:12,color:'rgba(255,255,255,.5)',marginTop:2}}>Ida: {fam[k].dropOff} · Busca: {pk}</div></div><div style={{textAlign:'right' as const}}><div style={{fontSize:13,fontWeight:700,color:cor}}>{pk}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>busca</div></div></div>)})}
      </Card>
      <Card title="Semana completa">
        <table style={{width:'100%',borderCollapse:'collapse' as const,fontSize:12}}>
          <thead><tr><th style={{textAlign:'left' as const,fontSize:11,color:'rgba(255,255,255,.4)',padding:'6px 8px',borderBottom:`1px solid ${C.line}`}}>Criança</th>{days.map(([d,dn])=>(<th key={d} style={{textAlign:'center' as const,fontSize:11,color:'rgba(255,255,255,.4)',padding:'6px 4px',borderBottom:`1px solid ${C.line}`,background:sd===d?'rgba(139,92,246,.1)':''}}>{dn}</th>))}</tr></thead>
          <tbody>{(['domi','derick'] as const).map(k=>(<tr key={k}><td style={{padding:'10px 8px',borderBottom:`1px solid ${C.line}`,fontWeight:600,color:'#fff'}}>{k==='domi'?'Domi':'Derick'}</td>{days.map(([d])=>(<td key={d} style={{padding:'10px 4px',borderBottom:`1px solid ${C.line}`,textAlign:'center' as const,color:'rgba(255,255,255,.6)',background:sd===d?'rgba(139,92,246,.07)':''}}>{fam[k].pk[d]||'—'}</td>))}</tr>))}</tbody>
        </table>
      </Card>
    </div>
    <Card title="📚 Calendário Avaliativo Escolar">
      <div style={{display:'flex',gap:8,marginBottom:16}}>
        {(['domi','derick'] as const).map(k=>(<button key={k} onClick={()=>setAbaKid(k)} style={{padding:'8px 18px',borderRadius:20,border:`2px solid ${abaKid===k?(k==='domi'?C.pink:C.ok):'rgba(255,255,255,.1)'}`,background:abaKid===k?`rgba(${k==='domi'?'244,114,182':'52,211,153'},.1)`:'transparent',color:'#fff',cursor:'pointer',fontWeight:600,fontSize:14}}>{k==='domi'?'Domi':'Derick'}</button>))}
      </div>
      {msg&&<div style={{background:msg.startsWith('✓')?'rgba(52,211,153,.1)':'rgba(248,113,113,.1)',border:`1px solid ${msg.startsWith('✓')?'rgba(52,211,153,.3)':'rgba(248,113,113,.3)'}`,borderRadius:10,padding:'10px 14px',fontSize:13,color:msg.startsWith('✓')?C.ok:C.danger,marginBottom:12}}>{msg}</div>}
      <div style={{display:'flex',gap:10,marginBottom:16,flexWrap:'wrap' as const}}>
        <input ref={pdfRef} type="file" accept="application/pdf" style={{display:'none'}} onChange={e=>{const f=e.target.files?.[0];if(f)uploadPDF(abaKid,f);if(pdfRef.current)pdfRef.current.value=''}}/>
        <button onClick={()=>pdfRef.current?.click()} disabled={loading} style={{display:'inline-flex',alignItems:'center',gap:8,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer',opacity:loading?0.6:1}}>
          {loading?'⏳ Lendo PDF...':'📄 Importar PDF do calendário'}
        </button>
        <span style={{fontSize:12,color:'rgba(255,255,255,.4)',alignSelf:'center'}}>ou adicione manualmente →</span>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 2fr auto',gap:8,marginBottom:12,alignItems:'end'}}>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data (DD/MM)</label><input value={novaAval.data} onChange={e=>setNovaAval(p=>({...p,data:e.target.value}))} placeholder="11/08" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Matéria</label><input value={novaAval.tipo} onChange={e=>setNovaAval(p=>({...p,tipo:e.target.value}))} placeholder="📝 Português AV1" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Conteúdo</label><input value={novaAval.obs} onChange={e=>setNovaAval(p=>({...p,obs:e.target.value}))} placeholder="Ex: Poema de Cordel · peso 10" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <button onClick={()=>addAval(abaKid)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>+ Adicionar</button>
      </div>
      <div style={{maxHeight:400,overflowY:'auto' as const}}>
        {(avals[abaKid]||[]).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma avaliação registrada. Importe o PDF ou adicione manualmente.</div>}
        {(avals[abaKid]||[]).map((a,i)=>{
          const diasRestantes=(()=>{
            const parts=a.data.split('/');if(parts.length<2)return null
            const ano=new Date().getFullYear()
            const d=new Date(`${ano}-${parts[1].padStart(2,'0')}-${parts[0].padStart(2,'0')}`)
            const diff=Math.ceil((d.getTime()-Date.now())/(1000*60*60*24))
            return diff
          })()
          const urgente=diasRestantes!==null&&diasRestantes>=0&&diasRestantes<=3
          const passada=diasRestantes!==null&&diasRestantes<0
          return(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 12px',borderRadius:10,marginBottom:4,background:a.feito?'rgba(52,211,153,.05)':urgente?'rgba(248,113,113,.08)':'rgba(255,255,255,.03)',border:a.feito?'1px solid rgba(52,211,153,.15)':urgente?'1px solid rgba(248,113,113,.2)':`1px solid ${C.line}`,opacity:passada&&!a.feito?0.5:1}}>
            <input type="checkbox" checked={a.feito} onChange={()=>toggleAval(abaKid,i)} style={{width:16,height:16,cursor:'pointer',accentColor:C.acc,flexShrink:0}}/>
            <span style={{width:44,fontSize:12,fontWeight:700,color:urgente?C.danger:passada?'rgba(255,255,255,.3)':C.acc2,flexShrink:0}}>{a.data}</span>
            <span style={{fontWeight:600,fontSize:13,color:a.feito?'rgba(255,255,255,.4)':'#fff',textDecoration:a.feito?'line-through':'none',minWidth:160,flexShrink:0}}>{a.tipo}</span>
            <span style={{flex:1,fontSize:12,color:'rgba(255,255,255,.5)'}}>{a.obs}</span>
            {diasRestantes!==null&&!passada&&!a.feito&&<span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:urgente?'rgba(248,113,113,.2)':diasRestantes<=7?'rgba(251,191,36,.15)':'rgba(52,211,153,.1)',color:urgente?C.danger:diasRestantes<=7?C.warn:C.ok,flexShrink:0,whiteSpace:'nowrap' as const}}>{diasRestantes===0?'Hoje!':diasRestantes===1?'Amanhã!':urgente?`${diasRestantes}d ⚠️`:`${diasRestantes}d`}</span>}
            {passada&&!a.feito&&<span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:'rgba(255,255,255,.07)',color:'rgba(255,255,255,.3)',flexShrink:0}}>passada</span>}
            {a.feito&&<span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:'rgba(52,211,153,.15)',color:C.ok,flexShrink:0}}>✓ feita</span>}
            <button onClick={()=>delAval(abaKid,i)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'3px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button>
          </div>)
        })}
      </div>
    </Card>
  </div>)}

function Trabalho(){const TAREFAS_SEED=[{t:'Finalizar proposta Sala Imersiva',p:'PixelSAV',s:'pendente'},{t:'Agente Vita no WhatsApp',p:'SecaVita',s:'andamento'},{t:'Arte de embalagem',p:'Impressões da Domi',s:'pendente'},{t:'Calculadora de projetores',p:'PixelSAV',s:'andamento'},{t:'Migração SGI',p:'SecaVita',s:'concluído'},{t:'Deploy do painel',p:'Lumera',s:'concluído'}];const [tasks,setTasksRaw]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_trabalho')||'null')||TAREFAS_SEED}catch{return TAREFAS_SEED}});const setTasks=(fn:any[]|((prev:any[])=>any[]))=>{setTasksRaw((prev:any[])=>{const n=typeof fn==='function'?(fn as (prev:any[])=>any[])(prev):fn;localStorage.setItem('dos_trabalho',JSON.stringify(n));return n})};const [nova,setNova]=React.useState('');const [proj,setProj]=React.useState('PixelSAV');const cols=[['pendente','Pendente',C.warn],['andamento','Em andamento',C.acc2],['aguardando','Aguardando',C.water],['concluído','Concluído',C.ok]] as [string,string,string][];return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Trabalho</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>PixelSAV · SecaVita · Impressões da Domi · Lumera</p><div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const}}><input value={nova} onChange={e=>setNova(e.target.value)} onKeyDown={e=>e.key==='Enter'&&nova&&(setTasks(t=>[{t:nova,p:proj,s:'pendente'},...t]),setNova(''))} placeholder="Nova tarefa…" style={{flex:1,minWidth:200,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14}}/><select value={proj} onChange={e=>setProj(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14,colorScheme:'dark'}}><option>PixelSAV</option><option>SecaVita</option><option>Impressões da Domi</option><option>Lumera</option></select><button onClick={()=>nova&&(setTasks(t=>[{t:nova,p:proj,s:'pendente'},...t]),setNova(''))} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar</button></div><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:12}}>{cols.map(([status,label,color])=>(<div key={status} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:12}}><div style={{fontSize:11,textTransform:'uppercase' as const,color:'rgba(255,255,255,.4)',marginBottom:10,display:'flex',justifyContent:'space-between' as const}}><span>{label}</span><span style={{color}}>{tasks.filter(t=>t.s===status).length}</span></div>{tasks.filter(t=>t.s===status).map((tk,i)=>(<div key={i} style={{background:C.s,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px',marginBottom:8}}><div style={{fontSize:13,marginBottom:6}}>{tk.t}</div><div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center'}}><span style={{fontSize:11,background:'rgba(139,92,246,.15)',color:C.acc2,padding:'2px 8px',borderRadius:20}}>{tk.p}</span><select value={tk.s} onChange={e=>{const ns=e.target.value;setTasks(ts=>ts.map(x=>x===tk?{...x,s:ns}:x))}} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.4)',fontSize:11,cursor:'pointer',colorScheme:'dark'}}>{cols.map(([s,l])=>(<option key={s} value={s}>{l}</option>))}</select></div></div>))}</div>))}</div></div>)}
function Desenvolvimento(){
  const [pag,setPag]=React.useState('')
  const [min,setMin]=React.useState('')
  const [apren,setApren]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const [leituras,setLeituras]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})
  const [livro,setLivro]=React.useState(()=>{try{return JSON.parse(localStorage.getItem('dos_livro_atual')||'null')||{titulo:'',autor:'',totalPaginas:0,paginaAtual:0}}catch{return {titulo:'',autor:'',totalPaginas:0,paginaAtual:0}}})
  function atualizarLivro(campo:string,valor:string){
    const n={...livro,[campo]:campo==='titulo'||campo==='autor'?valor:Number(valor)||0}
    setLivro(n);localStorage.setItem('dos_livro_atual',JSON.stringify(n))
  }
  const [estante,setEstante]=React.useState<any[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_estante')||'null')||[{titulo:'Hábitos Atômicos',autor:'James Clear',status:'lendo'},{titulo:'O Poder do Hábito',autor:'Charles Duhigg',status:'concluído'},{titulo:'Essencialismo',autor:'Greg McKeown',status:'quero ler'},{titulo:'Deep Work',autor:'Cal Newport',status:'quero ler'}]}catch{return []}})
  const [novoLivroT,setNovoLivroT]=React.useState('')
  const [novoLivroA,setNovoLivroA]=React.useState('')
  function addLivroEstante(){
    if(!novoLivroT)return
    const n=[...estante,{titulo:novoLivroT,autor:novoLivroA,status:'quero ler'}]
    setEstante(n);localStorage.setItem('dos_estante',JSON.stringify(n))
    setNovoLivroT('');setNovoLivroA('')
  }
  function delLivroEstante(i:number){
    const n=estante.filter((_,j)=>j!==i)
    setEstante(n);localStorage.setItem('dos_estante',JSON.stringify(n))
  }
  function salvarLeitura(){
    const reg={data:new Date().toISOString().slice(0,10),pag:Number(pag)||0,min:Number(min)||0,apren}
    const n=[reg,...leituras]
    setLeituras(n);localStorage.setItem('dos_leituras',JSON.stringify(n))
    if(livro.totalPaginas>0&&Number(pag)>0){
      const nl={...livro,paginaAtual:Math.min(livro.totalPaginas,livro.paginaAtual+Number(pag))}
      setLivro(nl);localStorage.setItem('dos_livro_atual',JSON.stringify(nl))
    }
    setSaved(true);setPag('');setMin('');setApren('')
  }
  const diasComLeitura=new Set(leituras.map((l:any)=>l.data))
  let sequenciaLeitura=0
  const dcursor=new Date()
  const hojeIso=new Date().toISOString().slice(0,10)
  if(!diasComLeitura.has(hojeIso))dcursor.setDate(dcursor.getDate()-1)
  while(diasComLeitura.has(dcursor.toISOString().slice(0,10))){sequenciaLeitura++;dcursor.setDate(dcursor.getDate()-1)}
  return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Desenvolvimento</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Biblioteca pessoal · 🔥 Sequência de {sequenciaLeitura} dia{sequenciaLeitura===1?'':'s'} de leitura</p><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}><Card title="Lendo agora"><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}><div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Título</label><input value={livro.titulo} onChange={e=>atualizarLivro('titulo',e.target.value)} placeholder="Nome do livro" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12.5}}/></div><div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Autor</label><input value={livro.autor} onChange={e=>atualizarLivro('autor',e.target.value)} placeholder="Autor" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12.5}}/></div></div><div style={{marginBottom:16}}><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Total de páginas</label><input type="number" value={livro.totalPaginas||''} onChange={e=>atualizarLivro('totalPaginas',e.target.value)} placeholder="320" style={{width:120,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12.5}}/>{livro.titulo&&livro.totalPaginas>0&&<><div style={{fontSize:13,color:'rgba(255,255,255,.4)',marginTop:8}}>{livro.paginaAtual} / {livro.totalPaginas} páginas · {Math.min(100,Math.round(livro.paginaAtual/livro.totalPaginas*100))}%</div><div style={{height:7,borderRadius:4,background:C.s3,overflow:'hidden',marginTop:6,width:180}}><div style={{height:'100%',width:`${Math.min(100,Math.round(livro.paginaAtual/livro.totalPaginas*100))}%`,borderRadius:4,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div></>}</div>{saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Leitura registrada!</div>}<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}><div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Páginas</label><input type="number" value={pag} onChange={e=>setPag(e.target.value)} placeholder="20" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div><div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Minutos</label><input type="number" value={min} onChange={e=>setMin(e.target.value)} placeholder="20" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div></div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Aprendizado</label><input value={apren} onChange={e=>setApren(e.target.value)} placeholder="O que aprendi…" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/><button onClick={salvarLeitura} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Registrar leitura</button>
{leituras.length>0&&<div style={{marginTop:16,borderTop:`1px solid ${C.line}`,paddingTop:12}}>
  <div style={{fontSize:12,fontWeight:700,marginBottom:8,color:'rgba(255,255,255,.6)'}}>Últimas leituras</div>
  {leituras.slice(0,5).map((l:any,i:number)=>(<div key={i} style={{display:'flex',gap:8,padding:'7px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,color:'rgba(255,255,255,.6)'}}><span style={{width:70}}>{l.data.slice(8,10)}/{l.data.slice(5,7)}</span><span style={{flex:1}}>{l.apren||'—'}</span><span>{l.pag}pg · {l.min}min</span></div>))}
</div>}
</Card><Card title="Minha estante">
  <div style={{display:'flex',gap:8,marginBottom:12}}>
    <input value={novoLivroT} onChange={e=>setNovoLivroT(e.target.value)} placeholder="Título do livro" style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12.5}}/>
    <input value={novoLivroA} onChange={e=>setNovoLivroA(e.target.value)} placeholder="Autor" style={{flex:1,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12.5}}/>
    <button onClick={addLivroEstante} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:8,padding:'7px 12px',fontSize:12,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>+ Lista de espera</button>
  </div>
  {estante.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum livro na estante.</div>}
  {estante.map((l,i)=>(<div key={i} style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}><div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',gap:8}}><div style={{flex:1}}><div style={{fontWeight:600,fontSize:13}}>{l.titulo}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{l.autor}</div></div><span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:l.status==='lendo'?'rgba(139,92,246,.15)':l.status==='concluído'?'rgba(52,211,153,.15)':'rgba(255,255,255,.07)',color:l.status==='lendo'?C.acc2:l.status==='concluído'?C.ok:'rgba(255,255,255,.4)',flexShrink:0}}>{l.status}</span><button onClick={()=>delLivroEstante(i)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'3px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button></div></div>))}
</Card></div></div>)}
function Casa(){const [items,setItems]=React.useState([{n:'Iogurte proteico sem lactose',cat:'Mercado',done:false},{n:'Whey isolado',cat:'Mercado',done:false},{n:'Frango',cat:'Mercado',done:false},{n:'Limpar casa',cat:'Doméstico',done:false},{n:'Pagar energia',cat:'Contas',done:false}]);const [nova,setNova]=React.useState('');const [cat,setCat]=React.useState('Mercado');const cats=['Mercado','Doméstico','Manutenção','Contas'];return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Casa</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Compras, tarefas, manutenção e contas</p><div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const}}><input value={nova} onChange={e=>setNova(e.target.value)} onKeyDown={e=>e.key==='Enter'&&nova&&(setItems(i=>[{n:nova,cat,done:false},...i]),setNova(''))} placeholder="Adicionar item…" style={{flex:1,minWidth:200,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14}}/><select value={cat} onChange={e=>setCat(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14,colorScheme:'dark'}}>{cats.map(c=>(<option key={c}>{c}</option>))}</select><button onClick={()=>nova&&(setItems(i=>[{n:nova,cat,done:false},...i]),setNova(''))} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar</button></div><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>{cats.map(c=>(<div key={c}><Card title={c}>{items.filter(i=>i.cat===c).map((item,idx)=>(<div key={idx} onClick={()=>setItems(it=>it.map(x=>x===item?{...x,done:!x.done}:x))} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,cursor:'pointer',opacity:item.done?0.5:1}}><span style={{width:22,height:22,borderRadius:6,border:`2px solid ${item.done?C.ok:'rgba(255,255,255,.2)'}`,background:item.done?'rgba(52,211,153,.2)':'transparent',display:'grid',placeItems:'center',color:C.ok,fontSize:12,flexShrink:0}}>{item.done&&'✓'}</span><span style={{fontSize:13,textDecoration:item.done?'line-through':'none',color:item.done?'rgba(255,255,255,.4)':'#fff'}}>{item.n}</span></div>))}{items.filter(i=>i.cat===c).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum item</div>}</Card></div>))}</div></div>)}
function Insights(){return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Insights</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Padrões observados — associações, não causas.</p>{[{t:'Humor mais alto nos dias com treino',d:'Nos últimos 7 dias, seu humor médio foi maior nos dias em que treinou.',p:'7 dias',c:'associação'},{t:'Proteína abaixo da meta 4 de 7 dias',d:'Queda maior nos fins de semana. Um lanche no sábado pode ajudar.',p:'7 dias',c:'atenção'},{t:'Menos água nas quartas-feiras',d:'Dia de célula à noite — um lembrete extra às 14h pode ajudar.',p:'4 semanas',c:'associação'},{t:'Sequência de leitura: 10 dias 👏',d:'Você manteve a leitura antes de dormir por 10 dias seguidos.',p:'10 dias',c:'conquista'},{t:'Intestino e hidratação caminham juntos',d:'Nos dias com mais de 2L de água, o intestino funcionou melhor.',p:'14 dias',c:'associação'}].map((i,idx)=>(<div key={idx} style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderLeft:`3px solid ${i.c==='conquista'?C.ok:i.c==='atenção'?C.warn:C.acc}`,borderRadius:12,padding:16,marginBottom:12}}><div style={{fontWeight:700,fontSize:14,marginBottom:6}}>{i.t}</div><div style={{fontSize:13,color:'rgba(255,255,255,.6)',lineHeight:1.5,marginBottom:10}}>{i.d}</div><div style={{display:'flex',gap:10,fontSize:11,color:'rgba(255,255,255,.4)'}}><span>{i.p}</span><span style={{background:i.c==='conquista'?'rgba(52,211,153,.15)':i.c==='atenção'?'rgba(251,191,36,.15)':'rgba(139,92,246,.15)',color:i.c==='conquista'?C.ok:i.c==='atenção'?C.warn:C.acc2,padding:'2px 8px',borderRadius:20}}>{i.c}</span></div></div>))}
</div>)}
function Relatorios(){return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Relatórios</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Score semanal e resumos</p><Card title="Score de consistência · últimas 7 semanas"><div style={{display:'flex',alignItems:'flex-end' as const,gap:10,height:130,padding:'10px 0'}}>{[{s:'S1',v:70},{s:'S2',v:78},{s:'S3',v:82},{s:'S4',v:75},{s:'S5',v:88},{s:'S6',v:84},{s:'S7',v:92}].map(b=>(<div key={b.s} style={{flex:1,display:'flex',flexDirection:'column' as const,alignItems:'center',gap:6}}><div style={{flex:1,width:'100%',display:'flex',alignItems:'flex-end' as const}}><div style={{width:'100%',borderRadius:'5px 5px 2px 2px',background:`linear-gradient(180deg,${C.acc2},#6d28d9)`,height:`${b.v}%`}}/></div><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{b.s}</span></div>))}</div></Card><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginTop:16}}><Card title="Resumo do período">{[['Espiritual','90%',C.acc2],['Exercícios','96%',C.ok],['Alimentação','78%',C.warn],['Hidratação','68%',C.warn],['Tirzepatida','100%',C.ok]].map(([p,v,c])=>(<div key={String(p)} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`}}><span style={{flex:1,fontSize:13}}>{p}</span><span style={{fontWeight:700,color:c}}>{v}</span></div>))}</Card><Card title="Tirzepatida">{[['Aplicações','8'],['Estoque atual','217,5 mg'],['Autonomia','~151 dias'],['Sua próxima','02/08/2026'],['Flávio','31/07/2026']].map(([l,v])=>(<div key={String(l)} style={{display:'flex',justifyContent:'space-between' as const,padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{color:'rgba(255,255,255,.6)'}}>{l}</span><span style={{fontWeight:600}}>{v}</span></div>))}</Card></div></div>)}
function Assistente(){const h=new Date().getHours(),g=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite';const [msgs,setMsgs]=React.useState([{me:false,t:`${g}, Denise! ☀️ Estoque tirzepatida: 217,5 mg (~151 dias). Sua próxima: 02/08. Flávio: 31/07. Como posso ajudar? 💜`}]);const [inp,setInp]=React.useState('');function reply(q:string){const ql=q.toLowerCase();if(ql.includes('estoque')||ql.includes('tirzepatida'))return'Estoque: 217,5 mg (~151 dias). Você: 02/08 · Flávio: 31/07.';if(ql.includes('próxim'))return'Sua próxima: 02/08 (5 mg). Flávio: 31/07 (2,5 mg).';if(ql.includes('água'))return'Registrado 💧 Quer que eu some no total?';if(ql.includes('score'))return'Score hoje: 75% — 12 de 16 hábitos.';if(ql.includes('rotina'))return'Hoje: Devocional ✓, escola ✓, calistenia ✓. Próximo: buscar Domi.';return'Anotado! 💜'}function send(){if(!inp.trim())return;const q=inp;setInp('');setMsgs(m=>[...m,{me:true,t:q}]);setTimeout(()=>setMsgs(m=>[...m,{me:false,t:reply(q)}]),400)}return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Assistente IA</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Direto, acolhedor e sem julgamento.</p><div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const,height:'60vh'}}><div style={{flex:1,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:12,paddingBottom:12}}>{msgs.map((m,i)=>(<div key={i} style={{maxWidth:'80%',padding:'11px 14px',borderRadius:14,fontSize:13.5,lineHeight:1.5,alignSelf:m.me?'flex-end':'flex-start',background:m.me?`linear-gradient(135deg,${C.acc},#7c3aed)`:'rgba(255,255,255,.06)',border:m.me?'none':`1px solid ${C.line}`}}>{m.t}</div>))}</div><div style={{display:'flex',flexWrap:'wrap' as const,gap:6,margin:'12px 0'}}>{['Resumo do dia','Próxima aplicação','Estoque tirzepatida','Score hoje'].map(c=>(<button key={c} onClick={()=>setInp(c)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:20,padding:'6px 12px',fontSize:11,color:'rgba(255,255,255,.6)',cursor:'pointer'}}>{c}</button>))}</div><div style={{display:'flex',gap:8,background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:12,padding:'8px 8px 8px 14px'}}><input value={inp} onChange={e=>setInp(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder="Pergunte qualquer coisa…" style={{flex:1,background:'none',border:'none',color:'#fff',fontSize:13.5,outline:'none'}}/><button onClick={send} style={{width:36,height:36,borderRadius:10,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',cursor:'pointer',fontSize:18}}>↑</button></div></div></div>)}
function Config(){
  const [notif,setNotif]=React.useState(()=>{try{return JSON.parse(localStorage.getItem('dos_cfg_notif')||'true')}catch{return true}})
  const [resumo,setResumo]=React.useState(()=>{try{return JSON.parse(localStorage.getItem('dos_cfg_resumo')||'true')}catch{return true}})
  const [fuso,setFuso]=React.useState(()=>localStorage.getItem('dos_cfg_fuso')||'America/Sao_Paulo')
  const [formatoData,setFormatoData]=React.useState(()=>localStorage.getItem('dos_cfg_formato')||'dd/MM/yyyy')
  const [saved,setSaved]=React.useState(false);
  function salvarConfig(){
    localStorage.setItem('dos_cfg_notif',JSON.stringify(notif))
    localStorage.setItem('dos_cfg_resumo',JSON.stringify(resumo))
    localStorage.setItem('dos_cfg_fuso',fuso)
    localStorage.setItem('dos_cfg_formato',formatoData)
    setSaved(true)
  }
  function exportarDados(){
    const dados:Record<string,any>={}
    for(let i=0;i<localStorage.length;i++){
      const k=localStorage.key(i)
      if(!k)continue
      try{dados[k]=JSON.parse(localStorage.getItem(k)||'null')}catch{dados[k]=localStorage.getItem(k)}
    }
    const blob=new Blob([JSON.stringify(dados,null,2)],{type:'application/json'})
    const url=URL.createObjectURL(blob)
    const a=document.createElement('a')
    a.href=url
    a.download=`denise-os-dados-${new Date().toISOString().slice(0,10)}.json`
    document.body.appendChild(a);a.click();document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
const Toggle=({on,toggle}:{on:boolean,toggle:()=>void})=>(<div onClick={toggle} style={{width:44,height:25,borderRadius:20,background:on?C.acc:'rgba(255,255,255,.1)',position:'relative' as const,cursor:'pointer',transition:'.2s',flexShrink:0}}><div style={{position:'absolute' as const,top:2,left:on?21:2,width:21,height:21,borderRadius:'50%',background:'#fff',transition:'.2s'}}/></div>);return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Configurações</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Perfil, notificações, IA e segurança</p>{saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 16px',fontSize:13,color:C.ok,marginBottom:16}}>✓ Configurações salvas!</div>}<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}><Card title="Perfil"><div style={{display:'flex',alignItems:'center',gap:14,marginBottom:16}}><Avatar id="denise" label="D" size={56} radius={14}/><div><div style={{fontWeight:700,fontSize:15}}>Denise</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)'}}>Toque na foto para alterar</div></div></div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Fuso horário</label><input value={fuso} onChange={e=>setFuso(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Formato de data</label><input value={formatoData} onChange={e=>setFormatoData(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></Card><Card title="Notificações">{[['Lembretes no app',notif,()=>setNotif((v:boolean)=>!v)],['Resumo diário',resumo,()=>setResumo((v:boolean)=>!v)]].map(([l,v,fn])=>(<div key={String(l)} style={{display:'flex',alignItems:'center',justifyContent:'space-between' as const,padding:'12px 0',borderBottom:`1px solid ${C.line}`}}><span style={{fontSize:13}}>{String(l)}</span><Toggle on={Boolean(v)} toggle={fn as ()=>void}/></div>))}</Card><Card title="Dados"><div style={{padding:'12px 0',borderBottom:`1px solid ${C.line}`}}><div style={{fontSize:13,fontWeight:600,marginBottom:8}}>Exportar meus dados (LGPD)</div><button onClick={exportarDados} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer'}}>Exportar</button></div><div style={{padding:'12px 0'}}><div style={{fontSize:13,fontWeight:600,color:C.danger,marginBottom:8}}>Limpar dados locais</div><button onClick={()=>{localStorage.clear();window.location.reload()}} style={{background:'rgba(248,113,113,.15)',border:'1px solid rgba(248,113,113,.3)',color:C.danger,borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer'}}>Limpar</button></div></Card></div><button onClick={salvarConfig} style={{marginTop:20,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:11,padding:'13px 28px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Salvar configurações</button></div>)}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><QueryClientProvider client={qc}><AuthGate><PhotoProvider><FamProvider><BrowserRouter><Routes><Route element={<Shell/>}><Route index element={<Home/>}/><Route path="rotina" element={<Rotina/>}/><Route path="agenda" element={<Agenda/>}/><Route path="espiritual" element={<Espiritual/>}/><Route path="saude" element={<Saude/>}/><Route path="alimentacao" element={<Alimentacao/>}/><Route path="exercicios" element={<Exercicios/>}/><Route path="tirzepatida" element={<TirzepatidaPage/>}/><Route path="familia" element={<Familia/>}/><Route path="trabalho" element={<Trabalho/>}/><Route path="desenvolvimento" element={<Desenvolvimento/>}/><Route path="casa" element={<Casa/>}/><Route path="insights" element={<Insights/>}/><Route path="relatorios" element={<Relatorios/>}/><Route path="assistente" element={<Assistente/>}/><Route path="config" element={<Config/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Route></Routes></BrowserRouter></FamProvider></PhotoProvider></AuthGate></QueryClientProvider></React.StrictMode>)
