import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, NavLink, Outlet, Navigate, useNavigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import { supabase } from './lib/supabase'
import { NOME_RESPONSAVEL_PADRAO, FAMILIA_PADRAO, ROTINA_PADRAO, LOCALIZACAO_PADRAO } from './config'

const qc=new QueryClient()
const C={bg:'#0a0a0f',s:'#16161f',s2:'#1c1c28',s3:'#22222f',line:'rgba(255,255,255,.07)',acc:'#8b5cf6',acc2:'#a78bfa',ok:'#34d399',water:'#38bdf8',warn:'#fbbf24',danger:'#f87171',pink:'#f472b6',teal:'#2dd4bf'}
function isoBR(d:Date){return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo'}).format(d)}
function hojeIsoAgua(){return isoBR(new Date())}
function lerAguaHoje(){
  try{
    const iso=hojeIsoAgua()
    const log=JSON.parse(localStorage.getItem('dos_agua_log')||'{}')
    if(typeof log[iso]==='number')return log[iso]
    return Number(localStorage.getItem('dos_wat')||0)
  }catch{return 0}
}
function salvarAguaHoje(ml:number){
  try{
    const iso=hojeIsoAgua()
    const log=JSON.parse(localStorage.getItem('dos_agua_log')||'{}')
    log[iso]=ml
    localStorage.setItem('dos_agua_log',JSON.stringify(log))
  }catch{}
}
type RefEntry={id:string,tipo:string,nome:string,prot?:number,cal?:number,carb?:number,gord?:number,hora:string,origem?:'app'|'whatsapp'}
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
const navItems=[['/', 'Home','🏠'],['/agenda','Agenda','📅'],['/espiritual','Espiritual','📖'],['/saude','Saúde','❤️'],['/alimentacao','Alimentação','🍽️'],['/exercicios','Atividade física','💪'],['/familia','Família','👨‍👩‍👧'],['/trabalho','Trabalho','💼'],['/desenvolvimento','Desenvolvimento','📈'],['/casa','Casa','🏡'],['/assistente','Luna','🌙'],['/relatorios','Relatórios','📊'],['/config','Configurações','⚙️']]

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
type FamData={dropOff:string,pk:{[k:number]:string},entrada?:string,responsavel?:string}
const defaultFam:Record<string,FamData>=FAMILIA_PADRAO as Record<string,FamData>
type ExcecaoFam={responsavel?:string,semAula?:boolean,horarioBusca?:string}
function lerExcecoesFam():Record<string,Record<string,ExcecaoFam>>{
  try{return JSON.parse(localStorage.getItem('dos_fam_excecoes')||'{}')}catch{return {}}
}
function salvarExcecoesFam(v:Record<string,Record<string,ExcecaoFam>>){localStorage.setItem('dos_fam_excecoes',JSON.stringify(v))}
function excecaoFamNaData(kid:string,iso:string):ExcecaoFam|null{
  const todas=lerExcecoesFam()
  return todas[iso]?.[kid]||null
}
function salvarExcecaoFam(kid:string,iso:string,exc:ExcecaoFam){
  const todas=lerExcecoesFam()
  todas[iso]={...(todas[iso]||{}),[kid]:{...(todas[iso]?.[kid]||{}),...exc}}
  salvarExcecoesFam(todas)
}
function buscaEfetivaFam(fam:Record<string,FamData>,kid:'domi'|'derick',iso:string,diaSemana:number):{horario:string,responsavel:string,semAula:boolean}{
  const base=fam[kid]
  const exc=excecaoFamNaData(kid,iso)
  return {
    horario:exc?.horarioBusca||base.pk[diaSemana]||'—',
    responsavel:exc?.responsavel||base.responsavel||(kid==='domi'?'denise':'flavio'),
    semAula:!!exc?.semAula,
  }
}
const NOME_RESPONSAVEL:Record<string,string>=NOME_RESPONSAVEL_PADRAO
type Aval={data:string,materia:string,tipoAvaliacao:string,conteudo:string,peso?:string,observacao?:string,status:'nao_iniciado'|'estudando'|'revisado'|'pronto'|'realizado'}
function migrarAval(a:any):Aval{
  if(a&&a.status)return a as Aval
  const origTipo=a?.tipo||''
  const tipoDetectado=/recupera/i.test(origTipo)?'Recuperação':/AV1/.test(origTipo)?'AV1':/AV2/.test(origTipo)?'AV2':/AV3/.test(origTipo)?'AV3':'Outros'
  return {data:a?.data||'',materia:origTipo,tipoAvaliacao:tipoDetectado,conteudo:a?.obs||'',status:a?.feito?'realizado':'nao_iniciado'}
}
const STATUS_AVAL_LABEL:Record<string,string>={nao_iniciado:'Não iniciado',estudando:'Estudando',revisado:'Revisado',pronto:'Pronto',realizado:'Realizado'}
const STATUS_AVAL_COR:Record<string,string>={nao_iniciado:'rgba(255,255,255,.4)',estudando:C.warn,revisado:C.water,pronto:C.acc2,realizado:C.ok}
function diasRestantesAvalGlobal(dataDDMM:string):number|null{
  const parts=(dataDDMM||'').split('/');if(parts.length<2)return null
  const ano=new Date().getFullYear()
  const d=new Date(`${ano}-${parts[1].padStart(2,'0')}-${parts[0].padStart(2,'0')}`)
  if(isNaN(d.getTime()))return null
  return Math.ceil((d.getTime()-Date.now())/(1000*60*60*24))
}
function proximaAvalPendente(lista:any[]):{aval:Aval,dias:number}|null{
  const comDias=(lista||[]).map(migrarAval).filter(a=>a.status!=='realizado').map(a=>({aval:a,dias:diasRestantesAvalGlobal(a.data)})).filter(x=>x.dias!==null&&(x.dias as number)>=0) as {aval:Aval,dias:number}[]
  comDias.sort((a,b)=>a.dias-b.dias)
  return comDias[0]||null
}
const FamCtx=React.createContext<{fam:typeof defaultFam,setFam:(f:typeof defaultFam)=>void}>({fam:defaultFam,setFam:()=>{}})
function FamProvider({children}:{children:React.ReactNode}){const [fam,setFamState]=React.useState<typeof defaultFam>(()=>{try{return JSON.parse(localStorage.getItem('dos_fam')||'null')||defaultFam}catch{return defaultFam}});const setFam=(f:typeof defaultFam)=>{setFamState(f);localStorage.setItem('dos_fam',JSON.stringify(f))};return <FamCtx.Provider value={{fam,setFam}}>{children}</FamCtx.Provider>}
function Ring({pct,color,size=72,label}:{pct:number,color:string,size?:number,label?:string}){const r=32,ci=2*Math.PI*r,off=ci-ci*pct/100;return(<div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:6,flex:1,minWidth:58}}><div style={{position:'relative',width:size,height:size}}><svg viewBox="0 0 72 72" width={size} height={size} style={{transform:'rotate(-90deg)'}}><circle cx="36" cy="36" r={r} fill="none" strokeWidth={7} stroke="rgba(255,255,255,.07)"/><circle cx="36" cy="36" r={r} fill="none" strokeWidth={7} strokeLinecap="round" stroke={color} strokeDasharray={ci} strokeDashoffset={off}/></svg><span style={{position:'absolute',inset:0,display:'grid',placeItems:'center',fontWeight:800,fontSize:13}}>{pct}%</span></div>{label&&<span style={{fontSize:11,color:'rgba(255,255,255,.7)',textAlign:'center'}}>{label}</span>}</div>)}
function Card({title,action,children}:{title:string,action?:React.ReactNode,children:React.ReactNode}){return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,minWidth:0}}><div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:14}}><h3 style={{fontSize:15,fontWeight:700,margin:0}}>{title}</h3>{action}</div>{children}</div>)}
function Lrow({icon,name,val,ok,color}:{icon:string,name:string,val:string,ok?:boolean,color?:string}){return(<div style={{display:'flex',alignItems:'center',gap:10,padding:'7px 2px',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{width:26,height:26,borderRadius:8,background:C.s2,display:'grid',placeItems:'center',color:color||'rgba(255,255,255,.6)',fontSize:14}}>{icon}</span><span style={{flex:1}}>{name}</span><span style={{color:ok?C.ok:'rgba(255,255,255,.6)',fontSize:12.5}}>{val}{ok&&' ✓'}</span></div>)}
function ModalFam({onClose}:{onClose:()=>void}){const {fam,setFam}=React.useContext(FamCtx);const [local,setLocal]=React.useState(JSON.parse(JSON.stringify(fam)));const days:[number,string][]=[[1,'Seg'],[2,'Ter'],[3,'Qua'],[4,'Qui'],[5,'Sex']];return(<div onClick={e=>{if(e.target===e.currentTarget)onClose()}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}><div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:480,maxHeight:'88vh',overflow:'auto'}}><div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}><h3 style={{margin:0,fontSize:16}}>Rotina das crianças</h3><button onClick={onClose} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button></div>{(['domi','derick'] as const).map(key=>{const nome=key==='domi'?'Domi':'Derick';return(<div key={key} style={{padding:'18px',borderBottom:`1px solid ${C.line}`}}><div style={{display:'flex',alignItems:'center',gap:12,marginBottom:14}}><Avatar id={key} label={nome[0]} size={52} radius={13}/><div><div style={{fontWeight:700,fontSize:15}}>{nome}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Toque na foto para alterar</div></div></div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:5}}>Ida</label><input type="time" value={local[key].dropOff} onChange={e=>setLocal((p:typeof fam)=>({...p,[key]:{...p[key],dropOff:e.target.value}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:15,marginBottom:14,colorScheme:'dark'}}/><label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:8}}>Busca por dia</label><div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:6}}>{days.map(([d,dn])=>(<div key={d}><div style={{fontSize:10.5,color:'rgba(255,255,255,.6)',textAlign:'center' as const,fontWeight:700,marginBottom:4}}>{dn}</div><input type="time" value={local[key].pk[d]||''} onChange={e=>setLocal((p:typeof fam)=>({...p,[key]:{...p[key],pk:{...p[key].pk,[d]:e.target.value}}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'7px 2px',color:'#fff',fontSize:11,textAlign:'center' as const,colorScheme:'dark'}}/></div>))}</div></div>)})}<div style={{display:'flex',gap:10,padding:'14px 18px',position:'sticky',bottom:0,background:'#1c1c28'}}><button onClick={onClose} style={{flex:1,background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Cancelar</button><button onClick={()=>{setFam(local);onClose()}} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>✓ Salvar</button></div></div></div>)}
function Shell(){
  React.useEffect(()=>{
    const EXCLUIR=['dos_google_token','dos_photos','dos_cfg_notif','dos_cfg_resumo','dos_cfg_fuso','dos_cfg_formato']
    async function sincronizarSnapshot(){
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
        const isoHojeSync=isoBR(new Date())
        const chaveHoje=`dos_rotina_done_${isoHojeSync}`
        if(Array.isArray(remoto[chaveHoje])){
          const uniao=Array.from(new Set([...(dados[chaveHoje]||[]),...remoto[chaveHoje]]))
          dados[chaveHoje]=uniao
          localStorage.setItem(chaveHoje,JSON.stringify(uniao))
        }
        const aguaRemotaHoje=(remoto.dos_agua_log||{})[isoHojeSync]
        if(typeof aguaRemotaHoje==='number'){
          const aguaLogLocal=dados.dos_agua_log||{}
          const aguaLocalHoje=Number(aguaLogLocal[isoHojeSync]||0)
          if(aguaRemotaHoje>aguaLocalHoje){
            const novoLogAgua={...aguaLogLocal,[isoHojeSync]:aguaRemotaHoje}
            dados.dos_agua_log=novoLogAgua
            localStorage.setItem('dos_agua_log',JSON.stringify(novoLogAgua))
          }
        }
        const refsRemotosHoje=(remoto.dos_refs_log||{})[isoHojeSync]
        if(Array.isArray(refsRemotosHoje)&&refsRemotosHoje.length>0){
          const refsLogLocal=dados.dos_refs_log||{}
          const refsLocaisHoje:any[]=refsLogLocal[isoHojeSync]||[]
          const idsLocais=new Set(refsLocaisHoje.map((r:any)=>r.id))
          const novosDoRemoto=refsRemotosHoje.filter((r:any)=>r&&r.id&&!idsLocais.has(r.id))
          if(novosDoRemoto.length>0){
            const unidos=[...novosDoRemoto,...refsLocaisHoje]
            const novoLogRefs={...refsLogLocal,[isoHojeSync]:unidos}
            dados.dos_refs_log=novoLogRefs
            localStorage.setItem('dos_refs_log',JSON.stringify(novoLogRefs))
          }
        }
        function mesclarArrayPorId(chave:string){
          const remotos=Array.isArray(remoto[chave])?remoto[chave]:[]
          if(remotos.length===0)return
          const locais=Array.isArray(dados[chave])?dados[chave]:[]
          const idsLocais=new Set(locais.map((it:any)=>it?.id))
          const novosDoRemoto=remotos.filter((it:any)=>it&&it.id&&!idsLocais.has(it.id))
          if(novosDoRemoto.length===0)return
          const unidos=[...locais,...novosDoRemoto]
          dados[chave]=unidos
          localStorage.setItem(chave,JSON.stringify(unidos))
        }
        mesclarArrayPorId('dos_casa_items')
        mesclarArrayPorId('dos_pedidos_oracao')
        mesclarArrayPorId('dos_agenda')
        if(remoto.dos_luna_pendente===undefined&&dados.dos_luna_pendente){
          delete dados.dos_luna_pendente
          localStorage.removeItem('dos_luna_pendente')
        }else if(remoto.dos_luna_pendente&&(!dados.dos_luna_pendente||(remoto.dos_luna_pendente.criadoEm||0)>(dados.dos_luna_pendente.criadoEm||0))){
          dados.dos_luna_pendente=remoto.dos_luna_pendente
          localStorage.setItem('dos_luna_pendente',JSON.stringify(remoto.dos_luna_pendente))
        }
      }catch{}
      supabase.from('app_snapshot').upsert({id:'denise',data:dados,updated_at:new Date().toISOString()}).then(()=>{})
    }
    sincronizarSnapshot()
    const t=setInterval(sincronizarSnapshot,30*1000)
    function sincronizarSeEscondeu(){if(document.hidden)sincronizarSnapshot()}
    window.addEventListener('beforeunload',sincronizarSnapshot)
    document.addEventListener('visibilitychange',sincronizarSeEscondeu)
    return()=>{
      clearInterval(t)
      window.removeEventListener('beforeunload',sincronizarSnapshot)
      document.removeEventListener('visibilitychange',sincronizarSeEscondeu)
    }
  },[])
  const ROTINA_DEF_SHELL=ROTINA_PADRAO
  const rotinaItensShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'null')||ROTINA_DEF_SHELL}catch{return ROTINA_DEF_SHELL}})() as any[]
  function diasUnicosShell(entries:any[]){return new Set(entries.map((e:any)=>e.data))}
  function sequenciaShell(dias:Set<string>){
    let n=0
    const dt=new Date()
    while(dias.has(isoBR(dt))){n++;dt.setDate(dt.getDate()-1)}
    return n
  }
  function pctDiaShell(iso:string){
    try{
      const done=JSON.parse(localStorage.getItem(`dos_rotina_done_${iso}`)||'[]')
      return rotinaItensShell.length>0?done.length/rotinaItensShell.length:0
    }catch{return 0}
  }
  function sequenciaAguaShell(){
    let n=0
    const dt=new Date()
    try{
      const log=JSON.parse(localStorage.getItem('dos_agua_log')||'{}')
      const metaAguaSeq=Number(localStorage.getItem('dos_meta_agua_ml')||2500)
      while((log[isoBR(dt)]||0)>=metaAguaSeq){n++;dt.setDate(dt.getDate()-1)}
    }catch{}
    return n
  }
  const devEntriesShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  const treinosShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]
  const leiturasShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  const seqEspiritual=sequenciaShell(diasUnicosShell(devEntriesShell))
  const seqTreino=sequenciaShell(diasUnicosShell(treinosShell))
  const seqLeitura=sequenciaShell(diasUnicosShell(leiturasShell))
  const seqAgua=sequenciaAguaShell()
  const ultimos7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(6-i));return isoBR(d)})
  const anteriores7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(13-i));return isoBR(d)})
  const pctSemanaAtual=ultimos7Shell.map(pctDiaShell)
  const pctSemanaAnterior=anteriores7Shell.map(pctDiaShell)
  const mediaAtual=Math.round(pctSemanaAtual.reduce((a,b)=>a+b,0)/7*100)
  const mediaAnterior=Math.round(pctSemanaAnterior.reduce((a,b)=>a+b,0)/7*100)
  const deltaSemana=mediaAtual-mediaAnterior
  return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}><aside style={{width:240,flexShrink:0,background:'linear-gradient(180deg,#101018,#0c0c12)',borderRight:`1px solid ${C.line}`,padding:'16px 12px',display:'flex',flexDirection:'column',gap:2,position:'sticky',top:0,height:'100vh',overflowY:'auto'}}><div style={{display:'flex',alignItems:'center',gap:10,padding:'4px 6px 14px'}}><div style={{width:38,height:38,borderRadius:11,background:'linear-gradient(145deg,#8b5cf6,#6d28d9)',display:'grid',placeItems:'center',fontSize:18}}>💜</div><div><div style={{fontWeight:800,fontSize:16}}>Denise OS</div><div style={{fontSize:10,color:'#7d7d90'}}>Seu sistema operacional de vida</div></div></div><nav style={{display:'flex',flexDirection:'column',gap:2}}>{navItems.map(([to,label,icon])=>(<NavLink key={to} to={to} end={to==='/'} style={({isActive})=>({display:'flex',alignItems:'center',gap:9,padding:'9px 10px',borderRadius:10,fontSize:13.5,fontWeight:500,color:isActive?'#fff':'rgba(255,255,255,.6)',background:isActive?'rgba(139,92,246,.15)':'transparent',textDecoration:'none',position:'relative'})}>{({isActive})=><>{isActive&&<span style={{position:'absolute',left:-12,top:8,bottom:8,width:3,borderRadius:'0 3px 3px 0',background:C.acc}}/>}<span style={{fontSize:14}}>{icon}</span>{label}</>}</NavLink>))}</nav><div style={{marginTop:14,background:C.s,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'#7d7d90',textTransform:'uppercase' as const,letterSpacing:'.6px',marginBottom:8}}>Score da semana</div><div style={{display:'flex',alignItems:'baseline',gap:8}}><span style={{fontSize:28,fontWeight:800}}>{mediaAtual}%</span><span style={{fontSize:11,color:deltaSemana>=0?C.ok:C.danger,fontWeight:700}}>{deltaSemana>=0?'▲':'▼'} {Math.abs(deltaSemana)}%</span></div><div style={{display:'flex',gap:4,alignItems:'flex-end',height:40,marginTop:10}}>{pctSemanaAtual.map((p,i)=><span key={i} style={{flex:1,borderRadius:'3px 3px 2px 2px',height:`${Math.max(Math.round(p*100),3)}%`,background:i===6?`linear-gradient(180deg,${C.ok},#15803d)`:`linear-gradient(180deg,${C.acc2},#6d28d9)`}}/>)}</div></div><div style={{marginTop:10,background:C.s,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'#7d7d90',textTransform:'uppercase' as const,letterSpacing:'.6px',marginBottom:12}}>Sequência atual</div><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:6}}>{[{n:seqEspiritual,l:'Espiritual',c:C.pink},{n:seqTreino,l:'Treino',c:C.ok},{n:seqLeitura,l:'Leitura',c:C.warn},{n:seqAgua,l:'Água',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}</div></div><button onClick={()=>supabase.auth.signOut()} style={{marginTop:10,width:'100%',background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)',borderRadius:10,padding:'9px',fontSize:12.5,cursor:'pointer'}}>Sair</button></aside><div style={{flex:1,minWidth:0}}><Outlet/></div></div>)}
function Home(){const navigate=useNavigate();
  const [tzSched,setTzSched]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [tzBalance,setTzBalance]=React.useState(0)
  const [tzApps,setTzApps]=React.useState<any[]>([])
  const [climaTemp,setClimaTemp]=React.useState<number|null>(null)
  React.useEffect(()=>{
    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${LOCALIZACAO_PADRAO.latitude}&longitude=${LOCALIZACAO_PADRAO.longitude}&current=temperature_2m&timezone=America%2FSao_Paulo`)
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
  function fmtIsoLongH(iso:string|null|undefined){if(!iso)return '—';return new Date(iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric'})}
  const tzAutonomy=(()=>{const dDen=tzSched.denise?.planned_dose_mg||5;const dFla=tzSched.flavio?.planned_dose_mg||2.5;const iDen=tzSched.denise?.interval_days||5;const iFla=tzSched.flavio?.interval_days||7;const mgDay=dDen/iDen+dFla/iFla;return mgDay>0?Math.floor(tzBalance/mgDay):0})()
  const tzUltimaDenise=tzApps.find((a:any)=>a.person==='denise')
  const h=new Date().getHours(),g=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite';const today=new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long',year:'numeric'});const {fam}=React.useContext(FamCtx);const day=new Date().getDay(),sd=(day>=1&&day<=5)?day:1
  const wat=lerAguaHoje()
  const [tick,setTick]=React.useState(0)
  const forceRefresh=()=>setTick(t=>t+1)
  const [localNome,setLocalNome]=React.useState(()=>localStorage.getItem('dos_local_nome')||'')
  const editarLocal=()=>{const v=window.prompt('Nome da sua localização',localNome||'');if(v===null)return;setLocalNome(v);localStorage.setItem('dos_local_nome',v)}
  const [showFam,setShowFam]=React.useState(false)
  const [showEditRotina,setShowEditRotina]=React.useState(false)
  const metaAguaHome=Number(localStorage.getItem('dos_meta_agua_ml')||2500)
  const hojeIsoHome=isoBR(new Date())
  type RItemHome={t:string,n:string,cat:string,dias?:number[]}
  const ROTINA_DEF_HOME:RItemHome[]=ROTINA_PADRAO as RItemHome[]
  const rotinaItens=(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'null')||ROTINA_DEF_HOME}catch{return ROTINA_DEF_HOME}})() as RItemHome[]
  const rotinaDiaKeyHome=`dos_rotina_done_${hojeIsoHome}`
  const rotinaDoneIdx=new Set<number>((()=>{try{return JSON.parse(localStorage.getItem(rotinaDiaKeyHome)||'[]')}catch{return []}})())
  const toggleRotinaHome=(i:number)=>{const n=rotinaDoneIdx.has(i)?[...rotinaDoneIdx].filter(x=>x!==i):[...rotinaDoneIdx,i];localStorage.setItem(rotinaDiaKeyHome,JSON.stringify(n));forceRefresh()}
  const hojeDiaHome=new Date(hojeIsoHome+'T12:00:00-03:00').getDay()
  const itemsHojeHome=rotinaItens.map((item,i)=>({item,i})).filter(({item})=>!item.dias||item.dias.includes(hojeDiaHome))
  const rotinaFeitos=itemsHojeHome.filter(({i})=>rotinaDoneIdx.has(i)).length
  const rotinaTotal=itemsHojeHome.length
  const rotinaPct=rotinaTotal>0?Math.round(rotinaFeitos/rotinaTotal*100):0
  const casaItensHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})() as {n:string,cat:string,done:boolean,venc?:string}[]
  const toggleCasaHome=(item:{n:string,cat:string,done:boolean,venc?:string})=>{const n=casaItensHome.map(x=>x===item?{...x,done:!x.done}:x);localStorage.setItem('dos_casa_items',JSON.stringify(n));forceRefresh()}
  const casaPendentesHome=casaItensHome.filter(c=>!c.done)
  const devEntries=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  const treinosHome=(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter(t=>t.status!=='nao_realizado')}catch{return []}})() as any[]
  function segundaDaSemanaHome(d:Date){const x=new Date(d);const dw=x.getDay();const diff=(dw===0?-6:1-dw);x.setDate(x.getDate()+diff);return x}
  const segIsoHome=isoBR(segundaDaSemanaHome(new Date()))
  const treinosSemana=treinosHome.filter((t:any)=>t.data>=segIsoHome)
  const diasTreinoPlanejados=lerMetaTreinos()
  const leiturasHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  const leituraHoje=leiturasHome.some((l:any)=>l.data===hojeIsoHome)
  const lembretes:[string,string,string][]=[]
  if(wat<metaAguaHome)lembretes.push(['💧','Beber mais água',`${((metaAguaHome-wat)/1000).toFixed(1).replace('.',',')} L restantes`])
  if(tzSched.denise?.next_application_date)lembretes.push(['💉','Tirzepatida · você',fmtIsoH(tzSched.denise.next_application_date)])
  if(tzSched.flavio?.next_application_date)lembretes.push(['💉','Tirzepatida · Flávio',fmtIsoH(tzSched.flavio.next_application_date)])
  if(!leituraHoje)lembretes.push(['📖','Leitura','Pendente hoje'])
  void devEntries
  const CORES_CAT_HOME:Record<string,string>={'Espiritual':C.acc2,'Saúde':C.ok,'Alimentação':C.warn,'Família':C.pink,'Exercícios':C.water,'Casa':C.teal,'Trabalho':C.danger,'Compromisso':C.acc,'Desenvolvimento':'#fb923c'}
  const ICONES_CAT_HOME:Record<string,string>={'Espiritual':'🙏','Saúde':'❤️','Alimentação':'🍽️','Família':'👨‍👩‍👧','Exercícios':'💪','Casa':'🏠','Trabalho':'💼','Compromisso':'📅','Desenvolvimento':'📚'}
  const QuadroHome=({tema}:{tema:string})=>{
    const cor=CORES_CAT_HOME[tema]||C.acc2
    const icon=ICONES_CAT_HOME[tema]||'📌'
    const bloco=itemsHojeHome.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
    const extraCasa=tema==='Casa'?casaPendentesHome:[]
    const resumoEspiritual=tema==='Espiritual'?(()=>{
      const devs=lerDevocionais()
      const planosLeitura=lerPlanosLeituraBiblia()
      return {feitoHoje:devs.some((e:any)=>e.data===hojeIsoHome),seq:calcularSequenciaDevocional(devs),leituraHoje:planosLeitura[0]?.leituraAtual||''}
    })():null
    if(bloco.length===0&&extraCasa.length===0&&!resumoEspiritual)return null
    return(<div style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
        <span style={{fontSize:16}}>{icon}</span>
        <span style={{fontWeight:800,fontSize:14,color:cor}}>{tema}</span>
        <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({bloco.length+extraCasa.length})</span>
      </div>
      {resumoEspiritual&&<div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',marginBottom:8,paddingBottom:8,borderBottom:`1px solid ${C.line}`}}>🙏 Devocional: {resumoEspiritual.feitoHoje?'Feito ✓':'Pendente'} · 🔥 {resumoEspiritual.seq}d{resumoEspiritual.leituraHoje?` · 📖 ${resumoEspiritual.leituraHoje}`:''}</div>}
      <div style={{maxHeight:225,overflowY:'auto' as const,flex:1}}>
        {bloco.map(({item,i})=>{
          const feito=rotinaDoneIdx.has(i)
          return(<div key={i} onClick={()=>toggleRotinaHome(i)} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`,cursor:'pointer'}}>
            <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:feito?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:feito?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>{feito?'✓':'○'}</span>
            <span style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{item.t}</span>
            <span style={{flex:1,fontSize:13.5,color:feito?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:feito?'line-through':'none',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' as const}}>{item.n}</span>
          </div>)
        })}
        {extraCasa.map((c,ci)=>(<div key={'casa'+ci} onClick={()=>toggleCasaHome(c)} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`,cursor:'pointer'}}>
          <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:'rgba(255,255,255,.07)',color:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>○</span>
          <span style={{width:42,fontSize:9.5,color:'rgba(255,255,255,.35)',flexShrink:0}}>{c.cat}</span>
          <span style={{flex:1,fontSize:13.5,color:'#f3f3f8',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' as const}}>{c.n}</span>
        </div>))}
      </div>
      <button onClick={()=>setShowEditRotina(true)} style={{marginTop:10,width:'100%',background:'transparent',border:`1px dashed ${C.line}`,color:C.acc2,borderRadius:9,padding:'8px',fontSize:12,fontWeight:600,cursor:'pointer'}}>+ Adicionar</button>
    </div>)
  }
  const eventosAgendaHome=(()=>{try{return lerEventosAgenda()}catch{return []}})()
  const googleCacheHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_google_events_cache')||'[]')}catch{return []}})() as any[]
  const googleIdsHome=new Set(eventosAgendaHome.filter((e:any)=>e.googleEventId).map((e:any)=>e.googleEventId))
  function horaLocalHome(iso:string){const d=new Date(iso);return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`}
  const compromissosHojeHome=(()=>{
    const locais=eventosAgendaHome.filter((e:any)=>!e.ehMestre&&e.data===hojeIsoHome).map((e:any)=>({hora:e.hora,nome:e.nome,cor:e.cor}))
    const google=googleCacheHome.filter((ev:any)=>!googleIdsHome.has(ev.id)).map((ev:any)=>{
      const inicio=ev.start?.dateTime||ev.start?.date
      if(!inicio||!String(inicio).startsWith(hojeIsoHome))return null
      const hora=ev.start?.dateTime?horaLocalHome(ev.start.dateTime):''
      return {hora,nome:ev.summary||'(sem título)',cor:'#4285F4'}
    }).filter(Boolean) as {hora:string,nome:string,cor:string}[]
    return [...locais,...google].sort((a,b)=>(a.hora||'').localeCompare(b.hora||''))
  })()
  const versiculoHoje=versiculoDoDia()
  void tick
  return(<div style={{padding:'20px 22px 40px'}}>
    {showFam&&<ModalFam onClose={()=>{setShowFam(false);forceRefresh()}}/>}
    {showEditRotina&&<div onClick={e=>{if(e.target===e.currentTarget){setShowEditRotina(false);forceRefresh()}}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:180,display:'flex',alignItems:'flex-start',justifyContent:'center',padding:'30px 20px',overflowY:'auto' as const}}>
      <div style={{background:C.bg,border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:1400,position:'relative' as const}}>
        <button onClick={()=>{setShowEditRotina(false);forceRefresh()}} style={{position:'absolute' as const,top:16,right:16,width:34,height:34,borderRadius:10,background:'rgba(255,255,255,.08)',border:'none',color:'#fff',fontSize:15,cursor:'pointer',zIndex:5}}>✕</button>
        <Rotina/>
      </div>
    </div>}
    <div style={{display:'flex',flexWrap:'wrap',gap:14,alignItems:'flex-start',marginBottom:18}}>
      <div><h1 style={{fontSize:25,fontWeight:800,margin:0}}>{g}, Denise! ☀️</h1><div style={{color:'rgba(255,255,255,.6)',fontSize:13,marginTop:5,display:'flex',gap:9,flexWrap:'wrap',alignItems:'center'}}><span style={{textTransform:'capitalize' as const}}>{today}</span><span onClick={editarLocal} style={{cursor:'pointer',background:C.s,border:`1px solid ${C.line}`,padding:'3px 10px',borderRadius:20,fontSize:12,display:'inline-flex',alignItems:'center',gap:5}}>📍 {localNome||'Minha localização'} <span style={{fontSize:10,opacity:.6}}>✎</span></span><span style={{background:C.s,border:`1px solid ${C.line}`,padding:'3px 10px',borderRadius:20,fontSize:12}}>☀️ {climaTemp!==null?`${climaTemp}°C`:'—'}</span></div></div>
      <div style={{marginLeft:'auto',display:'flex',flexDirection:'column' as const,gap:4}}>
        <div style={{background:`linear-gradient(135deg,${C.s2},${C.s})`,border:`1px solid ${C.line}`,borderRadius:16,padding:'13px 16px',maxWidth:360,display:'flex',gap:11}}><span style={{fontSize:22,color:C.acc2}}>"</span><div><p style={{fontSize:13,fontStyle:'italic',margin:0}}>{versiculoHoje.texto}</p><span style={{fontSize:11,color:'#7d7d90'}}>{versiculoHoje.ref}</span></div></div>
        <div style={{fontSize:10.5,color:'rgba(255,255,255,.35)',display:'flex',alignItems:'center',gap:5}}>🔮 Versículo do dia · Atualiza diariamente <span title="Um novo versículo aparece aqui todos os dias.">ⓘ</span></div>
      </div>
      <div style={{display:'flex',gap:9,alignItems:'center'}}><button style={{width:40,height:40,borderRadius:11,background:C.s,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:17}}>🔔</button><button onClick={()=>setShowEditRotina(true)} style={{display:'inline-flex',alignItems:'center',gap:7,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',fontWeight:700,fontSize:13,padding:'10px 14px',borderRadius:11,border:'none',cursor:'pointer'}}>⚡ Ação rápida</button><Avatar id="denise" label="D" size={40} radius={12}/></div>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14,marginBottom:14}}>
      <div style={{gridColumn:'span 3'}}><Card title="Progresso da rotina" action={<button onClick={()=>setShowEditRotina(true)} style={{fontSize:12,color:C.acc2,background:'rgba(139,92,246,.1)',border:'1px solid rgba(139,92,246,.2)',padding:'5px 9px',borderRadius:9,cursor:'pointer'}}>✏️ Editar rotina</button>}>
        <div style={{display:'flex',alignItems:'center',gap:16}}>
          <Ring pct={rotinaPct} color={C.acc2} size={78}/>
          <div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Hoje</div><div style={{fontWeight:800,fontSize:16}}>{rotinaFeitos} de {rotinaTotal}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>itens concluídos</div></div>
        </div>
        <div style={{height:9,borderRadius:6,background:C.s3,overflow:'hidden',marginTop:14}}><div style={{height:'100%',width:`${rotinaPct}%`,borderRadius:6,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div>
        <div style={{display:'flex',justifyContent:'space-between',marginTop:11,fontSize:12}}><span style={{color:'rgba(255,255,255,.5)'}}>Sequência atual: <b style={{color:'#fff'}}>1 dia 🔥</b></span><span style={{color:'rgba(255,255,255,.5)'}}>Meta semanal: <b style={{color:'#fff'}}>0%</b></span></div>
      </Card></div>
      <div style={{gridColumn:'span 3'}}><Card title="Tirzepatida" action={<NavLink to="/saude" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Gerenciar</NavLink>}><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,fontSize:13,marginBottom:11}}><div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Última aplicação</div><div style={{fontWeight:800}}>{tzUltimaDenise?fmtIsoLongH(String(tzUltimaDenise.applied_at).slice(0,10)):'—'}</div><div style={{fontSize:11,color:C.ok}}>{tzUltimaDenise?`${tzUltimaDenise.dose_mg} mg`:''}</div></div><div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Próxima aplicação</div><div style={{fontWeight:800}}>{fmtIsoLongH(tzSched.denise?.next_application_date)}</div><div style={{fontSize:11,color:C.danger}}>{tzSched.denise?.next_application_date?(()=>{const dias=Math.ceil((new Date(tzSched.denise.next_application_date+'T12:00:00').getTime()-Date.now())/86400000);return dias>0?`Em ${dias} dia${dias===1?'':'s'}`:dias===0?'Hoje':'Atrasada'})():''}</div></div></div><div style={{display:'flex',alignItems:'center',gap:11,background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'11px 13px',marginBottom:11}}><div style={{width:36,height:36,borderRadius:10,background:'rgba(139,92,246,.14)',display:'grid',placeItems:'center',fontSize:17}}>💉</div><div><div style={{fontSize:21,fontWeight:800}}>{tzBalance} <small style={{fontSize:13}}>mg</small></div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Estoque atual</div></div><div style={{marginLeft:'auto',textAlign:'right'}}><div style={{fontWeight:800,fontSize:14}}>~{tzAutonomy} dias</div><div style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>de estoque</div></div></div><NavLink to="/saude" style={{display:'flex',alignItems:'center',justifyContent:'center',gap:6,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,textDecoration:'none'}}>+ Registrar aplicação</NavLink><p style={{fontSize:10.5,color:'rgba(255,255,255,.4)',marginTop:10,borderTop:`1px solid ${C.line}`,paddingTop:9,lineHeight:1.4}}>Não substitui orientação médica.</p></Card></div>
      <div style={{gridColumn:'span 3'}}><Card title="Visão rápida"><div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>💧</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{(wat/1000).toFixed(1).replace('.',',')} L</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Água hoje / {(metaAguaHome/1000).toFixed(1).replace('.',',')} L</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>🥩</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{totalProteinaDia(hojeIsoHome)} / {lerMetaProteina()} g</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Proteína hoje</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>🔥</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{treinosSemana.length} / {diasTreinoPlanejados}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Treinos esta semana</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>📖</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>20 min</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Leitura hoje</div></div>
        <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'10px 12px'}}><div style={{fontSize:16}}>✅</div><div style={{fontWeight:800,fontSize:15,marginTop:4}}>{rotinaFeitos} / {rotinaTotal}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Tarefas concluídas hoje</div></div>
      </div><NavLink to="/insights" style={{display:'block',textAlign:'right' as const,marginTop:12,fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver insights completos →</NavLink></Card></div>
      <div style={{gridColumn:'span 3'}}><Card title="Ações rápidas">{([['💧','Registrar água','/alimentacao'],['🍽️','Registrar alimentação','/alimentacao'],['💪','Iniciar treino','/exercicios'],['💉','Registrar tirzepatida','/tirzepatida'],['✅','Nova tarefa','/trabalho']] as [string,string,string][]).map(([icon,label,rota])=>(<div key={label} onClick={()=>navigate(rota)} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 4px',borderBottom:`1px solid ${C.line}`,cursor:'pointer'}}><span style={{fontSize:15}}>{icon}</span><span style={{fontSize:13,flex:1}}>{label}</span><span style={{color:'rgba(255,255,255,.3)',fontSize:13}}>→</span></div>))}</Card></div>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14,marginBottom:14}}>
      <QuadroHome tema="Espiritual"/><QuadroHome tema="Saúde"/><QuadroHome tema="Alimentação"/><QuadroHome tema="Exercícios"/>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14,marginBottom:14}}>
      <QuadroHome tema="Trabalho"/><QuadroHome tema="Casa"/>
      <div style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const}}>
        <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}><span style={{fontSize:16}}>👨‍👩‍👧</span><span style={{fontWeight:800,fontSize:14,color:C.pink}}>Família</span><span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>(2)</span></div>
        <div style={{maxHeight:225,overflowY:'auto' as const,flex:1}}>
          {(['domi','derick'] as const).map(k=>{
            const nome=k==='domi'?'Domi':'Derick'
            const efet=buscaEfetivaFam(fam,k,isoBR(new Date()),sd)
            const avalsK=(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})() as Record<string,any[]>
            const proxAval=proximaAvalPendente(avalsK[k]||[])
            return(<div key={k} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`}}><Avatar id={k} label={nome[0]} size={30} radius={9}/><div style={{flex:1}}><div style={{fontWeight:700,fontSize:13}}>{nome}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{efet.semAula?'Sem aula hoje':`Buscar · ${efet.horario} · ${NOME_RESPONSAVEL[efet.responsavel]||efet.responsavel}`}</div>{proxAval&&<div style={{fontSize:10.5,color:C.warn,marginTop:2}}>{proxAval.aval.materia} · {proxAval.dias===0?'hoje':proxAval.dias===1?'amanhã':`em ${proxAval.dias} dias`}</div>}</div></div>)
          })}
        </div>
        <button onClick={()=>setShowFam(true)} style={{marginTop:10,width:'100%',background:'transparent',border:`1px dashed ${C.line}`,color:C.acc2,borderRadius:9,padding:'8px',fontSize:12,fontWeight:600,cursor:'pointer'}}>+ Adicionar</button>
      </div>
      <QuadroHome tema="Desenvolvimento"/>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14,marginBottom:14}}>
      <div style={{gridColumn:'span 12'}}><Card title="📅 Compromissos de hoje" action={<NavLink to="/agenda" style={{fontSize:12,color:C.acc2,textDecoration:'none'}}>Ver agenda completa →</NavLink>}>
        {compromissosHojeHome.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Nenhum compromisso hoje na agenda.</div>}
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(220px,1fr))',gap:10}}>
          {compromissosHojeHome.map((e,i)=>(<div key={i} style={{display:'flex',alignItems:'center',gap:10,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'9px 12px'}}>
            <span style={{width:4,height:20,borderRadius:2,background:e.cor,flexShrink:0}}/>
            <span style={{fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.hora||'Dia todo'}</span>
            <span style={{fontSize:13,flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' as const}}>{e.nome}</span>
          </div>))}
        </div>
      </Card></div>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14}}>
      <div style={{gridColumn:'span 4',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
        <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}><span style={{fontSize:16}}>💉</span><span style={{fontWeight:800,fontSize:14,color:C.acc2}}>Tirzepatida</span><span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({(['denise','flavio'] as const).filter(p=>tzSched[p]).length})</span></div>
        {(['denise','flavio'] as const).filter(p=>tzSched[p]).map(p=>{
          const info=tzSched[p]
          const dueToday=info.next_application_date===hojeIsoHome
          const overdue=!!info.next_application_date&&info.next_application_date<hojeIsoHome
          return(<div key={p} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
            <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:dueToday||overdue?'rgba(139,92,246,.2)':'rgba(255,255,255,.07)',color:dueToday||overdue?C.acc2:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>💉</span>
            <span style={{flex:1,fontSize:13.5,color:'#f3f3f8'}}>{p==='denise'?'Você':'Flávio'} · {info.planned_dose_mg} mg · {fmtIsoH(info.next_application_date)}{dueToday?' (hoje)':overdue?' (atrasada)':''}</span>
            <NavLink to="/saude" style={{fontSize:11,color:C.acc2,textDecoration:'none',flexShrink:0}}>Registrar →</NavLink>
          </div>)
        })}
        <NavLink to="/saude" style={{display:'block',marginTop:10,textAlign:'center' as const,fontSize:12,color:C.acc2,textDecoration:'none'}}>+ Registrar aplicação</NavLink>
      </div>
      <div style={{gridColumn:'span 4'}}><Card title="Lembretes">{lembretes.length>0?lembretes.map(([icon,name,val],i)=>(<Lrow key={i} icon={icon} name={name} val={val}/>)):<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Nenhum lembrete pendente 🎉</div>}<button onClick={()=>setShowEditRotina(true)} style={{marginTop:10,width:'100%',background:'transparent',border:`1px dashed ${C.line}`,color:C.acc2,borderRadius:9,padding:'8px',fontSize:12,fontWeight:600,cursor:'pointer'}}>+ Novo lembrete</button></Card></div>
      <div style={{gridColumn:'span 4'}}><Card title="Luna"><div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'12px 13px',fontSize:13,color:'rgba(255,255,255,.7)',lineHeight:1.5,marginBottom:11}}>{g}, Denise! 🌟<br/>Hoje é um ótimo dia para cuidar de você.<br/>Foco sugerido: Hidratação e constância. 💜</div><NavLink to="/assistente" style={{display:'flex',alignItems:'center',justifyContent:'center',gap:6,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,textDecoration:'none'}}>Falar com a Luna</NavLink></Card></div>
    </div>
  </div>)}

function Rotina(){
  type RItem={t:string,n:string,cat:string,dias?:number[]}
  const DEF:RItem[]=[{t:'05:30',n:'Devocional',cat:'Espiritual'},{t:'06:00',n:'Acordar · água · humor',cat:'Saúde'},{t:'06:30',n:'Café · whey · creatina',cat:'Alimentação'},{t:'07:00',n:'Levar crianças à escola',cat:'Família'},{t:'07:30',n:'Calistenia',cat:'Exercícios'},{t:'08:20',n:'Banho · skincare',cat:'Casa'},{t:'08:45',n:'Planejar o dia · prioridades',cat:'Trabalho'},{t:'09:30',n:'Lanche da manhã',cat:'Alimentação'},{t:'12:50',n:'Buscar Domi',cat:'Família'},{t:'15:30',n:'Whey da tarde',cat:'Alimentação'},{t:'17:00',n:'Buscar Derick',cat:'Família'},{t:'19:00',n:'Jantar',cat:'Alimentação'},{t:'20:00',n:'Célula (Qua) / Aula (Sex)',cat:'Compromisso'},{t:'21:30',n:'Probióticos',cat:'Saúde'},{t:'22:00',n:'Leitura · 20 min',cat:'Desenvolvimento'}]
  const [items,setItems]=React.useState<RItem[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'null')||DEF}catch{return DEF}})
  const rotinaDiaKey=`dos_rotina_done_${isoBR(new Date())}`
  const [done,setDoneRaw]=React.useState<number[]>(()=>{try{return JSON.parse(localStorage.getItem(rotinaDiaKey)||'[]')}catch{return []}})
  const setDone=(fn:number[]|((prev:number[])=>number[]))=>{setDoneRaw((prev:number[])=>{const n=typeof fn==='function'?(fn as (prev:number[])=>number[])(prev):fn;localStorage.setItem(rotinaDiaKey,JSON.stringify(n));return n})}
  const [editIdx,setEditIdx]=React.useState<number|null>(null)
  const [editItem,setEditItem]=React.useState<RItem>({t:'',n:'',cat:''})
  const [adding,setAdding]=React.useState(false)
  const [newItem,setNewItem]=React.useState<RItem>({t:'',n:'',cat:'Saúde'})
  const cats=['Espiritual','Saúde','Alimentação','Família','Exercícios','Casa','Trabalho','Compromisso','Desenvolvimento']
  const {fam}=React.useContext(FamCtx)
  const [tzSchedAll,setTzSchedAll]=React.useState<Record<string,{dose:number,next:string|null}>>({})
  React.useEffect(()=>{(async()=>{
    const {data:sched}=await supabase.from('tirzepatida_schedule').select('*')
    const map:Record<string,{dose:number,next:string|null}>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={dose:Number(row.planned_dose_mg),next:row.next_application_date}})
    setTzSchedAll(map)
  })()},[])
  const [casaItens,setCasaItens]=React.useState<{n:string,cat:string,done:boolean,venc?:string}[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})
  const toggleCasa=(item:{n:string,cat:string,done:boolean,venc?:string})=>{const n=casaItens.map(x=>x===item?{...x,done:!x.done}:x);setCasaItens(n);localStorage.setItem('dos_casa_items',JSON.stringify(n))}
  const casaPendentes=casaItens.filter(c=>!c.done)
  const [avals,setAvals]=React.useState<Record<string,{data:string,tipo:string,obs:string,feito:boolean}[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})
  const toggleAval=(kid:string,item:{data:string,tipo:string,obs:string,feito:boolean})=>{const lista=(avals[kid]||[]).map(x=>x===item?{...x,feito:!x.feito}:x);const n={...avals,[kid]:lista};setAvals(n);localStorage.setItem('dos_avals',JSON.stringify(n))}
  const save=(it:RItem[])=>{setItems(it);localStorage.setItem('dos_rotina',JSON.stringify(it))}
  const openEdit=(i:number)=>{setEditIdx(i);setEditItem({...items[i]})}
  const saveEdit=()=>{if(editIdx===null)return;const n=[...items];n[editIdx]=editItem;save(n);setEditIdx(null)}
  const del=(i:number)=>{save(items.filter((_,idx)=>idx!==i));setDone(d=>d.filter(x=>x!==i).map(x=>x>i?x-1:x))}
  const addItem=()=>{if(!newItem.n||!newItem.t)return;save([...items,newItem]);setAdding(false);setNewItem({t:'',n:'',cat:'Saúde'})}
  React.useEffect(()=>{
    const OBSOLETOS=new Set([
      'Buscar Domi',
      'Buscar Domi (sair 15 min antes) — Seg/Qua 12:50 · Ter/Qui 11:40 · Sex 13:00',
      'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Cicaplast + extra do dia — Seg/Qua/Sex: Vitacid · Ter/Qui/Sáb: Effaclar Duo+M · Domingo: sem extra',
    ])
    const chas:RItem[]=[
      {t:'06:00',n:'Chá verde + gengibre + canela',cat:'Alimentação'},
      {t:'12:00',n:'Chá hortelã + erva-doce (digestivo)',cat:'Alimentação'},
      {t:'15:00',n:'Chá hibisco + cavalinha',cat:'Alimentação'},
      {t:'20:30',n:'Chá camomila + melissa',cat:'Alimentação'},
      {t:'08:00',n:'Skincare manhã: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Filtro Solar La Roche-Posay, Cicaplast',cat:'Saúde'},
      {t:'12:35',n:'Sair para buscar a Domi (busca 12:50)',cat:'Família',dias:[1,3]},
      {t:'11:25',n:'Sair para buscar a Domi (busca 11:40)',cat:'Família',dias:[2,4]},
      {t:'12:45',n:'Sair para buscar a Domi (busca 13:00)',cat:'Família',dias:[5]},
      {t:'21:00',n:'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Vitacid, Cicaplast',cat:'Saúde',dias:[1,3,5]},
      {t:'21:00',n:'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Effaclar Duo+M, Cicaplast',cat:'Saúde',dias:[2,4,6]},
      {t:'21:00',n:'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Cicaplast',cat:'Saúde',dias:[0]},
      {t:'08:30',n:'Proteína leve: 2 ovos ou iogurte natural',cat:'Alimentação'},
      {t:'12:00',n:'Almoço: proteína (frango/carne/peixe) + legumes + fio de azeite + vitaminas A/D/E/K',cat:'Alimentação'},
    ]
    setItems(prev=>{
      const mantidos=prev.map((it,idx)=>({it,idx})).filter(({it})=>!OBSOLETOS.has(it.n))
      const removeuAlgo=mantidos.length!==prev.length
      const nomesAtuais=new Set(mantidos.map(({it})=>it.n))
      const faltando=chas.filter(c=>!nomesAtuais.has(c.n))
      if(faltando.length===0&&!removeuAlgo)return prev
      const novosItems=[...mantidos.map(({it})=>it),...faltando]
      if(removeuAlgo){
        const idxMap=new Map(mantidos.map(({idx},novoIdx)=>[idx,novoIdx]))
        setDone(d=>d.map(x=>idxMap.get(x)).filter((x):x is number=>x!==undefined))
      }
      localStorage.setItem('dos_rotina',JSON.stringify(novosItems))
      return novosItems
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])
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
      <div><h1 style={{fontSize:24,fontWeight:800,margin:0}}>Editar rotina</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginTop:4}}>Toque para marcar · ✏️ para editar · salva automaticamente</p></div>
      <button onClick={()=>setAdding(true)} style={{background:'linear-gradient(135deg,#8b5cf6,#7c3aed)',color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Novo item</button>
    </div>
    {(()=>{
      const hojeDia=new Date(isoBR(new Date())+'T12:00:00-03:00').getDay()
      const itemsHoje=items.map((item,i)=>({item,i})).filter(({item})=>!item.dias||item.dias.includes(hojeDia))
      const doneHoje=itemsHoje.filter(({i})=>done.includes(i))
      const CORES_CAT:Record<string,string>={'Espiritual':C.acc2,'Saúde':C.ok,'Alimentação':C.warn,'Família':C.pink,'Exercícios':C.water,'Casa':C.teal,'Trabalho':C.danger,'Compromisso':C.acc,'Desenvolvimento':'#fb923c'}
      const ICONES_CAT:Record<string,string>={'Espiritual':'🙏','Saúde':'❤️','Alimentação':'🍽️','Família':'👨‍👩‍👧','Exercícios':'💪','Casa':'🏠','Trabalho':'💼','Compromisso':'📅','Desenvolvimento':'📚'}
      return(<>
        <div style={{fontSize:13,color:'rgba(255,255,255,.5)',marginBottom:14}}>Hoje — {doneHoje.length} / {itemsHoje.length} concluídos ({itemsHoje.length>0?Math.round(doneHoje.length/itemsHoje.length*100):0}%)</div>
        <div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14}}>
        {cats.filter(tema=>tema!=='Família').map(tema=>{
          const cor=CORES_CAT[tema]||C.acc2
          const icon=ICONES_CAT[tema]||'📌'
          const bloco=itemsHoje.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
          const extraCasa=tema==='Casa'?casaPendentes:[]
          if(bloco.length===0&&extraCasa.length===0)return null
          return(<div key={tema} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>{icon}</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{tema}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({bloco.length+extraCasa.length})</span>
            </div>
            <div style={{maxHeight:225,overflowY:'auto' as const}}>
              {bloco.map(({item,i})=>{
                const feito=done.includes(i)
                return(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:feito?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:feito?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>{feito?'✓':'○'}</span>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,cursor:'pointer'}}>{item.t}</span>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{flex:1,fontSize:13.5,color:feito?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:feito?'line-through':'none',cursor:'pointer'}}>{item.n}</span>
                  <button onClick={()=>openEdit(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:13,flexShrink:0}}>✏️</button>
                  <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
                </div>)
              })}
              {extraCasa.map((c,ci)=>(<div key={'casa'+ci} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                <span onClick={()=>toggleCasa(c)} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:'rgba(255,255,255,.07)',color:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>○</span>
                <span style={{width:42,fontSize:9.5,color:'rgba(255,255,255,.35)',flexShrink:0}}>{c.cat}</span>
                <span onClick={()=>toggleCasa(c)} style={{flex:1,fontSize:13.5,color:'#f3f3f8',cursor:'pointer'}}>{c.n}</span>
              </div>))}
            </div>
          </div>)
        })}
        {(tzSchedAll.denise||tzSchedAll.flavio)&&(()=>{
          const hojeIsoTz=isoBR(new Date())
          const pessoas=(['denise','flavio'] as const).filter(p=>tzSchedAll[p])
          return(<div style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>💉</span>
              <span style={{fontWeight:800,fontSize:14,color:C.acc2}}>Tirzepatida</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({pessoas.length})</span>
            </div>
            <div style={{maxHeight:225,overflowY:'auto' as const}}>
              {pessoas.map(p=>{
                const info=tzSchedAll[p]
                const dueToday=info.next===hojeIsoTz
                const overdue=!!info.next&&info.next<hojeIsoTz
                return(<div key={p} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                  <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:dueToday||overdue?'rgba(139,92,246,.2)':'rgba(255,255,255,.07)',color:dueToday||overdue?C.acc2:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>💉</span>
                  <span style={{flex:1,fontSize:13.5,color:'#f3f3f8'}}>{p==='denise'?'Você':'Flávio'} · {info.dose} mg · {info.next?new Date(info.next+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}):'—'}{dueToday?' (hoje)':overdue?' (atrasada)':''}</span>
                  <NavLink to="/saude" style={{fontSize:11,color:C.acc2,textDecoration:'none',flexShrink:0}}>Registrar →</NavLink>
                </div>)
              })}
            </div>
          </div>)
        })()}
        {(['domi','derick'] as const).map(kid=>{
          const nome=kid==='domi'?'Domi':'Derick'
          const cor=kid==='domi'?C.pink:C.water
          const pk=fam[kid]?.pk?.[hojeDia]||'—'
          const itensKid=itemsHoje.filter(({item})=>item.cat==='Família'&&(item.n.includes(nome)||!(item.n.includes('Domi')||item.n.includes('Derick'))))
          const avalsKid=(avals[kid]||[]).filter(a=>!a.feito).sort((a,b)=>a.data.localeCompare(b.data))
          return(<div key={kid} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>👧</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{nome}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({itensKid.length+1+avalsKid.length})</span>
            </div>
            <div style={{maxHeight:225,overflowY:'auto' as const}}>
              <div style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:'rgba(255,255,255,.07)',color:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>🚗</span>
                <span style={{flex:1,fontSize:13.5,color:'#f3f3f8'}}>Buscar {nome}</span>
                <span style={{fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{pk}</span>
              </div>
              {itensKid.map(({item,i})=>{
                const feito=done.includes(i)
                return(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:feito?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:feito?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>{feito?'✓':'○'}</span>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,cursor:'pointer'}}>{item.t}</span>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{flex:1,fontSize:13.5,color:feito?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:feito?'line-through':'none',cursor:'pointer'}}>{item.n}</span>
                  <button onClick={()=>openEdit(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:13,flexShrink:0}}>✏️</button>
                  <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
                </div>)
              })}
              {avalsKid.map((a,ai)=>(<div key={'aval'+ai} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                <span onClick={()=>toggleAval(kid,a)} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:'rgba(255,255,255,.07)',color:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>○</span>
                <span style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{a.data}</span>
                <span onClick={()=>toggleAval(kid,a)} style={{flex:1,fontSize:13.5,color:'#f3f3f8',cursor:'pointer'}}>{a.tipo}{a.obs?<span style={{color:'rgba(255,255,255,.4)',fontSize:11.5}}> · {a.obs}</span>:null}</span>
              </div>))}
            </div>
          </div>)
        })}
        </div>
      </>)
    })()}
  </div>)}
const CATEGORIAS_AGENDA:Record<string,{label:string,cor:string}>={
  pessoal:{label:'Pessoal',cor:C.acc2},
  familia:{label:'Família',cor:C.pink},
  trabalho:{label:'Trabalho',cor:C.warn},
  saude:{label:'Saúde',cor:C.ok},
  casa:{label:'Casa',cor:C.water},
}
const LEMBRETE_OPCOES=[{min:0,label:'Na hora'},{min:15,label:'15 min antes'},{min:30,label:'30 min antes'},{min:60,label:'1h antes'},{min:1440,label:'1 dia antes'}]
const RECORRENCIA_OPCOES=[{v:'nao',label:'Não repete'},{v:'diaria',label:'Diariamente'},{v:'semanal',label:'Semanalmente'},{v:'dias_especificos',label:'Dias específicos'},{v:'mensal',label:'Mensalmente'},{v:'anual',label:'Anualmente'}]
const DIAS_SEMANA_LABEL=['Dom','Seg','Ter','Qua','Qui','Sex','Sab']

function novoIdEvento(){return 'ev_'+Date.now().toString(36)+Math.random().toString(36).slice(2,8)}

function migrarEventoAgenda(e:any):any{
  const categoria=e.categoria||'pessoal'
  return {
    id:e.id||novoIdEvento(),
    nome:e.nome||'',
    data:e.data||'',
    hora:e.hora||'',
    horaFim:e.horaFim||'',
    local:e.local||'',
    descricao:e.descricao||'',
    categoria,
    origem:e.origem||'app',
    pessoa:e.pessoa||'',
    cor:e.cor||(CATEGORIAS_AGENDA[categoria]?.cor||C.acc2),
    googleEventId:e.googleEventId||null,
    recorrencia:e.recorrencia||null,
    recorrenciaId:e.recorrenciaId||null,
    ehMestre:!!e.ehMestre,
    excecoes:Array.isArray(e.excecoes)?e.excecoes:[],
    lembretes:Array.isArray(e.lembretes)?e.lembretes:[],
  }
}

function lerEventosAgenda():any[]{
  try{
    const bruto=JSON.parse(localStorage.getItem('dos_agenda')||'[]')
    if(!Array.isArray(bruto))return []
    const migrado=bruto.map(migrarEventoAgenda)
    if(JSON.stringify(bruto)!==JSON.stringify(migrado))localStorage.setItem('dos_agenda',JSON.stringify(migrado))
    return migrado
  }catch{return []}
}
function salvarEventosAgenda(lista:any[]){localStorage.setItem('dos_agenda',JSON.stringify(lista))}

function pad2Ag(n:number){return String(n).padStart(2,'0')}
function toISOAg(d:Date){return `${d.getFullYear()}-${pad2Ag(d.getMonth()+1)}-${pad2Ag(d.getDate())}`}

function proximaDataRecorrencia(dataISO:string,tipo:string,diasSemana?:number[]):string{
  const d=new Date(dataISO+'T12:00:00')
  if(tipo==='diaria'){d.setDate(d.getDate()+1);return toISOAg(d)}
  if(tipo==='semanal'){d.setDate(d.getDate()+7);return toISOAg(d)}
  if(tipo==='dias_especificos'&&diasSemana&&diasSemana.length>0){
    for(let i=1;i<=14;i++){const t=new Date(d);t.setDate(t.getDate()+i);if(diasSemana.includes(t.getDay()))return toISOAg(t)}
    return toISOAg(d)
  }
  if(tipo==='mensal'){d.setMonth(d.getMonth()+1);return toISOAg(d)}
  if(tipo==='anual'){d.setFullYear(d.getFullYear()+1);return toISOAg(d)}
  return toISOAg(d)
}

function materializarRecorrencia(mestre:any,existentes:any[],horizonteDias=120):any[]{
  const rec=mestre.recorrencia
  if(!rec)return []
  const jaExistem=new Set(existentes.filter(e=>e.recorrenciaId===mestre.id).map(e=>e.data))
  const excecoes=new Set(mestre.excecoes||[])
  const limite=toISOAg(new Date(Date.now()+horizonteDias*86400000))
  const novos:any[]=[]
  let cursor=mestre.data
  let contagemTotal=jaExistem.size+excecoes.size
  const maxOcorrencias=rec.ocorrencias||99999
  while(contagemTotal<maxOcorrencias&&cursor<=limite&&(!rec.ate||cursor<=rec.ate)){
    if(!jaExistem.has(cursor)&&!excecoes.has(cursor)){
      novos.push({...mestre,id:novoIdEvento(),ehMestre:false,recorrencia:null,recorrenciaId:mestre.id,googleEventId:null,data:cursor,excecoes:[]})
      jaExistem.add(cursor)
    }
    contagemTotal++
    cursor=rec.tipo==='dias_especificos'?proximaDataRecorrencia(cursor,rec.tipo,rec.diasSemana):proximaDataRecorrencia(cursor,rec.tipo)
  }
  return novos
}

async function sincronizarEventoGoogle(evento:any,acao:'criar'|'editar'):Promise<string|null>{
  try{
    const resp=await fetch('/api/agenda-sync-google',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({acao,googleEventId:evento.googleEventId,evento:{nome:evento.nome,data:evento.data,hora:evento.hora,horaFim:evento.horaFim,local:evento.local,descricao:evento.descricao}})})
    const j=await resp.json()
    return j?.google_evento?.id||evento.googleEventId||null
  }catch{return evento.googleEventId||null}
}
async function excluirEventoGoogleSync(googleEventId:string|null|undefined){
  if(!googleEventId)return
  try{await fetch('/api/agenda-sync-google',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({acao:'excluir',googleEventId})})}catch{}
}

async function criarEventoAgenda(campos:any):Promise<any>{
  const categoria=campos.categoria||'pessoal'
  const base=migrarEventoAgenda({...campos,categoria,cor:campos.cor||CATEGORIAS_AGENDA[categoria]?.cor,origem:campos.origem||'app'})
  const eventos=lerEventosAgenda()
  if(campos.recorrencia){
    const mestre={...base,ehMestre:true,recorrencia:campos.recorrencia,excecoes:[]}
    const instancias=materializarRecorrencia(mestre,eventos,120)
    for(const inst of instancias){inst.googleEventId=await sincronizarEventoGoogle(inst,'criar')}
    salvarEventosAgenda([...eventos,mestre,...instancias])
    return mestre
  }
  const novo={...base}
  novo.googleEventId=await sincronizarEventoGoogle(novo,'criar')
  salvarEventosAgenda([...eventos,novo])
  return novo
}

async function editarEventoAgenda(id:string,campos:any,escopo:'este'|'futuros'|'serie'):Promise<void>{
  const eventos=lerEventosAgenda()
  const alvo=eventos.find(e=>e.id===id)
  if(!alvo)return
  if(!alvo.recorrenciaId){
    const atualizado={...alvo,...campos}
    atualizado.googleEventId=await sincronizarEventoGoogle(atualizado,atualizado.googleEventId?'editar':'criar')
    salvarEventosAgenda(eventos.map(e=>e.id===id?atualizado:e))
    return
  }
  const recId=alvo.recorrenciaId
  if(escopo==='este'){
    const atualizado={...alvo,...campos}
    atualizado.googleEventId=await sincronizarEventoGoogle(atualizado,atualizado.googleEventId?'editar':'criar')
    salvarEventosAgenda(eventos.map(e=>e.id===id?atualizado:e))
    return
  }
  if(escopo==='futuros'){
    const alvos=eventos.filter(e=>e.recorrenciaId===recId&&e.data>=alvo.data)
    const atualizados:any[]=[]
    for(const e of alvos){
      const at={...e,...campos,data:e.data}
      at.googleEventId=await sincronizarEventoGoogle(at,at.googleEventId?'editar':'criar')
      atualizados.push(at)
    }
    let novaLista=eventos.map(e=>atualizados.find(a=>a.id===e.id)||e)
    novaLista=novaLista.map(e=>e.id===recId&&e.ehMestre?{...e,...campos,data:e.data,recorrencia:e.recorrencia}:e)
    salvarEventosAgenda(novaLista)
    return
  }
  const alvos=eventos.filter(e=>e.recorrenciaId===recId||e.id===recId)
  const atualizados:any[]=[]
  for(const e of alvos){
    const at={...e,...campos,data:e.data,recorrencia:e.recorrencia,ehMestre:e.ehMestre}
    if(!e.ehMestre)at.googleEventId=await sincronizarEventoGoogle(at,at.googleEventId?'editar':'criar')
    atualizados.push(at)
  }
  salvarEventosAgenda(eventos.map(e=>atualizados.find(a=>a.id===e.id)||e))
}

async function excluirEventoAgenda(id:string,escopo:'este'|'futuros'|'serie'):Promise<void>{
  const eventos=lerEventosAgenda()
  const alvo=eventos.find(e=>e.id===id)
  if(!alvo)return
  if(!alvo.recorrenciaId){
    await excluirEventoGoogleSync(alvo.googleEventId)
    salvarEventosAgenda(eventos.filter(e=>e.id!==id))
    return
  }
  const recId=alvo.recorrenciaId
  if(escopo==='este'){
    await excluirEventoGoogleSync(alvo.googleEventId)
    salvarEventosAgenda(eventos.filter(e=>e.id!==id).map(e=>e.id===recId?{...e,excecoes:[...(e.excecoes||[]),alvo.data]}:e))
    return
  }
  if(escopo==='futuros'){
    const remover=eventos.filter(e=>e.recorrenciaId===recId&&e.data>=alvo.data)
    for(const e of remover)await excluirEventoGoogleSync(e.googleEventId)
    const idsRemover=new Set(remover.map(e=>e.id))
    const diaAnterior=toISOAg(new Date(new Date(alvo.data+'T12:00:00').getTime()-86400000))
    salvarEventosAgenda(eventos.filter(e=>!idsRemover.has(e.id)).map(e=>e.id===recId&&e.ehMestre?{...e,recorrencia:{...e.recorrencia,ate:diaAnterior}}:e))
    return
  }
  const remover=eventos.filter(e=>e.recorrenciaId===recId||e.id===recId)
  for(const e of remover)await excluirEventoGoogleSync(e.googleEventId)
  const idsRemover=new Set(remover.map(e=>e.id))
  salvarEventosAgenda(eventos.filter(e=>!idsRemover.has(e.id)))
}

async function estenderMaterializacaoAgenda():Promise<void>{
  const eventos=lerEventosAgenda()
  const mestres=eventos.filter(e=>e.ehMestre&&e.recorrencia)
  if(mestres.length===0)return
  let novaLista=eventos
  let mudou=false
  for(const mestre of mestres){
    const novos=materializarRecorrencia(mestre,novaLista,120)
    if(novos.length>0){
      for(const n of novos)n.googleEventId=await sincronizarEventoGoogle(n,'criar')
      novaLista=[...novaLista,...novos]
      mudou=true
    }
  }
  if(mudou)salvarEventosAgenda(novaLista)
}

function detectarConflitosAgenda(evsDoDia:any[],horaIni:string,horaFimP:string,ignorarTitulo?:string):any[]{
  if(!horaIni)return []
  const fim=horaFimP||horaIni
  return evsDoDia.filter(e=>e.time&&e.title!==ignorarTitulo).filter(e=>{
    const fimE=e.timeFim||e.time
    return e.time<fim&&horaIni<fimE
  })
}

function Agenda(){
  const GOOGLE_CLIENT_ID='386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'
  const GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar.events'
  const NOVO_VAZIO={data:'',hora:'',horaFim:'',nome:'',local:'',descricao:'',categoria:'pessoal',cor:CATEGORIAS_AGENDA.pessoal.cor,lembretes:[] as number[],repete:'nao',diasSemana:[] as number[],repeteAte:'',repeteOcorrencias:''}
  const [eventos,setEventos]=React.useState<any[]>(()=>lerEventosAgenda())
  const [novo,setNovo]=React.useState<any>(NOVO_VAZIO)
  const [mostrarMais,setMostrarMais]=React.useState(false)
  const [eventoEditando,setEventoEditando]=React.useState<any>(null)
  const [detalheEvento,setDetalheEvento]=React.useState<any>(null)
  const [escopoPendente,setEscopoPendente]=React.useState<any>(null)
  const [reagendando,setReagendando]=React.useState<any>(null)
  const [busca,setBusca]=React.useState('')
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

  function recarregar(){setEventos(lerEventosAgenda())}

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
    estenderMaterializacaoAgenda().then(recarregar)
    if(gToken){buscarEventosGoogle(gToken);return}
    tentarReconectarSilencioso()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  React.useEffect(()=>{
    const iv=setInterval(()=>{tentarReconectarSilencioso()},45*60*1000)
    return ()=>clearInterval(iv)
  },[])

  function buscarEventosGoogle(token:string){
    setGLoading(true);setGErro('')
    const hoje=new Date()
    const timeMin=new Date(hoje.getFullYear(),hoje.getMonth()-2,1).toISOString()
    const timeMax=new Date(hoje.getFullYear(),hoje.getMonth()+10,1).toISOString()
    fetch(`https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&maxResults=250&singleEvents=true&orderBy=startTime`,{headers:{Authorization:`Bearer ${token}`}})
      .then(r=>r.json())
      .then(data=>{
        const items=data.items||[]
        setGEventos(items)
        setGLoading(false)
        try{localStorage.setItem('dos_google_events_cache',JSON.stringify(items))}catch{}
      })
      .catch(()=>{setGErro('Erro ao buscar eventos do Google.');setGLoading(false)})
  }

  function tentarReconectarSilencioso(){
    fetch('/api/google-token').then(r=>r.json()).then(data=>{
      if(data&&data.access_token){
        setGToken(data.access_token)
        try{localStorage.setItem('dos_google_token',JSON.stringify({token:data.access_token,expiresAt:data.expires_at||(Date.now()+50*60*1000)}))}catch{}
        buscarEventosGoogle(data.access_token)
      }
    }).catch(()=>{})
  }

  function conectarGoogle(){
    const redirectUri=`${window.location.origin}/api/google-oauth-callback`
    const url=`https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&access_type=offline&prompt=consent&scope=${encodeURIComponent(GOOGLE_SCOPE)}`
    window.location.href=url
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
    recarregar()
    try{setMedicamentosAg(JSON.parse(localStorage.getItem('dos_medicamentos')||'{}'))}catch{}
    supabase.from('tirzepatida_schedule').select('*').then(({data}:any)=>{
      const m:any={}
      ;(data||[]).forEach((r:any)=>{m[r.person]=r})
      setSchedules(m)
    })
    if(gToken)buscarEventosGoogle(gToken)
  }

  const eventosVisiveis=eventos.filter((e:any)=>!e.ehMestre)
  const googleIdsLocais=new Set(eventosVisiveis.filter((e:any)=>e.googleEventId).map((e:any)=>e.googleEventId))
  const localEvs=eventosVisiveis.map((e:any)=>({id:e.id,date:e.data,time:e.hora,timeFim:e.horaFim||e.hora,title:e.nome,color:e.cor,source:'app' as const,categoria:e.categoria,evento:e}))
  const googleEvs=gEventos.filter((ev:any)=>!googleIdsLocais.has(ev.id)).map((ev:any)=>{
    const inicio=ev.start?.dateTime||ev.start?.date
    const fimRaw=ev.end?.dateTime
    const isDate=!!ev.start?.date
    const d=new Date(inicio)
    const time=isDate?'':`${pad2(d.getHours())}:${pad2(d.getMinutes())}`
    const timeFim=fimRaw?(()=>{const df=new Date(fimRaw);return `${pad2(df.getHours())}:${pad2(df.getMinutes())}`})():time
    return {id:ev.id,date:toISO(d),time,timeFim,title:ev.summary||'(Sem titulo)',color:'#4285F4',source:'google' as const,categoria:'',evento:null}
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
          medEvs.push({id:`med_${kid}_${m.nome}_${iso}_${h}`,date:iso,time:h,timeFim:h,title:`${m.nome} - ${info.nome}`,color:info.cor,source:'medicamento' as const,categoria:'saude',evento:null})
        })
      }
    })
  })
  const tirzoEvs:any[]=[]
  if(schedules.denise?.next_application_date)tirzoEvs.push({id:'tirzo_denise',date:schedules.denise.next_application_date,time:'',timeFim:'',title:'Tirzepatida - Denise',color:C.acc2,source:'tirzo' as const,categoria:'saude',evento:null})
  if(schedules.flavio?.next_application_date)tirzoEvs.push({id:'tirzo_flavio',date:schedules.flavio.next_application_date,time:'',timeFim:'',title:'Tirzepatida - Flavio',color:C.water,source:'tirzo' as const,categoria:'saude',evento:null})
  const allEvs=[...localEvs,...googleEvs,...tirzoEvs,...medEvs]
  const evsByDate:Record<string,any[]>={}
  allEvs.forEach((e:any)=>{(evsByDate[e.date]=evsByDate[e.date]||[]).push(e)})
  Object.values(evsByDate).forEach((arr:any)=>arr.sort((a:any,b:any)=>(a.time||'').localeCompare(b.time||'')))

  const buscaLower=busca.trim().toLowerCase()
  const resultadosBusca=buscaLower?allEvs.filter((e:any)=>e.title.toLowerCase().includes(buscaLower)||(e.evento?.local||'').toLowerCase().includes(buscaLower)||(e.evento?.descricao||'').toLowerCase().includes(buscaLower)).sort((a:any,b:any)=>(a.date+a.time).localeCompare(b.date+b.time)):[]

  function fmtDiaLong(d:Date){return d.toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long',year:'numeric'})}
  function fmtMesAno(d:Date){const s2=d.toLocaleDateString('pt-BR',{month:'long',year:'numeric'});return s2.charAt(0).toUpperCase()+s2.slice(1)}
  function fmtDiaCurto(d:Date){return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}

  function abrirDetalhe(e:any){setDetalheEvento(e)}
  function fecharDetalhe(){setDetalheEvento(null)}

  function abrirEdicao(e:any){
    const ev=e.evento
    if(!ev||ev.origem!=='app')return
    setEventoEditando(ev)
    setNovo({data:ev.data,hora:ev.hora||'',horaFim:ev.horaFim||'',nome:ev.nome,local:ev.local||'',descricao:ev.descricao||'',categoria:ev.categoria||'pessoal',cor:ev.cor||CATEGORIAS_AGENDA[ev.categoria||'pessoal']?.cor,lembretes:ev.lembretes||[],repete:'nao',diasSemana:[],repeteAte:'',repeteOcorrencias:''})
    setMostrarMais(true)
    setDetalheEvento(null)
  }

  function cancelarEdicao(){
    setEventoEditando(null)
    setNovo(NOVO_VAZIO)
    setMostrarMais(false)
  }

  async function salvarEvento(){
    if(!novo.data||!novo.nome)return
    const campos:any={nome:novo.nome,data:novo.data,hora:novo.hora,horaFim:novo.horaFim,local:novo.local,descricao:novo.descricao,categoria:novo.categoria,cor:novo.cor,lembretes:novo.lembretes}
    if(eventoEditando){
      if(eventoEditando.recorrenciaId){
        setEscopoPendente({acao:'editar',id:eventoEditando.id,campos})
        return
      }
      await editarEventoAgenda(eventoEditando.id,campos,'este')
    }else{
      if(novo.repete!=='nao'){
        campos.recorrencia={tipo:novo.repete,diasSemana:novo.diasSemana,ate:novo.repeteAte||undefined,ocorrencias:novo.repeteOcorrencias?Number(novo.repeteOcorrencias):undefined}
      }
      await criarEventoAgenda(campos)
    }
    finalizarFormulario()
  }

  function finalizarFormulario(){
    setNovo(NOVO_VAZIO)
    setEventoEditando(null)
    setMostrarMais(false)
    setSaved(true)
    recarregar()
    if(gToken)buscarEventosGoogle(gToken)
  }

  async function pedirExclusao(e:any){
    const ev=e.evento
    if(!ev||ev.origem!=='app')return
    if(ev.recorrenciaId){setEscopoPendente({acao:'excluir',id:ev.id});return}
    if(!window.confirm(`Excluir "${ev.nome}"?`))return
    await excluirEventoAgenda(ev.id,'este')
    fecharDetalhe()
    recarregar()
    if(gToken)buscarEventosGoogle(gToken)
  }

  async function confirmarEscopo(escopo:'este'|'futuros'|'serie'){
    if(!escopoPendente)return
    if(escopoPendente.acao==='editar')await editarEventoAgenda(escopoPendente.id,escopoPendente.campos,escopo)
    else await excluirEventoAgenda(escopoPendente.id,escopo)
    setEscopoPendente(null)
    fecharDetalhe()
    finalizarFormulario()
  }

  function abrirReagendar(e:any){
    const ev=e.evento
    if(!ev||ev.origem!=='app')return
    setReagendando({id:ev.id,data:ev.data,hora:ev.hora||'',recorrenciaId:ev.recorrenciaId})
    setDetalheEvento(null)
  }

  async function confirmarReagendar(){
    if(!reagendando)return
    const campos={data:reagendando.data,hora:reagendando.hora}
    if(reagendando.recorrenciaId){
      setEscopoPendente({acao:'editar',id:reagendando.id,campos})
      setReagendando(null)
      return
    }
    await editarEventoAgenda(reagendando.id,campos,'este')
    setReagendando(null)
    recarregar()
    if(gToken)buscarEventosGoogle(gToken)
  }

  function toggleLembrete(min:number){
    setNovo((p:any)=>({...p,lembretes:p.lembretes.includes(min)?p.lembretes.filter((x:number)=>x!==min):[...p.lembretes,min]}))
  }
  function toggleDiaSemana(dia:number){
    setNovo((p:any)=>({...p,diasSemana:p.diasSemana.includes(dia)?p.diasSemana.filter((x:number)=>x!==dia):[...p.diasSemana,dia]}))
  }

  const conflitosForm=novo.data&&novo.hora?detectarConflitosAgenda(evsByDate[novo.data]||[],novo.hora,novo.horaFim,eventoEditando?.nome):[]

  const origemLabel:Record<string,string>={app:'Denise OS',google:'Google Calendar',medicamento:'Medicamento',tirzo:'Tirzepatida'}

  function ChipEvento({e}:{e:any}){
    return(<div onClick={(ev)=>{ev.stopPropagation();abrirDetalhe(e)}} style={{fontSize:10.5,padding:'2px 4px',borderRadius:4,background:`${e.color}22`,color:e.color,marginBottom:2,overflow:'hidden',whiteSpace:'nowrap' as const,textOverflow:'ellipsis',cursor:'pointer'}}>{e.time?`${e.time} `:''}{e.title}</div>)
  }

  function renderDia(){
    const diaISO=toISO(cursor)
    const evs=evsByDate[diaISO]||[]
    return(<Card title={fmtDiaLong(cursor)}>
      {evs.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum evento neste dia.</div>}
      {evs.map((e:any,i:number)=>(<div key={i} onClick={()=>abrirDetalhe(e)} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:`1px solid ${C.line}`,alignItems:'center',cursor:'pointer'}}>
        <span style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.time}</span>
        <span style={{width:4,height:20,borderRadius:2,background:e.color,flexShrink:0}}/>
        <span style={{fontSize:13.5,flex:1}}>{e.title}</span>
        <span style={{fontSize:10,color:'rgba(255,255,255,.35)',flexShrink:0}}>{origemLabel[e.source]||''}</span>
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
            {evs.slice(0,4).map((e:any,j:number)=>(<ChipEvento key={j} e={e}/>))}
            {evs.length>4&&<div style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>+{evs.length-4} (clique pra ver todos)</div>}
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
            {evs.slice(0,2).map((e:any,j:number)=>(<div key={j} onClick={(ev)=>{ev.stopPropagation();abrirDetalhe(e)}} style={{fontSize:9.5,padding:'1px 3px',borderRadius:3,background:`${e.color}22`,color:e.color,marginBottom:1,overflow:'hidden',whiteSpace:'nowrap' as const,textOverflow:'ellipsis',cursor:'pointer'}}>{e.title}</div>))}
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
    <div style={{marginBottom:16}}>
      <input value={busca} onChange={e=>setBusca(e.target.value)} placeholder="🔎 Buscar evento por nome, local ou descrição..." style={{width:'100%',background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:13}}/>
      {buscaLower&&<div style={{marginTop:8,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',maxHeight:200,overflowY:'auto' as const}}>
        {resultadosBusca.length===0&&<div style={{fontSize:12.5,color:'rgba(255,255,255,.4)',padding:'6px 0'}}>Nada encontrado.</div>}
        {resultadosBusca.map((e:any,i:number)=>(<div key={i} onClick={()=>abrirDetalhe(e)} style={{display:'flex',gap:10,padding:'6px 0',borderBottom:i<resultadosBusca.length-1?`1px solid ${C.line}`:'none',cursor:'pointer'}}>
          <span style={{fontSize:11.5,color:'rgba(255,255,255,.4)',width:110,flexShrink:0}}>{e.date}{e.time?` · ${e.time}`:''}</span>
          <span style={{fontSize:13,color:e.color}}>{e.title}</span>
        </div>))}
      </div>}
    </div>
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
    <Card title={eventoEditando?'Editar evento':'Adicionar evento'}>
      {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>Salvo!{gToken?' (e sincronizado com o Google Calendar)':''}</div>}
      {conflitosForm.length>0&&<div style={{background:'rgba(251,191,36,.1)',border:'1px solid rgba(251,191,36,.3)',borderRadius:10,padding:'8px 12px',fontSize:12,color:C.warn,marginBottom:12}}>⚠️ Conflito de horário com: {conflitosForm.map((c:any)=>`${c.title} (${c.time}${c.timeFim&&c.timeFim!==c.time?`–${c.timeFim}`:''})`).join(', ')}</div>}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 2fr',gap:8,marginBottom:10}}>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novo.data} onChange={e=>setNovo((p:any)=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Hora</label><input type="time" value={novo.hora} onChange={e=>setNovo((p:any)=>({...p,hora:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Evento</label><input value={novo.nome} onChange={e=>setNovo((p:any)=>({...p,nome:e.target.value}))} placeholder="Ex: Célula" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
      </div>
      <button onClick={()=>setMostrarMais(m=>!m)} style={{background:'none',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'4px 0',marginBottom:10}}>{mostrarMais?'▲ Menos opções':'▼ Mais opções'}</button>
      {mostrarMais&&<div style={{marginBottom:10}}>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:8,marginBottom:10}}>
          <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Hora fim</label><input type="time" value={novo.horaFim} onChange={e=>setNovo((p:any)=>({...p,horaFim:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
          <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Categoria</label><select value={novo.categoria} onChange={e=>setNovo((p:any)=>({...p,categoria:e.target.value,cor:CATEGORIAS_AGENDA[e.target.value]?.cor||p.cor}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}>{Object.entries(CATEGORIAS_AGENDA).map(([k,v])=>(<option key={k} value={k}>{v.label}</option>))}</select></div>
          <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Cor</label><input type="color" value={novo.cor} onChange={e=>setNovo((p:any)=>({...p,cor:e.target.value}))} style={{width:'100%',height:36,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:2,cursor:'pointer'}}/></div>
        </div>
        <div style={{marginBottom:10}}><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Local</label><input value={novo.local} onChange={e=>setNovo((p:any)=>({...p,local:e.target.value}))} placeholder="Ex: Igreja" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div style={{marginBottom:10}}><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Descrição</label><input value={novo.descricao} onChange={e=>setNovo((p:any)=>({...p,descricao:e.target.value}))} placeholder="Detalhes do evento" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div style={{marginBottom:10}}>
          <label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Lembretes</label>
          <div style={{display:'flex',gap:6,flexWrap:'wrap' as const}}>
            {LEMBRETE_OPCOES.map(o=>(<button key={o.min} type="button" onClick={()=>toggleLembrete(o.min)} style={{background:novo.lembretes.includes(o.min)?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,border:`1px solid ${novo.lembretes.includes(o.min)?'transparent':C.line}`,color:'#fff',borderRadius:8,padding:'5px 10px',fontSize:11.5,cursor:'pointer'}}>{o.label}</button>))}
          </div>
        </div>
        {!eventoEditando&&<div style={{marginBottom:10}}>
          <label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Repetir</label>
          <select value={novo.repete} onChange={e=>setNovo((p:any)=>({...p,repete:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:8}}>{RECORRENCIA_OPCOES.map(o=>(<option key={o.v} value={o.v}>{o.label}</option>))}</select>
          {novo.repete==='dias_especificos'&&<div style={{display:'flex',gap:6,flexWrap:'wrap' as const,marginBottom:8}}>
            {DIAS_SEMANA_LABEL.map((lbl,dia)=>(<button key={dia} type="button" onClick={()=>toggleDiaSemana(dia)} style={{background:novo.diasSemana.includes(dia)?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,border:`1px solid ${novo.diasSemana.includes(dia)?'transparent':C.line}`,color:'#fff',borderRadius:8,padding:'5px 10px',fontSize:11.5,cursor:'pointer'}}>{lbl}</button>))}
          </div>}
          {novo.repete!=='nao'&&<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
            <div><label style={{fontSize:10.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Repetir até (opcional)</label><input type="date" value={novo.repeteAte} onChange={e=>setNovo((p:any)=>({...p,repeteAte:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
            <div><label style={{fontSize:10.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Número de ocorrências (opcional)</label><input type="number" min={1} value={novo.repeteOcorrencias} onChange={e=>setNovo((p:any)=>({...p,repeteOcorrencias:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
          </div>}
        </div>}
      </div>}
      <div style={{display:'flex',gap:8}}>
        <button onClick={salvarEvento} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>{eventoEditando?'✓ Salvar alterações':'+ Adicionar evento'}</button>
        {eventoEditando&&<button onClick={cancelarEdicao} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'11px 18px',fontSize:13,cursor:'pointer'}}>Cancelar</button>}
      </div>
    </Card>

    {detalheEvento&&<div onClick={fecharDetalhe} style={{position:'fixed' as const,inset:0,background:'rgba(0,0,0,.6)',display:'grid',placeItems:'center',zIndex:100,padding:20}}>
      <div onClick={e=>e.stopPropagation()} style={{background:C.s,border:`1px solid ${C.line}`,borderRadius:16,padding:22,maxWidth:420,width:'100%'}}>
        <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
          <span style={{width:10,height:10,borderRadius:5,background:detalheEvento.color,flexShrink:0}}/>
          <h3 style={{fontSize:16,fontWeight:800,flex:1}}>{detalheEvento.title}</h3>
        </div>
        <div style={{fontSize:12.5,color:'rgba(255,255,255,.5)',marginBottom:10}}>{origemLabel[detalheEvento.source]||''}{detalheEvento.categoria?` · ${CATEGORIAS_AGENDA[detalheEvento.categoria]?.label||detalheEvento.categoria}`:''}</div>
        <div style={{fontSize:13.5,marginBottom:6}}>📅 {detalheEvento.date}{detalheEvento.time?` · ${detalheEvento.time}${detalheEvento.timeFim&&detalheEvento.timeFim!==detalheEvento.time?`–${detalheEvento.timeFim}`:''}`:' (dia todo)'}</div>
        {detalheEvento.evento?.local&&<div style={{fontSize:13.5,marginBottom:6}}>📍 {detalheEvento.evento.local}</div>}
        {detalheEvento.evento?.descricao&&<div style={{fontSize:13,color:'rgba(255,255,255,.6)',marginBottom:6}}>{detalheEvento.evento.descricao}</div>}
        {detalheEvento.evento?.lembretes?.length>0&&<div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:10}}>🔔 {detalheEvento.evento.lembretes.map((m:number)=>LEMBRETE_OPCOES.find(o=>o.min===m)?.label||`${m} min antes`).join(', ')}</div>}
        <div style={{display:'flex',gap:8,marginTop:14,flexWrap:'wrap' as const}}>
          {detalheEvento.source==='app'&&<>
            <button onClick={()=>abrirEdicao(detalheEvento)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'10px 14px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>✏️ Editar</button>
            <button onClick={()=>abrirReagendar(detalheEvento)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'10px 14px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>📅 Reagendar</button>
            <button onClick={()=>pedirExclusao(detalheEvento)} style={{background:'rgba(248,113,113,.15)',border:'1px solid rgba(248,113,113,.3)',color:C.danger,borderRadius:10,padding:'10px 14px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>🗑️ Excluir</button>
          </>}
          <button onClick={fecharDetalhe} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'10px 16px',fontSize:12.5,cursor:'pointer'}}>Fechar</button>
        </div>
      </div>
    </div>}

    {reagendando&&<div style={{position:'fixed' as const,inset:0,background:'rgba(0,0,0,.6)',display:'grid',placeItems:'center',zIndex:105,padding:20}}>
      <div style={{background:C.s,border:`1px solid ${C.line}`,borderRadius:16,padding:22,maxWidth:340,width:'100%'}}>
        <h3 style={{fontSize:15,fontWeight:800,marginBottom:14}}>Reagendar evento</h3>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:16}}>
          <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={reagendando.data} onChange={e=>setReagendando((p:any)=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
          <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Hora</label><input type="time" value={reagendando.hora} onChange={e=>setReagendando((p:any)=>({...p,hora:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
        </div>
        <div style={{display:'flex',gap:8}}>
          <button onClick={confirmarReagendar} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Confirmar</button>
          <button onClick={()=>setReagendando(null)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'10px 16px',fontSize:13,cursor:'pointer'}}>Cancelar</button>
        </div>
      </div>
    </div>}

    {escopoPendente&&<div style={{position:'fixed' as const,inset:0,background:'rgba(0,0,0,.6)',display:'grid',placeItems:'center',zIndex:110,padding:20}}>
      <div style={{background:C.s,border:`1px solid ${C.line}`,borderRadius:16,padding:22,maxWidth:380,width:'100%'}}>
        <h3 style={{fontSize:15,fontWeight:800,marginBottom:10}}>Esse evento se repete. O que você quer {escopoPendente.acao==='editar'?'editar':'excluir'}?</h3>
        <div style={{display:'flex',flexDirection:'column' as const,gap:8}}>
          <button onClick={()=>confirmarEscopo('este')} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,cursor:'pointer'}}>Somente este evento</button>
          <button onClick={()=>confirmarEscopo('futuros')} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,cursor:'pointer'}}>Este e os próximos</button>
          <button onClick={()=>confirmarEscopo('serie')} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'10px',fontSize:13,cursor:'pointer'}}>Toda a série</button>
          <button onClick={()=>setEscopoPendente(null)} style={{background:'none',border:'none',color:'rgba(255,255,255,.4)',padding:'6px',fontSize:12.5,cursor:'pointer'}}>Cancelar</button>
        </div>
      </div>
    </div>}
  </div>)
}
function gerarId(prefixo:string){return prefixo+'_'+Date.now().toString(36)+Math.random().toString(36).slice(2,8)}

const VERSICULOS_POOL:[string,string][]=[
  ['Ensina-me a fazer a tua vontade, pois tu és o meu Deus; guie-me a tua boa vontade pela terra da retidão.','Salmos 143:10'],
  ['Tudo posso naquele que me fortalece.','Filipenses 4:13'],
  ['O Senhor é o meu pastor; nada me faltará.','Salmos 23:1'],
  ['Entrega o teu caminho ao Senhor; confia nele, e o mais ele fará.','Salmos 37:5'],
  ['Porque eu bem sei os pensamentos que penso de vós, diz o Senhor; pensamentos de paz, e não de mal, para vos dar o fim que esperais.','Jeremias 29:11'],
  ['Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus.','Isaías 41:10'],
  ['Confia no Senhor de todo o teu coração, e não te estribes no teu próprio entendimento.','Provérbios 3:5'],
  ['O Senhor é a minha luz e a minha salvação; a quem temerei?','Salmos 27:1'],
  ['Buscai primeiro o Reino de Deus, e a sua justiça, e todas estas coisas vos serão acrescentadas.','Mateus 6:33'],
  ['Alegrai-vos sempre no Senhor; outra vez digo, alegrai-vos.','Filipenses 4:4'],
  ['O Senhor é bom, um refúgio no dia da angústia; e conhece os que confiam nele.','Naum 1:7'],
  ['Ainda que eu andasse pelo vale da sombra da morte, não temeria mal algum, porque tu estás comigo.','Salmos 23:4'],
  ['Sede fortes e corajosos; não temais, nem vos atemorizeis diante deles, porque o Senhor teu Deus é o que vai contigo.','Deuteronômio 31:6'],
  ['Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei.','Mateus 11:28'],
  ['A alegria do Senhor é a vossa força.','Neemias 8:10'],
  ['Lancem sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós.','1 Pedro 5:7'],
  ['Bem-aventurados os que choram, porque eles serão consolados.','Mateus 5:4'],
  ['O Senhor está perto dos que têm o coração quebrantado, e salva os contritos de espírito.','Salmos 34:18'],
  ['Não andeis ansiosos por coisa alguma; em tudo, porém, sejam conhecidas as vossas petições diante de Deus.','Filipenses 4:6'],
  ['Aquietai-vos e sabei que eu sou Deus.','Salmos 46:10'],
  ['Deleita-te no Senhor, e ele te concederá os desejos do teu coração.','Salmos 37:4'],
  ['Porque para Deus nada é impossível.','Lucas 1:37'],
  ['O amor é sofredor, é benigno; o amor não é invejoso; o amor não trata com leviandade, não se ensoberbece.','1 Coríntios 13:4'],
  ['Graças a Deus pelo seu dom inefável!','2 Coríntios 9:15'],
  ['Este é o dia que fez o Senhor; alegremo-nos, e regozijemo-nos nele.','Salmos 118:24'],
  ['Não vos inquieteis, pois, pelo dia de amanhã, porque o dia de amanhã cuidará de si mesmo.','Mateus 6:34'],
  ['Perto está o Senhor de todos os que o invocam, de todos os que o invocam em verdade.','Salmos 145:18'],
  ['Sede fortes, e esforce-se o vosso coração, vós todos que esperais no Senhor.','Salmos 31:24'],
  ['Porque eu, o Senhor teu Deus, te tomo pela tua mão direita e te digo: não temas, eu te ajudo.','Isaías 41:13'],
  ['Tudo o que fizerem, façam de todo o coração, como para o Senhor, e não para os homens.','Colossenses 3:23'],
  ['O Senhor é o meu rochedo, a minha fortaleza e o meu libertador.','Salmos 18:2'],
  ['Ele dá força ao cansado e multiplica as forças ao que não tem nenhum vigor.','Isaías 40:29'],
  ['Porque a palavra de Deus é viva, e eficaz, e mais penetrante do que espada alguma de dois gumes.','Hebreus 4:12'],
  ['Mas os que esperam no Senhor renovarão as suas forças; subirão com asas como águias.','Isaías 40:31'],
  ['Fiel é Deus, pelo qual fostes chamados para a comunhão de seu Filho Jesus Cristo, nosso Senhor.','1 Coríntios 1:9'],
  ['O amor de Deus é derramado em nossos corações pelo Espírito Santo que nos foi dado.','Romanos 5:5'],
  ['Sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus.','Romanos 8:28'],
  ['Se Deus é por nós, quem será contra nós?','Romanos 8:31'],
  ['O justo florescerá como a palmeira; crescerá como o cedro no Líbano.','Salmos 92:12'],
  ['Serena a tua alma, e ela há de ser doce como o mel, diz o Senhor.','Provérbios 24:14'],
]
function versiculoDoDia():{texto:string,ref:string}{
  const iso=isoBR(new Date())
  const dias=Math.floor(new Date(iso+'T00:00:00Z').getTime()/86400000)
  const idx=((dias%VERSICULOS_POOL.length)+VERSICULOS_POOL.length)%VERSICULOS_POOL.length
  const [texto,ref]=VERSICULOS_POOL[idx]
  return {texto,ref}
}

function lerDevocionais():any[]{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}}
function calcularSequenciaDevocional(entries:any[]):number{
  const dias=new Set(entries.map((e:any)=>e.data))
  let seq=0
  const cursor=new Date()
  const hoje=isoBR(cursor)
  if(!dias.has(hoje))cursor.setDate(cursor.getDate()-1)
  while(dias.has(isoBR(cursor))){seq++;cursor.setDate(cursor.getDate()-1)}
  return seq
}
function calcularMelhorSequenciaDevocional(entries:any[]):number{
  const dias=Array.from(new Set(entries.map((e:any)=>e.data))).sort()
  let melhor=0,atual=0,anterior:string|null=null
  dias.forEach(d=>{
    if(anterior){
      const diff=Math.round((new Date(d+'T12:00:00').getTime()-new Date(anterior+'T12:00:00').getTime())/86400000)
      atual=diff===1?atual+1:1
    }else atual=1
    melhor=Math.max(melhor,atual)
    anterior=d
  })
  return melhor
}

function lerPedidosOracao():any[]{try{return JSON.parse(localStorage.getItem('dos_pedidos_oracao')||'[]')}catch{return []}}
function salvarPedidosOracao(lista:any[]){localStorage.setItem('dos_pedidos_oracao',JSON.stringify(lista))}

function lerPlanosLeituraBiblia():any[]{try{return JSON.parse(localStorage.getItem('dos_planos_biblia')||'[]')}catch{return []}}
function salvarPlanosLeituraBiblia(lista:any[]){localStorage.setItem('dos_planos_biblia',JSON.stringify(lista))}

const MESES_ABREV_PT=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
const DIAS_SEMANA_ABREV_PT=['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']
function construirHeatmapAno(ano:number){
  const inicio=new Date(ano,0,1)
  const fim=new Date(ano,11,31)
  const diaSemanaInicio=(inicio.getDay()+6)%7
  const cursor=new Date(inicio)
  cursor.setDate(cursor.getDate()-diaSemanaInicio)
  const semanas:{data:string,mes:number}[][]=[]
  const mesesLabel:{mes:number,col:number}[]=[]
  let ultimoMes=-1
  let col=0
  while(cursor<=fim){
    const semana:{data:string,mes:number}[]=[]
    for(let d=0;d<7;d++){
      semana.push({data:toISOAg(cursor),mes:cursor.getMonth()})
      cursor.setDate(cursor.getDate()+1)
    }
    if(semana[0].mes!==ultimoMes){mesesLabel.push({mes:semana[0].mes,col});ultimoMes=semana[0].mes}
    semanas.push(semana)
    col++
  }
  return {semanas,mesesLabel}
}

function Espiritual(){
  const PERGUNTAS_VAZIAS={mandamento:'',promessa:'',pecado:'',aplicacao:'',novoDeus:'',quem:'',oque:'',quando:'',onde:'',porque:''}
  const [ref,setRef]=React.useState('')
  const [perguntas,setPerguntas]=React.useState(PERGUNTAS_VAZIAS)
  const [grat,setGrat]=React.useState('')
  const [apren,setApren]=React.useState('')
  const [saved,setSaved]=React.useState(false)
  const [expandido,setExpandido]=React.useState<number|null>(null)
  const [entries,setEntries]=React.useState<any[]>(()=>lerDevocionais())
  const [buscaDevoc,setBuscaDevoc]=React.useState('')
  const [filtroMes,setFiltroMes]=React.useState('')
  const [filtroPeriodo,setFiltroPeriodo]=React.useState<'todos'|'30'|'90'|'ano'>('todos')
  const [pedidos,setPedidos]=React.useState<any[]>(()=>lerPedidosOracao())
  const [novoPedido,setNovoPedido]=React.useState({pedido:'',pessoaTema:'',data:'',observacoes:''})
  const [respondendoId,setRespondendoId]=React.useState<string|null>(null)
  const [respostaForm,setRespostaForm]=React.useState({dataResposta:'',testemunho:''})
  const [planos,setPlanos]=React.useState<any[]>(()=>lerPlanosLeituraBiblia())
  const [mostrarNovoPlano,setMostrarNovoPlano]=React.useState(false)
  const [novoPlanoNome,setNovoPlanoNome]=React.useState('')
  const [novoPlanoTotal,setNovoPlanoTotal]=React.useState('')
  const [planoExpandidoId,setPlanoExpandidoId]=React.useState<string|null>(null)
  const [mostrarNovoPedido,setMostrarNovoPedido]=React.useState(false)
  const [pedidoMenuId,setPedidoMenuId]=React.useState<string|null>(null)
  const [mostrarTodosPedidos,setMostrarTodosPedidos]=React.useState(false)
  const [mostrarTodosDevocionais,setMostrarTodosDevocionais]=React.useState(false)
  function isoHoje(){return isoBR(new Date())}
  function setPergunta(campo:string,valor:string){setPerguntas(p=>({...p,[campo]:valor}))}
  function salvar(){
    const hoje=isoHoje()
    const reg={data:hoje,horario:new Date().toTimeString().slice(0,5),pessoa:'denise',ref,...perguntas,grat,apren}
    const outros=entries.filter((e:any)=>e.data!==hoje)
    const n=[reg,...outros].sort((a:any,b:any)=>b.data.localeCompare(a.data))
    setEntries(n);localStorage.setItem('dos_devocionais',JSON.stringify(n))
    setSaved(true);setPerguntas(PERGUNTAS_VAZIAS);setRef('');setGrat('');setApren('')
  }
  const sequencia=calcularSequenciaDevocional(entries)
  const melhorSequencia=calcularMelhorSequenciaDevocional(entries)
  const anoNum=new Date().getFullYear()
  const anoAtual=String(anoNum)
  const diasNoAno=entries.filter((e:any)=>e.data.startsWith(anoAtual)).length
  const diasNoAnoTotal=((anoNum%4===0&&anoNum%100!==0)||anoNum%400===0)?366:365
  const {texto:versTexto,ref:versRef}=versiculoDoDia()
  const diasComDevSet=new Set(entries.map((e:any)=>e.data))
  const {semanas:heatmapSemanas,mesesLabel:heatmapMeses}=construirHeatmapAno(anoNum)

  const mesesDisponiveis=Array.from(new Set(entries.map((e:any)=>e.data.slice(0,7)))).sort().reverse()
  const limitePeriodo=filtroPeriodo==='30'?isoBR(new Date(Date.now()-30*86400000)):filtroPeriodo==='90'?isoBR(new Date(Date.now()-90*86400000)):filtroPeriodo==='ano'?`${anoAtual}-01-01`:null
  const buscaLower=buscaDevoc.trim().toLowerCase()
  const entriesFiltradas=entries.filter((e:any)=>{
    if(filtroMes&&!e.data.startsWith(filtroMes))return false
    if(limitePeriodo&&e.data<limitePeriodo)return false
    if(buscaLower){
      const alvo=[e.ref,e.apren,e.grat,e.mandamento,e.promessa,e.pecado,e.aplicacao,e.novoDeus].filter(Boolean).join(' ').toLowerCase()
      if(!alvo.includes(buscaLower))return false
    }
    return true
  }).sort((a:any,b:any)=>b.data.localeCompare(a.data))

  function salvarPedidosLocal(lista:any[]){setPedidos(lista);salvarPedidosOracao(lista)}
  function addPedido(){
    if(!novoPedido.pedido.trim())return
    const novo={id:gerarId('oracao'),pedido:novoPedido.pedido.trim(),pessoaTema:novoPedido.pessoaTema,data:novoPedido.data||isoHoje(),observacoes:novoPedido.observacoes,status:'em_oracao',dataResposta:'',testemunho:''}
    salvarPedidosLocal([novo,...pedidos])
    setNovoPedido({pedido:'',pessoaTema:'',data:'',observacoes:''})
  }
  function abrirResposta(id:string){setRespondendoId(id);setRespostaForm({dataResposta:isoHoje(),testemunho:''})}
  function confirmarResposta(){
    if(!respondendoId)return
    salvarPedidosLocal(pedidos.map((p:any)=>p.id===respondendoId?{...p,status:'respondida',dataResposta:respostaForm.dataResposta,testemunho:respostaForm.testemunho}:p))
    setRespondendoId(null)
  }
  const pedidosOrdenados=[...pedidos].sort((a:any,b:any)=>b.data.localeCompare(a.data))
  const pedidosPreview=mostrarTodosPedidos?pedidosOrdenados:pedidosOrdenados.slice(0,3)

  function salvarPlanosLocal(lista:any[]){setPlanos(lista);salvarPlanosLeituraBiblia(lista)}
  function addPlano(){
    if(!novoPlanoNome.trim()||!novoPlanoTotal)return
    const novo={id:gerarId('plano'),nome:novoPlanoNome.trim(),total:Number(novoPlanoTotal)||0,concluidas:0,leituraAtual:'',historico:[]}
    salvarPlanosLocal([...planos,novo])
    setNovoPlanoNome('');setNovoPlanoTotal('');setMostrarNovoPlano(false)
  }
  function atualizarLeituraAtual(id:string,texto:string){
    salvarPlanosLocal(planos.map((p:any)=>p.id===id?{...p,leituraAtual:texto}:p))
  }
  function concluirLeitura(id:string){
    const p=planos.find((pl:any)=>pl.id===id)
    if(!p||!p.leituraAtual.trim())return
    const historico=[{data:isoHoje(),texto:p.leituraAtual},...(p.historico||[])]
    salvarPlanosLocal(planos.map((pl:any)=>pl.id===id?{...pl,concluidas:pl.concluidas+1,historico,leituraAtual:''}:pl))
  }

  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Espiritual</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Devocional diário · Conecte-se com Deus todos os dias</p>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginBottom:16}}>
      <Card title="Devocional de hoje">
        {saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Devocional salvo!</div>}
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Referência bíblica</label>
        <input value={ref} onChange={e=>setRef(e.target.value)} placeholder="Ex: Salmos 143:10" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        {([
          ['mandamento','Existe um mandamento a obedecer?'],
          ['promessa','Uma promessa a reivindicar?'],
          ['pecado','Um pecado a evitar?'],
          ['aplicacao','Uma aplicação a fazer?'],
          ['novoDeus','Algo novo sobre Deus?'],
        ] as [string,string][]).map(([campo,label])=>(
          <div key={campo} style={{marginBottom:10}}>
            <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>{label}</label>
            <input value={(perguntas as any)[campo]} onChange={e=>setPergunta(campo,e.target.value)} placeholder="..." style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:13.5}}/>
          </div>
        ))}
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Gratidão</label>
        <input value={grat} onChange={e=>setGrat(e.target.value)} placeholder="Sou grata por…" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Aprendizado</label>
        <input value={apren} onChange={e=>setApren(e.target.value)} placeholder="O que levo pro dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/>
        <button onClick={salvar} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Salvar devocional</button>
      </Card>
      <div>
        <Card title="📈 Consistência espiritual">
          {entries.length===0?<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum devocional registrado ainda.</div>:<>
            <div style={{display:'flex',gap:28,marginBottom:16}}>
              <div><div style={{fontSize:24,fontWeight:800}}>{diasNoAno}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)',lineHeight:1.35}}>Dias com devocional<br/>/ {diasNoAnoTotal}</div></div>
              <div><div style={{fontSize:24,fontWeight:800}}>{sequencia}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)',lineHeight:1.35}}>Sequência atual<br/>dias</div></div>
              <div><div style={{fontSize:24,fontWeight:800}}>{melhorSequencia}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)',lineHeight:1.35}}>Melhor sequência<br/>dias</div></div>
            </div>
            <div style={{overflowX:'auto' as const}}>
              <div style={{position:'relative' as const,width:24+heatmapSemanas.length*12,height:14}}>
                {heatmapMeses.map((m,i)=>(<span key={i} style={{position:'absolute' as const,left:24+m.col*12,top:0,fontSize:9,color:'rgba(255,255,255,.4)'}}>{MESES_ABREV_PT[m.mes]}</span>))}
              </div>
              <div style={{display:'flex',gap:2}}>
                <div style={{display:'flex',flexDirection:'column' as const,gap:2,width:22,flexShrink:0}}>
                  {DIAS_SEMANA_ABREV_PT.map((d,i)=>(<div key={i} style={{height:10,fontSize:8,color:'rgba(255,255,255,.35)',display:'flex',alignItems:'center'}}>{d[0]}</div>))}
                </div>
                <div style={{display:'flex',gap:2}}>
                  {heatmapSemanas.map((semana,si)=>(<div key={si} style={{display:'flex',flexDirection:'column' as const,gap:2}}>
                    {semana.map((dia,di)=>{
                      const feito=diasComDevSet.has(dia.data)
                      const hoje=dia.data===isoHoje()
                      const futuro=dia.data>isoHoje()
                      return(<div key={di} title={`${dia.data}${feito?' · devocional feito':''}`} style={{width:10,height:10,borderRadius:2,background:futuro?'transparent':feito?C.acc2:C.s3,border:hoje?`1px solid ${C.acc}`:'none'}}/>)
                    })}
                  </div>))}
                </div>
              </div>
              <div style={{display:'flex',gap:14,marginTop:10,fontSize:10.5,color:'rgba(255,255,255,.4)',flexWrap:'wrap' as const}}>
                <span style={{display:'flex',alignItems:'center',gap:5}}><span style={{width:9,height:9,borderRadius:2,background:C.acc2,display:'inline-block'}}/>Devocional feito</span>
                <span style={{display:'flex',alignItems:'center',gap:5}}><span style={{width:9,height:9,borderRadius:2,background:C.s3,display:'inline-block'}}/>Não feito</span>
                <span style={{display:'flex',alignItems:'center',gap:5}}><span style={{width:9,height:9,borderRadius:2,border:`1px solid ${C.acc}`,display:'inline-block'}}/>Hoje</span>
              </div>
            </div>
          </>}
        </Card>
        <div style={{marginTop:16}}><Card title="⭐ Versículo do dia"><p style={{fontSize:13,fontStyle:'italic',lineHeight:1.6}}>"{versTexto}"</p><span style={{fontSize:12,color:C.acc2}}>{versRef}</span></Card></div>
        <div style={{marginTop:16}}><Card title="📖 Plano de leitura bíblica" action={planos.length>0?<button onClick={()=>setPlanoExpandidoId(id=>id?null:planos[0].id)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Ver plano</button>:undefined}>
          {planos.length===0&&!mostrarNovoPlano&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'6px 0 12px'}}>Nenhum plano de leitura cadastrado ainda.</div>}
          {planos.map((p:any)=>{
            const pct=p.total>0?Math.min(100,Math.round(p.concluidas/p.total*100)):0
            return(<div key={p.id} style={{marginBottom:14,paddingBottom:14,borderBottom:`1px solid ${C.line}`}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline',fontSize:13,fontWeight:700,marginBottom:6}}><span>{p.nome}</span><span style={{color:C.acc2}}>{pct}%</span></div>
              <div style={{height:8,borderRadius:5,background:C.s3,overflow:'hidden',marginBottom:12}}><div style={{height:'100%',width:`${pct}%`,borderRadius:5,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Leitura de hoje</div>
              <input value={p.leituraAtual} onChange={e=>atualizarLeituraAtual(p.id,e.target.value)} placeholder="Ex: Salmos 90–92" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:15,fontWeight:700,marginBottom:10}}/>
              <div style={{display:'flex',justifyContent:'flex-end'}}>
                <button onClick={()=>concluirLeitura(p.id)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:20,padding:'8px 16px',fontSize:12,fontWeight:700,cursor:'pointer'}}>📝 Marcar como concluída</button>
              </div>
              {planoExpandidoId===p.id&&<div style={{marginTop:12,paddingTop:12,borderTop:`1px solid ${C.line}`}}>
                <div style={{fontSize:11.5,fontWeight:700,color:'rgba(255,255,255,.6)',marginBottom:6}}>Histórico de leituras</div>
                {(!p.historico||p.historico.length===0)&&<div style={{fontSize:12,color:'rgba(255,255,255,.3)'}}>Nenhuma leitura concluída ainda.</div>}
                {(p.historico||[]).slice(0,20).map((h:any,hi:number)=>(<div key={hi} style={{display:'flex',justifyContent:'space-between',fontSize:12,padding:'5px 0',borderBottom:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)'}}><span>{h.texto}</span><span style={{color:'rgba(255,255,255,.4)'}}>{h.data}</span></div>))}
              </div>}
            </div>)
          })}
          {mostrarNovoPlano?<div>
            <input value={novoPlanoNome} onChange={e=>setNovoPlanoNome(e.target.value)} placeholder="Nome do plano (ex: Bíblia em 1 ano)" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:13,marginBottom:8}}/>
            <input type="number" value={novoPlanoTotal} onChange={e=>setNovoPlanoTotal(e.target.value)} placeholder="Total de leituras (ex: 365)" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:13,marginBottom:8}}/>
            <div style={{display:'flex',gap:8}}>
              <button onClick={addPlano} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'8px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>Criar</button>
              <button onClick={()=>setMostrarNovoPlano(false)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'8px 12px',fontSize:12.5,cursor:'pointer'}}>Cancelar</button>
            </div>
          </div>:<button onClick={()=>setMostrarNovoPlano(true)} style={{width:'100%',background:'transparent',border:`1px dashed ${C.line}`,color:C.acc2,borderRadius:9,padding:'8px',fontSize:12,fontWeight:600,cursor:'pointer'}}>+ Novo plano</button>}
        </Card></div>
      </div>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="🙏 Pedidos de oração" action={<button onClick={()=>setMostrarNovoPedido(m=>!m)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>{mostrarNovoPedido?'Cancelar':'+ Novo pedido'}</button>}>
        {mostrarNovoPedido&&<div style={{marginBottom:14,paddingBottom:14,borderBottom:`1px solid ${C.line}`}}>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:8}}>
            <input value={novoPedido.pedido} onChange={e=>setNovoPedido(p=>({...p,pedido:e.target.value}))} placeholder="Pedido" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:13}}/>
            <input value={novoPedido.pessoaTema} onChange={e=>setNovoPedido(p=>({...p,pessoaTema:e.target.value}))} placeholder="Pessoa/tema" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:13}}/>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 2fr',gap:8,marginBottom:8}}>
            <input type="date" value={novoPedido.data} onChange={e=>setNovoPedido(p=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/>
            <input value={novoPedido.observacoes} onChange={e=>setNovoPedido(p=>({...p,observacoes:e.target.value}))} placeholder="Observações" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:13}}/>
          </div>
          <button onClick={()=>{addPedido();setMostrarNovoPedido(false)}} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar pedido</button>
        </div>}
        {pedidos.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum pedido de oração registrado ainda.</div>}
        {pedidosPreview.map((p:any)=>(<div key={p.id}>
          <div style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`}}>
            <Avatar id={p.id} label={(p.pessoaTema||p.pedido||'?')[0].toUpperCase()} size={34} radius={10}/>
            <div style={{flex:1,minWidth:0}}>
              <div style={{fontWeight:700,fontSize:12.5,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' as const}}>{p.pedido}</div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{p.pessoaTema?`${p.pessoaTema} · `:''}{p.data}</div>
            </div>
            <span style={{fontSize:10.5,fontWeight:700,color:p.status==='respondida'?C.acc2:C.ok,background:p.status==='respondida'?'rgba(167,139,250,.15)':'rgba(52,211,153,.15)',padding:'3px 9px',borderRadius:20,flexShrink:0}}>{p.status==='respondida'?'Respondida':'Em oração'}</span>
            <button onClick={()=>setPedidoMenuId(id=>id===p.id?null:p.id)} style={{background:'none',border:'none',color:'rgba(255,255,255,.4)',cursor:'pointer',fontSize:16,padding:'0 4px',flexShrink:0}}>⋮</button>
          </div>
          {pedidoMenuId===p.id&&<div style={{background:C.s2,borderRadius:9,padding:10,marginBottom:8}}>
            {p.observacoes&&<div style={{fontSize:11.5,color:'rgba(255,255,255,.5)',marginBottom:6}}>{p.observacoes}</div>}
            {p.status==='respondida'?<>
              <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Respondida em {p.dataResposta}</div>
              {p.testemunho&&<div style={{fontSize:12,color:'rgba(255,255,255,.6)'}}>{p.testemunho}</div>}
            </>:respondendoId===p.id?<>
              <label style={{fontSize:10.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:3}}>Data da resposta</label>
              <input type="date" value={respostaForm.dataResposta} onChange={e=>setRespostaForm(f=>({...f,dataResposta:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'6px 8px',color:'#fff',fontSize:12,marginBottom:6,colorScheme:'dark'}}/>
              <label style={{fontSize:10.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:3}}>Testemunho</label>
              <input value={respostaForm.testemunho} onChange={e=>setRespostaForm(f=>({...f,testemunho:e.target.value}))} placeholder="Como Deus respondeu" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'6px 8px',color:'#fff',fontSize:12,marginBottom:8}}/>
              <div style={{display:'flex',gap:6}}>
                <button onClick={()=>{confirmarResposta();setPedidoMenuId(null)}} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:7,padding:'6px',fontSize:11.5,fontWeight:700,cursor:'pointer'}}>Confirmar</button>
                <button onClick={()=>{setRespondendoId(null);setPedidoMenuId(null)}} style={{background:C.s3,border:'none',color:'#fff',borderRadius:7,padding:'6px 10px',fontSize:11.5,cursor:'pointer'}}>Cancelar</button>
              </div>
            </>:<button onClick={()=>abrirResposta(p.id)} style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',color:C.ok,borderRadius:7,padding:'5px 10px',fontSize:11.5,cursor:'pointer'}}>✓ Marcar como respondida</button>}
          </div>}
        </div>))}
        {pedidosOrdenados.length>3&&<div onClick={()=>setMostrarTodosPedidos(m=>!m)} style={{textAlign:'center' as const,fontSize:12,color:C.acc2,cursor:'pointer',marginTop:10}}>{mostrarTodosPedidos?'Ver menos':'Ver todos os pedidos'}</div>}
      </Card>

      <Card title="Meus devocionais">
        <div style={{display:'flex',gap:8,marginBottom:10,flexWrap:'wrap' as const}}>
          <input value={buscaDevoc} onChange={e=>setBuscaDevoc(e.target.value)} placeholder="🔎 Buscar..." style={{flex:1,minWidth:120,background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:9,padding:'7px 10px',color:'#fff',fontSize:12.5}}/>
          <select value={filtroMes} onChange={e=>setFiltroMes(e.target.value)} style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:9,padding:'7px 8px',color:'#fff',fontSize:12}}>
            <option value="">Todos os meses</option>
            {mesesDisponiveis.map(m=>(<option key={m} value={m}>{m}</option>))}
          </select>
          <select value={filtroPeriodo} onChange={e=>setFiltroPeriodo(e.target.value as any)} style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:9,padding:'7px 8px',color:'#fff',fontSize:12}}>
            <option value="todos">Todo período</option>
            <option value="30">Últimos 30 dias</option>
            <option value="90">Últimos 90 dias</option>
            <option value="ano">Este ano</option>
          </select>
        </div>
        {entries.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum devocional registrado ainda.</div>}
        {entries.length>0&&entriesFiltradas.length===0&&<div style={{fontSize:12.5,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nada encontrado com esses filtros.</div>}
        <div style={{maxHeight:mostrarTodosDevocionais?400:'none',overflowY:mostrarTodosDevocionais?'auto' as const:'visible' as const}}>
          {(mostrarTodosDevocionais?entriesFiltradas:entriesFiltradas.slice(0,4)).map((e:any,i:number)=>(<div key={i} style={{padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
            <div onClick={()=>setExpandido(x=>x===i?null:i)} style={{display:'flex',alignItems:'center',gap:8,marginBottom:2,cursor:'pointer'}}>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontWeight:700,fontSize:12.5,color:C.acc2}}>{e.ref||'—'}</div>
                <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{e.data}{e.apren?` · ${e.apren}`:''}</div>
              </div>
              <span style={{fontSize:14,color:'rgba(255,255,255,.3)',transform:expandido===i?'rotate(90deg)':'none',transition:'transform .15s',flexShrink:0}}>›</span>
            </div>
            {expandido===i&&<div style={{marginTop:8,fontSize:11.5,color:'rgba(255,255,255,.6)',display:'grid',gap:5}}>
              {e.mandamento&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Mandamento a obedecer:</b> {e.mandamento}</div>}
              {e.promessa&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Promessa a reivindicar:</b> {e.promessa}</div>}
              {e.pecado&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Pecado a evitar:</b> {e.pecado}</div>}
              {e.aplicacao&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Aplicação a fazer:</b> {e.aplicacao}</div>}
              {e.novoDeus&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Algo novo sobre Deus:</b> {e.novoDeus}</div>}
              {e.grat&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Gratidão:</b> {e.grat}</div>}
              {e.quem&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Quem:</b> {e.quem}</div>}
              {e.oque&&<div><b style={{color:'rgba(255,255,255,.4)'}}>O quê:</b> {e.oque}</div>}
              {e.quando&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Quando:</b> {e.quando}</div>}
              {e.onde&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Onde:</b> {e.onde}</div>}
              {e.porque&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Por quê:</b> {e.porque}</div>}
              {e.reflex&&<div><b style={{color:'rgba(255,255,255,.4)'}}>Reflexão (registro antigo):</b> {e.reflex}</div>}
              {e.horario&&<div style={{color:'rgba(255,255,255,.35)'}}>Registrado às {e.horario}</div>}
            </div>}
          </div>))}
        </div>
        {entriesFiltradas.length>4&&<div onClick={()=>setMostrarTodosDevocionais(m=>!m)} style={{textAlign:'center' as const,fontSize:12,color:C.acc2,cursor:'pointer',marginTop:10}}>{mostrarTodosDevocionais?'Ver menos':'Ver todos os devocionais'}</div>}
      </Card>
    </div>
  </div>)
}
function lerLogMarcador(chave:string):Record<string,string>{try{return JSON.parse(localStorage.getItem(chave)||'{}')}catch{return {}}}
function marcarHoje(chave:string,setState:(v:Record<string,string>)=>void){
  const log=lerLogMarcador(chave)
  const hoje=isoBR(new Date())
  const n={...log,[hoje]:new Date().toTimeString().slice(0,5)}
  localStorage.setItem(chave,JSON.stringify(n));setState(n)
}
function classificarIMC(imc:number){
  if(!imc)return {label:'—',cor:'rgba(255,255,255,.4)'}
  if(imc<18.5)return {label:'Abaixo do peso',cor:C.warn}
  if(imc<25)return {label:'Saudável',cor:C.ok}
  if(imc<30)return {label:'Sobrepeso',cor:C.warn}
  return {label:'Atenção',cor:C.danger}
}
function deltaInfo(atual:number|null|undefined,anterior:number|null|undefined,casas=1,unidade=''){
  if(atual==null||anterior==null||!isFinite(atual)||!isFinite(anterior))return null
  const dif=Math.round((atual-anterior)*Math.pow(10,casas))/Math.pow(10,casas)
  if(dif===0)return {texto:`Estável`,cor:'rgba(255,255,255,.4)',seta:'▬'}
  const sinal=dif>0?'▲':'▼'
  return {texto:`${sinal} ${Math.abs(dif).toFixed(casas).replace('.',',')}${unidade}`,cor:dif>0?C.danger:C.ok,seta:sinal}
}
function paraDataAproxDDMM(ddmm:string,anoPadrao:number){
  const m=/^(\d{2})\/(\d{2})$/.exec(ddmm)
  if(!m)return null
  const hojeStr=isoBR(new Date())
  const candAtual=`${anoPadrao}-${m[2]}-${m[1]}`
  return candAtual<=hojeStr?candAtual:`${anoPadrao-1}-${m[2]}-${m[1]}`
}
function DonutComposicao({segmentos,centroValor,centroLabel}:{segmentos:{valor:number,cor:string,label:string}[],centroValor:string,centroLabel:string}){
  const total=segmentos.reduce((a,s)=>a+s.valor,0)
  if(total<=0)return <div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0'}}>Sem dados suficientes ainda.</div>
  let acc=0
  const stops=segmentos.map(s=>{const de=acc/total*360;acc+=s.valor;const ate=acc/total*360;return `${s.cor} ${de}deg ${ate}deg`}).join(',')
  return(<div style={{display:'flex',alignItems:'center',gap:18,flexWrap:'wrap' as const}}>
    <div style={{width:132,height:132,borderRadius:'50%',background:`conic-gradient(${stops})`,position:'relative' as const,flexShrink:0}}>
      <div style={{position:'absolute' as const,inset:18,borderRadius:'50%',background:'#131320',display:'flex',flexDirection:'column' as const,alignItems:'center',justifyContent:'center'}}>
        <div style={{fontSize:15,fontWeight:800}}>{centroValor}</div>
        <div style={{fontSize:9.5,color:'rgba(255,255,255,.4)'}}>{centroLabel}</div>
      </div>
    </div>
    <div style={{flex:1,minWidth:120}}>
      {segmentos.map(s=>(<div key={s.label} style={{display:'flex',alignItems:'center',gap:8,padding:'5px 0'}}>
        <span style={{width:9,height:9,borderRadius:3,background:s.cor,flexShrink:0}}/>
        <span style={{flex:1,fontSize:12.5,color:'rgba(255,255,255,.7)'}}>{s.label}</span>
        <span style={{fontSize:12.5,fontWeight:700}}>{s.valor.toFixed(1)}kg</span>
        <span style={{fontSize:11,color:'rgba(255,255,255,.4)',width:38,textAlign:'right' as const}}>{Math.round(s.valor/total*100)}%</span>
      </div>))}
    </div>
  </div>)
}
function LinhaEvolucao({pontos,cor,unidade='kg',rotulo='Peso atual'}:{pontos:{iso:string,valor:number}[],cor:string,unidade?:string,rotulo?:string}){
  if(pontos.length===0)return <div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'30px 0',textAlign:'center' as const}}>Nenhum registro no período selecionado.</div>
  const fmt=(v:number)=>Number.isInteger(v)?String(v):v.toFixed(1).replace('.',',')
  if(pontos.length===1)return(<div style={{padding:'20px 0'}}><div style={{fontSize:24,fontWeight:800}}>{fmt(pontos[0].valor)}{unidade}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Único registro no período · {new Date(pontos[0].iso+'T12:00:00').toLocaleDateString('pt-BR')}</div></div>)
  const vals=pontos.map(p=>p.valor)
  const mnRaw=Math.min(...vals),mxRaw=Math.max(...vals)
  const folga=(mxRaw-mnRaw||1)*0.12
  const mn=mnRaw-folga,mx=mxRaw+folga
  const range=mx-mn||1
  const W=600,H=150,pad=8
  const xy=pontos.map((p,i)=>{const x=pad+(i/(pontos.length-1))*(W-pad*2);const y=H-pad-((p.valor-mn)/range)*(H-pad*2);return [x,y]})
  const atual=pontos[pontos.length-1].valor
  const eixoY=[mx,mn+range*0.75,mn+range*0.5,mn+range*0.25,mn]
  const qtdLabelsX=Math.min(5,pontos.length)
  const idxLabelsX=Array.from({length:qtdLabelsX},(_,i)=>Math.round(i*(pontos.length-1)/(qtdLabelsX-1||1)))
  return(<div>
    <div style={{display:'flex',justifyContent:'flex-end',marginBottom:4}}>
      <div style={{textAlign:'right' as const}}>
        <div style={{fontSize:16,fontWeight:800}}>{fmt(atual)} {unidade}</div>
        <div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>{rotulo}</div>
      </div>
    </div>
    <div style={{display:'flex',gap:6}}>
      <div style={{display:'flex',flexDirection:'column' as const,justifyContent:'space-between',fontSize:10,color:'rgba(255,255,255,.35)',paddingBottom:18,textAlign:'right' as const,minWidth:30}}>
        {eixoY.map((v,i)=>(<span key={i}>{fmt(v)}</span>))}
      </div>
      <div style={{flex:1,minWidth:0}}>
        <svg viewBox={`0 0 ${W} ${H}`} style={{width:'100%',height:140,display:'block'}} preserveAspectRatio="none">
          {[0,0.25,0.5,0.75,1].map((f,i)=>(<line key={i} x1={0} x2={W} y1={H-pad-f*(H-pad*2)} y2={H-pad-f*(H-pad*2)} stroke="rgba(255,255,255,.06)" strokeWidth={1}/>))}
          <polyline points={xy.map(([x,y])=>`${x},${y}`).join(' ')} fill="none" stroke={cor} strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round"/>
          {xy.map(([x,y],i)=>(<circle key={i} cx={x} cy={y} r={i===xy.length-1?4:2} fill={cor}/>))}
        </svg>
        <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)',marginTop:6}}>
          {idxLabelsX.map((idx,i)=>(<span key={i}>{new Date(pontos[idx].iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>))}
        </div>
      </div>
    </div>
    <div style={{textAlign:'center' as const,fontSize:11,color:'rgba(255,255,255,.4)',marginTop:8}}>
      <span style={{display:'inline-flex',alignItems:'center',gap:5}}><span style={{width:14,height:2,background:cor,display:'inline-block'}}/>{rotulo==='Peso atual'?'Peso':rotulo} ({unidade})</span>
    </div>
  </div>)
}
function IndicadorCard({label,valor,delta,badge,sub}:{label:string,valor:string|number,delta?:{texto:string,cor:string}|null,badge?:{label:string,cor:string},sub?:string}){
  return(<div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14,minWidth:0}}>
    <div style={{fontSize:19,fontWeight:800,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' as const}}>{valor}</div>
    <div style={{fontSize:11.5,color:'rgba(255,255,255,.4)',marginTop:2}}>{label}</div>
    {badge&&<span style={{display:'inline-block',fontSize:10,fontWeight:700,color:badge.cor,background:`${badge.cor}22`,padding:'2px 7px',borderRadius:20,marginTop:4}}>{badge.label}</span>}
    {delta&&<div style={{fontSize:10.5,color:delta.cor,marginTop:3}}>{delta.texto}</div>}
    {sub&&<div style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginTop:3}}>{sub}</div>}
  </div>)
}
const acaoBtnStyle:React.CSSProperties={background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'10px 6px',fontSize:11.5,fontWeight:600,cursor:'pointer',textAlign:'center' as const}
type SRegQuick={data:string,peso:number,imc:number,gordura:number,humor:number,energia:number,intestino:string,sint:string,sono?:number}
function registrarCampoRapido(
  pessoa:'denise'|'flavio',
  campo:'peso'|'humor'|'energia'|'intestino'|'sono',
  rotulo:string,
  lista:SRegQuick[],
  setLista:(n:SRegQuick[])=>void,
){
  const valor=window.prompt(rotulo)
  if(valor===null||valor.trim()==='')return
  const chave=pessoa==='denise'?'dos_saude_extra':'dos_saude_extra_flavio'
  const hojeStr=new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})
  const idx=lista.findIndex(r=>r.data===hojeStr)
  const base:SRegQuick=idx>=0?{...lista[idx]}:{data:hojeStr,peso:0,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:'',sono:0}
  if(campo==='peso'){base.peso=Number(valor.replace(',','.'))||0;if(pessoa==='denise')base.imc=Number((base.peso/(1.63**2)).toFixed(1))}
  if(campo==='humor')base.humor=Number(valor)||0
  if(campo==='energia')base.energia=Number(valor)||0
  if(campo==='intestino')base.intestino=valor
  if(campo==='sono')base.sono=Number(valor.replace(',','.'))||0
  const n=idx>=0?lista.map((r,i)=>i===idx?base:r):[base,...lista]
  setLista(n);localStorage.setItem(chave,JSON.stringify(n))
}
function registrarVariosRapido(pessoa:'denise'|'flavio',lista:SRegQuick[],setLista:(n:SRegQuick[])=>void){
  const chave=pessoa==='denise'?'dos_saude_extra':'dos_saude_extra_flavio'
  const hojeStr=new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})
  const idx=lista.findIndex(r=>r.data===hojeStr)
  const base:SRegQuick=idx>=0?{...lista[idx]}:{data:hojeStr,peso:0,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:'',sono:0}
  const peso=window.prompt('Peso (kg)? Deixe em branco pra pular.',base.peso?String(base.peso):'')
  if(peso&&peso.trim()){base.peso=Number(peso.replace(',','.'))||0;if(pessoa==='denise')base.imc=Number((base.peso/(1.63**2)).toFixed(1))}
  const gordura=window.prompt('Gordura corporal (%)? Deixe em branco pra pular.',base.gordura?String(base.gordura):'')
  if(gordura&&gordura.trim())base.gordura=Number(gordura.replace(',','.'))||0
  const humor=window.prompt('Humor (1 a 10)? Deixe em branco pra pular.',base.humor?String(base.humor):'')
  if(humor&&humor.trim())base.humor=Number(humor)||0
  const energia=window.prompt('Energia (1 a 10)? Deixe em branco pra pular.',base.energia?String(base.energia):'')
  if(energia&&energia.trim())base.energia=Number(energia)||0
  const intestino=window.prompt('Intestino (Regular/Preso/Solto)? Deixe em branco pra pular.',base.intestino||'')
  if(intestino&&intestino.trim())base.intestino=intestino
  const sono=window.prompt('Sono (horas)? Deixe em branco pra pular.',base.sono?String(base.sono):'')
  if(sono&&sono.trim())base.sono=Number(sono.replace(',','.'))||0
  const sint=window.prompt('Sintomas (opcional)? Deixe em branco pra pular.',base.sint||'')
  if(sint&&sint.trim())base.sint=sint
  const n=idx>=0?lista.map((r,i)=>i===idx?base:r):[base,...lista]
  setLista(n);localStorage.setItem(chave,JSON.stringify(n))
}
function Saude(){
  type SReg={data:string,peso:number,imc:number,gordura:number,humor:number,energia:number,intestino:string,sint:string,sono?:number}
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
  const [extras,setExtras]=React.useState<SReg[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_saude_extra')||'[]')}catch{return []}})
  const [aba,setAba]=React.useState<'denise'|'flavio'|'domi'|'derick'>('denise')
  const [consuls,setConsuls]=React.useState<Record<string,ConsReg[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_consuls')||'{}')}catch{return {}}})
  const [criancas,setCriancas]=React.useState<Record<string,CriancaReg[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_criancas')||'{}')}catch{return {}}})
  const [tamanhos,setTamanhos]=React.useState<Record<string,Record<string,string>>>(()=>{try{return JSON.parse(localStorage.getItem('dos_tamanhos')||'{}')}catch{return {}}})
  const [novaConsulta,setNovaConsulta]=React.useState({tipo:'',data:'',obs:'',proximo:''})
  const [novaCrianca,setNovaCrianca]=React.useState({peso:'',altura:'',obs:''})
  const [savedC,setSavedC]=React.useState(false)
  const [extrasF,setExtrasF]=React.useState<SReg[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_saude_extra_flavio')||'null');return v||[{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}catch{return [{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}})
  const [medD]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_denise')||'null');return v||[{data:'04/06',pescoco:0,ombro:37,peito:91,cintura:73,bracE:25,bracD:25.5,antebracoE:19.5,antebracoD:19,abdSup:78,abdInf:81,coxaE:48,coxaD:49,panturE:31,panturD:33,quadril:91.5}]}catch{return []}})
  const [medF]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_flavio')||'null');return v||[{data:'29/07',pescoco:41,ombro:42,peito:99,cintura:100,bracE:33,bracD:33,antebracoE:28,antebracoD:29,abdSup:96,abdInf:103,coxaE:56,coxaD:55,panturE:42,panturD:42,quadril:108}]}catch{return []}})
  const [aguaDenise,setAguaDenise]=React.useState(lerAguaHoje)
  function addAguaDenise(ml:number){const n=Math.min(aguaDenise+ml,6000);setAguaDenise(n);salvarAguaHoje(n)}
  const [aguaFlavio,setAguaFlavio]=React.useState<number>(()=>Number(lerLogMarcador('dos_agua_log_flavio')[isoBR(new Date())]||0))
  function addAguaFlavio(ml:number){
    const n=Math.min(aguaFlavio+ml,6000);setAguaFlavio(n)
    const log=lerLogMarcador('dos_agua_log_flavio');log[isoBR(new Date())]=String(n);localStorage.setItem('dos_agua_log_flavio',JSON.stringify(log))
  }
  const [skincareLog,setSkincareLog]=React.useState<Record<string,string>>(()=>lerLogMarcador('dos_skincare'))
  const [skincareLogF,setSkincareLogF]=React.useState<Record<string,string>>(()=>lerLogMarcador('dos_skincare_flavio'))
  const [probioticosLog,setProbioticosLog]=React.useState<Record<string,string>>(()=>lerLogMarcador('dos_probioticos'))
  const [probioticosLogF,setProbioticosLogF]=React.useState<Record<string,string>>(()=>lerLogMarcador('dos_probioticos_flavio'))
  const [periodoPeso,setPeriodoPeso]=React.useState<'7'|'30'|'90'|'365'>('30')
  const [diaSelecionado,setDiaSelecionado]=React.useState(()=>isoBR(new Date()))
  const [cresModo,setCresModo]=React.useState<'peso'|'altura'>('peso')
  function navegarDia(delta:number){
    const d=new Date(diaSelecionado+'T12:00:00');d.setDate(d.getDate()+delta)
    const novo=isoBR(d)
    if(novo>isoBR(new Date()))return
    setDiaSelecionado(novo)
  }
  const diaEhHoje=diaSelecionado===isoBR(new Date())
  const [mostrarTodasMedidasCrianca,setMostrarTodasMedidasCrianca]=React.useState(false)
  const diaLabel=diaEhHoje?`Hoje, ${new Date(diaSelecionado+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'long'})}`:new Date(diaSelecionado+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'long',year:'numeric'})

  const [tzSchedules,setTzSchedules]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [tzBalance,setTzBalance]=React.useState(0)
  const [tzApplications,setTzApplications]=React.useState<any[]>([])
  const [tzLoading,setTzLoading]=React.useState(true)
  const [tzMsg,setTzMsg]=React.useState('')
  const [tzMostrarGestao,setTzMostrarGestao]=React.useState<null|'aplicar'|'estoque'|'ajuste'|'protocolo'|'historico'>(null)
  const [tzDose,setTzDose]=React.useState('')
  const [tzData,setTzData]=React.useState(()=>isoBR(new Date()))
  const [tzEstoqueQtd,setTzEstoqueQtd]=React.useState('')
  const [tzEstoqueObs,setTzEstoqueObs]=React.useState('')
  const [tzAjusteQtd,setTzAjusteQtd]=React.useState('')
  const [tzAjusteMotivo,setTzAjusteMotivo]=React.useState('')
  const [tzProtocoloDose,setTzProtocoloDose]=React.useState('')
  const [tzProtocoloIntervalo,setTzProtocoloIntervalo]=React.useState('')

  async function tzLoad(){
    setTzLoading(true)
    const [{data:sched},{data:bal},{data:apps}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
      supabase.from('tirzepatida_applications').select('*').order('applied_at',{ascending:false}),
    ])
    const map:Record<string,any>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={planned_dose_mg:Number(row.planned_dose_mg),interval_days:row.interval_days,next_application_date:row.next_application_date}})
    setTzSchedules(map);setTzBalance(Number(bal?.current_balance_mg??0));setTzApplications(apps||[]);setTzLoading(false)
  }
  React.useEffect(()=>{tzLoad()},[])

  function tzCalcularProxima(pessoa:string,intervaloDias:number){
    const appsPessoa=tzApplications.filter((a:any)=>a.person===pessoa&&a.counted_in_stock).sort((a:any,b:any)=>b.applied_at.localeCompare(a.applied_at))
    if(appsPessoa.length===0)return null
    const ultima=new Date(appsPessoa[0].applied_at);ultima.setDate(ultima.getDate()+intervaloDias)
    return isoBR(ultima)
  }
  async function tzRegistrarAplicacao(pessoa:'denise'|'flavio'){
    const d=parseFloat(tzDose.replace(',','.'))
    if(!d||d<=0){setTzMsg('❌ Dose inválida.');return}
    if(d>tzBalance){setTzMsg('❌ Estoque insuficiente.');return}
    const duplicada=tzApplications.some((a:any)=>a.person===pessoa&&a.applied_at?.slice(0,10)===tzData&&Number(a.dose_mg)===d)
    if(duplicada&&!window.confirm('Já existe uma aplicação igual (mesma pessoa, data e dose). Registrar mesmo assim?'))return
    try{
      const appliedAt=new Date(tzData+'T'+new Date().toTimeString().slice(0,8)).toISOString()
      const {error}=await supabase.rpc('tirze_apply_dose',{p_person:pessoa,p_applied_at:appliedAt,p_dose_mg:d})
      if(error)throw error
      setTzMsg('✓ Aplicação registrada.');setTzMostrarGestao(null);setTzDose('');await tzLoad()
    }catch(e:any){setTzMsg('❌ '+(e?.message||String(e)))}
  }
  async function tzEstornar(app:any){
    if(!window.confirm('Estornar esta aplicação? A dose volta para o estoque.'))return
    if(app.counted_in_stock)await supabase.rpc('tirze_register_movement',{p_type:'correcao',p_amount_mg:Number(app.dose_mg),p_person:app.person,p_notes:'Estorno de aplicação'})
    await supabase.from('tirzepatida_applications').delete().eq('id',app.id)
    setTzMsg('✓ Aplicação estornada e devolvida ao estoque.');await tzLoad()
  }
  async function tzAdicionarEstoque(){
    const q=parseFloat(tzEstoqueQtd.replace(',','.'))
    if(!q||q<=0){setTzMsg('❌ Quantidade inválida.');return}
    try{
      const {error}=await supabase.rpc('tirze_register_movement',{p_type:'entrada',p_amount_mg:q,p_notes:tzEstoqueObs||'Entrada de estoque'})
      if(error)throw error
      setTzMsg(`✓ +${q}mg adicionados ao estoque.`);setTzEstoqueQtd('');setTzEstoqueObs('');setTzMostrarGestao(null);await tzLoad()
    }catch(e:any){setTzMsg('❌ '+(e?.message||String(e)))}
  }
  async function tzAjustarEstoque(){
    const q=parseFloat(tzAjusteQtd.replace(',','.'))
    if(!q||!tzAjusteMotivo.trim()){setTzMsg('❌ Informe a quantidade (pode ser negativa) e o motivo do ajuste.');return}
    try{
      const {error}=await supabase.rpc('tirze_register_movement',{p_type:'correcao',p_amount_mg:q,p_notes:tzAjusteMotivo})
      if(error)throw error
      setTzMsg('✓ Ajuste de estoque registrado.');setTzAjusteQtd('');setTzAjusteMotivo('');setTzMostrarGestao(null);await tzLoad()
    }catch(e:any){setTzMsg('❌ '+(e?.message||String(e)))}
  }
  async function tzSalvarProtocolo(pessoa:'denise'|'flavio'){
    const dose=parseFloat(tzProtocoloDose.replace(',','.'))
    const intervalo=Number(tzProtocoloIntervalo)
    if(!dose||!intervalo){setTzMsg('❌ Informe dose e intervalo válidos.');return}
    try{
      const prox=tzCalcularProxima(pessoa,intervalo)
      const {error}=await supabase.from('tirzepatida_schedule').update({planned_dose_mg:dose,interval_days:intervalo,...(prox?{next_application_date:prox}:{})}).eq('person',pessoa)
      if(error)throw error
      setTzMsg('✓ Protocolo atualizado. Aplicações antigas continuam com a dose registrada na época.');setTzMostrarGestao(null);await tzLoad()
    }catch(e:any){setTzMsg('❌ '+(e?.message||String(e)))}
  }
  const tzAutonomia=(()=>{
    const dDen=tzSchedules.denise?.planned_dose_mg||0,dFla=tzSchedules.flavio?.planned_dose_mg||0
    const iDen=tzSchedules.denise?.interval_days||1,iFla=tzSchedules.flavio?.interval_days||1
    const mgDay=(dDen&&iDen?dDen/iDen:0)+(dFla&&iFla?dFla/iFla:0)
    return mgDay>0?Math.floor(tzBalance/mgDay):null
  })()
  function tzStatusProxima(iso:string|null|undefined){
    if(!iso)return {texto:'Sem próxima aplicação definida',cor:'rgba(255,255,255,.4)'}
    const hoje=isoBR(new Date())
    const dif=Math.round((new Date(iso+'T12:00:00').getTime()-new Date(hoje+'T12:00:00').getTime())/86400000)
    if(dif<0)return {texto:`Atrasada ${Math.abs(dif)} dia${Math.abs(dif)>1?'s':''}`,cor:C.danger}
    if(dif===0)return {texto:'Hoje',cor:C.warn}
    if(dif===1)return {texto:'Amanhã',cor:C.acc2}
    return {texto:`Em ${dif} dias`,cor:'rgba(255,255,255,.6)'}
  }
  const displayList=[...[...OKOK].reverse(),...extras]
  const pesoAtual=displayList[0].peso
  const pesoAtualF=extrasF[0].peso
  const [medicamentos,setMedicamentos]=React.useState<Record<string,any[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_medicamentos')||'{}')}catch{return {}}})
  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''})
  function addMedicamento(kid:string){
    if(!novoMed.nome||!novoMed.dosagem)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),nome:novoMed.nome,dosagem:novoMed.dosagem,frequencia:novoMed.frequencia,horarios:novoMed.horarios,ate:novoMed.ate}
    const n={...medicamentos,[kid]:[reg,...(medicamentos[kid]||[])]}
    setMedicamentos(n);localStorage.setItem('dos_medicamentos',JSON.stringify(n))
    setNovoMed({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''})
  }
  function delMedicamento(kid:string,idx:number){
    const n={...medicamentos,[kid]:(medicamentos[kid]||[]).filter((_c:any,i:number)=>i!==idx)}
    setMedicamentos(n);localStorage.setItem('dos_medicamentos',JSON.stringify(n))
  }
  async function addConsulta(kid:string){
    if(!novaConsulta.tipo||!novaConsulta.data)return
    const n={...consuls,[kid]:[{...novaConsulta},...(consuls[kid]||[])]}
    setConsuls(n);localStorage.setItem('dos_consuls',JSON.stringify(n))
    const nomeEvento=`Consulta: ${novaConsulta.tipo}${kid?` (${kid.charAt(0).toUpperCase()+kid.slice(1)})`:''}`
    await criarEventoAgenda({nome:nomeEvento,data:novaConsulta.data,hora:'',categoria:'saude',origem:'saude',pessoa:kid,descricao:novaConsulta.obs||''})
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
  const membros=[
    {id:'denise',nome:'Denise',label:'Você',cor:C.acc2},
    {id:'flavio',nome:'Flávio',label:'Flávio',cor:C.water},
    {id:'domi',nome:'Domi',label:'Domi',cor:C.pink},
    {id:'derick',nome:'Derick',label:'Derick',cor:C.ok},
  ]

  function renderTirzepatidaCard(pessoa:'denise'|'flavio',cor:string){
    const sched=tzSchedules[pessoa]
    const status=tzStatusProxima(sched?.next_application_date)
    const historico=tzApplications.filter((a:any)=>a.person===pessoa)
    return(<Card title="💉 Tirzepatida" action={<button onClick={()=>setTzMostrarGestao(g=>g?null:'aplicar')} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>{tzMostrarGestao?'Fechar':'Gerenciar'}</button>}>
      {tzLoading?<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Carregando…</div>:!sched?<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Protocolo ainda não cadastrado para {pessoa==='denise'?'você':'Flávio'}.</div>:<>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
          <div><div style={{fontSize:16,fontWeight:800}}>{sched.planned_dose_mg} mg</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Dose atual</div></div>
          <div><div style={{fontSize:16,fontWeight:800,color:status.cor}}>{status.texto}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Próxima aplicação{sched.next_application_date?` · ${new Date(sched.next_application_date+'T12:00:00').toLocaleDateString('pt-BR')}`:''}</div></div>
          <div><div style={{fontSize:16,fontWeight:800}}>{tzBalance} mg</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Estoque compartilhado</div></div>
          <div><div style={{fontSize:16,fontWeight:800}}>{tzAutonomia!=null?`~${tzAutonomia} dias`:'—'}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>Autonomia estimada</div></div>
        </div>
        {historico[0]&&<div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:6}}>Última aplicação: {new Date(historico[0].applied_at).toLocaleDateString('pt-BR')} · {Number(historico[0].dose_mg)}mg</div>}
      </>}
      {tzMsg&&<div style={{fontSize:12,color:tzMsg.startsWith('✓')?C.ok:C.danger,marginBottom:8}}>{tzMsg}</div>}
      {tzMostrarGestao&&<div style={{marginTop:10,paddingTop:10,borderTop:`1px solid ${C.line}`}}>
        <div style={{display:'flex',gap:6,marginBottom:10,flexWrap:'wrap' as const}}>
          {([['aplicar','Registrar aplicação'],['protocolo','Editar protocolo'],['estoque','Adicionar estoque'],['ajuste','Ajustar estoque'],['historico','Histórico']] as [any,string][]).map(([v,l])=>(
            <button key={v} onClick={()=>setTzMostrarGestao(v)} style={{background:tzMostrarGestao===v?cor:C.s2,border:'none',color:tzMostrarGestao===v?'#fff':'rgba(255,255,255,.6)',borderRadius:20,padding:'5px 10px',fontSize:11,cursor:'pointer'}}>{l}</button>
          ))}
        </div>
        {tzMostrarGestao==='aplicar'&&<div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:8}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Data</label><input type="date" value={tzData} onChange={e=>setTzData(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12,colorScheme:'dark' as const}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Dose (mg)</label><input type="number" step="0.5" value={tzDose||String(sched?.planned_dose_mg||'')} onChange={e=>setTzDose(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12}}/></div>
          </div>
          <button onClick={()=>tzRegistrarAplicacao(pessoa)} style={{width:'100%',background:`linear-gradient(135deg,${cor},#6d28d9)`,color:'#fff',border:'none',borderRadius:9,padding:'9px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>Registrar aplicação</button>
        </div>}
        {tzMostrarGestao==='protocolo'&&<div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:8}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Nova dose (mg)</label><input type="number" step="0.5" value={tzProtocoloDose} onChange={e=>setTzProtocoloDose(e.target.value)} placeholder={String(sched?.planned_dose_mg||'')} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Intervalo (dias)</label><input type="number" value={tzProtocoloIntervalo} onChange={e=>setTzProtocoloIntervalo(e.target.value)} placeholder={String(sched?.interval_days||'')} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12}}/></div>
          </div>
          <p style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginBottom:8}}>Aplicações antigas continuam com a dose que estava valendo na época.</p>
          <button onClick={()=>tzSalvarProtocolo(pessoa)} style={{width:'100%',background:`linear-gradient(135deg,${cor},#6d28d9)`,color:'#fff',border:'none',borderRadius:9,padding:'9px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>Salvar protocolo</button>
        </div>}
        {tzMostrarGestao==='estoque'&&<div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:8}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Quantidade recebida (mg)</label><input type="number" value={tzEstoqueQtd} onChange={e=>setTzEstoqueQtd(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Observação (opcional)</label><input value={tzEstoqueObs} onChange={e=>setTzEstoqueObs(e.target.value)} placeholder="Ex: lote/farmácia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12}}/></div>
          </div>
          <button onClick={tzAdicionarEstoque} style={{width:'100%',background:`linear-gradient(135deg,${C.ok},#15803d)`,color:'#fff',border:'none',borderRadius:9,padding:'9px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>+ Adicionar ao estoque</button>
        </div>}
        {tzMostrarGestao==='ajuste'&&<div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:8}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Ajuste (mg, use - pra reduzir)</label><input type="number" value={tzAjusteQtd} onChange={e=>setTzAjusteQtd(e.target.value)} placeholder="Ex: -2,5" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Motivo</label><input value={tzAjusteMotivo} onChange={e=>setTzAjusteMotivo(e.target.value)} placeholder="Ex: divergência na contagem" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 8px',color:'#fff',fontSize:12}}/></div>
          </div>
          <button onClick={tzAjustarEstoque} style={{width:'100%',background:`linear-gradient(135deg,${C.warn},#b45309)`,color:'#fff',border:'none',borderRadius:9,padding:'9px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>Registrar ajuste</button>
        </div>}
        {tzMostrarGestao==='historico'&&<div style={{maxHeight:220,overflowY:'auto' as const}}>
          {historico.length===0&&<div style={{fontSize:12,color:'rgba(255,255,255,.3)'}}>Nenhuma aplicação registrada ainda.</div>}
          {historico.map((a:any)=>(<div key={a.id} style={{display:'flex',alignItems:'center',gap:8,padding:'7px 0',borderBottom:`1px solid ${C.line}`,fontSize:11.5,color:'rgba(255,255,255,.6)'}}>
            <span style={{width:70}}>{new Date(a.applied_at).toLocaleDateString('pt-BR')}</span>
            <span style={{flex:1}}>{Number(a.dose_mg)}mg</span>
            <span style={{background:a.counted_in_stock?'rgba(52,211,153,.15)':C.s3,color:a.counted_in_stock?C.ok:'rgba(255,255,255,.4)',padding:'2px 7px',borderRadius:20,fontSize:10.5}}>{a.counted_in_stock?'✓':'histórico'}</span>
            {a.counted_in_stock&&<button onClick={()=>tzEstornar(a)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'3px 8px',fontSize:10.5,cursor:'pointer'}}>Estornar</button>}
          </div>))}
        </div>}
      </div>}
    </Card>)
  }

  function renderAdulto(p:{pessoa:'denise'|'flavio',nome:string,cor:string,variant:'imc'|'medidas'}){
    const lista=p.pessoa==='denise'?displayList:extrasF
    const pesoAt=p.pessoa==='denise'?pesoAtual:pesoAtualF
    const aguaChave=p.pessoa==='denise'?'dos_agua_log':'dos_agua_log_flavio'
    const aguaAt=diaEhHoje?(p.pessoa==='denise'?aguaDenise:aguaFlavio):Number(lerLogMarcador(aguaChave)[diaSelecionado]||0)
    const addAgua=p.pessoa==='denise'?addAguaDenise:addAguaFlavio
    const skinLog=p.pessoa==='denise'?skincareLog:skincareLogF
    const setSkinLog=p.pessoa==='denise'?setSkincareLog:setSkincareLogF
    const skinChave=p.pessoa==='denise'?'dos_skincare':'dos_skincare_flavio'
    const probLog=p.pessoa==='denise'?probioticosLog:probioticosLogF
    const setProbLog=p.pessoa==='denise'?setProbioticosLog:setProbioticosLogF
    const probChave=p.pessoa==='denise'?'dos_probioticos':'dos_probioticos_flavio'
    const consultasP=consuls[p.pessoa]||[]
    const medidasP=p.pessoa==='denise'?medD:medF

    const hoje=diaSelecionado
    const anoAtual=new Date().getFullYear()
    const registroHojeIdx=lista.findIndex((r:any)=>paraDataAproxDDMM(r.data,anoAtual)===hoje)
    const registroHoje=registroHojeIdx>=0?lista[registroHojeIdx]:null
    const anterior=lista[registroHojeIdx>=0?registroHojeIdx+1:1]

    const gorduraAtualReg=lista.find((r:any)=>r.gordura>0)
    const gorduraAnteriorReg=gorduraAtualReg?lista.slice(lista.indexOf(gorduraAtualReg)+1).find((r:any)=>r.gordura>0):null
    const massaMagraAtual=gorduraAtualReg?Math.round(pesoAt*(1-gorduraAtualReg.gordura/100)*100)/100:null
    const massaMagraAnt=(gorduraAnteriorReg&&anterior)?Math.round(anterior.peso*(1-gorduraAnteriorReg.gordura/100)*100)/100:null

    const imcAtual=lista[0]?.imc||0
    const imcClass=classificarIMC(imcAtual)
    const metaAguaP=Number(localStorage.getItem('dos_meta_agua_ml')||2500)
    const pctAgua=Math.min(100,Math.round(aguaAt/metaAguaP*100))

    const serieCompleta:{iso:string,valor:number}[]=[...lista].map((r:any)=>({iso:paraDataAproxDDMM(r.data,anoAtual),valor:r.peso})).filter((x:any):x is {iso:string,valor:number}=>!!x.iso&&!!x.valor).sort((a,b)=>a.iso.localeCompare(b.iso))
    const corteDias=Number(periodoPeso)
    const limiteIso=isoBR(new Date(Date.now()-corteDias*86400000))
    const serieFiltrada=serieCompleta.filter((x:any)=>x.iso>=limiteIso)

    const itensHoje:[string,string,string][]=[]
    if(registroHoje?.peso)itensHoje.push(['⚖️','Peso',`${registroHoje.peso} kg`])
    if(aguaAt>0)itensHoje.push(['💧','Água',`${aguaAt} ml`])
    if(registroHoje?.sono)itensHoje.push(['🌙','Sono',`${registroHoje.sono}h`])
    if(registroHoje?.energia)itensHoje.push(['⚡','Energia',`${registroHoje.energia} / 10`])
    if(registroHoje?.humor)itensHoje.push(['😊','Humor',`${registroHoje.humor} / 10`])
    if(registroHoje?.intestino)itensHoje.push(['💚','Intestino',registroHoje.intestino])
    if(skinLog[hoje])itensHoje.push(['🧴','Skin care',`✓ Concluído · ${skinLog[hoje]}`])
    if(probLog[hoje])itensHoje.push(['💊','Probióticos',`✓ Tomado · ${probLog[hoje]}`])

    const proximasConsultas=consultasP.filter((c:any)=>c.data&&c.data>=hoje).map((c:any)=>({data:c.data,titulo:c.tipo,sub:c.obs||''}))
    const proximaTz=tzSchedules[p.pessoa]?.next_application_date?[{data:tzSchedules[p.pessoa].next_application_date as string,titulo:'💉 Aplicação de Tirzepatida',sub:`${tzSchedules[p.pessoa].planned_dose_mg}mg`}]:[]
    const proximos=[...proximasConsultas,...proximaTz].sort((a,b)=>a.data.localeCompare(b.data)).slice(0,5)

    const seteAtras=isoBR(new Date(Date.now()-7*86400000))
    const catorzeAtras=isoBR(new Date(Date.now()-14*86400000))
    const semAtual=serieCompleta.filter(x=>x.iso>=seteAtras)
    const semAnt=serieCompleta.filter(x=>x.iso>=catorzeAtras&&x.iso<seteAtras)
    const mediaAtual=semAtual.length?Math.round(semAtual.reduce((a,x)=>a+x.valor,0)/semAtual.length*100)/100:null
    const mediaAnt=semAnt.length?Math.round(semAnt.reduce((a,x)=>a+x.valor,0)/semAnt.length*100)/100:null
    const treinosSemana=p.pessoa==='denise'?(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter((t:any)=>t.data>=seteAtras).length}catch{return 0}})():null
    const deltaMedia=deltaInfo(mediaAtual,mediaAnt,2,'kg')

    return(<>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(120px,1fr))',gap:10,marginBottom:16}}>
        <IndicadorCard label="Peso atual" valor={`${pesoAt} kg`} delta={deltaInfo(pesoAt,anterior?.peso,1,'kg')}/>
        {gorduraAtualReg&&<IndicadorCard label="Gordura corporal" valor={`${gorduraAtualReg.gordura}%`} delta={deltaInfo(gorduraAtualReg.gordura,gorduraAnteriorReg?.gordura,1,'%')}/>}
        {p.variant==='imc'?(<>
          {massaMagraAtual!=null&&<IndicadorCard label="Massa magra" valor={`${massaMagraAtual} kg`} delta={deltaInfo(massaMagraAtual,massaMagraAnt,1,'kg')}/>}
          <IndicadorCard label="IMC" valor={imcAtual||'—'} badge={imcAtual?imcClass:undefined}/>
        </>):(<>
          {medidasP[0]&&<IndicadorCard label="Cintura" valor={`${medidasP[0].cintura} cm`} delta={deltaInfo(medidasP[0].cintura,medidasP[1]?.cintura,1,'cm')}/>}
          {medidasP[0]&&<IndicadorCard label="Quadril" valor={`${medidasP[0].quadril} cm`} delta={deltaInfo(medidasP[0].quadril,medidasP[1]?.quadril,1,'cm')}/>}
          {medidasP[0]&&<IndicadorCard label="Peito" valor={`${medidasP[0].peito} cm`} delta={deltaInfo(medidasP[0].peito,medidasP[1]?.peito,1,'cm')}/>}
        </>)}
        <IndicadorCard label="Água hoje" valor={`${(aguaAt/1000).toFixed(2).replace('.',',')} / ${(metaAguaP/1000).toFixed(1).replace('.',',')} L`} sub={`${pctAgua}% da meta`}/>
        <IndicadorCard label="Sono hoje" valor={registroHoje?.sono?`${registroHoje.sono}h`:'—'}/>
        <IndicadorCard label="Energia hoje" valor={registroHoje?.energia?`${registroHoje.energia} / 10`:'—'}/>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'2fr 1fr',gap:16}}>
        <div>
          <Card title="Evolução do peso" action={<div style={{display:'flex',gap:6}}>{(['7','30','90','365'] as const).map(v=>(<button key={v} onClick={()=>setPeriodoPeso(v)} style={{background:periodoPeso===v?p.cor:C.s2,border:'none',color:periodoPeso===v?'#fff':'rgba(255,255,255,.5)',borderRadius:8,padding:'5px 10px',fontSize:11,fontWeight:600,cursor:'pointer'}}>{v==='365'?'1 ano':`${v}d`}</button>))}</div>}>
            <LinhaEvolucao pontos={serieFiltrada} cor={p.cor} unidade="kg" rotulo="Peso atual"/>
          </Card>
          <div style={{marginTop:16}}>
            <Card title="Composição corporal">
              {massaMagraAtual!=null&&gorduraAtualReg?(
                <DonutComposicao centroValor={`${pesoAt} kg`} centroLabel="Peso atual" segmentos={[
                  {valor:massaMagraAtual,cor:p.cor,label:'Massa magra'},
                  {valor:Math.round(pesoAt*gorduraAtualReg.gordura/100*100)/100,cor:C.pink,label:'Gordura'},
                ]}/>
              ):<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0'}}>Registre a gordura corporal em "Registrar hoje" pra ver a composição.</div>}
            </Card>
          </div>
          <div style={{marginTop:16}}>
            <Card title="Hábitos em dia">
              <div style={{fontSize:22,fontWeight:800}}>{itensHoje.length} / 8</div>
              <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden',margin:'8px 0'}}><div style={{height:'100%',width:`${itensHoje.length/8*100}%`,borderRadius:4,background:p.cor}}/></div>
              <div style={{fontSize:12,color:'rgba(255,255,255,.4)'}}>{itensHoje.length===8?'Todos os registros de hoje em dia! 🎉':itensHoje.length>0?'Continue registrando ao longo do dia.':'Nada registrado ainda hoje.'}</div>
            </Card>
          </div>
        </div>
        <div>
          <Card title="Registros de hoje">
            {itensHoje.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nada registrado hoje ainda.</div>}
            {itensHoje.map(([icone,nome,valor])=>(<Lrow key={nome} icon={icone} name={nome} val={valor}/>))}
          </Card>
          <div style={{marginTop:16}}>
            <Card title="Ações rápidas">
              {!diaEhHoje&&<div style={{fontSize:11.5,color:'rgba(255,255,255,.35)',marginBottom:10}}>Ações rápidas registram sempre em "hoje" — volte pro dia atual pra usar.</div>}
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,opacity:diaEhHoje?1:.4,pointerEvents:diaEhHoje?'auto' as const:'none' as const}}>
                <button onClick={()=>registrarCampoRapido(p.pessoa,'peso','Peso (kg)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>⚖️ Registrar peso</button>
                <button onClick={()=>addAgua(250)} style={acaoBtnStyle}>💧 Registrar água</button>
                <button onClick={()=>registrarCampoRapido(p.pessoa,'sono','Quantas horas de sono?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>🌙 Registrar sono</button>
                <button onClick={()=>registrarCampoRapido(p.pessoa,'energia','Energia (1 a 10)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>⚡ Registrar energia</button>
                <button onClick={()=>registrarCampoRapido(p.pessoa,'humor','Humor (1 a 10)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>😊 Registrar humor</button>
                <button onClick={()=>registrarCampoRapido(p.pessoa,'intestino','Intestino (Regular/Preso/Solto)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>💚 Registrar intestino</button>
                <button onClick={()=>marcarHoje(skinChave,setSkinLog)} style={acaoBtnStyle}>🧴 Skin care{skinLog[hoje]?' ✓':''}</button>
                <button onClick={()=>marcarHoje(probChave,setProbLog)} style={acaoBtnStyle}>💊 Probióticos{probLog[hoje]?' ✓':''}</button>
              </div>
              <button onClick={()=>registrarVariosRapido(p.pessoa,p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={{...acaoBtnStyle,width:'100%',marginTop:8,opacity:diaEhHoje?1:.4,pointerEvents:diaEhHoje?'auto' as const:'none' as const}}>+ Outro registro</button>
            </Card>
          </div>
          <div style={{marginTop:16}}>{renderTirzepatidaCard(p.pessoa,p.cor)}</div>
          <div style={{marginTop:16}}>
            <Card title="Próximos itens">
              {proximos.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum item próximo registrado.</div>}
              {proximos.map((it,i)=>(<div key={i} style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
                <div><div style={{fontSize:12.5,fontWeight:700}}>{it.titulo}</div>{it.sub&&<div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{it.sub}</div>}</div>
                <span style={{fontSize:11,color:p.cor}}>{new Date(it.data+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>
              </div>))}
              <NavLink to="/agenda" style={{display:'block',textAlign:'center' as const,fontSize:12,color:p.cor,textDecoration:'none',marginTop:10}}>Ver agenda completa</NavLink>
            </Card>
          </div>
        </div>
      </div>

      <div style={{marginTop:16}}>
        <Card title="Resumo semanal">
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(120px,1fr))',gap:14}}>
            <div><div style={{fontSize:18,fontWeight:800}}>{mediaAtual??'—'}{mediaAtual!=null?' kg':''}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Peso médio</div>{deltaMedia&&<div style={{fontSize:10.5,color:deltaMedia.cor}}>{deltaMedia.texto} vs semana anterior</div>}</div>
            {p.pessoa==='denise'&&treinosSemana!=null&&<div><div style={{fontSize:18,fontWeight:800}}>{treinosSemana}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Treinos</div></div>}
            <div><div style={{fontSize:18,fontWeight:800}}>{itensHoje.length}/8</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Hábitos concluídos hoje</div></div>
          </div>
        </Card>
      </div>
    </>)
  }

  function renderCrianca(kid:'domi'|'derick',nome:string,cor:string,corGrad:string){
    const kidCrianca=criancas[kid]||[]
    const kidConsuls=consuls[kid]||[]
    const kidMeds=medicamentos[kid]||[]
    const hojeIso=isoBR(new Date())
    const ultimaMedicao=kidCrianca[0]
    const proximasConsultas=[...kidConsuls].filter((c:any)=>c.data&&c.data>=hojeIso).sort((a:any,b:any)=>a.data.localeCompare(b.data))
    const proximaConsulta=proximasConsultas[0]
    const medsAtivos=kidMeds.filter((m:any)=>!m.ate||m.ate>=hojeIso).length
    const anoAtual=new Date().getFullYear()
    const serieCresc:{iso:string,valor:number}[]=[...kidCrianca].map((r:any)=>({iso:paraDataAproxDDMM(r.data,anoAtual),valor:cresModo==='peso'?r.peso:r.altura})).filter((x:any):x is {iso:string,valor:number}=>!!x.iso&&!!x.valor).sort((a,b)=>a.iso.localeCompare(b.iso))
    const medidasVisiveis=mostrarTodasMedidasCrianca?kidCrianca:kidCrianca.slice(0,5)
    const t=tamanhos[kid]||{}

    return(<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <div style={{gridColumn:'1 / -1',display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:12}}>
        <IndicadorCard label="Peso atual" valor={ultimaMedicao?`${ultimaMedicao.peso} kg`:'—'} delta={ultimaMedicao&&kidCrianca[1]?deltaInfo(ultimaMedicao.peso,kidCrianca[1].peso,1,'kg'):null}/>
        <IndicadorCard label="Altura atual" valor={ultimaMedicao?.altura?`${ultimaMedicao.altura} cm`:'—'} delta={ultimaMedicao?.altura&&kidCrianca[1]?.altura?deltaInfo(ultimaMedicao.altura,kidCrianca[1].altura,1,'cm'):null}/>
        <IndicadorCard label="Última medição" valor={ultimaMedicao?ultimaMedicao.data:'—'}/>
        <IndicadorCard label="Próxima consulta" valor={proximaConsulta?proximaConsulta.data:'—'} sub={proximaConsulta?.tipo}/>
        <IndicadorCard label="Medicamentos ativos" valor={medsAtivos}/>
      </div>
      <div>
        <Card title={`Crescimento — ${nome}`} action={<div style={{display:'flex',gap:6}}>{(['peso','altura'] as const).map(v=>(<button key={v} onClick={()=>setCresModo(v)} style={{background:cresModo===v?cor:C.s2,border:'none',color:cresModo===v?'#fff':'rgba(255,255,255,.5)',borderRadius:8,padding:'5px 10px',fontSize:11,fontWeight:600,cursor:'pointer',textTransform:'capitalize' as const}}>{v}</button>))}</div>}>
          <LinhaEvolucao pontos={serieCresc} cor={cor} unidade={cresModo==='peso'?'kg':'cm'} rotulo={cresModo==='peso'?'Peso atual':'Altura atual'}/>
        </Card>
      </div>
      <div>
        <div id={`card-registrar-${kid}`}>
        <Card title="Registrar hoje">
          {savedC&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 12px',fontSize:13,color:C.ok,marginBottom:12}}>✓ Salvo!</div>}
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Peso (kg)</label><input type="number" step="0.1" value={novaCrianca.peso} onChange={e=>setNovaCrianca(p=>({...p,peso:e.target.value}))} placeholder="35" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Altura (cm)</label><input type="number" step="0.5" value={novaCrianca.altura} onChange={e=>setNovaCrianca(p=>({...p,altura:e.target.value}))} placeholder="140" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
          </div>
          <label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Observações</label>
          <textarea value={novaCrianca.obs} onChange={e=>setNovaCrianca(p=>({...p,obs:e.target.value}))} placeholder="Ex: Tudo bem, sem sintomas." rows={3} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10,resize:'none' as const}}/>
          <button onClick={()=>addCrianca(kid)} style={{width:'100%',background:`linear-gradient(135deg,${cor},${corGrad})`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Salvar medida</button>
        </Card>
        </div>
      </div>
      <div>
        <Card title="Tamanhos" action={<span style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>{t.atualizadoEm?`(${t.atualizadoEm})`:''}</span>}>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            {[['roupa','Roupa'],['calcado','Calçado'],['camiseta','Camiseta'],['calca','Calça']].map(([campo,label])=>(<div key={campo}><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:3}}>{label}</label><input value={t[campo]||''} onChange={e=>setTamanho(kid,campo,e.target.value)} placeholder="—" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'8px 10px',color:'#fff',fontSize:12}}/></div>))}
          </div>
          <button onClick={()=>setTamanho(kid,'atualizadoEm',new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}))} style={{width:'100%',background:`linear-gradient(135deg,${cor},${corGrad})`,color:'#fff',border:'none',borderRadius:10,padding:'10px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>Atualizar tamanhos</button>
        </Card>
      </div>
      <div style={{gridColumn:'1 / -1',display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:16}}>
        <Card title="Histórico de medidas">
          {kidCrianca.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhuma medida registrada ainda.</div>}
          {kidCrianca.length>0&&<div style={{maxHeight:mostrarTodasMedidasCrianca?260:'none',overflowY:mostrarTodasMedidasCrianca?'auto' as const:'visible' as const}}>
            <div style={{display:'flex',gap:6,fontSize:10.5,color:'rgba(255,255,255,.4)',borderBottom:`1px solid ${C.line}`,paddingBottom:6,marginBottom:4}}><span style={{width:44}}>Data</span><span style={{width:56}}>Peso</span><span style={{width:56}}>Altura</span><span style={{flex:1}}>Obs.</span></div>
            {medidasVisiveis.map((r:any,i:number)=>(<div key={i} style={{display:'flex',gap:6,padding:'6px 0',borderBottom:`1px solid ${C.line}`,fontSize:11.5,color:'rgba(255,255,255,.6)'}}><span style={{width:44}}>{r.data}</span><span style={{width:56,color:cor}}>{r.peso}kg</span><span style={{width:56}}>{r.altura?`${r.altura}cm`:'—'}</span><span style={{flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' as const}}>{r.obs||'—'}</span></div>))}
          </div>}
          {kidCrianca.length>5&&<div onClick={()=>setMostrarTodasMedidasCrianca(m=>!m)} style={{textAlign:'center' as const,fontSize:12,color:cor,cursor:'pointer',marginTop:10}}>{mostrarTodasMedidasCrianca?'Ver menos':'Ver todas as medidas'}</div>}
        </Card>
        <Card title="Consultas">
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Tipo</label>
            <select value={novaConsulta.tipo} onChange={e=>setNovaConsulta(p=>({...p,tipo:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}>
              <option value="">Selecionar</option><option>Pediatria</option><option>Dentista</option><option>Dermatologia</option><option>Vacina</option><option>Oftalmologia</option><option>Ortopedia</option><option>Outro</option>
            </select></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novaConsulta.data} onChange={e=>setNovaConsulta(p=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}/></div>
          </div>
          <input value={novaConsulta.obs} onChange={e=>setNovaConsulta(p=>({...p,obs:e.target.value}))} placeholder="Observações / diagnóstico" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
          <button onClick={()=>addConsulta(kid)} style={{width:'100%',background:`linear-gradient(135deg,${cor},${corGrad})`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer',marginBottom:10}}>+ Registrar consulta</button>
          {kidConsuls.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhuma consulta registrada.</div>}
          {[...kidConsuls].sort((a:any,b:any)=>b.data.localeCompare(a.data)).slice(0,4).map((c:any,i:number)=>{
            const futura=c.data>=hojeIso
            return(<div key={i} style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
              <div><div style={{fontWeight:700,fontSize:12.5,color:cor}}>{c.tipo}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{c.data}</div></div>
              <div style={{display:'flex',alignItems:'center',gap:6}}>
                <span style={{fontSize:10.5,fontWeight:700,color:futura?C.warn:C.ok,background:futura?'rgba(251,191,36,.12)':'rgba(52,211,153,.15)',padding:'3px 9px',borderRadius:20}}>{futura?'Próxima':'✓'}</span>
                <button onClick={()=>delConsulta(kid,kidConsuls.indexOf(c))} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button>
              </div>
            </div>)
          })}
        </Card>
        <Card title="Medicamentos">
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:8}}>
            <input value={novoMed.nome} onChange={e=>setNovoMed(p=>({...p,nome:e.target.value}))} placeholder="Medicamento" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:12.5}}/>
            <input value={novoMed.dosagem} onChange={e=>setNovoMed(p=>({...p,dosagem:e.target.value}))} placeholder="Dosagem" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:12.5}}/>
            <input value={novoMed.frequencia} onChange={e=>setNovoMed(p=>({...p,frequencia:e.target.value}))} placeholder="Frequência" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:12.5}}/>
            <input value={novoMed.horarios} onChange={e=>setNovoMed(p=>({...p,horarios:e.target.value}))} placeholder="Horários" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:12.5}}/>
          </div>
          <button onClick={()=>addMedicamento(kid)} style={{width:'100%',background:`linear-gradient(135deg,${cor},${corGrad})`,color:'#fff',border:'none',borderRadius:10,padding:'10px',fontSize:12.5,fontWeight:700,cursor:'pointer',marginBottom:10}}>+ Registrar medicamento</button>
          {kidMeds.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum medicamento registrado.</div>}
          {kidMeds.slice(0,4).map((m:any,i:number)=>{
            const ativo=!m.ate||m.ate>=hojeIso
            return(<div key={i} style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
              <div><div style={{fontWeight:700,fontSize:12.5,color:cor}}>{m.nome}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{m.dosagem}{m.frequencia?` · ${m.frequencia}`:''}</div></div>
              <div style={{display:'flex',alignItems:'center',gap:6}}>
                <span style={{fontSize:10.5,fontWeight:700,color:ativo?C.ok:'rgba(255,255,255,.4)',background:ativo?'rgba(52,211,153,.15)':C.s3,padding:'3px 9px',borderRadius:20}}>{ativo?'Ativo':'Encerrado'}</span>
                <button onClick={()=>delMedicamento(kid,i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button>
              </div>
            </div>)
          })}
          {kidMeds.length>4&&<div style={{textAlign:'center' as const,fontSize:12,color:cor,marginTop:6}}>Ver todos medicamentos ({kidMeds.length})</div>}
        </Card>
      </div>
    </div>)
  }

  const corAba=membros.find(m=>m.id===aba)?.cor||C.acc2
  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'flex-start',marginBottom:20,gap:16,flexWrap:'wrap' as const}}>
      <div>
        <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Saúde da Família</h1>
        <p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Acompanhamento individual · registros · consultas</p>
      </div>
      <div style={{display:'flex',alignItems:'center',gap:14}}>
        <span title="Buscar" style={{cursor:'pointer',color:'rgba(255,255,255,.5)',fontSize:16}}>🔍</span>
        <span title="Notificações" style={{cursor:'pointer',color:'rgba(255,255,255,.5)',fontSize:16,position:'relative' as const}}>🔔</span>
        <span title="Tema" style={{cursor:'pointer',color:'rgba(255,255,255,.5)',fontSize:16}}>🌙</span>
        <div style={{display:'flex',alignItems:'center',gap:8,cursor:'pointer'}}>
          <Avatar id="denise" label="D" size={30} radius={9}/>
          <span style={{fontSize:13,fontWeight:600}}>Denise</span>
          <span style={{color:'rgba(255,255,255,.4)',fontSize:11}}>▾</span>
        </div>
      </div>
    </div>
    <div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',marginBottom:20,gap:16,flexWrap:'wrap' as const}}>
      <div style={{display:'flex',gap:10}}>
        {membros.map(m=>(<button key={m.id} onClick={()=>setAba(m.id as typeof aba)} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 16px',borderRadius:12,border:`2px solid ${aba===m.id?m.cor:'rgba(255,255,255,.1)'}`,background:aba===m.id?`rgba(${m.cor==='#a78bfa'?'167,139,250':m.cor==='#38bdf8'?'56,189,248':m.cor==='#f472b6'?'244,114,182':'52,211,153'},.1)`:'transparent',cursor:'pointer',color:'#fff'}}>
          <Avatar id={m.id} label={m.nome[0]} size={32} radius={8}/>
          <span style={{fontWeight:600,fontSize:14}}>{m.nome}</span>
        </button>))}
      </div>
      <div style={{display:'flex',alignItems:'center',gap:10}}>
        <div style={{display:'flex',alignItems:'center',gap:4,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'6px 8px'}}>
          <button onClick={()=>navegarDia(-1)} style={{background:'none',border:'none',color:'#fff',cursor:'pointer',fontSize:14,padding:'2px 6px'}}>‹</button>
          <span style={{fontSize:12.5,fontWeight:600,padding:'0 4px',whiteSpace:'nowrap' as const}}>📅 {diaLabel}</span>
          <button onClick={()=>navegarDia(1)} disabled={diaEhHoje} style={{background:'none',border:'none',color:diaEhHoje?'rgba(255,255,255,.2)':'#fff',cursor:diaEhHoje?'default':'pointer',fontSize:14,padding:'2px 6px'}}>›</button>
        </div>
        <button onClick={()=>{if(aba==='denise'||aba==='flavio')registrarVariosRapido(aba,aba==='denise'?extras:extrasF,aba==='denise'?setExtras:setExtrasF);else document.getElementById(`card-registrar-${aba}`)?.scrollIntoView({behavior:'smooth',block:'center'})}} style={{background:`linear-gradient(135deg,${corAba},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>{aba==='denise'||aba==='flavio'?'+ Novo registro':'+ Nova medida'}</button>
      </div>
    </div>

    {aba==='denise'&&<div>
      {renderAdulto({pessoa:'denise',nome:'Denise',cor:C.acc2,variant:'imc'})}
    </div>}

    {aba==='flavio'&&<div>
      {renderAdulto({pessoa:'flavio',nome:'Flávio',cor:C.water,variant:'medidas'})}
    </div>}

    {aba==='domi'&&<div>{renderCrianca('domi','Domi',C.pink,'#9d174d')}</div>}
    {aba==='derick'&&<div>{renderCrianca('derick','Derick',C.ok,'#15803d')}</div>}
  </div>)}

function Alimentacao(){
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
  </div>)}

type ExercicioPlano={nome:string,series?:number,reps?:string,carga?:string,descansoSeg?:number,duracaoSeg?:number,obs?:string}
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
}
function Familia(){
  const {fam,setFam}=React.useContext(FamCtx)
  const [showEdit,setShowEdit]=React.useState(false)
  const [editKey,setEditKey]=React.useState<'domi'|'derick'|null>(null)
  const [local,setLocal]=React.useState(JSON.parse(JSON.stringify(fam)))
  const [showExcecao,setShowExcecao]=React.useState<'domi'|'derick'|null>(null)
  const [excData,setExcData]=React.useState(isoBR(new Date()))
  const [excSemAula,setExcSemAula]=React.useState(false)
  const [excResp,setExcResp]=React.useState('denise')
  const [excHorario,setExcHorario]=React.useState('')
  const [tick,setTick]=React.useState(0)
  const forceRefreshFam=()=>setTick(t=>t+1)
  const days:[number,string][]=[[1,'Seg'],[2,'Ter'],[3,'Qua'],[4,'Qui'],[5,'Sex']]
  const membros=[{id:'denise',nome:'Denise',papel:'Você · mãe',cor:'#8b5cf6'},{id:'flavio',nome:'Flávio',papel:'Pai',cor:'#38bdf8'},{id:'domi',nome:'Domi',papel:'Filha · escola',cor:'#f472b6'},{id:'derick',nome:'Derick',papel:'Filho · escola',cor:'#34d399'}]
  const [eventosFam,setEventosFam]=React.useState<any[]>(()=>lerEventosAgenda())
  const [showNovoComp,setShowNovoComp]=React.useState(false)
  const [novoCompNome,setNovoCompNome]=React.useState('')
  const [novoCompData,setNovoCompData]=React.useState(isoBR(new Date()))
  const [novoCompHora,setNovoCompHora]=React.useState('')
  const [novoCompPessoa,setNovoCompPessoa]=React.useState<'geral'|'domi'|'derick'>('geral')
  async function salvarNovoCompromisso(){
    if(!novoCompNome||!novoCompData)return
    await criarEventoAgenda({nome:novoCompNome,data:novoCompData,hora:novoCompHora,categoria:'familia',pessoa:novoCompPessoa==='geral'?undefined:novoCompPessoa})
    setEventosFam(lerEventosAgenda())
    setNovoCompNome('');setNovoCompHora('');setNovoCompPessoa('geral');setShowNovoComp(false)
  }
  const hojeIsoFam=isoBR(new Date())
  const compromissosFamilia=(()=>{
    const relevantes=eventosFam.filter((e:any)=>!e.ehMestre&&e.data>=hojeIsoFam&&(e.categoria==='familia'||e.pessoa==='domi'||e.pessoa==='derick'))
    const vistos=new Set<string>()
    const unicos:any[]=[]
    relevantes.sort((a:any,b:any)=>(a.data+a.hora).localeCompare(b.data+b.hora)).forEach((e:any)=>{
      const chave=e.recorrenciaId||e.id
      if(vistos.has(chave))return
      vistos.add(chave);unicos.push(e)
    })
    return unicos.slice(0,5)
  })()
  const [avals,setAvals]=React.useState<Record<string,Aval[]>>(()=>{
    try{
      const stored=JSON.parse(localStorage.getItem('dos_avals')||'{}')
      const migrado:Record<string,Aval[]>={}
      Object.keys(stored).forEach(k=>{migrado[k]=(stored[k]||[]).map(migrarAval)})
      return migrado
    }catch{return {domi:[],derick:[]}}
  })
  const [abaKid,setAbaKid]=React.useState<'domi'|'derick'>('domi')
  const [filtroAval,setFiltroAval]=React.useState<'proximas'|'todas'|'realizadas'|'recuperacoes'>('proximas')
  const [novaAval,setNovaAval]=React.useState({data:'',materia:'',conteudo:''})
  const [novoTipoAval,setNovoTipoAval]=React.useState('AV1')
  const [novoPesoAval,setNovoPesoAval]=React.useState('')
  const [loading,setLoading]=React.useState(false)
  const [msg,setMsg]=React.useState('')
  const [previewPDF,setPreviewPDF]=React.useState<Aval[]|null>(null)
  const [previewKid,setPreviewKid]=React.useState<'domi'|'derick'>('domi')
  const pdfRef=React.useRef<HTMLInputElement>(null)
  function saveAvals(kid:string, list:Aval[]){
    const n={...avals,[kid]:list}
    setAvals(n);localStorage.setItem('dos_avals',JSON.stringify(n))
  }
  function addAval(kid:string){
    if(!novaAval.materia)return
    const nova:Aval={data:novaAval.data,materia:novaAval.materia,tipoAvaliacao:novoTipoAval,conteudo:novaAval.conteudo,peso:novoPesoAval||undefined,status:'nao_iniciado'}
    saveAvals(kid,[...(avals[kid]||[]),nova].sort((a,b)=>a.data.localeCompare(b.data)))
    setNovaAval({data:'',materia:'',conteudo:''});setNovoPesoAval('')
    setMsg('✓ Avaliação adicionada!')
    setTimeout(()=>setMsg(''),3000)
  }
  function delAval(kid:string,i:number){saveAvals(kid,(avals[kid]||[]).filter((_,j)=>j!==i))}
  function toggleRealizado(kid:string,i:number){
    const list=[...(avals[kid]||[])]
    list[i]={...list[i],status:list[i].status==='realizado'?'nao_iniciado':'realizado'}
    saveAvals(kid,list)
  }
  function mudarStatus(kid:string,i:number,status:Aval['status']){
    const list=[...(avals[kid]||[])]
    list[i]={...list[i],status}
    saveAvals(kid,list)
  }
  async function uploadPDF(kid:string, file:File){
    setLoading(true);setMsg('Lendo calendário com IA...')
    try{
      const base64=await new Promise<string>((res,rej)=>{
        const r=new FileReader();r.onload=()=>res((r.result as string).split(',')[1]);r.onerror=rej;r.readAsDataURL(file)
      })
      const resp=await fetch('/api/parse-calendar',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({pdfBase64:base64})
      })
      const data=await resp.json()
      if(!resp.ok) throw new Error(data?.error||'Falha ao processar o PDF.')
      const extracted:any[]=data.avaliacoes||[]
      const existentes=avals[kid]||[]
      const novos=extracted.map(migrarAval).filter(n=>!existentes.some(e=>e.data===n.data&&e.materia===n.materia))
      if(novos.length===0){setMsg('Nenhuma avaliação nova encontrada no PDF (todas já estavam cadastradas).')}
      else{setPreviewKid(kid as 'domi'|'derick');setPreviewPDF(novos);setMsg('')}
    }catch(e:any){setMsg(`❌ ${e?.message||'Erro ao ler PDF. Tente novamente.'}`)}
    setLoading(false)
  }
  function removerLinhaPreview(i:number){setPreviewPDF(p=>p?p.filter((_,j)=>j!==i):p)}
  function confirmarImportacaoPDF(){
    if(!previewPDF)return
    saveAvals(previewKid,[...(avals[previewKid]||[]),...previewPDF].sort((a,b)=>a.data.localeCompare(b.data)))
    setMsg(`✓ ${previewPDF.length} avaliações importadas!`)
    setPreviewPDF(null)
    setTimeout(()=>setMsg(''),4000)
  }
  function openEdit(key:'domi'|'derick'){setLocal(JSON.parse(JSON.stringify(fam)));setEditKey(key);setShowEdit(true)}
  function saveEdit(){if(!editKey)return;setFam(local);setShowEdit(false)}
  function abrirExcecao(kid:'domi'|'derick'){
    setExcData(isoBR(new Date()));setExcSemAula(false);setExcResp(fam[kid].responsavel||(kid==='domi'?'denise':'flavio'));setExcHorario('')
    setShowExcecao(kid)
  }
  function salvarExcecaoForm(){
    if(!showExcecao)return
    salvarExcecaoFam(showExcecao,excData,{responsavel:excResp,semAula:excSemAula,horarioBusca:excHorario||undefined})
    setShowExcecao(null);forceRefreshFam()
  }
  const day=new Date().getDay(),sd=(day>=1&&day<=5)?day:1
  const avalsFiltradas=(avals[abaKid]||[]).filter(a=>{
    if(filtroAval==='realizadas')return a.status==='realizado'
    if(filtroAval==='recuperacoes')return a.tipoAvaliacao==='Recuperação'
    if(filtroAval==='proximas'){const dr=diasRestantesAvalGlobal(a.data);return a.status!=='realizado'&&(dr===null||dr>=-1)}
    return true
  }).slice().sort((a,b)=>a.data.localeCompare(b.data))
  void tick
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
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:16}}>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:5}}>Entrada na escola</label><input type="time" value={local[editKey].entrada||''} onChange={e=>setLocal((p:typeof fam)=>({...p,[editKey]:{...p[editKey],entrada:e.target.value}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:15,colorScheme:'dark'}}/></div>
            <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:5}}>Sair de casa</label><input type="time" value={local[editKey].dropOff} onChange={e=>setLocal((p:typeof fam)=>({...p,[editKey]:{...p[editKey],dropOff:e.target.value}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:15,colorScheme:'dark'}}/></div>
          </div>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const,letterSpacing:'.4px',display:'block',marginBottom:5}}>Responsável padrão pela busca</label>
          <select value={local[editKey].responsavel||'denise'} onChange={e=>setLocal((p:typeof fam)=>({...p,[editKey]:{...p[editKey],responsavel:e.target.value}}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:15,marginBottom:16,colorScheme:'dark' as const}}>
            <option value="denise">Denise</option><option value="flavio">Flávio</option>
          </select>
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
    {showExcecao&&<div onClick={e=>{if(e.target===e.currentTarget)setShowExcecao(null)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:400}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`}}>
          <h3 style={{margin:0,fontSize:16}}>Exceção · {showExcecao==='domi'?'Domi':'Derick'}</h3>
          <button onClick={()=>setShowExcecao(null)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          <p style={{fontSize:11.5,color:'rgba(255,255,255,.4)',marginTop:0,marginBottom:14}}>Vale só para a data escolhida. A rotina recorrente não é alterada.</p>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Data</label>
          <input type="date" value={excData} onChange={e=>setExcData(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:14,colorScheme:'dark' as const}}/>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'flex',alignItems:'center',gap:8,marginBottom:14,cursor:'pointer'}}>
            <input type="checkbox" checked={excSemAula} onChange={e=>setExcSemAula(e.target.checked)}/> Sem aula nesse dia
          </label>
          {!excSemAula&&<>
            <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Responsável pela busca</label>
            <select value={excResp} onChange={e=>setExcResp(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:14,colorScheme:'dark' as const}}>
              <option value="denise">Denise</option><option value="flavio">Flávio</option>
            </select>
            <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Horário da busca (opcional, se for diferente do normal)</label>
            <input type="time" value={excHorario} onChange={e=>setExcHorario(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:16,colorScheme:'dark' as const}}/>
          </>}
          <button onClick={salvarExcecaoForm} style={{width:'100%',background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'12px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Salvar exceção</button>
        </div>
      </div>
    </div>}
    {previewPDF&&<div onClick={e=>{if(e.target===e.currentTarget)setPreviewPDF(null)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:560,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Foram identificadas {previewPDF.length} avaliações</h3>
          <button onClick={()=>setPreviewPDF(null)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          <p style={{fontSize:12,color:'rgba(255,255,255,.4)',marginTop:0}}>Revise antes de confirmar. Remova as linhas que não fizerem sentido — o que sobrar aqui será salvo para {previewKid==='domi'?'Domi':'Derick'}.</p>
          {previewPDF.map((a,i)=>(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}>
            <span style={{width:44,color:C.acc2,fontWeight:700,flexShrink:0}}>{a.data}</span>
            <span style={{minWidth:150,flexShrink:0}}>{a.materia}</span>
            <span style={{flex:1,color:'rgba(255,255,255,.5)',fontSize:12}}>{a.conteudo}</span>
            <button onClick={()=>removerLinhaPreview(i)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'4px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button>
          </div>))}
          {previewPDF.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma linha restante.</div>}
        </div>
        <div style={{display:'flex',gap:10,padding:'14px 18px',position:'sticky',bottom:0,background:'#1c1c28'}}>
          <button onClick={()=>setPreviewPDF(null)} style={{flex:1,background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Cancelar</button>
          <button onClick={confirmarImportacaoPDF} disabled={previewPDF.length===0} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer',opacity:previewPDF.length===0?.5:1}}>✓ Confirmar importação</button>
        </div>
      </div>
    </div>}
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Família</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Painel operacional da família · rotina · escola · compromissos</p>
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
        {(['domi','derick'] as const).map(k=>{
          const nome=k==='domi'?'Domi':'Derick'
          const cor=k==='domi'?C.pink:C.ok
          const efet=buscaEfetivaFam(fam,k,hojeIsoFam,sd)
          return(<div key={k} style={{padding:'12px 0',borderBottom:`1px solid ${C.line}`}}>
            <div style={{display:'flex',alignItems:'center',gap:12}}>
              <Avatar id={k} label={nome[0]} size={40} radius={11}/>
              <div style={{flex:1}}><div style={{fontWeight:700,fontSize:14}}>{nome}</div></div>
              {efet.semAula?<span style={{fontSize:11,fontWeight:700,color:C.warn,background:'rgba(251,191,36,.12)',padding:'3px 10px',borderRadius:20,flexShrink:0}}>Sem aula hoje</span>:<div style={{textAlign:'right' as const}}><div style={{fontSize:13,fontWeight:700,color:cor}}>{efet.horario}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>busca</div></div>}
            </div>
            {!efet.semAula&&<div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:8,fontSize:12,color:'rgba(255,255,255,.5)',paddingLeft:52,marginTop:8}}>
              <div><div style={{fontSize:10,color:'rgba(255,255,255,.35)'}}>Entrada</div><div style={{fontWeight:600,color:'#fff'}}>{fam[k].entrada||'—'}</div></div>
              <div><div style={{fontSize:10,color:'rgba(255,255,255,.35)'}}>Sair de casa</div><div style={{fontWeight:600,color:'#fff'}}>{fam[k].dropOff}</div></div>
              <div><div style={{fontSize:10,color:'rgba(255,255,255,.35)'}}>Responsável</div><div style={{fontWeight:600,color:'#fff'}}>{NOME_RESPONSAVEL[efet.responsavel]||efet.responsavel}</div></div>
            </div>}
            <button onClick={()=>abrirExcecao(k)} style={{marginLeft:52,marginTop:8,background:'transparent',border:'none',color:C.acc2,fontSize:11.5,cursor:'pointer',padding:0}}>Registrar exceção para uma data →</button>
          </div>)
        })}
        <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:8}}>Horários baseados na rotina atual. Toque em "Editar rotina" no card da criança pra mudar.</div>
      </Card>
      <Card title="Semana completa">
        <table style={{width:'100%',borderCollapse:'collapse' as const,fontSize:12}}>
          <thead><tr><th style={{textAlign:'left' as const,fontSize:11,color:'rgba(255,255,255,.4)',padding:'6px 8px',borderBottom:`1px solid ${C.line}`}}>Criança</th>{days.map(([d,dn])=>(<th key={d} style={{textAlign:'center' as const,fontSize:11,color:'rgba(255,255,255,.4)',padding:'6px 4px',borderBottom:`1px solid ${C.line}`,background:sd===d?'rgba(139,92,246,.1)':''}}>{dn}</th>))}</tr></thead>
          <tbody>{(['domi','derick'] as const).map(k=>(<tr key={k}><td style={{padding:'10px 8px',borderBottom:`1px solid ${C.line}`,fontWeight:600,color:'#fff'}}>{k==='domi'?'Domi':'Derick'}</td>{days.map(([d])=>(<td key={d} style={{padding:'10px 4px',borderBottom:`1px solid ${C.line}`,textAlign:'center' as const,color:'rgba(255,255,255,.6)',background:sd===d?'rgba(139,92,246,.07)':''}}>{fam[k].pk[d]||'—'}</td>))}</tr>))}</tbody>
        </table>
        <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:10}}>Responsável padrão: Domi · {NOME_RESPONSAVEL[fam.domi.responsavel||'denise']} · Derick · {NOME_RESPONSAVEL[fam.derick.responsavel||'flavio']}</div>
      </Card>
    </div>
    <Card title="📅 Próximos compromissos da família" action={<button onClick={()=>setShowNovoComp(v=>!v)} style={{fontSize:12,color:C.acc2,background:'rgba(139,92,246,.1)',border:'1px solid rgba(139,92,246,.2)',padding:'5px 10px',borderRadius:9,cursor:'pointer',fontWeight:600}}>{showNovoComp?'✕ Cancelar':'+ Novo compromisso'}</button>}>
      {showNovoComp&&<div style={{display:'grid',gridTemplateColumns:'1.6fr .9fr .7fr .9fr auto',gap:8,marginBottom:14,alignItems:'end'}}>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Nome</label><input value={novoCompNome} onChange={e=>setNovoCompNome(e.target.value)} placeholder="Ex: Reunião escolar" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novoCompData} onChange={e=>setNovoCompData(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Hora</label><input type="time" value={novoCompHora} onChange={e=>setNovoCompHora(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Quem</label><select value={novoCompPessoa} onChange={e=>setNovoCompPessoa(e.target.value as 'geral'|'domi'|'derick')} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}><option value="geral">Família toda</option><option value="domi">Domi</option><option value="derick">Derick</option></select></div>
        <button onClick={salvarNovoCompromisso} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>+ Adicionar</button>
      </div>}
      {compromissosFamilia.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum compromisso de família nos próximos dias.</div>}
      {compromissosFamilia.map((e:any,i:number)=>(<div key={i} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:i<compromissosFamilia.length-1?`1px solid ${C.line}`:'none',alignItems:'center'}}>
        <span style={{width:80,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.data}{e.hora?` · ${e.hora}`:''}</span>
        <span style={{width:4,height:20,borderRadius:2,background:e.cor,flexShrink:0}}/>
        <span style={{fontSize:13.5,flex:1}}>{e.nome}</span>
        {e.pessoa&&<span style={{fontSize:11,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.pessoa==='domi'?'Domi':'Derick'}</span>}
      </div>))}
      <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:8}}>Compromissos também podem ser criados direto na Agenda, com categoria "Família".</div>
    </Card>
    <Card title="📚 Calendário Avaliativo Escolar">
      <div style={{display:'flex',gap:8,marginBottom:16}}>
        {(['domi','derick'] as const).map(k=>(<button key={k} onClick={()=>setAbaKid(k)} style={{padding:'8px 18px',borderRadius:20,border:`2px solid ${abaKid===k?(k==='domi'?C.pink:C.ok):'rgba(255,255,255,.1)'}`,background:abaKid===k?`rgba(${k==='domi'?'244,114,182':'52,211,153'},.1)`:'transparent',color:'#fff',cursor:'pointer',fontWeight:600,fontSize:14}}>{k==='domi'?'Domi':'Derick'}</button>))}
      </div>
      {msg&&<div style={{background:msg.startsWith('✓')?'rgba(52,211,153,.1)':msg.startsWith('❌')?'rgba(248,113,113,.1)':'rgba(139,92,246,.1)',border:`1px solid ${msg.startsWith('✓')?'rgba(52,211,153,.3)':msg.startsWith('❌')?'rgba(248,113,113,.3)':'rgba(139,92,246,.25)'}`,borderRadius:10,padding:'10px 14px',fontSize:13,color:msg.startsWith('✓')?C.ok:msg.startsWith('❌')?C.danger:C.acc2,marginBottom:12}}>{msg}</div>}
      <div style={{display:'flex',gap:10,marginBottom:16,flexWrap:'wrap' as const}}>
        <input ref={pdfRef} type="file" accept="application/pdf" style={{display:'none'}} onChange={e=>{const f=e.target.files?.[0];if(f)uploadPDF(abaKid,f);if(pdfRef.current)pdfRef.current.value=''}}/>
        <button onClick={()=>pdfRef.current?.click()} disabled={loading} style={{display:'inline-flex',alignItems:'center',gap:8,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer',opacity:loading?0.6:1}}>
          {loading?'⏳ Lendo PDF...':'📄 Importar PDF do calendário'}
        </button>
        <span style={{fontSize:12,color:'rgba(255,255,255,.4)',alignSelf:'center'}}>ou adicione manualmente →</span>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'.8fr 1.3fr .8fr .6fr 1.6fr auto',gap:8,marginBottom:12,alignItems:'end'}}>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data (DD/MM)</label><input value={novaAval.data} onChange={e=>setNovaAval(p=>({...p,data:e.target.value}))} placeholder="11/08" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Matéria</label><input value={novaAval.materia} onChange={e=>setNovaAval(p=>({...p,materia:e.target.value}))} placeholder="📝 Português" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Tipo</label><select value={novoTipoAval} onChange={e=>setNovoTipoAval(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}>{['AV1','AV2','AV3','Trabalho','Produção textual','Recuperação','Outros'].map(t=>(<option key={t}>{t}</option>))}</select></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Peso</label><input value={novoPesoAval} onChange={e=>setNovoPesoAval(e.target.value)} placeholder="10" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Conteúdo</label><input value={novaAval.conteudo} onChange={e=>setNovaAval(p=>({...p,conteudo:e.target.value}))} placeholder="Ex: Poema de Cordel" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <button onClick={()=>addAval(abaKid)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>+ Adicionar</button>
      </div>
      <div style={{display:'flex',gap:6,marginBottom:12,flexWrap:'wrap' as const}}>
        {(['proximas','todas','realizadas','recuperacoes'] as const).map(f=>(<button key={f} onClick={()=>setFiltroAval(f)} style={{background:filtroAval===f?`linear-gradient(135deg,${C.acc},#7c3aed)`:'transparent',color:filtroAval===f?'#fff':'rgba(255,255,255,.5)',border:`1px solid ${filtroAval===f?'transparent':C.line}`,borderRadius:20,padding:'6px 14px',fontSize:12,fontWeight:600,cursor:'pointer'}}>{f==='proximas'?'Próximas':f==='todas'?'Todas':f==='realizadas'?'Realizadas':'Recuperações'}</button>))}
      </div>
      <div style={{maxHeight:400,overflowY:'auto' as const}}>
        {avalsFiltradas.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma avaliação nesse filtro.</div>}
        {avalsFiltradas.map((a)=>{
          const i=(avals[abaKid]||[]).indexOf(a)
          const diasRestantes=diasRestantesAvalGlobal(a.data)
          const urgente=diasRestantes!==null&&diasRestantes>=0&&diasRestantes<=3
          const passada=diasRestantes!==null&&diasRestantes<0
          const feita=a.status==='realizado'
          return(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 12px',borderRadius:10,marginBottom:4,background:feita?'rgba(52,211,153,.05)':urgente?'rgba(248,113,113,.08)':'rgba(255,255,255,.03)',border:feita?'1px solid rgba(52,211,153,.15)':urgente?'1px solid rgba(248,113,113,.2)':`1px solid ${C.line}`,opacity:passada&&!feita?0.6:1,flexWrap:'wrap' as const}}>
            <input type="checkbox" checked={feita} onChange={()=>toggleRealizado(abaKid,i)} style={{width:16,height:16,cursor:'pointer',accentColor:C.acc,flexShrink:0}}/>
            <span style={{width:44,fontSize:12,fontWeight:700,color:urgente?C.danger:passada?'rgba(255,255,255,.3)':C.acc2,flexShrink:0}}>{a.data}</span>
            <span style={{fontWeight:600,fontSize:13,color:feita?'rgba(255,255,255,.4)':'#fff',textDecoration:feita?'line-through':'none',minWidth:150,flexShrink:0}}>{a.materia}</span>
            <span style={{flex:1,fontSize:12,color:'rgba(255,255,255,.5)',minWidth:120}}>{a.conteudo}{a.peso?` · peso ${a.peso}`:''}</span>
            <select value={a.status} onChange={e=>mudarStatus(abaKid,i,e.target.value as Aval['status'])} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:8,padding:'3px 8px',fontSize:11,color:STATUS_AVAL_COR[a.status],flexShrink:0,colorScheme:'dark' as const}}>
              {(['nao_iniciado','estudando','revisado','pronto','realizado'] as const).map(st=>(<option key={st} value={st}>{STATUS_AVAL_LABEL[st]}</option>))}
            </select>
            {diasRestantes!==null&&!passada&&!feita&&<span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:urgente?'rgba(248,113,113,.2)':diasRestantes<=7?'rgba(251,191,36,.15)':'rgba(52,211,153,.1)',color:urgente?C.danger:diasRestantes<=7?C.warn:C.ok,flexShrink:0,whiteSpace:'nowrap' as const}}>{diasRestantes===0?'Hoje!':diasRestantes===1?'Amanhã!':urgente?`${diasRestantes}d ⚠️`:`${diasRestantes}d`}</span>}
            {passada&&!feita&&<span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:'rgba(255,255,255,.07)',color:'rgba(255,255,255,.3)',flexShrink:0}}>atrasada</span>}
            <button onClick={()=>delAval(abaKid,i)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'3px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button>
          </div>)
        })}
      </div>
      {filtroAval!=='todas'&&<button onClick={()=>setFiltroAval('todas')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12.5,fontWeight:600,cursor:'pointer',marginTop:10,padding:0}}>Ver calendário completo →</button>}
    </Card>
  </div>)}

type ChecklistItemTrab={id:string,texto:string,feito:boolean}
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
const CORES_PROJETO_TRAB:Record<string,string>={'PixelSAV':C.acc2,'SecaVita':C.ok,'Impressões da Domi':C.pink,'Lumera':C.water,'Outros':C.warn}
const PALETA_PROJETO_FALLBACK_TRAB=[C.acc2,C.ok,C.pink,C.water,C.warn,C.teal,'#fb923c']
function hexParaRgbaTrab(hex:string,alpha:number):string{
  const h=hex.replace('#','')
  const r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16)
  return `rgba(${r},${g},${b},${alpha})`
}
function corProjetoTrab(nome:string):string{
  if(CORES_PROJETO_TRAB[nome])return CORES_PROJETO_TRAB[nome]
  let hash=0
  for(let i=0;i<nome.length;i++)hash=(hash*31+nome.charCodeAt(i))>>>0
  return PALETA_PROJETO_FALLBACK_TRAB[hash%PALETA_PROJETO_FALLBACK_TRAB.length]
}

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
        <span style={{fontSize:11,background:hexParaRgbaTrab(corProjetoTrab(tk.p),.15),color:corProjetoTrab(tk.p),padding:'2px 8px',borderRadius:20}}>{tk.p}</span>
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
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><span style={{fontSize:11,color:corProjetoTrab(tk.p),fontWeight:600}}>{tk.p}</span>{pl&&<span style={{fontSize:10.5,color:pl.cor}}>{pl.texto}</span>}</div>
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
}
type StatusLivroDev='quero_ler'|'na_fila'|'lendo'|'pausado'|'concluido'|'abandonado'
type LivroDev={id:string,titulo:string,autor:string,totalPaginas:number,paginaAtual:number,status:StatusLivroDev,dataInicio?:string,dataConclusao?:string,observacao?:string}
type SessaoLeituraDev={id:string,livroId:string,data:string,paginas:number,minutos:number,aprendizado?:string,observacao?:string,origem?:'app'|'whatsapp'}
type StatusCursoDev='quero_estudar'|'andamento'|'pausado'|'concluido'
type CursoDev={id:string,nome:string,tema?:string,fonte?:string,status:StatusCursoDev,progressoPct?:number,observacao?:string,dataInicio?:string,dataConclusao?:string}
type SessaoEstudoDev={id:string,cursoId:string,data:string,assunto?:string,minutos:number,aprendizado?:string,observacao?:string,origem?:'app'|'whatsapp'}
type MetaDev={id:string,label:string,tipo:'minutos_dia_leitura'|'livros_mes'|'sessoes_semana_estudo'|'minutos_semana_dev',valor:number,ativa:boolean}
const STATUS_LIVRO_LABEL:Record<StatusLivroDev,string>={quero_ler:'Quero ler',na_fila:'Na fila',lendo:'Lendo',pausado:'Pausado',concluido:'Concluído',abandonado:'Abandonado'}
const STATUS_LIVRO_COR:Record<StatusLivroDev,string>={quero_ler:'rgba(255,255,255,.4)',na_fila:C.water,lendo:C.acc2,pausado:C.warn,concluido:C.ok,abandonado:'rgba(255,255,255,.3)'}
const STATUS_CURSO_LABEL:Record<StatusCursoDev,string>={quero_estudar:'Quero estudar',andamento:'Em andamento',pausado:'Pausado',concluido:'Concluído'}
const STATUS_CURSO_COR:Record<StatusCursoDev,string>={quero_estudar:'rgba(255,255,255,.4)',andamento:C.acc2,pausado:C.warn,concluido:C.ok}
function novoIdDev(){return `${Date.now()}_${Math.random().toString(36).slice(2,8)}`}
function migrarBibliotecaDev():{livros:LivroDev[],sessoes:SessaoLeituraDev[]}{
  try{
    const existentes=JSON.parse(localStorage.getItem('dos_livros')||'null')
    if(Array.isArray(existentes)){
      let sessoesExistentes:SessaoLeituraDev[]=[]
      try{sessoesExistentes=JSON.parse(localStorage.getItem('dos_sessoes_leitura')||'[]')}catch{}
      return {livros:existentes,sessoes:sessoesExistentes}
    }
  }catch{}
  let estanteOld:any[]=[],atualOld:any=null,leiturasOld:any[]=[]
  try{estanteOld=JSON.parse(localStorage.getItem('dos_estante')||'[]')}catch{}
  try{atualOld=JSON.parse(localStorage.getItem('dos_livro_atual')||'null')}catch{}
  try{leiturasOld=JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{}
  const mapStatusAntigo:Record<string,StatusLivroDev>={'lendo':'lendo','concluído':'concluido','quero ler':'quero_ler'}
  const livros:LivroDev[]=estanteOld.map((e:any):LivroDev=>({id:novoIdDev(),titulo:e.titulo||'',autor:e.autor||'',totalPaginas:0,paginaAtual:0,status:mapStatusAntigo[e.status]||'quero_ler'}))
  let livroLendoId:string|null=null
  if(atualOld&&atualOld.titulo){
    const norm=(x:string)=>(x||'').trim().toLowerCase()
    const match=livros.find(l=>norm(l.titulo)===norm(atualOld.titulo))
    if(match){
      match.totalPaginas=Number(atualOld.totalPaginas)||0
      match.paginaAtual=Number(atualOld.paginaAtual)||0
      match.status='lendo'
      livroLendoId=match.id
    }else{
      const novo:LivroDev={id:novoIdDev(),titulo:atualOld.titulo,autor:atualOld.autor||'',totalPaginas:Number(atualOld.totalPaginas)||0,paginaAtual:Number(atualOld.paginaAtual)||0,status:'lendo'}
      livros.push(novo)
      livroLendoId=novo.id
    }
  }
  const sessoes:SessaoLeituraDev[]=livroLendoId?leiturasOld.map((l:any,i:number):SessaoLeituraDev=>({id:`legado_${i}`,livroId:livroLendoId as string,data:l.data,paginas:Number(l.pag)||0,minutos:Number(l.min)||0,aprendizado:l.apren||undefined,origem:'app'})):[]
  localStorage.setItem('dos_livros',JSON.stringify(livros))
  localStorage.setItem('dos_sessoes_leitura',JSON.stringify(sessoes))
  return {livros,sessoes}
}
function lerLivrosDev():LivroDev[]{return migrarBibliotecaDev().livros}
function salvarLivrosDev(v:LivroDev[]){localStorage.setItem('dos_livros',JSON.stringify(v))}
function lerSessoesLeituraDev():SessaoLeituraDev[]{
  try{const v=JSON.parse(localStorage.getItem('dos_sessoes_leitura')||'null');if(Array.isArray(v))return v}catch{}
  return migrarBibliotecaDev().sessoes
}
function salvarSessoesLeituraDev(v:SessaoLeituraDev[]){localStorage.setItem('dos_sessoes_leitura',JSON.stringify(v))}
function lerCursosDev():CursoDev[]{try{return JSON.parse(localStorage.getItem('dos_cursos')||'[]')}catch{return []}}
function salvarCursosDev(v:CursoDev[]){localStorage.setItem('dos_cursos',JSON.stringify(v))}
function lerSessoesEstudoDev():SessaoEstudoDev[]{try{return JSON.parse(localStorage.getItem('dos_sessoes_estudo')||'[]')}catch{return []}}
function salvarSessoesEstudoDev(v:SessaoEstudoDev[]){localStorage.setItem('dos_sessoes_estudo',JSON.stringify(v))}
const METAS_DEV_PADRAO:MetaDev[]=[
  {id:'m1',label:'Minutos de leitura por dia',tipo:'minutos_dia_leitura',valor:20,ativa:true},
  {id:'m2',label:'Livros por mês',tipo:'livros_mes',valor:1,ativa:true},
  {id:'m3',label:'Sessões de estudo por semana',tipo:'sessoes_semana_estudo',valor:3,ativa:true},
  {id:'m4',label:'Minutos de desenvolvimento por semana',tipo:'minutos_semana_dev',valor:120,ativa:false},
]
function lerMetasDev():MetaDev[]{
  try{const v=JSON.parse(localStorage.getItem('dos_metas_dev')||'null');if(Array.isArray(v))return v}catch{}
  localStorage.setItem('dos_metas_dev',JSON.stringify(METAS_DEV_PADRAO))
  return METAS_DEV_PADRAO
}
function salvarMetasDev(v:MetaDev[]){localStorage.setItem('dos_metas_dev',JSON.stringify(v))}

function Desenvolvimento(){
  const hojeIsoDev=isoBR(new Date())
  const [livros,setLivrosRaw]=React.useState<LivroDev[]>(lerLivrosDev)
  const setLivros=(fn:LivroDev[]|((p:LivroDev[])=>LivroDev[]))=>setLivrosRaw(p=>{const n=typeof fn==='function'?(fn as any)(p):fn;salvarLivrosDev(n);return n})
  const [sessoesLeitura,setSessoesLeituraRaw]=React.useState<SessaoLeituraDev[]>(lerSessoesLeituraDev)
  const setSessoesLeitura=(fn:SessaoLeituraDev[]|((p:SessaoLeituraDev[])=>SessaoLeituraDev[]))=>setSessoesLeituraRaw(p=>{const n=typeof fn==='function'?(fn as any)(p):fn;salvarSessoesLeituraDev(n);return n})
  const [cursos,setCursosRaw]=React.useState<CursoDev[]>(lerCursosDev)
  const setCursos=(fn:CursoDev[]|((p:CursoDev[])=>CursoDev[]))=>setCursosRaw(p=>{const n=typeof fn==='function'?(fn as any)(p):fn;salvarCursosDev(n);return n})
  const [sessoesEstudo,setSessoesEstudoRaw]=React.useState<SessaoEstudoDev[]>(lerSessoesEstudoDev)
  const setSessoesEstudo=(fn:SessaoEstudoDev[]|((p:SessaoEstudoDev[])=>SessaoEstudoDev[]))=>setSessoesEstudoRaw(p=>{const n=typeof fn==='function'?(fn as any)(p):fn;salvarSessoesEstudoDev(n);return n})
  const [metas,setMetasRaw]=React.useState<MetaDev[]>(lerMetasDev)
  const setMetas=(fn:MetaDev[]|((p:MetaDev[])=>MetaDev[]))=>setMetasRaw(p=>{const n=typeof fn==='function'?(fn as any)(p):fn;salvarMetasDev(n);return n})

  const [filtroPrincipal,setFiltroPrincipal]=React.useState<'tudo'|'livros'|'cursos'>('tudo')
  const [buscaDev,setBuscaDev]=React.useState('')
  const [filtroEstante,setFiltroEstante]=React.useState<'todos'|StatusLivroDev>('todos')
  const [showRegistrar,setShowRegistrar]=React.useState(false)
  const [regPagina,setRegPagina]=React.useState('')
  const [regMinutos,setRegMinutos]=React.useState('')
  const [regAprendizado,setRegAprendizado]=React.useState('')
  const [regObs,setRegObs]=React.useState('')
  const [novoLivroTitulo,setNovoLivroTitulo]=React.useState('')
  const [novoLivroAutor,setNovoLivroAutor]=React.useState('')
  const [novoLivroPaginas,setNovoLivroPaginas]=React.useState('')
  const [novoLivroStatus,setNovoLivroStatus]=React.useState<StatusLivroDev>('quero_ler')
  const [showHistCompleto,setShowHistCompleto]=React.useState(false)
  const [novoCursoNome,setNovoCursoNome]=React.useState('')
  const [novoCursoTema,setNovoCursoTema]=React.useState('')

  const livroLendo=livros.find(l=>l.status==='lendo')||null

  function iniciarLeitura(id:string){setLivros(ls=>ls.map(l=>l.id===id?{...l,status:'lendo',dataInicio:l.dataInicio||hojeIsoDev}:l))}
  function pausarLivro(id:string){setLivros(ls=>ls.map(l=>l.id===id?{...l,status:'pausado'}:l))}
  function concluirLivro(id:string){setLivros(ls=>ls.map(l=>l.id===id?{...l,status:'concluido',dataConclusao:hojeIsoDev}:l))}
  function abandonarLivro(id:string){setLivros(ls=>ls.map(l=>l.id===id?{...l,status:'abandonado'}:l))}
  function addLivro(){
    if(!novoLivroTitulo.trim())return
    const novo:LivroDev={id:novoIdDev(),titulo:novoLivroTitulo.trim(),autor:novoLivroAutor.trim(),totalPaginas:Number(novoLivroPaginas)||0,paginaAtual:0,status:novoLivroStatus,dataInicio:novoLivroStatus==='lendo'?hojeIsoDev:undefined}
    setLivros(ls=>[...ls,novo])
    setNovoLivroTitulo('');setNovoLivroAutor('');setNovoLivroPaginas('');setNovoLivroStatus('quero_ler')
  }
  function abrirRegistrar(){
    if(!livroLendo)return
    setRegPagina(String(livroLendo.paginaAtual));setRegMinutos('');setRegAprendizado('');setRegObs('');setShowRegistrar(true)
  }
  function salvarRegistroLeitura(){
    if(!livroLendo)return
    const novaPagina=Math.max(livroLendo.paginaAtual,Number(regPagina)||livroLendo.paginaAtual)
    const paginasLidas=Math.max(0,novaPagina-livroLendo.paginaAtual)
    const sessao:SessaoLeituraDev={id:novoIdDev(),livroId:livroLendo.id,data:hojeIsoDev,paginas:paginasLidas,minutos:Number(regMinutos)||0,aprendizado:regAprendizado.trim()||undefined,observacao:regObs.trim()||undefined,origem:'app'}
    setSessoesLeitura(s=>[sessao,...s])
    setLivros(ls=>ls.map(l=>l.id===livroLendo.id?{...l,paginaAtual:novaPagina}:l))
    setShowRegistrar(false)
  }
  function addCurso(){
    if(!novoCursoNome.trim())return
    const novo:CursoDev={id:novoIdDev(),nome:novoCursoNome.trim(),tema:novoCursoTema.trim()||undefined,status:'andamento',dataInicio:hojeIsoDev}
    setCursos(cs=>[...cs,novo])
    setNovoCursoNome('');setNovoCursoTema('')
  }
  function mudarStatusCurso(id:string,status:StatusCursoDev){
    setCursos(cs=>cs.map(c=>c.id===id?{...c,status,dataConclusao:status==='concluido'?hojeIsoDev:c.dataConclusao}:c))
  }
  function definirProgressoCurso(id:string){
    const curso=cursos.find(c=>c.id===id);if(!curso)return
    const v=window.prompt('Progresso (%)? Deixe em branco pra não definir.',curso.progressoPct!=null?String(curso.progressoPct):'')
    if(v===null)return
    setCursos(cs=>cs.map(c=>c.id===id?{...c,progressoPct:v.trim()?Math.min(100,Math.max(0,Number(v))):undefined}:c))
  }
  function registrarSessaoEstudo(id:string){
    const curso=cursos.find(c=>c.id===id);if(!curso)return
    const minutos=window.prompt(`Quantos minutos você estudou de "${curso.nome}"?`,'30')
    if(minutos===null||!minutos.trim())return
    const assunto=window.prompt('Aula/assunto (opcional)','')
    const aprendizado=window.prompt('O que você aprendeu? (opcional)','')
    const sessao:SessaoEstudoDev={id:novoIdDev(),cursoId:id,data:hojeIsoDev,assunto:assunto&&assunto.trim()?assunto.trim():undefined,minutos:Number(minutos)||0,aprendizado:aprendizado&&aprendizado.trim()?aprendizado.trim():undefined,origem:'app'}
    setSessoesEstudo(s=>[sessao,...s])
  }

  const pctLivroLendo=livroLendo&&livroLendo.totalPaginas>0?Math.min(100,Math.round(livroLendo.paginaAtual/livroLendo.totalPaginas*100)):0
  const paginasRestantes=livroLendo?Math.max(0,livroLendo.totalPaginas-livroLendo.paginaAtual):0
  const sessoesDoLivroLendo=livroLendo?sessoesLeitura.filter(s=>s.livroId===livroLendo.id):[]
  const ultimaLeitura=sessoesDoLivroLendo[0]||null

  const diasComLeituraDev=new Set(sessoesLeitura.map(s=>s.data))
  let sequenciaLeitura=0
  const dCursorSeq=new Date()
  if(!diasComLeituraDev.has(hojeIsoDev))dCursorSeq.setDate(dCursorSeq.getDate()-1)
  while(diasComLeituraDev.has(isoBR(dCursorSeq))){sequenciaLeitura++;dCursorSeq.setDate(dCursorSeq.getDate()-1)}
  let melhorSequencia=0,seqTmp=0
  const diasOrdenados=Array.from(diasComLeituraDev).sort()
  for(let i=0;i<diasOrdenados.length;i++){
    if(i>0){
      const ant=new Date(diasOrdenados[i-1]+'T12:00:00'),atual=new Date(diasOrdenados[i]+'T12:00:00')
      const diff=Math.round((atual.getTime()-ant.getTime())/86400000)
      seqTmp=diff===1?seqTmp+1:1
    }else seqTmp=1
    if(seqTmp>melhorSequencia)melhorSequencia=seqTmp
  }

  const segundaDev=(()=>{const d=new Date();const dw=d.getDay();const diff=(dw===0?-6:1-dw);d.setDate(d.getDate()+diff);d.setHours(0,0,0,0);return d})()
  const segIsoDev=isoBR(segundaDev)
  const minutosSemanaDev=sessoesLeitura.filter(s=>s.data>=segIsoDev).reduce((a,s)=>a+s.minutos,0)+sessoesEstudo.filter(s=>s.data>=segIsoDev).reduce((a,s)=>a+s.minutos,0)
  const anoAtualDev=hojeIsoDev.slice(0,4)
  const concluidosNoAno=livros.filter(l=>l.status==='concluido'&&l.dataConclusao&&l.dataConclusao.slice(0,4)===anoAtualDev).length

  const livrosFiltrados=livros.filter(l=>filtroEstante==='todos'||l.status===filtroEstante)
  const cursosVisiveis=filtroPrincipal==='livros'?[]:cursos
  const livrosVisiveis=filtroPrincipal==='cursos'?[]:livrosFiltrados

  type AprendizadoItem={id:string,data:string,origem:'Livro'|'Curso',nome:string,texto:string}
  const aprendizados:AprendizadoItem[]=[
    ...sessoesLeitura.filter(s=>s.aprendizado).map(s=>({id:s.id,data:s.data,origem:'Livro' as const,nome:livros.find(l=>l.id===s.livroId)?.titulo||'—',texto:s.aprendizado as string})),
    ...(filtroPrincipal==='livros'?[]:sessoesEstudo.filter(s=>s.aprendizado).map(s=>({id:s.id,data:s.data,origem:'Curso' as const,nome:cursos.find(c=>c.id===s.cursoId)?.nome||'—',texto:s.aprendizado as string}))),
  ].sort((a,b)=>b.data.localeCompare(a.data))
  const buscaDevLower=buscaDev.trim().toLowerCase()
  const aprendizadosFiltrados=buscaDevLower?aprendizados.filter(a=>(a.nome+' '+a.texto).toLowerCase().includes(buscaDevLower)):aprendizados

  const historicoUnificado=[
    ...sessoesLeitura.map(s=>({id:s.id,data:s.data,tipo:'Livro' as const,nome:livros.find(l=>l.id===s.livroId)?.titulo||'—',detalhe:`${s.paginas} páginas · ${s.minutos} min`,aprendizado:s.aprendizado})),
    ...sessoesEstudo.map(s=>({id:s.id,data:s.data,tipo:'Curso' as const,nome:cursos.find(c=>c.id===s.cursoId)?.nome||'—',detalhe:`${s.minutos} min${s.assunto?` · ${s.assunto}`:''}`,aprendizado:s.aprendizado})),
  ].sort((a,b)=>b.data.localeCompare(a.data))

  function calcMetaProgressoDev(m:MetaDev){
    if(m.tipo==='minutos_dia_leitura'){const v=sessoesLeitura.filter(s=>s.data===hojeIsoDev).reduce((a,s)=>a+s.minutos,0);return {atual:v,alvo:m.valor,pct:Math.min(100,Math.round(v/m.valor*100))}}
    if(m.tipo==='livros_mes'){const mesAtual=hojeIsoDev.slice(0,7);const v=livros.filter(l=>l.status==='concluido'&&l.dataConclusao&&l.dataConclusao.slice(0,7)===mesAtual).length;return {atual:v,alvo:m.valor,pct:Math.min(100,Math.round(v/m.valor*100))}}
    if(m.tipo==='sessoes_semana_estudo'){const v=sessoesEstudo.filter(s=>s.data>=segIsoDev).length;return {atual:v,alvo:m.valor,pct:Math.min(100,Math.round(v/m.valor*100))}}
    const v=minutosSemanaDev;return {atual:v,alvo:m.valor,pct:Math.min(100,Math.round(v/m.valor*100))}
  }
  const ultimos30Dev=Array.from({length:30},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(29-i));return isoBR(d)})
  const diasComAtividadeDev=new Set([...sessoesLeitura.map(s=>s.data),...sessoesEstudo.map(s=>s.data)])
  const diasAtivos30=ultimos30Dev.filter(d=>diasComAtividadeDev.has(d)).length
  const pctConsistencia30=Math.round(diasAtivos30/30*100)
  const diasDesenvolvimentoMes=new Set(Array.from(diasComAtividadeDev).filter(d=>d.slice(0,7)===hojeIsoDev.slice(0,7))).size
  const diasLeituraMes=new Set(Array.from(diasComLeituraDev).filter(d=>d.slice(0,7)===hojeIsoDev.slice(0,7))).size

  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Desenvolvimento</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:16}}>Biblioteca pessoal · estudos · progresso</p>

    <div style={{display:'flex',gap:8,marginBottom:16}}>
      {(['tudo','livros','cursos'] as const).map(f=>(<button key={f} onClick={()=>setFiltroPrincipal(f)} style={{background:filtroPrincipal===f?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,color:'#fff',border:`1px solid ${filtroPrincipal===f?'transparent':C.line}`,borderRadius:10,padding:'8px 16px',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>{f==='tudo'?'Tudo':f==='livros'?'Livros':'Cursos/Estudos'}</button>))}
    </div>

    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(170px,1fr))',gap:10,marginBottom:20}}>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Livro atual</div><div style={{fontSize:15,fontWeight:800}}>{livroLendo?livroLendo.titulo:'—'}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>{livroLendo?livroLendo.autor:'nenhum livro em leitura'}</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Progresso</div><div style={{fontSize:22,fontWeight:800}}>{pctLivroLendo}%</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>do livro atual</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Sequência de leitura</div><div style={{fontSize:22,fontWeight:800}}>{sequenciaLeitura}d 🔥</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>melhor: {melhorSequencia}d</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Minutos esta semana</div><div style={{fontSize:22,fontWeight:800}}>{minutosSemanaDev}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>leitura + estudo</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Concluídos no ano</div><div style={{fontSize:22,fontWeight:800,color:C.ok}}>{concluidosNoAno}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>livros</div></div>
    </div>

    <div style={{display:'grid',gridTemplateColumns:'1.1fr 1fr',gap:16,marginBottom:16}}>
      {filtroPrincipal!=='cursos'&&<Card title="Lendo agora">
        {!livroLendo?(
          <div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum livro marcado como "Lendo". Escolha um na sua estante abaixo.</div>
        ):(<>
          <div style={{fontSize:17,fontWeight:800}}>{livroLendo.titulo}</div>
          <div style={{fontSize:12.5,color:'rgba(255,255,255,.5)',marginBottom:12}}>{livroLendo.autor}</div>
          {livroLendo.totalPaginas>0&&<>
            <div style={{display:'flex',justifyContent:'space-between',fontSize:12.5,color:'rgba(255,255,255,.5)',marginBottom:6}}><span>Página {livroLendo.paginaAtual} de {livroLendo.totalPaginas}</span><span>{pctLivroLendo}% concluído</span></div>
            <div style={{height:8,borderRadius:4,background:C.s3,overflow:'hidden',marginBottom:12}}><div style={{height:'100%',width:`${pctLivroLendo}%`,borderRadius:4,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div style={{background:C.s2,borderRadius:10,padding:'8px 12px'}}><div style={{fontSize:10,color:'rgba(255,255,255,.35)'}}>Páginas restantes</div><div style={{fontWeight:700}}>{paginasRestantes}</div></div>
              <div style={{background:C.s2,borderRadius:10,padding:'8px 12px'}}><div style={{fontSize:10,color:'rgba(255,255,255,.35)'}}>Última leitura</div><div style={{fontWeight:700}}>{ultimaLeitura?new Date(ultimaLeitura.data+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}):'—'}</div></div>
            </div>
          </>}
          {showRegistrar&&<div style={{background:C.bg,border:`1px solid ${C.line}`,borderRadius:12,padding:14,marginBottom:14}}>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
              <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Página atual</label><input type="number" value={regPagina} onChange={e=>setRegPagina(e.target.value)} style={{width:'100%',background:C.s2,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'8px 10px',color:'#fff',fontSize:13}}/></div>
              <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Minutos</label><input type="number" value={regMinutos} onChange={e=>setRegMinutos(e.target.value)} placeholder="20" style={{width:'100%',background:C.s2,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'8px 10px',color:'#fff',fontSize:13}}/></div>
            </div>
            <label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>O que aprendi?</label>
            <input value={regAprendizado} onChange={e=>setRegAprendizado(e.target.value)} placeholder="Ex: Ambiente influencia o comportamento" style={{width:'100%',background:C.s2,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'8px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
            <label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Observação (opcional)</label>
            <input value={regObs} onChange={e=>setRegObs(e.target.value)} style={{width:'100%',background:C.s2,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'8px 10px',color:'#fff',fontSize:13,marginBottom:12}}/>
            <div style={{display:'flex',gap:8}}>
              <button onClick={()=>setShowRegistrar(false)} style={{flex:1,background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',borderRadius:8,padding:'9px',fontSize:12.5,cursor:'pointer'}}>Cancelar</button>
              <button onClick={salvarRegistroLeitura} style={{flex:2,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',borderRadius:8,padding:'9px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>✓ Salvar sessão</button>
            </div>
          </div>}
          <div style={{display:'flex',gap:8,flexWrap:'wrap' as const}}>
            <button onClick={abrirRegistrar} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer',minWidth:140}}>📖 Registrar leitura</button>
            <button onClick={()=>pausarLivro(livroLendo.id)} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:10,padding:'11px 16px',fontSize:13,fontWeight:600,cursor:'pointer'}}>⏸ Pausar</button>
            <button onClick={()=>concluirLivro(livroLendo.id)} style={{background:'rgba(52,211,153,.12)',border:'1px solid rgba(52,211,153,.3)',color:C.ok,borderRadius:10,padding:'11px 16px',fontSize:13,fontWeight:600,cursor:'pointer'}}>✓ Concluir</button>
          </div>
        </>)}
      </Card>}

      <Card title="Aprendizados recentes">
        <input value={buscaDev} onChange={e=>setBuscaDev(e.target.value)} placeholder="🔎 Buscar aprendizados…" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'8px 10px',color:'#fff',fontSize:12.5,marginBottom:12}}/>
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {aprendizadosFiltrados.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum aprendizado registrado ainda.</div>}
          {aprendizadosFiltrados.map(a=>(<div key={a.id} style={{padding:'9px 0',borderBottom:`1px solid ${C.line}`}}>
            <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:3}}><span>{a.origem} · {a.nome}</span><span>{new Date(a.data+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span></div>
            <div style={{fontSize:13}}>"{a.texto}"</div>
          </div>))}
        </div>
      </Card>
    </div>

    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginBottom:16}}>
      {filtroPrincipal!=='cursos'&&<Card title="Minha estante">
        <div style={{display:'flex',gap:6,marginBottom:12,flexWrap:'wrap' as const}}>
          {(['todos','quero_ler','na_fila','lendo','pausado','concluido'] as const).map(f=>(<button key={f} onClick={()=>setFiltroEstante(f)} style={{background:filtroEstante===f?C.acc:'transparent',color:filtroEstante===f?'#fff':'rgba(255,255,255,.5)',border:`1px solid ${filtroEstante===f?'transparent':C.line}`,borderRadius:20,padding:'5px 11px',fontSize:11,fontWeight:600,cursor:'pointer'}}>{f==='todos'?'Todos':STATUS_LIVRO_LABEL[f]}</button>))}
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr .6fr auto',gap:6,marginBottom:12}}>
          <input value={novoLivroTitulo} onChange={e=>setNovoLivroTitulo(e.target.value)} placeholder="Título" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12}}/>
          <input value={novoLivroAutor} onChange={e=>setNovoLivroAutor(e.target.value)} placeholder="Autor" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12}}/>
          <input type="number" value={novoLivroPaginas} onChange={e=>setNovoLivroPaginas(e.target.value)} placeholder="Págs" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12}}/>
          <button onClick={addLivro} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:8,padding:'7px 12px',fontSize:12,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>+ Adicionar</button>
        </div>
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {livrosVisiveis.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum livro nesse filtro.</div>}
          {livrosVisiveis.map(l=>(<div key={l.id} style={{padding:'9px 0',borderBottom:`1px solid ${C.line}`}}>
            <div style={{display:'flex',alignItems:'center',gap:8}}>
              <div style={{flex:1,minWidth:0}}><div style={{fontWeight:600,fontSize:13,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' as const}}>{l.titulo}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{l.autor}</div></div>
              <span style={{fontSize:10.5,padding:'2px 8px',borderRadius:20,background:'rgba(255,255,255,.07)',color:STATUS_LIVRO_COR[l.status],flexShrink:0}}>{STATUS_LIVRO_LABEL[l.status]}</span>
            </div>
            <div style={{display:'flex',gap:6,marginTop:6,flexWrap:'wrap' as const}}>
              {l.status!=='lendo'&&l.status!=='concluido'&&<button onClick={()=>iniciarLeitura(l.id)} style={{fontSize:10.5,background:'transparent',border:`1px solid ${C.line}`,color:C.acc2,borderRadius:6,padding:'3px 8px',cursor:'pointer'}}>Começar a ler</button>}
              {l.status==='lendo'&&<button onClick={()=>pausarLivro(l.id)} style={{fontSize:10.5,background:'transparent',border:`1px solid ${C.line}`,color:C.warn,borderRadius:6,padding:'3px 8px',cursor:'pointer'}}>Pausar</button>}
              {l.status!=='concluido'&&<button onClick={()=>concluirLivro(l.id)} style={{fontSize:10.5,background:'transparent',border:`1px solid ${C.line}`,color:C.ok,borderRadius:6,padding:'3px 8px',cursor:'pointer'}}>Concluir</button>}
              {l.status!=='abandonado'&&l.status!=='concluido'&&<button onClick={()=>abandonarLivro(l.id)} style={{fontSize:10.5,background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.4)',borderRadius:6,padding:'3px 8px',cursor:'pointer'}}>Abandonar</button>}
            </div>
          </div>))}
        </div>
      </Card>}

      {filtroPrincipal!=='livros'&&<Card title="Cursos / Estudos">
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr auto',gap:6,marginBottom:12}}>
          <input value={novoCursoNome} onChange={e=>setNovoCursoNome(e.target.value)} placeholder="Nome do curso/estudo" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12}}/>
          <input value={novoCursoTema} onChange={e=>setNovoCursoTema(e.target.value)} placeholder="Tema (opcional)" style={{background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:8,padding:'7px 9px',color:'#fff',fontSize:12}}/>
          <button onClick={addCurso} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:8,padding:'7px 12px',fontSize:12,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>+ Adicionar</button>
        </div>
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {cursosVisiveis.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum curso/estudo cadastrado.</div>}
          {cursosVisiveis.map(c=>(<div key={c.id} style={{padding:'9px 0',borderBottom:`1px solid ${C.line}`}}>
            <div style={{display:'flex',alignItems:'center',gap:8}}>
              <div style={{flex:1,minWidth:0}}><div style={{fontWeight:600,fontSize:13}}>{c.nome}</div>{c.tema&&<div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{c.tema}</div>}</div>
              <select value={c.status} onChange={e=>mudarStatusCurso(c.id,e.target.value as StatusCursoDev)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:8,padding:'3px 6px',fontSize:10.5,color:STATUS_CURSO_COR[c.status],colorScheme:'dark' as const,flexShrink:0}}>{(['quero_estudar','andamento','pausado','concluido'] as const).map(st=>(<option key={st} value={st}>{STATUS_CURSO_LABEL[st]}</option>))}</select>
            </div>
            {typeof c.progressoPct==='number'&&<div style={{height:6,borderRadius:3,background:C.s3,overflow:'hidden',marginTop:6}}><div style={{height:'100%',width:`${c.progressoPct}%`,borderRadius:3,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div>}
            <div style={{display:'flex',gap:6,marginTop:6}}>
              <button onClick={()=>registrarSessaoEstudo(c.id)} style={{fontSize:10.5,background:'transparent',border:`1px solid ${C.line}`,color:C.acc2,borderRadius:6,padding:'3px 8px',cursor:'pointer'}}>+ Registrar sessão</button>
              <button onClick={()=>definirProgressoCurso(c.id)} style={{fontSize:10.5,background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.4)',borderRadius:6,padding:'3px 8px',cursor:'pointer'}}>Definir progresso</button>
            </div>
          </div>))}
        </div>
      </Card>}
    </div>

    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Histórico de leitura" action={<button onClick={()=>setShowHistCompleto(true)} style={{fontSize:12,color:C.acc2,background:'transparent',border:'none',cursor:'pointer'}}>Ver histórico completo →</button>}>
        <div style={{maxHeight:260,overflowY:'auto' as const}}>
          {historicoUnificado.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum registro ainda.</div>}
          {historicoUnificado.slice(0,10).map(h=>(<div key={h.id} style={{padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5}}>
            <div style={{display:'flex',justifyContent:'space-between',color:'rgba(255,255,255,.6)'}}><span>{new Date(h.data+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})} · {h.nome}</span><span>{h.detalhe}</span></div>
            {h.aprendizado&&<div style={{color:'rgba(255,255,255,.4)',fontSize:11.5,marginTop:2}}>{h.aprendizado}</div>}
          </div>))}
        </div>
      </Card>

      <Card title="Metas e consistência">
        {metas.map(m=>{
          const {atual,alvo,pct}=calcMetaProgressoDev(m)
          function editarMeta(){
            const v=window.prompt(`Nova meta para "${m.label}"?`,String(m.valor))
            if(v===null||!v.trim())return
            setMetas(ms=>ms.map(x=>x.id===m.id?{...x,valor:Number(v)||x.valor}:x))
          }
          function toggleMetaAtiva(){setMetas(ms=>ms.map(x=>x.id===m.id?{...x,ativa:!x.ativa}:x))}
          return(<div key={m.id} style={{marginBottom:12,opacity:m.ativa?1:.4}}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',fontSize:12.5,marginBottom:4}}>
              <span style={{cursor:'pointer'}} onClick={toggleMetaAtiva} title={m.ativa?'Clique para desativar':'Clique para ativar'}>{m.label}</span>
              <span style={{color:'rgba(255,255,255,.5)',cursor:'pointer'}} onClick={editarMeta}>{atual} / {alvo} ✎</span>
            </div>
            {m.ativa&&<div style={{height:6,borderRadius:3,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${pct}%`,borderRadius:3,background:pct>=100?`linear-gradient(90deg,${C.ok},#15803d)`:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div>}
          </div>)
        })}
        <div style={{marginTop:14,paddingTop:14,borderTop:`1px solid ${C.line}`}}>
          <div style={{display:'flex',justifyContent:'space-between',marginBottom:8}}><span style={{fontSize:11,color:'rgba(255,255,255,.4)',textTransform:'uppercase' as const}}>Consistência · últimos 30 dias</span><span style={{fontWeight:800,color:C.acc2}}>{pctConsistencia30}%</span></div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(15,1fr)',gap:4}}>
            {ultimos30Dev.map(d=>(<div key={d} title={d} style={{aspectRatio:'1',borderRadius:3,background:diasComAtividadeDev.has(d)?`linear-gradient(135deg,${C.acc2},${C.acc})`:'rgba(255,255,255,.06)'}}/>))}
          </div>
          <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:'rgba(255,255,255,.4)',marginTop:8}}><span>Dias com leitura no mês: {diasLeituraMes}</span><span>Dias com desenvolvimento no mês: {diasDesenvolvimentoMes}</span></div>
        </div>
      </Card>
    </div>

    {showHistCompleto&&<div onClick={e=>{if(e.target===e.currentTarget)setShowHistCompleto(false)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:600,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Histórico completo</h3>
          <button onClick={()=>setShowHistCompleto(false)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          {historicoUnificado.map(h=>(<div key={h.id} style={{padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}>
            <div style={{display:'flex',justifyContent:'space-between',color:'rgba(255,255,255,.6)'}}><span>{new Date(h.data+'T12:00:00').toLocaleDateString('pt-BR')} · {h.tipo} · {h.nome}</span><span>{h.detalhe}</span></div>
            {h.aprendizado&&<div style={{color:'rgba(255,255,255,.4)',fontSize:12,marginTop:2}}>{h.aprendizado}</div>}
          </div>))}
        </div>
      </div>
    </div>}
  </div>)}
type PrioridadeCasa='baixa'|'media'|'alta'
type CategoriaCasa='Mercado'|'Doméstico'|'Manutenção'|'Contas'
type CasaItem={
  id:string,n:string,cat:CategoriaCasa,done:boolean,
  qtd?:number,unidade?:string,prioridade?:PrioridadeCasa,recorrente?:boolean,frequencia?:string,compradoEm?:string,
  responsavel?:string,statusDom?:'pendente'|'andamento'|'concluida',data?:string,horario?:string,freqDom?:string,concluidaEm?:string,
  area?:string,statusManut?:'pendente'|'agendada'|'andamento'|'aguardando'|'concluida',prazo?:string,aguardandoQuem?:string,followUp?:string,custo?:number,prestador?:string,
  valor?:number,venc?:string,pago?:boolean,pagoEm?:string,valorPago?:number,recorrenteConta?:boolean,formaPagamento?:string,
  observacao?:string,criadaEm?:string,
}
const PRIORIDADE_CASA_LABEL:Record<PrioridadeCasa,string>={baixa:'Baixa',media:'Média',alta:'Alta'}
const PRIORIDADE_CASA_COR:Record<PrioridadeCasa,string>={baixa:C.water,media:C.warn,alta:C.danger}
const AREAS_CASA_PADRAO=['Cozinha','Sala','Quarto','Banheiro','Lavanderia','Área externa','Geral','Outro']
const STATUS_DOM_LABEL:Record<string,string>={pendente:'Pendente',andamento:'Em andamento',concluida:'Concluída'}
const STATUS_DOM_COR:Record<string,string>={pendente:'rgba(255,255,255,.4)',andamento:C.acc2,concluida:C.ok}
const STATUS_MANUT_LABEL:Record<string,string>={pendente:'Pendente',agendada:'Agendada',andamento:'Em andamento',aguardando:'Aguardando',concluida:'Concluída'}
const STATUS_MANUT_COR:Record<string,string>={pendente:'rgba(255,255,255,.4)',agendada:C.water,andamento:C.acc2,aguardando:C.warn,concluida:C.ok}
function novoIdCasa(){return `${Date.now()}_${Math.random().toString(36).slice(2,8)}`}
function migrarItemCasa(it:any,i:number):CasaItem{
  return {
    id:it.id||`legado_${i}_${String(it.n||'').slice(0,10)}`,
    n:it.n||'',cat:it.cat||'Mercado',done:!!it.done,
    qtd:it.qtd,unidade:it.unidade,prioridade:it.prioridade,recorrente:it.recorrente,frequencia:it.frequencia,compradoEm:it.compradoEm,
    responsavel:it.responsavel,statusDom:it.statusDom||(it.cat==='Doméstico'?(it.done?'concluida':'pendente'):undefined),data:it.data,horario:it.horario,freqDom:it.freqDom,concluidaEm:it.concluidaEm,
    area:it.area,statusManut:it.statusManut||(it.cat==='Manutenção'?(it.done?'concluida':'pendente'):undefined),prazo:it.prazo,aguardandoQuem:it.aguardandoQuem,followUp:it.followUp,custo:it.custo,prestador:it.prestador,
    valor:it.valor,venc:it.venc,pago:it.pago!=null?it.pago:(it.cat==='Contas'?it.done:undefined),pagoEm:it.pagoEm,valorPago:it.valorPago,recorrenteConta:it.recorrenteConta,formaPagamento:it.formaPagamento,
    observacao:it.observacao,criadaEm:it.criadaEm,
  }
}
function calcStatusContaCasa(item:CasaItem):{label:string,cor:string,atrasada:boolean}{
  if(item.pago)return {label:'Paga',cor:C.ok,atrasada:false}
  if(!item.venc)return {label:'Sem vencimento',cor:'rgba(255,255,255,.4)',atrasada:false}
  const hoje=isoBR(new Date())
  if(item.venc<hoje)return {label:'Atrasada',cor:C.danger,atrasada:true}
  if(item.venc===hoje)return {label:'Vence hoje',cor:C.warn,atrasada:false}
  return {label:'A vencer',cor:'rgba(255,255,255,.5)',atrasada:false}
}
function proximaDataRecorrenciaCasa(dataIso:string,freq:string):string{
  const d=new Date(dataIso+'T12:00:00')
  if(freq==='diaria')d.setDate(d.getDate()+1)
  else if(freq==='quinzenal')d.setDate(d.getDate()+14)
  else if(freq==='mensal')d.setMonth(d.getMonth()+1)
  else d.setDate(d.getDate()+7)
  return isoBR(d)
}

function Casa(){
  const hojeIsoCasa=isoBR(new Date())
  const {fam}=React.useContext(FamCtx)
  const MEMBROS_CASA=[{id:'denise',nome:'Denise'},{id:'flavio',nome:'Flávio'},{id:'domi',nome:'Domi'},{id:'derick',nome:'Derick'}]
  void fam
  const [items,setItemsRaw]=React.useState<CasaItem[]>(()=>{
    try{
      const raw=JSON.parse(localStorage.getItem('dos_casa_items')||'null')
      if(Array.isArray(raw)&&raw.length>0)return raw.map(migrarItemCasa)
    }catch{}
    return [{n:'Iogurte proteico sem lactose',cat:'Mercado' as const,done:false},{n:'Whey isolado',cat:'Mercado' as const,done:false},{n:'Frango',cat:'Mercado' as const,done:false},{n:'Limpar casa',cat:'Doméstico' as const,done:false},{n:'Pagar energia',cat:'Contas' as const,done:false}].map(migrarItemCasa)
  })
  const setItems=(fn:CasaItem[]|((p:CasaItem[])=>CasaItem[]))=>setItemsRaw(p=>{const n=typeof fn==='function'?(fn as any)(p):fn;localStorage.setItem('dos_casa_items',JSON.stringify(n));return n})

  const [filtroPrincipal,setFiltroPrincipal]=React.useState<'Tudo'|CategoriaCasa>('Tudo')
  const [filtroComplementar,setFiltroComplementar]=React.useState<'pendentes'|'hoje'|'proximos'|'concluidos'>('pendentes')
  const [buscaCasa,setBuscaCasa]=React.useState('')
  const [nova,setNova]=React.useState('')
  const [cat,setCat]=React.useState<CategoriaCasa>('Mercado')
  const [itemAberto,setItemAberto]=React.useState<CasaItem|null>(null)
  const [showHistorico,setShowHistorico]=React.useState<CategoriaCasa|null>(null)

  function atualizarItem(id:string,campos:Partial<CasaItem>){
    setItems(its=>its.map(x=>x.id===id?{...x,...campos}:x))
    setItemAberto(ia=>ia&&ia.id===id?{...ia,...campos}:ia)
  }
  function excluirItem(id:string){
    if(!window.confirm('Excluir este item? Essa ação não pode ser desfeita.'))return
    setItems(its=>its.filter(x=>x.id!==id))
    setItemAberto(null)
  }
  function addItem(){
    if(!nova.trim())return
    const novo:CasaItem={id:novoIdCasa(),n:nova.trim(),cat,done:false,criadaEm:new Date().toISOString(),
      statusDom:cat==='Doméstico'?'pendente':undefined,statusManut:cat==='Manutenção'?'pendente':undefined}
    setItems(its=>[novo,...its])
    setNova('')
    setItemAberto(novo)
  }
  function toggleMercado(id:string){
    const it=items.find(x=>x.id===id);if(!it)return
    atualizarItem(id,{done:!it.done,compradoEm:!it.done?new Date().toISOString():undefined})
  }
  function toggleDomestico(id:string){
    const it=items.find(x=>x.id===id);if(!it)return
    const concluir=it.statusDom!=='concluida'
    atualizarItem(id,{statusDom:concluir?'concluida':'pendente',done:concluir,concluidaEm:concluir?new Date().toISOString():undefined})
    if(concluir&&it.freqDom&&it.data){
      const prox:CasaItem={id:novoIdCasa(),n:it.n,cat:'Doméstico',done:false,statusDom:'pendente',responsavel:it.responsavel,data:proximaDataRecorrenciaCasa(it.data,it.freqDom),horario:it.horario,freqDom:it.freqDom,criadaEm:new Date().toISOString()}
      setItems(its=>[prox,...its])
    }
  }
  function toggleManutencao(id:string){
    const it=items.find(x=>x.id===id);if(!it)return
    const concluir=it.statusManut!=='concluida'
    atualizarItem(id,{statusManut:concluir?'concluida':'pendente',done:concluir,concluidaEm:concluir?new Date().toISOString():undefined})
  }
  function pagarConta(id:string){
    const it=items.find(x=>x.id===id);if(!it)return
    const pagar=!it.pago
    atualizarItem(id,{pago:pagar,done:pagar,pagoEm:pagar?new Date().toISOString():undefined,valorPago:pagar?it.valor:undefined})
    if(pagar&&it.recorrenteConta&&it.venc){
      const prox:CasaItem={id:novoIdCasa(),n:it.n,cat:'Contas',done:false,pago:false,valor:it.valor,venc:proximaDataRecorrenciaCasa(it.venc,'mensal'),recorrenteConta:true,formaPagamento:it.formaPagamento,criadaEm:new Date().toISOString()}
      setItems(its=>[prox,...its])
    }
  }

  const buscaLowerCasa=buscaCasa.trim().toLowerCase()
  function passaComplementarCasa(it:CasaItem):boolean{
    if(filtroComplementar==='concluidos')return it.done
    if(it.done)return false
    if(filtroComplementar==='pendentes')return true
    const dataRef=it.cat==='Doméstico'?it.data:it.cat==='Manutenção'?(it.followUp||it.prazo):it.cat==='Contas'?it.venc:undefined
    if(filtroComplementar==='hoje')return dataRef===hojeIsoCasa
    if(filtroComplementar==='proximos'){
      if(!dataRef)return false
      const dias=Math.round((new Date(dataRef+'T12:00:00').getTime()-new Date(hojeIsoCasa+'T12:00:00').getTime())/86400000)
      return dias>=0&&dias<=7
    }
    return true
  }
  const itemsFiltrados=items.filter(it=>{
    if(filtroPrincipal!=='Tudo'&&it.cat!==filtroPrincipal)return false
    if(buscaLowerCasa){
      const alvo=[it.n,it.observacao,it.responsavel,it.area,it.aguardandoQuem,it.prestador].filter(Boolean).join(' ').toLowerCase()
      if(!alvo.includes(buscaLowerCasa))return false
    }
    return passaComplementarCasa(it)
  })
  const mercadoLista=itemsFiltrados.filter(i=>i.cat==='Mercado')
  const domesticoLista=itemsFiltrados.filter(i=>i.cat==='Doméstico')
  const manutLista=itemsFiltrados.filter(i=>i.cat==='Manutenção')
  const contasLista=itemsFiltrados.filter(i=>i.cat==='Contas').slice().sort((a,b)=>(a.venc||'9999').localeCompare(b.venc||'9999'))

  const mercadoPendentes=items.filter(i=>i.cat==='Mercado'&&!i.done).length
  const domesticoHojeCount=items.filter(i=>i.cat==='Doméstico'&&!i.done&&i.data===hojeIsoCasa).length
  const manutPendentes=items.filter(i=>i.cat==='Manutenção'&&!i.done).length
  const contasVenceHojeCount=items.filter(i=>i.cat==='Contas'&&!i.pago&&i.venc===hojeIsoCasa).length

  type AtencaoItem={id:string,titulo:string,subtitulo:string,urgente:boolean,acaoLabel:string,onAcao:()=>void}
  const atencaoHoje:AtencaoItem[]=[]
  items.forEach(it=>{
    if(it.done)return
    if(it.cat==='Contas'){
      const st=calcStatusContaCasa(it)
      if(st.atrasada)atencaoHoje.push({id:it.id,titulo:`${it.n} atrasada`,subtitulo:it.valor?`R$ ${it.valor.toFixed(2)}`:'',urgente:true,acaoLabel:'Pagar',onAcao:()=>pagarConta(it.id)})
      else if(it.venc===hojeIsoCasa)atencaoHoje.push({id:it.id,titulo:`${it.n} vence hoje`,subtitulo:it.valor?`R$ ${it.valor.toFixed(2)}`:'',urgente:true,acaoLabel:'Pagar',onAcao:()=>pagarConta(it.id)})
    }
    if(it.cat==='Doméstico'&&it.data===hojeIsoCasa)atencaoHoje.push({id:it.id,titulo:it.n,subtitulo:'Tarefa doméstica',urgente:false,acaoLabel:'Ver',onAcao:()=>setItemAberto(it)})
    if(it.cat==='Manutenção'){
      if(it.prioridade==='alta')atencaoHoje.push({id:it.id,titulo:it.n,subtitulo:it.aguardandoQuem?`Aguardando ${it.aguardandoQuem}`:'Manutenção urgente',urgente:true,acaoLabel:'Ver',onAcao:()=>setItemAberto(it)})
      else if(it.followUp===hojeIsoCasa)atencaoHoje.push({id:it.id,titulo:it.n,subtitulo:'Revisar hoje',urgente:false,acaoLabel:'Ver',onAcao:()=>setItemAberto(it)})
    }
  })
  if(mercadoPendentes>0)atencaoHoje.push({id:'mercado-agregado',titulo:`${mercadoPendentes} ${mercadoPendentes===1?'item':'itens'} no mercado`,subtitulo:'Lista de compras',urgente:false,acaoLabel:'Ver',onAcao:()=>setFiltroPrincipal('Mercado')})
  const atencaoTotal=atencaoHoje.length

  function AvatarResponsavel({id}:{id?:string}){
    if(!id)return <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>—</span>
    const m=MEMBROS_CASA.find(x=>x.id===id)
    return(<div style={{display:'flex',alignItems:'center',gap:6}}><Avatar id={id} label={(m?.nome||id)[0]} size={20} radius={7}/><span style={{fontSize:12}}>{m?.nome||id}</span></div>)
  }

  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Casa</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:16}}>Organize tudo o que precisa da casa em um só lugar.</p>

    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(170px,1fr))',gap:10,marginBottom:20}}>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Mercado</div><div style={{fontSize:22,fontWeight:800}}>{mercadoPendentes}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>itens pendentes</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Doméstico</div><div style={{fontSize:22,fontWeight:800}}>{domesticoHojeCount}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>tarefas hoje</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Manutenção</div><div style={{fontSize:22,fontWeight:800}}>{manutPendentes}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>pendente{manutPendentes===1?'':'s'}</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Contas</div><div style={{fontSize:22,fontWeight:800,color:contasVenceHojeCount>0?C.danger:'#fff'}}>{contasVenceHojeCount}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>vence hoje</div></div>
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:14,padding:14}}><div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>Atenção total</div><div style={{fontSize:22,fontWeight:800,color:C.acc2}}>{atencaoTotal}</div><div style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>itens importantes</div></div>
    </div>

    <div style={{display:'flex',gap:10,marginBottom:14,flexWrap:'wrap' as const}}>
      <input value={nova} onChange={e=>setNova(e.target.value)} onKeyDown={e=>e.key==='Enter'&&addItem()} placeholder="Adicionar item rápido…" style={{flex:1,minWidth:200,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14}}/>
      <select value={cat} onChange={e=>setCat(e.target.value as CategoriaCasa)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{(['Mercado','Doméstico','Manutenção','Contas'] as const).map(c=>(<option key={c}>{c}</option>))}</select>
      <button onClick={addItem} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar</button>
    </div>

    <div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const,alignItems:'center'}}>
      <div style={{display:'flex',gap:6}}>
        {(['Tudo','Mercado','Doméstico','Manutenção','Contas'] as const).map(f=>(<button key={f} onClick={()=>setFiltroPrincipal(f)} style={{background:filtroPrincipal===f?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,color:'#fff',border:`1px solid ${filtroPrincipal===f?'transparent':C.line}`,borderRadius:10,padding:'8px 14px',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>{f}</button>))}
      </div>
      <input value={buscaCasa} onChange={e=>setBuscaCasa(e.target.value)} placeholder="🔎 Buscar na Casa…" style={{flex:1,minWidth:160,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5}}/>
      <select value={filtroComplementar} onChange={e=>setFiltroComplementar(e.target.value as any)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}>
        <option value="pendentes">Pendentes</option><option value="hoje">Hoje</option><option value="proximos">Próximos 7 dias</option><option value="concluidos">Concluídos</option>
      </select>
    </div>

    {atencaoHoje.length>0&&<div style={{marginBottom:20}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}><span style={{fontSize:16}}>⚠️</span><span style={{fontWeight:700,fontSize:14}}>Atenção hoje</span></div>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:10}}>
        {atencaoHoje.slice(0,6).map(a=>(<div key={a.id} style={{background:a.urgente?'rgba(248,113,113,.08)':C.s2,border:`1px solid ${a.urgente?'rgba(248,113,113,.25)':C.line}`,borderRadius:12,padding:'12px 14px',display:'flex',justifyContent:'space-between',alignItems:'center',gap:8}}>
          <div><div style={{fontSize:13,fontWeight:700}}>{a.titulo}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{a.subtitulo}</div></div>
          <button onClick={a.onAcao} style={{background:a.urgente?C.danger:'transparent',color:a.urgente?'#fff':C.acc2,border:a.urgente?'none':`1px solid ${C.line}`,borderRadius:8,padding:'6px 12px',fontSize:11.5,fontWeight:600,cursor:'pointer',whiteSpace:'nowrap' as const}}>{a.acaoLabel}</button>
        </div>))}
      </div>
    </div>}

    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Mercado" action={<span style={{fontSize:11,color:C.acc2}}>{mercadoPendentes} pendentes</span>}>
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {mercadoLista.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum item.</div>}
          {mercadoLista.map(it=>(<div key={it.id} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,opacity:it.done?.5:1}}>
            <span onClick={()=>toggleMercado(it.id)} style={{width:20,height:20,borderRadius:6,border:`2px solid ${it.done?C.ok:'rgba(255,255,255,.2)'}`,background:it.done?'rgba(52,211,153,.2)':'transparent',display:'grid',placeItems:'center',color:C.ok,fontSize:11,flexShrink:0,cursor:'pointer'}}>{it.done&&'✓'}</span>
            <div onClick={()=>setItemAberto(it)} style={{flex:1,cursor:'pointer',minWidth:0}}>
              <div style={{fontSize:13,textDecoration:it.done?'line-through':'none',color:it.done?'rgba(255,255,255,.4)':'#fff'}}>{it.n}</div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{it.qtd?`${it.qtd}${it.unidade?` ${it.unidade}`:''}`:''}{it.prioridade?` · ${PRIORIDADE_CASA_LABEL[it.prioridade]}`:''}{it.responsavel?` · ${MEMBROS_CASA.find(m=>m.id===it.responsavel)?.nome||it.responsavel}`:''}</div>
            </div>
            {it.prioridade&&!it.done&&<span style={{fontSize:10,fontWeight:700,color:PRIORIDADE_CASA_COR[it.prioridade]}}>{PRIORIDADE_CASA_LABEL[it.prioridade]}</span>}
            <button onClick={()=>excluirItem(it.id)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'3px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button>
          </div>))}
        </div>
        <button onClick={()=>setShowHistorico('Mercado')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:11.5,cursor:'pointer',padding:'8px 0 0'}}>Ver histórico de compras →</button>
      </Card>

      <Card title="Doméstico" action={<span style={{fontSize:11,color:C.acc2}}>{domesticoHojeCount} para hoje</span>}>
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {domesticoLista.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhuma tarefa.</div>}
          {domesticoLista.map(it=>(<div key={it.id} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,opacity:it.done?.5:1}}>
            <span onClick={()=>toggleDomestico(it.id)} style={{width:20,height:20,borderRadius:6,border:`2px solid ${it.done?C.ok:'rgba(255,255,255,.2)'}`,background:it.done?'rgba(52,211,153,.2)':'transparent',display:'grid',placeItems:'center',color:C.ok,fontSize:11,flexShrink:0,cursor:'pointer'}}>{it.done&&'✓'}</span>
            <div onClick={()=>setItemAberto(it)} style={{flex:1,cursor:'pointer',minWidth:0}}>
              <div style={{fontSize:13,textDecoration:it.done?'line-through':'none',color:it.done?'rgba(255,255,255,.4)':'#fff'}}>{it.n}</div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{it.freqDom?`${it.freqDom} · `:''}{it.data?new Date(it.data+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}):''}{it.statusDom?<span style={{color:STATUS_DOM_COR[it.statusDom]}}> · {STATUS_DOM_LABEL[it.statusDom]}</span>:null}</div>
            </div>
            <AvatarResponsavel id={it.responsavel}/>
          </div>))}
        </div>
        <button onClick={()=>setShowHistorico('Doméstico')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:11.5,cursor:'pointer',padding:'8px 0 0'}}>Ver histórico de tarefas →</button>
      </Card>

      <Card title="Manutenção" action={<span style={{fontSize:11,color:C.acc2}}>{manutPendentes} pendente{manutPendentes===1?'':'s'}</span>}>
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {manutLista.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhuma manutenção.</div>}
          {manutLista.map(it=>(<div key={it.id} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,opacity:it.done?.5:1}}>
            <span onClick={()=>toggleManutencao(it.id)} style={{width:20,height:20,borderRadius:6,border:`2px solid ${it.done?C.ok:'rgba(255,255,255,.2)'}`,background:it.done?'rgba(52,211,153,.2)':'transparent',display:'grid',placeItems:'center',color:C.ok,fontSize:11,flexShrink:0,cursor:'pointer'}}>{it.done&&'✓'}</span>
            <div onClick={()=>setItemAberto(it)} style={{flex:1,cursor:'pointer',minWidth:0}}>
              <div style={{fontSize:13,textDecoration:it.done?'line-through':'none',color:it.done?'rgba(255,255,255,.4)':'#fff'}}>{it.n}</div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{it.area?`${it.area} · `:''}{it.statusManut&&<span style={{color:STATUS_MANUT_COR[it.statusManut]}}>{it.statusManut==='aguardando'&&it.aguardandoQuem?`Aguardando ${it.aguardandoQuem}`:STATUS_MANUT_LABEL[it.statusManut]}</span>}</div>
            </div>
            {it.prioridade&&!it.done&&<span style={{fontSize:10,fontWeight:700,color:PRIORIDADE_CASA_COR[it.prioridade]}}>{PRIORIDADE_CASA_LABEL[it.prioridade]}</span>}
          </div>))}
        </div>
        <button onClick={()=>setShowHistorico('Manutenção')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:11.5,cursor:'pointer',padding:'8px 0 0'}}>Ver histórico de manutenções →</button>
      </Card>

      <Card title="Contas" action={<span style={{fontSize:11,color:contasVenceHojeCount>0?C.danger:C.acc2}}>{contasVenceHojeCount} vence hoje</span>}>
        <div style={{maxHeight:280,overflowY:'auto' as const}}>
          {contasLista.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhuma conta.</div>}
          {contasLista.map(it=>{
            const st=calcStatusContaCasa(it)
            return(<div key={it.id} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,opacity:it.pago?.5:1}}>
              <span onClick={()=>pagarConta(it.id)} style={{width:20,height:20,borderRadius:6,border:`2px solid ${it.pago?C.ok:'rgba(255,255,255,.2)'}`,background:it.pago?'rgba(52,211,153,.2)':'transparent',display:'grid',placeItems:'center',color:C.ok,fontSize:11,flexShrink:0,cursor:'pointer'}}>{it.pago&&'✓'}</span>
              <div onClick={()=>setItemAberto(it)} style={{flex:1,cursor:'pointer',minWidth:0}}>
                <div style={{fontSize:13,textDecoration:it.pago?'line-through':'none',color:it.pago?'rgba(255,255,255,.4)':'#fff'}}>{it.n}</div>
                <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{it.venc?new Date(it.venc+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}):''}{it.valor?` · R$ ${it.valor.toFixed(2)}`:''}</div>
              </div>
              <span style={{fontSize:10.5,fontWeight:700,color:st.cor,whiteSpace:'nowrap' as const}}>{st.label}</span>
            </div>)
          })}
        </div>
        <button onClick={()=>setShowHistorico('Contas')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:11.5,cursor:'pointer',padding:'8px 0 0'}}>Ver histórico de contas →</button>
      </Card>
    </div>

    {itemAberto&&<div onClick={e=>{if(e.target===e.currentTarget)setItemAberto(null)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:520,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>{itemAberto.cat}</h3>
          <button onClick={()=>setItemAberto(null)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Nome</label>
          <input value={itemAberto.n} onChange={e=>atualizarItem(itemAberto.id,{n:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:14}}/>

          {itemAberto.cat==='Mercado'&&<>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Qtd</label><input type="number" value={itemAberto.qtd||''} onChange={e=>atualizarItem(itemAberto.id,{qtd:Number(e.target.value)||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Unidade</label><input value={itemAberto.unidade||''} onChange={e=>atualizarItem(itemAberto.id,{unidade:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Prioridade</label><select value={itemAberto.prioridade||'media'} onChange={e=>atualizarItem(itemAberto.id,{prioridade:e.target.value as PrioridadeCasa})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{(['baixa','media','alta'] as const).map(pr=>(<option key={pr} value={pr}>{PRIORIDADE_CASA_LABEL[pr]}</option>))}</select></div>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Responsável</label><select value={itemAberto.responsavel||''} onChange={e=>atualizarItem(itemAberto.id,{responsavel:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}><option value="">Sem responsável</option>{MEMBROS_CASA.map(m=>(<option key={m.id} value={m.id}>{m.nome}</option>))}</select></div>
              <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'flex',alignItems:'center',gap:8,marginTop:24}}><input type="checkbox" checked={!!itemAberto.recorrente} onChange={e=>atualizarItem(itemAberto.id,{recorrente:e.target.checked})}/> Item recorrente</label>
            </div>
          </>}

          {itemAberto.cat==='Doméstico'&&<>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Responsável</label><select value={itemAberto.responsavel||''} onChange={e=>atualizarItem(itemAberto.id,{responsavel:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}><option value="">Sem responsável</option>{MEMBROS_CASA.map(m=>(<option key={m.id} value={m.id}>{m.nome}</option>))}</select></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Status</label><select value={itemAberto.statusDom||'pendente'} onChange={e=>atualizarItem(itemAberto.id,{statusDom:e.target.value as any,done:e.target.value==='concluida'})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{(['pendente','andamento','concluida'] as const).map(st=>(<option key={st} value={st}>{STATUS_DOM_LABEL[st]}</option>))}</select></div>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Data</label><input type="date" value={itemAberto.data||''} onChange={e=>atualizarItem(itemAberto.id,{data:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Horário</label><input type="time" value={itemAberto.horario||''} onChange={e=>atualizarItem(itemAberto.id,{horario:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Frequência</label><select value={itemAberto.freqDom||''} onChange={e=>atualizarItem(itemAberto.id,{freqDom:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}><option value="">Não repete</option><option value="diaria">Diária</option><option value="semanal">Semanal</option><option value="quinzenal">Quinzenal</option><option value="mensal">Mensal</option></select></div>
            </div>
          </>}

          {itemAberto.cat==='Manutenção'&&<>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Área</label><select value={itemAberto.area||''} onChange={e=>atualizarItem(itemAberto.id,{area:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}><option value="">Selecionar</option>{AREAS_CASA_PADRAO.map(a=>(<option key={a}>{a}</option>))}</select></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Prioridade</label><select value={itemAberto.prioridade||'media'} onChange={e=>atualizarItem(itemAberto.id,{prioridade:e.target.value as PrioridadeCasa})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}>{(['baixa','media','alta'] as const).map(pr=>(<option key={pr} value={pr}>{PRIORIDADE_CASA_LABEL[pr]}</option>))}</select></div>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Prazo</label><input type="date" value={itemAberto.prazo||''} onChange={e=>atualizarItem(itemAberto.id,{prazo:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Responsável</label><select value={itemAberto.responsavel||''} onChange={e=>atualizarItem(itemAberto.id,{responsavel:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}><option value="">Sem responsável</option>{MEMBROS_CASA.map(m=>(<option key={m.id} value={m.id}>{m.nome}</option>))}</select></div>
            </div>
            <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Status</label>
            <select value={itemAberto.statusManut||'pendente'} onChange={e=>atualizarItem(itemAberto.id,{statusManut:e.target.value as any,done:e.target.value==='concluida'})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:14,colorScheme:'dark' as const}}>{(['pendente','agendada','andamento','aguardando','concluida'] as const).map(st=>(<option key={st} value={st}>{STATUS_MANUT_LABEL[st]}</option>))}</select>
            {itemAberto.statusManut==='aguardando'&&<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14,background:'rgba(251,191,36,.06)',border:'1px solid rgba(251,191,36,.2)',borderRadius:10,padding:12}}>
              <div><label style={{fontSize:12,color:C.warn,display:'block',marginBottom:5}}>Aguardando quem/o quê?</label><input value={itemAberto.aguardandoQuem||''} onChange={e=>atualizarItem(itemAberto.id,{aguardandoQuem:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
              <div><label style={{fontSize:12,color:C.warn,display:'block',marginBottom:5}}>Revisar novamente em</label><input type="date" value={itemAberto.followUp||''} onChange={e=>atualizarItem(itemAberto.id,{followUp:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
            </div>}
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Prestador (opcional)</label><input value={itemAberto.prestador||''} onChange={e=>atualizarItem(itemAberto.id,{prestador:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Custo (opcional)</label><input type="number" value={itemAberto.custo||''} onChange={e=>atualizarItem(itemAberto.id,{custo:Number(e.target.value)||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
            </div>
          </>}

          {itemAberto.cat==='Contas'&&<>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Valor</label><input type="number" value={itemAberto.valor||''} onChange={e=>atualizarItem(itemAberto.id,{valor:Number(e.target.value)||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Vencimento</label><input type="date" value={itemAberto.venc||''} onChange={e=>atualizarItem(itemAberto.id,{venc:e.target.value||undefined})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,colorScheme:'dark' as const}}/></div>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:14}}>
              <div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Forma de pagamento (opcional)</label><input value={itemAberto.formaPagamento||''} onChange={e=>atualizarItem(itemAberto.id,{formaPagamento:e.target.value})} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></div>
              <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'flex',alignItems:'center',gap:8,marginTop:24}}><input type="checkbox" checked={!!itemAberto.recorrenteConta} onChange={e=>atualizarItem(itemAberto.id,{recorrenteConta:e.target.checked})}/> Conta recorrente (mensal)</label>
            </div>
            <div style={{fontSize:12.5,color:'rgba(255,255,255,.5)',marginBottom:14}}>Status: <b style={{color:calcStatusContaCasa(itemAberto).cor}}>{calcStatusContaCasa(itemAberto).label}</b>{itemAberto.pago&&itemAberto.pagoEm?` · paga em ${new Date(itemAberto.pagoEm).toLocaleDateString('pt-BR')}`:''}</div>
          </>}

          <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Observação</label>
          <textarea value={itemAberto.observacao||''} onChange={e=>atualizarItem(itemAberto.id,{observacao:e.target.value})} rows={2} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:13.5,resize:'vertical' as const,fontFamily:'inherit'}}/>
        </div>
        <div style={{display:'flex',gap:10,padding:'14px 18px',position:'sticky',bottom:0,background:'#1c1c28'}}>
          <button onClick={()=>excluirItem(itemAberto.id)} style={{background:'rgba(248,113,113,.1)',border:'1px solid rgba(248,113,113,.25)',color:C.danger,borderRadius:10,padding:'11px 16px',fontSize:13,fontWeight:600,cursor:'pointer'}}>Excluir</button>
          <button onClick={()=>setItemAberto(null)} style={{flex:1,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Fechar</button>
        </div>
      </div>
    </div>}

    {showHistorico&&<div onClick={e=>{if(e.target===e.currentTarget)setShowHistorico(null)}} style={{position:'fixed',inset:0,background:'rgba(0,0,0,.65)',backdropFilter:'blur(4px)',zIndex:200,display:'flex',alignItems:'center',justifyContent:'center',padding:20}}>
      <div style={{background:'linear-gradient(180deg,#1c1c28,#16161f)',border:'1px solid rgba(255,255,255,.12)',borderRadius:20,width:'100%',maxWidth:560,maxHeight:'88vh',overflow:'auto'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'16px 18px',borderBottom:`1px solid ${C.line}`,position:'sticky',top:0,background:'#1c1c28'}}>
          <h3 style={{margin:0,fontSize:16}}>Histórico · {showHistorico}</h3>
          <button onClick={()=>setShowHistorico(null)} style={{width:30,height:30,borderRadius:9,background:C.s3,border:'none',color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:16}}>✕</button>
        </div>
        <div style={{padding:18}}>
          {items.filter(i=>i.cat===showHistorico&&i.done).sort((a,b)=>(b.concluidaEm||b.compradoEm||b.pagoEm||'').localeCompare(a.concluidaEm||a.compradoEm||a.pagoEm||'')).map(it=>(<div key={it.id} onClick={()=>{setShowHistorico(null);setItemAberto(it)}} style={{display:'flex',justifyContent:'space-between',padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13,cursor:'pointer'}}>
            <span>{it.n}</span>
            <span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{(()=>{const d=it.concluidaEm||it.compradoEm||it.pagoEm;return d?new Date(d).toLocaleDateString('pt-BR'):''})()}</span>
          </div>))}
          {items.filter(i=>i.cat===showHistorico&&i.done).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum registro concluído ainda.</div>}
        </div>
      </div>
    </div>}
  </div>)}
type AreaRel='geral'|'saude'|'alimentacao'|'exercicios'|'espiritual'|'familia'|'trabalho'|'desenvolvimento'|'casa'
const AREAS_REL_INFO:{key:AreaRel,nome:string,icone:string,rota:string}[]=[
  {key:'geral',nome:'Visão geral',icone:'📊',rota:'/relatorios'},
  {key:'saude',nome:'Saúde',icone:'❤️',rota:'/saude'},
  {key:'alimentacao',nome:'Alimentação',icone:'🍽️',rota:'/alimentacao'},
  {key:'exercicios',nome:'Exercícios',icone:'💪',rota:'/exercicios'},
  {key:'espiritual',nome:'Espiritual',icone:'📖',rota:'/espiritual'},
  {key:'familia',nome:'Família',icone:'👨‍👩‍👧',rota:'/familia'},
  {key:'trabalho',nome:'Trabalho',icone:'💼',rota:'/trabalho'},
  {key:'desenvolvimento',nome:'Desenvolvimento',icone:'📈',rota:'/desenvolvimento'},
  {key:'casa',nome:'Casa',icone:'🏡',rota:'/casa'},
]
function diasIntervaloRel(inicioIso:string,fimIso:string):string[]{
  const out:string[]=[]
  let d=new Date(inicioIso+'T12:00:00')
  const fim=new Date(fimIso+'T12:00:00')
  let guarda=0
  while(d.getTime()<=fim.getTime()&&guarda<3660){out.push(isoBR(d));d.setDate(d.getDate()+1);guarda++}
  return out
}
function calcularJanelaRel(periodo:'semana'|'30d'|'90d'|'ano'|'personalizado',ini:string,fim:string){
  const hoje=isoBR(new Date())
  let inicioIso=hoje,fimIso=hoje
  if(periodo==='semana'){const d=new Date();const dw=d.getDay();const diff=(dw===0?-6:1-dw);const seg=new Date(d);seg.setDate(seg.getDate()+diff);inicioIso=isoBR(seg);fimIso=hoje}
  else if(periodo==='30d'){const d=new Date();d.setDate(d.getDate()-29);inicioIso=isoBR(d);fimIso=hoje}
  else if(periodo==='90d'){const d=new Date();d.setDate(d.getDate()-89);inicioIso=isoBR(d);fimIso=hoje}
  else if(periodo==='ano'){inicioIso=`${new Date().getFullYear()}-01-01`;fimIso=hoje}
  else{inicioIso=ini||(()=>{const d=new Date();d.setDate(d.getDate()-29);return isoBR(d)})();fimIso=fim||hoje}
  const diasAtual=diasIntervaloRel(inicioIso,fimIso)
  const n=diasAtual.length||1
  const antFim=new Date(inicioIso+'T12:00:00');antFim.setDate(antFim.getDate()-1)
  const antIni=new Date(antFim);antIni.setDate(antIni.getDate()-(n-1))
  return {inicioIso,fimIso,diasAtual,inicioAntIso:isoBR(antIni),fimAntIso:isoBR(antFim)}
}
function sequenciaMaximaNoPeriodo(diasAtivos:Set<string>,periodo:string[]):number{
  let max=0,atual=0
  for(const iso of periodo){if(diasAtivos.has(iso)){atual++;max=Math.max(max,atual)}else atual=0}
  return max
}
function Relatorios(){
  const navigate=useNavigate()
  const [tzSched,setTzSched]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [tzBalance,setTzBalance]=React.useState(0)
  const [tzApps,setTzApps]=React.useState<any[]>([])
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
  const [periodoRel,setPeriodoRel]=React.useState<'semana'|'30d'|'90d'|'ano'|'personalizado'>('30d')
  const [personalizadoIniRel,setPersonalizadoIniRel]=React.useState('')
  const [personalizadoFimRel,setPersonalizadoFimRel]=React.useState('')
  const [areaRel,setAreaRel]=React.useState<AreaRel>('geral')
  const [granularidadeRel,setGranularidadeRel]=React.useState<'dia'|'semana'|'mes'>('semana')

  const janela=calcularJanelaRel(periodoRel,personalizadoIniRel,personalizadoFimRel)
  const diasAtualRel=janela.diasAtual
  const diasAnteriorRel=diasIntervaloRel(janela.inicioAntIso,janela.fimAntIso)

  const devRel=lerDevocionais()
  const treinosRel=lerTreinos().filter(t=>t.status==='concluido')
  const sessoesLeituraRel=lerSessoesLeituraDev()
  const sessoesEstudoRel=lerSessoesEstudoDev()
  const refsLogRel=lerRefsLog()
  const aguaLogRel=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
  const metaAguaRel=Number(localStorage.getItem('dos_meta_agua_ml')||2500)
  const metaProteinaRel=lerMetaProteina()
  const casaItensRel=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_casa_items')||'[]');return Array.isArray(raw)?raw.map(migrarItemCasa):[]}catch{return []}})() as CasaItem[]
  const trabalhoItensRel=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_trabalho')||'[]');return Array.isArray(raw)?raw.map(migrarTarefaTrab):[]}catch{return []}})() as TarefaTrab[]
  const avalsFamRel=(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})() as Record<string,any[]>

  const diasEspiritualRel=new Set(devRel.map((d:any)=>d.data))
  const diasExerciciosRel=new Set(treinosRel.map(t=>t.data))
  const diasDesenvolvimentoRel=new Set([...sessoesLeituraRel.map(s=>s.data),...sessoesEstudoRel.map(s=>s.data)])
  const diasAlimentacaoRel=new Set(Object.keys(refsLogRel).filter(iso=>(refsLogRel[iso]||[]).length>0))
  const diasSaudeRel=new Set(Object.keys(aguaLogRel).filter(iso=>Number(aguaLogRel[iso]||0)>0))
  const diasTrabalhoRel=new Set(trabalhoItensRel.filter(t=>t.concluidaEm).map(t=>String(t.concluidaEm).slice(0,10)))
  const diasCasaRel=new Set(casaItensRel.flatMap(it=>[it.compradoEm,it.concluidaEm,it.pagoEm].filter(Boolean).map(d=>String(d).slice(0,10))))

  const AREAS_SCORE_REL:{chave:AreaRel,nome:string,set:Set<string>}[]=[
    {chave:'saude',nome:'Saúde',set:diasSaudeRel},
    {chave:'exercicios',nome:'Exercícios',set:diasExerciciosRel},
    {chave:'desenvolvimento',nome:'Desenvolvimento',set:diasDesenvolvimentoRel},
    {chave:'espiritual',nome:'Espiritual',set:diasEspiritualRel},
    {chave:'alimentacao',nome:'Alimentação',set:diasAlimentacaoRel},
    {chave:'casa',nome:'Casa',set:diasCasaRel},
    {chave:'trabalho',nome:'Trabalho',set:diasTrabalhoRel},
  ]
  function scoreAreaRel(set:Set<string>,dias:string[]):number{if(dias.length===0)return 0;const ativos=dias.filter(d=>set.has(d)).length;return Math.round(ativos/dias.length*100)}
  const consistenciaPorArea=AREAS_SCORE_REL.map(a=>({nome:a.nome,chave:a.chave,atual:scoreAreaRel(a.set,diasAtualRel),anterior:scoreAreaRel(a.set,diasAnteriorRel)}))
  const temAlgumDadoRel=diasAtualRel.some(d=>AREAS_SCORE_REL.some(a=>a.set.has(d)))||diasAnteriorRel.some(d=>AREAS_SCORE_REL.some(a=>a.set.has(d)))

  const scorePeriodoAtual=Math.round(consistenciaPorArea.reduce((a,c)=>a+c.atual,0)/consistenciaPorArea.length)
  const scorePeriodoAnterior=Math.round(consistenciaPorArea.reduce((a,c)=>a+c.anterior,0)/consistenciaPorArea.length)
  const deltaScorePeriodo=scorePeriodoAtual-scorePeriodoAnterior
  const melhorAreaRel=[...consistenciaPorArea].sort((a,b)=>b.atual-a.atual)[0]
  const piorAreaRel=[...consistenciaPorArea].sort((a,b)=>a.atual-b.atual)[0]
  const diasAtivosUniaoRel=diasAtualRel.filter(d=>AREAS_SCORE_REL.some(a=>a.set.has(d))).length
  function labelScoreRel(v:number){if(v>=80)return 'Ótimo';if(v>=60)return 'Bom';if(v>=40)return 'Regular';return 'Baixo'}

  function agregarPontosRel(set:Set<string>|null,dias:string[],granularidade:'dia'|'semana'|'mes'){
    function scoreDiaUniao(iso:string){return Math.round(AREAS_SCORE_REL.filter(a=>a.set.has(iso)).length/AREAS_SCORE_REL.length*100)}
    function valorDia(iso:string){return set?(set.has(iso)?100:0):scoreDiaUniao(iso)}
    if(granularidade==='dia')return dias.map(iso=>({iso,valor:valorDia(iso)}))
    const grupos=new Map<string,{soma:number,n:number,iso:string}>()
    dias.forEach(iso=>{
      let chave=iso
      if(granularidade==='semana'){const d=new Date(iso+'T12:00:00');const dw=d.getDay();const diff=(dw===0?-6:1-dw);const seg=new Date(d);seg.setDate(seg.getDate()+diff);chave=isoBR(seg)}
      else{chave=iso.slice(0,7)+'-01'}
      const atual=grupos.get(chave)||{soma:0,n:0,iso:chave}
      atual.soma+=valorDia(iso);atual.n+=1
      grupos.set(chave,atual)
    })
    return Array.from(grupos.values()).sort((a,b)=>a.iso.localeCompare(b.iso)).map(g=>({iso:g.iso,valor:Math.round(g.soma/g.n)}))
  }
  const areaSelecionadaInfo=AREAS_SCORE_REL.find(a=>a.chave===areaRel)||null
  const pontosGraficoRel=agregarPontosRel(areaSelecionadaInfo?areaSelecionadaInfo.set:null,diasAtualRel,granularidadeRel)

  function somaAguaPeriodoRel(dias:string[]){return dias.reduce((a,iso)=>a+Number(aguaLogRel[iso]||0),0)}
  const aguaMediaAtualRel=diasAtualRel.length?somaAguaPeriodoRel(diasAtualRel)/diasAtualRel.length:0
  const aguaMediaAnteriorRel=diasAnteriorRel.length?somaAguaPeriodoRel(diasAnteriorRel)/diasAnteriorRel.length:0
  const treinosAtualNRel=treinosRel.filter(t=>diasAtualRel.includes(t.data)).length
  const treinosAnteriorNRel=treinosRel.filter(t=>diasAnteriorRel.includes(t.data)).length
  const minLeituraAtualRel=sessoesLeituraRel.filter(sx=>diasAtualRel.includes(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)
  const minLeituraAnteriorRel=sessoesLeituraRel.filter(sx=>diasAnteriorRel.includes(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)
  const minEstudoAtualRel=sessoesEstudoRel.filter(sx=>diasAtualRel.includes(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)
  const tarefasConcluidasAtualRel=trabalhoItensRel.filter(t=>t.concluidaEm&&diasAtualRel.includes(String(t.concluidaEm).slice(0,10))).length
  const tarefasConcluidasAnteriorRel=trabalhoItensRel.filter(t=>t.concluidaEm&&diasAnteriorRel.includes(String(t.concluidaEm).slice(0,10))).length
  const tarefasAtrasadasRel=trabalhoItensRel.filter(t=>t.s!=='concluído'&&calcPrazoLabelTrab(t.prazo)?.atrasada).length
  const tarefasAguardandoRel=trabalhoItensRel.filter(t=>t.s==='aguardando').length
  const proteinaMediaRel=diasAtualRel.length?diasAtualRel.reduce((a,iso)=>a+((refsLogRel[iso]||[]).reduce((x,r)=>x+(r.prot||0),0)),0)/diasAtualRel.length:0
  const diasComMetaProtRel=diasAtualRel.filter(iso=>(refsLogRel[iso]||[]).reduce((a,r)=>a+(r.prot||0),0)>=metaProteinaRel).length
  const mediaRefeicoesRel=diasAtualRel.length?(diasAtualRel.reduce((a,iso)=>a+((refsLogRel[iso]||[]).length),0)/diasAtualRel.length):0

  const seqLeituraPeriodoRel=sequenciaMaximaNoPeriodo(new Set(sessoesLeituraRel.map(sx=>sx.data)),diasAtualRel)
  const contasPeriodoRel=casaItensRel.filter(it=>it.cat==='Contas'&&it.pago&&it.pagoEm&&diasAtualRel.includes(String(it.pagoEm).slice(0,10)))
  const contasNoPrazoRel=contasPeriodoRel.filter(it=>!it.venc||String(it.pagoEm).slice(0,10)<=(it.venc as string)).length
  const contasAtrasadasAgoraRel=casaItensRel.filter(it=>it.cat==='Contas'&&!it.pago&&calcStatusContaCasa(it).atrasada).length
  const pixelsavConcluidasRel=trabalhoItensRel.filter(t=>t.p==='PixelSAV'&&t.s==='concluído'&&t.concluidaEm&&diasAtualRel.includes(String(t.concluidaEm).slice(0,10))).length
  const mercadoConcluidoRel=casaItensRel.filter(it=>it.cat==='Mercado'&&it.done&&it.compradoEm&&diasAtualRel.includes(String(it.compradoEm).slice(0,10))).length
  const destaquesRel:string[]=[]
  if(seqLeituraPeriodoRel>=2)destaquesRel.push(`Maior sequência de leitura do período: ${seqLeituraPeriodoRel} dias`)
  if(treinosAtualNRel>0)destaquesRel.push(`${treinosAtualNRel} treino${treinosAtualNRel===1?'':'s'} realizado${treinosAtualNRel===1?'':'s'} no período`)
  if(tarefasConcluidasAtualRel>0)destaquesRel.push(`${tarefasConcluidasAtualRel} tarefa${tarefasConcluidasAtualRel===1?'':'s'} concluída${tarefasConcluidasAtualRel===1?'':'s'} no período`)
  if(pixelsavConcluidasRel>0)destaquesRel.push(`${pixelsavConcluidasRel} tarefa${pixelsavConcluidasRel===1?'':'s'} da PixelSAV concluída${pixelsavConcluidasRel===1?'':'s'} no período`)
  if(contasPeriodoRel.length>0)destaquesRel.push(contasNoPrazoRel===contasPeriodoRel.length?`Todas as ${contasPeriodoRel.length} contas pagas no período estavam em dia`:`${contasNoPrazoRel} de ${contasPeriodoRel.length} contas pagas no prazo`)
  if(contasAtrasadasAgoraRel===0)destaquesRel.push('Nenhuma conta em atraso no momento')
  if(mercadoConcluidoRel>0)destaquesRel.push(`${mercadoConcluidoRel} item${mercadoConcluidoRel===1?'':'ns'} de mercado resolvido${mercadoConcluidoRel===1?'':'s'} no período`)

  const comparacoesRel:[string,string,string,number|null][]=[
    ['Score geral',`${scorePeriodoAtual}%`,`${scorePeriodoAnterior}%`,deltaScorePeriodo],
    ['Água média',`${(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia`,`${(aguaMediaAnteriorRel/1000).toFixed(1).replace('.',',')} L/dia`,Math.round(aguaMediaAtualRel-aguaMediaAnteriorRel)],
    ['Treinos realizados',String(treinosAtualNRel),String(treinosAnteriorNRel),treinosAtualNRel-treinosAnteriorNRel],
    ['Minutos de leitura',String(minLeituraAtualRel),String(minLeituraAnteriorRel),minLeituraAtualRel-minLeituraAnteriorRel],
    ['Tarefas concluídas',String(tarefasConcluidasAtualRel),String(tarefasConcluidasAnteriorRel),tarefasConcluidasAtualRel-tarefasConcluidasAnteriorRel],
  ]

  function perguntarLunaSobreRelatorio(){
    const areaNome=AREAS_REL_INFO.find(a=>a.key===areaRel)?.nome||'Visão geral'
    const periodoTxt=periodoRel==='semana'?'esta semana':periodoRel==='30d'?'os últimos 30 dias':periodoRel==='90d'?'os últimos 90 dias':periodoRel==='ano'?'este ano':`de ${janela.inicioIso} a ${janela.fimIso}`
    const pergunta=`Analisando o relatório de "${areaNome}" em ${periodoTxt}: o score está em ${scorePeriodoAtual}% (era ${scorePeriodoAnterior}% no período anterior). O que mais chama atenção nesses números?`
    try{localStorage.setItem('dos_luna_pergunta_pendente',pergunta)}catch{}
    navigate('/assistente')
  }
  function exportarRelatorioRel(){window.print()}

  const CardResumoRel=({icone,titulo,valor,sub,cor}:{icone:string,titulo:string,valor:string,sub?:React.ReactNode,cor?:string})=>(
    <div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:8}}><span style={{fontSize:16}}>{icone}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)'}}>{titulo}</span></div>
      <div style={{fontSize:20,fontWeight:800,color:cor||'#fff'}}>{valor}</div>
      {sub&&<div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}>{sub}</div>}
    </div>
  )
  const Seta=({delta}:{delta:number|null})=>delta===null?null:(<span style={{color:delta>0?C.ok:delta<0?C.danger:'rgba(255,255,255,.4)',fontWeight:700}}>{delta>0?'▲':delta<0?'▼':'—'} {Math.abs(delta)}%</span>)

  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:6,flexWrap:'wrap' as const}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Relatórios</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Acompanhe sua evolução ao longo do tempo</p></div>
      <div style={{display:'flex',gap:10,flexWrap:'wrap' as const}}>
        <button onClick={perguntarLunaSobreRelatorio} style={{display:'inline-flex',alignItems:'center',gap:7,background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:10,padding:'9px 14px',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>🌙 Perguntar à Luna sobre este relatório</button>
        <button onClick={exportarRelatorioRel} style={{display:'inline-flex',alignItems:'center',gap:7,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 16px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>⬇ Exportar relatório</button>
      </div>
    </div>

    <div style={{display:'flex',gap:10,marginBottom:14,flexWrap:'wrap' as const,alignItems:'center'}}>
      <select value={periodoRel} onChange={e=>setPeriodoRel(e.target.value as any)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}>
        <option value="semana">Esta semana</option><option value="30d">Últimos 30 dias</option><option value="90d">Últimos 90 dias</option><option value="ano">Este ano</option><option value="personalizado">Personalizado</option>
      </select>
      {periodoRel==='personalizado'&&<>
        <input type="date" value={personalizadoIniRel} onChange={e=>setPersonalizadoIniRel(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}/>
        <span style={{color:'rgba(255,255,255,.3)',fontSize:12}}>até</span>
        <input type="date" value={personalizadoFimRel} onChange={e=>setPersonalizadoFimRel(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}/>
      </>}
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'rgba(255,255,255,.5)',fontSize:12.5}}>Comparando com: {diasAtualRel.length} dia{diasAtualRel.length===1?'':'s'} anteriores</div>
      <div style={{flex:1}}/>
      <div style={{display:'flex',gap:4,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:4,flexWrap:'wrap' as const}}>
        {AREAS_REL_INFO.map(a=>(<button key={a.key} onClick={()=>setAreaRel(a.key)} title={a.nome} style={{background:areaRel===a.key?`linear-gradient(135deg,${C.acc},#7c3aed)`:'transparent',border:'none',borderRadius:8,color:areaRel===a.key?'#fff':'rgba(255,255,255,.5)',fontSize:13,padding:'6px 9px',cursor:'pointer'}}>{a.icone}{areaRel===a.key?` ${a.nome}`:''}</button>))}
      </div>
    </div>

    {!temAlgumDadoRel&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)',background:'rgba(255,255,255,.03)',border:`1px dashed ${C.line}`,borderRadius:12,padding:'16px 18px',marginBottom:16}}>Sem dados suficientes neste período. Continue registrando pelo app para os relatórios ganharem forma.</div>}

    {areaRel==='geral'&&<>
      <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:12,marginBottom:16}}>
        <CardResumoRel icone="💜" titulo="Score do período" valor={`${scorePeriodoAtual}%`} cor={C.acc2} sub={<span>{labelScoreRel(scorePeriodoAtual)} · <Seta delta={deltaScorePeriodo}/></span>}/>
        <CardResumoRel icone="🏆" titulo="Melhor área" valor={melhorAreaRel?melhorAreaRel.nome:'—'} cor={C.ok} sub={melhorAreaRel?`${melhorAreaRel.atual}% no período`:''}/>
        <CardResumoRel icone="⚠️" titulo="Área com menor consistência" valor={piorAreaRel?piorAreaRel.nome:'—'} cor={C.warn} sub={piorAreaRel?`${piorAreaRel.atual}% no período`:''}/>
        <CardResumoRel icone="📅" titulo="Dias ativos" valor={`${diasAtivosUniaoRel} de ${diasAtualRel.length}`} sub={`${Math.round(diasAtivosUniaoRel/(diasAtualRel.length||1)*100)}% dos dias`}/>
        <CardResumoRel icone="📈" titulo="Média geral" valor={`${(scorePeriodoAtual/10).toFixed(1)} / 10`} sub={<span>{(scorePeriodoAnterior/10).toFixed(1)} anterior · <Seta delta={deltaScorePeriodo}/></span>}/>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1.7fr 1fr',gap:16,marginBottom:16}}>
        <Card title="Evolução do período" action={<div style={{display:'flex',gap:4}}>{(['dia','semana','mes'] as const).map(g=>(<button key={g} onClick={()=>setGranularidadeRel(g)} style={{background:granularidadeRel===g?'rgba(139,92,246,.15)':'transparent',border:`1px solid ${granularidadeRel===g?'rgba(139,92,246,.3)':C.line}`,color:granularidadeRel===g?C.acc2:'rgba(255,255,255,.4)',borderRadius:8,padding:'5px 10px',fontSize:11.5,cursor:'pointer'}}>{g==='dia'?'Dia':g==='semana'?'Semana':'Mês'}</button>))}</div>}>
          <LinhaEvolucao pontos={pontosGraficoRel} cor={C.acc2} unidade="%" rotulo="Score geral"/>
        </Card>
        <Card title="Consistência por área">
          <div style={{maxHeight:280,overflowY:'auto' as const}}>
            <div style={{display:'grid',gridTemplateColumns:'1.3fr .7fr .7fr .7fr',gap:6,fontSize:11,color:'rgba(255,255,255,.35)',padding:'0 0 8px'}}><span>Área</span><span>Atual</span><span>Anterior</span><span>Variação</span></div>
            {consistenciaPorArea.map(a=>(<div key={a.chave} onClick={()=>setAreaRel(a.chave)} style={{display:'grid',gridTemplateColumns:'1.3fr .7fr .7fr .7fr',gap:6,padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,cursor:'pointer'}}>
              <span>{a.nome}</span><span style={{fontWeight:700}}>{a.atual}%</span><span style={{color:'rgba(255,255,255,.5)'}}>{a.anterior}%</span><Seta delta={a.atual-a.anterior}/>
            </div>))}
          </div>
          <button onClick={()=>setAreaRel(piorAreaRel?piorAreaRel.chave:'saude')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'8px 0 0'}}>Ver relatório completo por área →</button>
        </Card>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1.7fr 1fr',gap:16,marginBottom:16}}>
        <Card title="Destaques do período">
          {destaquesRel.length===0?<div style={{fontSize:12.5,color:'rgba(255,255,255,.35)'}}>Sem destaques suficientes neste período.</div>:
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))',gap:10}}>
            {destaquesRel.map((d,i)=>(<div key={i} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 12px',fontSize:12.5,color:'rgba(255,255,255,.8)'}}>{d}</div>))}
          </div>}
        </Card>
        <Card title="Comparação com período anterior">
          <div style={{maxHeight:220,overflowY:'auto' as const}}>
            {comparacoesRel.map(([lbl,atual,anterior,delta])=>(<div key={lbl} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5}}>
              <span style={{color:'rgba(255,255,255,.6)'}}>{lbl}</span>
              <span style={{display:'flex',gap:8,alignItems:'center'}}><b>{atual}</b><span style={{color:'rgba(255,255,255,.35)',fontSize:11}}>{anterior}</span><Seta delta={delta}/></span>
            </div>))}
          </div>
          <button onClick={()=>{}} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'8px 0 0'}}>Ver todas as comparações →</button>
        </Card>
      </div>

      <Card title="Resumo rápido por área">
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(190px,1fr))',gap:12}}>
          <div onClick={()=>setAreaRel('saude')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.pink}}>❤️ Saúde</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Água média</span><b>{(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
          </div>
          <div onClick={()=>setAreaRel('alimentacao')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.warn}}>🍽️ Alimentação</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Proteína média</span><b>{Math.round(proteinaMediaRel)} g/dia</b></div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Refeições/dia</span><b>{mediaRefeicoesRel.toFixed(1)}</b></div>
          </div>
          <div onClick={()=>setAreaRel('exercicios')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.ok}}>💪 Exercícios</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Treinos</span><b>{treinosAtualNRel}</b></div>
          </div>
          <div onClick={()=>setAreaRel('trabalho')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.danger}}>💼 Trabalho</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Concluídas</span><b>{tarefasConcluidasAtualRel}</b></div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Atrasadas</span><b>{tarefasAtrasadasRel}</b></div>
          </div>
          <div onClick={()=>setAreaRel('desenvolvimento')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:'#fb923c'}}>📈 Desenvolvimento</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Leitura</span><b>{minLeituraAtualRel} min</b></div>
          </div>
        </div>
        <button onClick={()=>{}} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'10px 0 0'}}>Ver todos os indicadores · Explore todos os dados detalhados por área →</button>
      </Card>
    </>}

    {areaRel!=='geral'&&<>
      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12,marginBottom:16}}>
        {areaSelecionadaInfo?<>
          <CardResumoRel icone="💜" titulo="Score da área" valor={`${consistenciaPorArea.find(a=>a.chave===areaRel)?.atual??0}%`} cor={C.acc2}/>
          <CardResumoRel icone="📅" titulo="Dias ativos" valor={`${diasAtualRel.filter(d=>areaSelecionadaInfo.set.has(d)).length} de ${diasAtualRel.length}`}/>
          <CardResumoRel icone="↕️" titulo="Vs. período anterior" valor={`${consistenciaPorArea.find(a=>a.chave===areaRel)?.anterior??0}%`} sub={<Seta delta={(consistenciaPorArea.find(a=>a.chave===areaRel)?.atual??0)-(consistenciaPorArea.find(a=>a.chave===areaRel)?.anterior??0)}/>}/>
        </>:<CardResumoRel icone="👨‍👩‍👧" titulo="Família" valor="Sem score" sub="Família não recebe pontuação — só indicadores."/>}
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1.7fr 1fr',gap:16,marginBottom:16}}>
        <Card title="Evolução do período">
          {areaSelecionadaInfo?<LinhaEvolucao pontos={pontosGraficoRel} cor={C.acc2} unidade="%" rotulo={AREAS_REL_INFO.find(a=>a.key===areaRel)?.nome||''}/>:<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'30px 0',textAlign:'center' as const}}>Família não tem gráfico de consistência (não é pontuada).</div>}
        </Card>
        <Card title={`Indicadores · ${AREAS_REL_INFO.find(a=>a.key===areaRel)?.nome}`}>
          <div style={{maxHeight:280,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:8,fontSize:12.5}}>
            {areaRel==='saude'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Água média</span><b>{(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Meta de água</span><b>{(metaAguaRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Tirzepatida · estoque</span><b>{Object.keys(tzSched).length>0?`${tzBalance} mg`:'—'}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Aplicações registradas</span><b>{tzApps.length}</b></div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:6}}>Peso, sono e humor detalhados por pessoa ficam na Etapa 2 deste relatório — hoje eles moram em Saúde.</div>
            </>}
            {areaRel==='alimentacao'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Proteína média</span><b>{Math.round(proteinaMediaRel)} g/dia</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Dias com meta batida</span><b>{diasComMetaProtRel} de {diasAtualRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Refeições/dia (média)</span><b>{mediaRefeicoesRel.toFixed(1)}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Água média</span><b>{(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
            </>}
            {areaRel==='exercicios'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Treinos realizados</span><b>{treinosAtualNRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Meta semanal</span><b>{lerMetaTreinos()}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Vs. período anterior</span><Seta delta={treinosAtualNRel-treinosAnteriorNRel}/></div>
            </>}
            {areaRel==='espiritual'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Dias com devocional</span><b>{diasAtualRel.filter(d=>diasEspiritualRel.has(d)).length} de {diasAtualRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Sequência atual</span><b>{calcularSequenciaDevocional(devRel)} dias</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Pedidos de oração</span><b>{(()=>{try{return lerPedidosOracao().filter((p:any)=>!p.respondido).length}catch{return 0}})()} em aberto</b></div>
            </>}
            {areaRel==='trabalho'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Concluídas no período</span><b>{tarefasConcluidasAtualRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Atrasadas agora</span><b style={{color:tarefasAtrasadasRel>0?C.danger:'#fff'}}>{tarefasAtrasadasRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Aguardando</span><b>{tarefasAguardandoRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>PixelSAV concluídas</span><b>{pixelsavConcluidasRel}</b></div>
            </>}
            {areaRel==='desenvolvimento'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Minutos de leitura</span><b>{minLeituraAtualRel} min</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Minutos de estudo</span><b>{minEstudoAtualRel} min</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Maior sequência de leitura</span><b>{seqLeituraPeriodoRel} dias</b></div>
            </>}
            {areaRel==='casa'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Itens de mercado resolvidos</span><b>{mercadoConcluidoRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Contas pagas no período</span><b>{contasPeriodoRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Pagas no prazo</span><b>{contasNoPrazoRel} de {contasPeriodoRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Atrasadas agora</span><b style={{color:contasAtrasadasAgoraRel>0?C.danger:'#fff'}}>{contasAtrasadasAgoraRel}</b></div>
            </>}
            {areaRel==='familia'&&<>
              {(['domi','derick'] as const).map(k=>{
                const lista=(avalsFamRel[k]||[]).map(migrarAval)
                const noPeriodo=lista.length
                const realizadas=lista.filter((a:any)=>a.status==='realizado').length
                return(<div key={k} style={{display:'flex',justifyContent:'space-between'}}><span>Avaliações · {k==='domi'?'Domi':'Derick'}</span><b>{realizadas} de {noPeriodo} realizadas</b></div>)
              })}
              <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:6}}>Sem score de família — só indicadores objetivos, como pedido.</div>
            </>}
          </div>
        </Card>
      </div>
    </>}
  </div>)
}
type CategoriaLuna='Saúde'|'Trabalho'|'Família'|'Casa'|'Desenvolvimento'|'Espiritual'
type LunaInsight={id:string,tipo:'atencao'|'padrao'|'progresso'|'sugestao',titulo:string,conclusao:string,evidencia:string,periodo:string,modulo:CategoriaLuna,rota:string,acaoPerguntar?:string,deltaLabel?:string,rotuloCurto?:string,acaoPrimariaLabel?:string}
const ICONE_TIPO_LUNA:Record<LunaInsight['tipo'],string>={atencao:'⚠️',padrao:'🔎',progresso:'📈',sugestao:'💡'}
const LABEL_TIPO_LUNA:Record<LunaInsight['tipo'],string>={atencao:'Atenção',padrao:'Padrão',progresso:'Progresso',sugestao:'Sugestão'}
const COR_TIPO_LUNA:Record<LunaInsight['tipo'],string>={atencao:C.danger,padrao:C.acc2,progresso:C.ok,sugestao:C.warn}
function gerarInsightsLuna(tzSched:Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>,tzBalance:number,periodoDias:number):LunaInsight[]{
  const out:LunaInsight[]=[]
  const hojeG=isoBR(new Date())
  function ultimosNDiasG(n:number):string[]{const arr:string[]=[];for(let i=n-1;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);arr.push(isoBR(d))}return arr}
  function anterioresNDiasG(n:number):string[]{const arr:string[]=[];for(let i=2*n-1;i>=n;i--){const d=new Date();d.setDate(d.getDate()-i);arr.push(isoBR(d))}return arr}
  const ultN=ultimosNDiasG(periodoDias)
  const antN=anterioresNDiasG(periodoDias)

  const casaItensG=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_casa_items')||'[]');return Array.isArray(raw)?raw.map(migrarItemCasa):[]}catch{return []}})() as CasaItem[]
  const contasAtrasadasG=casaItensG.filter(it=>it.cat==='Contas'&&!it.pago&&calcStatusContaCasa(it).atrasada)
  const contasHojeG=casaItensG.filter(it=>it.cat==='Contas'&&!it.pago&&it.venc===hojeG)
  if(contasAtrasadasG.length>0){
    out.push({id:`casa_contas_atrasadas_${contasAtrasadasG.length}`,tipo:'atencao',titulo:`${contasAtrasadasG.length} conta${contasAtrasadasG.length===1?'':'s'} atrasada${contasAtrasadasG.length===1?'':'s'}`,conclusao:`${contasAtrasadasG.map(c=>c.n).join(', ')} — já passou da data de vencimento.`,evidencia:contasAtrasadasG.map(c=>`${c.n}${c.valor?` (R$ ${c.valor.toFixed(2)})`:''}`).join(' · '),periodo:'agora',modulo:'Casa',rota:'/casa',acaoPerguntar:'Quer que eu te ajude a organizar as contas atrasadas da Casa?'})
  }else if(contasHojeG.length>0){
    out.push({id:`casa_contas_hoje_${contasHojeG.length}`,tipo:'atencao',titulo:`${contasHojeG.length} conta${contasHojeG.length===1?'':'s'} vencendo hoje`,conclusao:`${contasHojeG.map(c=>c.n).join(', ')} vence${contasHojeG.length===1?'':'m'} hoje.`,evidencia:contasHojeG.map(c=>`${c.n}${c.valor?` (R$ ${c.valor.toFixed(2)})`:''}`).join(' · '),periodo:'hoje',modulo:'Casa',rota:'/casa'})
  }
  const manutUrgenteG=casaItensG.filter(it=>it.cat==='Manutenção'&&!it.done&&it.prioridade==='alta')
  if(manutUrgenteG.length>0){
    const manutTxtG=manutUrgenteG.length===1?'manutenção de prioridade alta em aberto':'manutenções de prioridade alta em aberto'
    out.push({id:`casa_manut_alta_${manutUrgenteG.length}`,tipo:'atencao',titulo:`${manutUrgenteG.length} ${manutTxtG}`,conclusao:manutUrgenteG.map(m=>m.n).join(', '),evidencia:'Casa · Manutenção',periodo:'agora',modulo:'Casa',rota:'/casa'})
  }

  const tarefasTrabG=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_trabalho')||'[]');return Array.isArray(raw)?raw.map(migrarTarefaTrab):[]}catch{return []}})() as TarefaTrab[]
  const trabAtrasadasG=tarefasTrabG.filter(t=>t.s!=='concluído'&&calcPrazoLabelTrab(t.prazo)?.atrasada)
  if(trabAtrasadasG.length>0){
    out.push({id:`trab_atrasadas_${trabAtrasadasG.length}`,tipo:'atencao',titulo:`${trabAtrasadasG.length} tarefa${trabAtrasadasG.length===1?'':'s'} do Trabalho atrasada${trabAtrasadasG.length===1?'':'s'}`,conclusao:trabAtrasadasG.slice(0,5).map(t=>t.t).join(', '),evidencia:`Projeto${trabAtrasadasG.length===1?'':'s'}: ${Array.from(new Set(trabAtrasadasG.map(t=>t.p))).join(', ')}`,periodo:'agora',modulo:'Trabalho',rota:'/trabalho',acaoPerguntar:'Quer que eu te ajude a priorizar as tarefas atrasadas do Trabalho?'})
  }

  const avalsFamG=(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})() as Record<string,any[]>
  ;(['domi','derick'] as const).forEach(k=>{
    const prox=proximaAvalPendente(avalsFamG[k]||[])
    if(prox&&prox.dias<=2){
      const nome=k==='domi'?'Domi':'Derick'
      out.push({id:`fam_aval_${k}_${prox.aval.data}_${prox.aval.materia}`,tipo:'atencao',titulo:`${nome} tem ${prox.aval.materia} ${prox.dias===0?'hoje':prox.dias===1?'amanhã':`em ${prox.dias} dias`}`,conclusao:`${prox.aval.tipoAvaliacao} de ${prox.aval.materia}, status atual: ${STATUS_AVAL_LABEL[prox.aval.status]}.`,evidencia:`Calendário avaliativo · ${nome}`,periodo:prox.dias===0?'hoje':`em ${prox.dias} dias`,modulo:'Família',rota:'/familia'})
    }
  })

  let autonomiaTzG=0
  if(Object.keys(tzSched).length>0){
    const dDenG=tzSched.denise?.planned_dose_mg||5,dFlaG=tzSched.flavio?.planned_dose_mg||2.5
    const iDenG=tzSched.denise?.interval_days||5,iFlaG=tzSched.flavio?.interval_days||7
    const mgDayG=dDenG/iDenG+dFlaG/iFlaG
    autonomiaTzG=mgDayG>0?Math.floor(tzBalance/mgDayG):0
    if(autonomiaTzG<=14){
      out.push({id:`saude_tz_estoque_baixo_${autonomiaTzG}`,tipo:'atencao',titulo:`Estoque de tirzepatida com autonomia de ~${autonomiaTzG} dias`,conclusao:'O estoque atual está abaixo de 14 dias de autonomia considerando as doses programadas.',evidencia:`Saldo atual: ${tzBalance} mg`,periodo:'agora',modulo:'Saúde',rota:'/saude',acaoPerguntar:'Quer que eu te lembre de repor o estoque de tirzepatida?'})
    }
  }

  const aguaLogG=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
  const aguaPorDiaSemanaG:Record<number,number[]>={}
  Object.keys(aguaLogG).forEach(iso=>{
    const v=Number(aguaLogG[iso]||0)
    if(v<=0)return
    const dw=new Date(iso+'T12:00:00-03:00').getDay()
    if(!aguaPorDiaSemanaG[dw])aguaPorDiaSemanaG[dw]=[]
    aguaPorDiaSemanaG[dw].push(v)
  })
  const DIAS_NOME_G=['domingo','segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado']
  let padraoAguaDiaG:{dw:number,nome:string}|null=null
  const mediasPorDiaG=Object.entries(aguaPorDiaSemanaG).filter(([,vs])=>vs.length>=2).map(([dw,vs])=>({dw:Number(dw),media:vs.reduce((a,b)=>a+b,0)/vs.length,n:vs.length}))
  if(mediasPorDiaG.length>=2){
    const mediaGeralG=mediasPorDiaG.reduce((a,m)=>a+m.media,0)/mediasPorDiaG.length
    const piorDiaG=mediasPorDiaG.reduce((pior,m)=>m.media<pior.media?m:pior)
    if(piorDiaG.media<mediaGeralG*0.85){
      padraoAguaDiaG={dw:piorDiaG.dw,nome:DIAS_NOME_G[piorDiaG.dw]}
      out.push({id:`padrao_agua_dow_${piorDiaG.dw}`,tipo:'padrao',titulo:`Parece haver uma associação entre ${padraoAguaDiaG.nome}s e menor ingestão de água`,conclusao:`Nos registros disponíveis, a ingestão de água às ${padraoAguaDiaG.nome}s tende a ficar abaixo da média dos demais dias.`,evidencia:`Média de ${(piorDiaG.media/1000).toFixed(1).replace('.',',')}L nesse dia vs ${(mediaGeralG/1000).toFixed(1).replace('.',',')}L nos demais dias, com base em ${piorDiaG.n} registros.`,periodo:'baseado no histórico registrado',modulo:'Saúde',rota:'/alimentacao'})
    }
  }

  const treinosConcluidosG=lerTreinos().filter(t=>t.status==='concluido')
  const treinoPorDiaSemanaG:Record<number,number>={}
  treinosConcluidosG.forEach(t=>{const dw=new Date(t.data+'T12:00:00-03:00').getDay();treinoPorDiaSemanaG[dw]=(treinoPorDiaSemanaG[dw]||0)+1})
  const diasComTreinoG=Object.entries(treinoPorDiaSemanaG).filter(([,n])=>n>=2)
  if(treinosConcluidosG.length>=8&&diasComTreinoG.length>=1){
    const melhorDiaG=diasComTreinoG.reduce((a,b)=>b[1]>a[1]?b:a)
    out.push({id:`padrao_treino_dow_${melhorDiaG[0]}`,tipo:'padrao',titulo:`Seus treinos tendem a se concentrar às ${DIAS_NOME_G[Number(melhorDiaG[0])]}s`,conclusao:'Esse é o dia da semana com mais treinos concluídos no seu histórico.',evidencia:`${melhorDiaG[1]} de ${treinosConcluidosG.length} treinos concluídos caíram nesse dia.`,periodo:'baseado no histórico registrado',modulo:'Saúde',rota:'/exercicios'})
  }

  const refsLogG=lerRefsLog()
  const metaProtG=lerMetaProteina()
  function diasComRegistroProtG(dias:string[]){return dias.filter(iso=>(refsLogG[iso]||[]).length>0).length}
  function diasComMetaProtG(dias:string[]){return dias.filter(iso=>{const refs=refsLogG[iso]||[];return refs.reduce((a,r)=>a+(r.prot||0),0)>=metaProtG}).length}
  const regAtualG=diasComRegistroProtG(ultN),regAntG=diasComRegistroProtG(antN)
  if(regAtualG>=3&&regAntG>=3){
    const metaAtualG=diasComMetaProtG(ultN),metaAntG=diasComMetaProtG(antN)
    if(metaAtualG!==metaAntG){
      out.push({id:`progresso_proteina_${periodoDias}_${metaAtualG}_${metaAntG}`,tipo:'progresso',titulo:`Consistência da meta de proteína ${metaAtualG>metaAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Meta batida em ${metaAtualG} de ${ultN.length} dias, contra ${metaAntG} de ${antN.length} dias no período anterior.`,evidencia:`Comparação de ${periodoDias} dias.`,periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/alimentacao',rotuloCurto:'Proteína',deltaLabel:`${metaAtualG-metaAntG>=0?'+':''}${metaAtualG-metaAntG}`})
    }
  }

  function contarTreinosG(dias:string[]){const set=new Set(dias);return treinosConcluidosG.filter(t=>set.has(t.data)).length}
  const treinoAtualG=contarTreinosG(ultN),treinoAntG=contarTreinosG(antN)
  if(treinosConcluidosG.length>=4&&(treinoAtualG>0||treinoAntG>0)&&treinoAtualG!==treinoAntG){
    out.push({id:`progresso_treino_${periodoDias}_${treinoAtualG}_${treinoAntG}`,tipo:'progresso',titulo:`Frequência de treinos ${treinoAtualG>treinoAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${treinoAtualG} treino${treinoAtualG===1?'':'s'} concluído${treinoAtualG===1?'':'s'} nos últimos ${periodoDias} dias, contra ${treinoAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Exercícios.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/exercicios',rotuloCurto:'Treinos',deltaLabel:`${treinoAtualG-treinoAntG>=0?'+':''}${treinoAtualG-treinoAntG}`})
  }

  const sessoesLeituraG=lerSessoesLeituraDev()
  function minutosLeituraG(dias:string[]){const set=new Set(dias);return sessoesLeituraG.filter(sx=>set.has(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)}
  const minAtualG=minutosLeituraG(ultN),minAntG=minutosLeituraG(antN)
  if(sessoesLeituraG.length>=3&&(minAtualG>0||minAntG>0)&&minAtualG!==minAntG){
    out.push({id:`progresso_leitura_${periodoDias}_${minAtualG}_${minAntG}`,tipo:'progresso',titulo:`Tempo de leitura ${minAtualG>minAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${minAtualG} minutos lidos nos últimos ${periodoDias} dias, contra ${minAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Desenvolvimento.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Desenvolvimento',rota:'/desenvolvimento',rotuloCurto:'Leitura',deltaLabel:`${minAtualG-minAntG>=0?'+':''}${minAtualG-minAntG} min`})
  }

  const devEntriesG=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  function diasComDevocionalG(dias:string[]){const set=new Set(dias);return devEntriesG.filter((e:any)=>set.has(e.data)).length}
  const devAtualG=diasComDevocionalG(ultN),devAntG=diasComDevocionalG(antN)
  if(devEntriesG.length>=3&&(devAtualG>0||devAntG>0)&&devAtualG!==devAntG){
    out.push({id:`progresso_devocional_${periodoDias}_${devAtualG}_${devAntG}`,tipo:'progresso',titulo:`Consistência do devocional ${devAtualG>devAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Devocional feito em ${devAtualG} de ${ultN.length} dias, contra ${devAntG} de ${antN.length} dias no período anterior.`,evidencia:'Baseado nos registros de Espiritual.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Espiritual',rota:'/espiritual',rotuloCurto:'Devocional',deltaLabel:`${devAtualG-devAntG>=0?'+':''}${devAtualG-devAntG}`})
  }

  const metaTreinosSemanaG=lerMetaTreinos()
  const segIsoInsG=isoBR(segundaDaSemanaEx(new Date()))
  const treinosEstaSemanaG=treinosConcluidosG.filter(t=>t.data>=segIsoInsG).length
  if(treinosEstaSemanaG<metaTreinosSemanaG){
    const faltaG=metaTreinosSemanaG-treinosEstaSemanaG
    out.push({id:`sugestao_treino_meta_${faltaG}`,tipo:'sugestao',titulo:'Ajustar o plano de treino desta semana?',conclusao:`Faltam ${faltaG} treino${faltaG===1?'':'s'} para bater a meta semanal de ${metaTreinosSemanaG}.`,evidencia:`${treinosEstaSemanaG} de ${metaTreinosSemanaG} treinos concluídos essa semana.`,periodo:'semana atual',modulo:'Saúde',rota:'/exercicios',acaoPerguntar:'Quer me ajudar a encaixar os treinos que faltam essa semana?',acaoPrimariaLabel:'Organizar agora'})
  }
  if(padraoAguaDiaG){
    out.push({id:`sugestao_agua_${padraoAguaDiaG.dw}`,tipo:'sugestao',titulo:`Configurar um lembrete extra de água às ${padraoAguaDiaG.nome}s?`,conclusao:'Baseado no padrão percebido de menor ingestão nesse dia da semana.',evidencia:'Ver o padrão em "Padrões percebidos".',periodo:'sugestão',modulo:'Saúde',rota:'/alimentacao',acaoPerguntar:`Quer me ajudar a lembrar de beber mais água às ${padraoAguaDiaG.nome}s?`,acaoPrimariaLabel:'Configurar lembrete'})
  }
  const leiturasTodasG=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  function diasUnicosG(entries:any[]):Set<string>{return new Set(entries.map((e:any)=>e.data))}
  function sequenciaG(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(isoBR(d))){n++;d.setDate(d.getDate()-1)}return n}
  const seqLeituraAtualG=sequenciaG(diasUnicosG(leiturasTodasG))
  if(leiturasTodasG.length>=5&&seqLeituraAtualG===0){
    out.push({id:'sugestao_retomar_leitura',tipo:'sugestao',titulo:'Retomar a leitura de hoje?',conclusao:'Você tinha um histórico de leitura frequente e não há registro nos últimos dias.',evidencia:`${leiturasTodasG.length} sessões de leitura registradas ao todo.`,periodo:'agora',modulo:'Desenvolvimento',rota:'/desenvolvimento',acaoPerguntar:'Quer que eu te lembre de retomar a leitura hoje?',acaoPrimariaLabel:'Manter'})
  }

  return out
}
function Assistente(){
  const navigate=useNavigate()
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
  const LUNA_CHAT_KEY='dos_luna_chat'
  const LUNA_CONVERSAS_KEY='dos_luna_conversas'
  const LUNA_ATIVA_KEY='dos_luna_conversa_ativa'
  const WHATSAPP_THREAD_ID='whatsapp'
  type LunaMsg={me:boolean,t:string,at?:number}
  type LunaConversa={id:string,titulo:string,criadaEm:string,msgs:LunaMsg[],fixada?:boolean}
  const saudacaoInicial=():LunaMsg[]=>[{me:false,t:`${g}, Denise! Sou a Luna 💜 Pode falar comigo por texto, áudio ou mandar uma foto. Como posso ajudar?`,at:Date.now()}]
  function gerarIdConversa(){return 'c'+Date.now().toString(36)+Math.random().toString(36).slice(2,7)}
  function tituloAPartir(txt:string){const t=txt.trim().replace(/\s+/g,' ');return t.length>40?t.slice(0,40)+'…':(t||'Nova conversa')}

  const [whatsMsgs,setWhatsMsgs]=React.useState<LunaMsg[]>(()=>{
    try{
      const salvo=JSON.parse(localStorage.getItem(LUNA_CHAT_KEY)||'null')
      if(Array.isArray(salvo)&&salvo.length>0)return salvo
    }catch{}
    return saudacaoInicial()
  })
  const [conversas,setConversas]=React.useState<LunaConversa[]>(()=>{
    try{
      const salvo=JSON.parse(localStorage.getItem(LUNA_CONVERSAS_KEY)||'null')
      if(Array.isArray(salvo))return salvo
    }catch{}
    return []
  })
  const [ativaId,setAtivaId]=React.useState<string>(()=>localStorage.getItem(LUNA_ATIVA_KEY)||WHATSAPP_THREAD_ID)

  React.useEffect(()=>{try{localStorage.setItem(LUNA_CHAT_KEY,JSON.stringify(whatsMsgs.slice(-40)))}catch{}},[whatsMsgs])
  React.useEffect(()=>{try{localStorage.setItem(LUNA_CONVERSAS_KEY,JSON.stringify(conversas))}catch{}},[conversas])
  React.useEffect(()=>{try{localStorage.setItem(LUNA_ATIVA_KEY,ativaId)}catch{}},[ativaId])

  React.useEffect(()=>{
    (async()=>{
      try{
        const local=JSON.parse(localStorage.getItem(LUNA_CHAT_KEY)||'null')
        if(Array.isArray(local)&&local.length>1)return
        const {data:snap}=await supabase.from('app_snapshot').select('data').eq('id','denise').maybeSingle()
        const remoto=snap?.data?.[LUNA_CHAT_KEY]
        if(Array.isArray(remoto)&&remoto.length>1){
          setWhatsMsgs(remoto)
          localStorage.setItem(LUNA_CHAT_KEY,JSON.stringify(remoto))
        }
      }catch{}
    })()
  },[])

  const conversaAtiva=ativaId===WHATSAPP_THREAD_ID?null:conversas.find(c=>c.id===ativaId)||null
  const msgs=ativaId===WHATSAPP_THREAD_ID?whatsMsgs:(conversaAtiva?.msgs||[])
  function setMsgsAtual(updater:(prev:LunaMsg[])=>LunaMsg[]){
    if(ativaId===WHATSAPP_THREAD_ID){setWhatsMsgs(prev=>updater(prev));return}
    setConversas(prev=>prev.map(c=>c.id===ativaId?{...c,msgs:updater(c.msgs)}:c))
  }
  const [abaLuna,setAbaLuna]=React.useState<'insights'|'conversar'>('insights')
  React.useEffect(()=>{
    let perguntaPendente:string|null=null
    try{perguntaPendente=localStorage.getItem('dos_luna_pergunta_pendente')}catch{}
    if(!perguntaPendente)return
    try{localStorage.removeItem('dos_luna_pergunta_pendente')}catch{}
    setAbaLuna('conversar')
    send({textoOverride:perguntaPendente})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])
  const [categoriaLuna,setCategoriaLuna]=React.useState<'Todos'|CategoriaLuna>('Todos')
  const [periodoLuna,setPeriodoLuna]=React.useState<7|30|90>(7)
  const [verTodosLuna,setVerTodosLuna]=React.useState<Record<string,boolean>>({})
  const [buscaLuna,setBuscaLuna]=React.useState('')
  const [buscaLunaAberta,setBuscaLunaAberta]=React.useState(false)
  const [buscaConversaLuna,setBuscaConversaLuna]=React.useState('')
  const [ignoradosLuna,setIgnoradosLuna]=React.useState<Record<string,string>>(()=>{try{return JSON.parse(localStorage.getItem('dos_luna_insights_ignorados')||'{}')}catch{return {}}})
  const [tiposOcultosLuna,setTiposOcultosLuna]=React.useState<Record<string,string>>(()=>{try{return JSON.parse(localStorage.getItem('dos_luna_insights_tipos_ocultos')||'{}')}catch{return {}}})
  const [feedbackLuna,setFeedbackLuna]=React.useState<Record<string,'util'|'nao_util'>>(()=>{try{return JSON.parse(localStorage.getItem('dos_luna_insights_feedback')||'{}')}catch{return {}}})
  function ignorarInsightLuna(id:string){const n={...ignoradosLuna,[id]:isoBR(new Date(Date.now()+3*86400000))};setIgnoradosLuna(n);localStorage.setItem('dos_luna_insights_ignorados',JSON.stringify(n))}
  function ocultarTipoLuna(tipo:string){const n={...tiposOcultosLuna,[tipo]:isoBR(new Date(Date.now()+14*86400000))};setTiposOcultosLuna(n);localStorage.setItem('dos_luna_insights_tipos_ocultos',JSON.stringify(n))}
  function darFeedbackLuna(id:string,v:'util'|'nao_util'){const n={...feedbackLuna,[id]:v};setFeedbackLuna(n);localStorage.setItem('dos_luna_insights_feedback',JSON.stringify(n))}
  function perguntarLuna(pergunta:string){setAbaLuna('conversar');send({textoOverride:pergunta})}
  function novaConversa(){
    const id=gerarIdConversa()
    const nova:LunaConversa={id,titulo:'Nova conversa',criadaEm:new Date().toISOString(),msgs:saudacaoInicial()}
    setConversas(prev=>[nova,...prev])
    setAtivaId(id)
  }
  function excluirConversa(id:string){
    setConversas(prev=>prev.filter(c=>c.id!==id))
    if(ativaId===id)setAtivaId(WHATSAPP_THREAD_ID)
  }
  const [inp,setInp]=React.useState('')
  const [sending,setSending]=React.useState(false)
  const [pendingImg,setPendingImg]=React.useState<{mediaType:string,base64:string,preview:string}|null>(null)
  const [recording,setRecording]=React.useState(false)
  const fileRef=React.useRef<HTMLInputElement>(null)
  const mediaRecRef=React.useRef<MediaRecorder|null>(null)
  const chunksRef=React.useRef<Blob[]>([])

  function toBase64(blob:Blob):Promise<string>{return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(String(r.result).split(',')[1]||'');r.onerror=rej;r.readAsDataURL(blob)})}
  function renderMsgLuna(t:string){
    return t.split('\n').map((linha,li)=>{
      const bullet=/^[-•]\s+/.test(linha)
      const conteudo=bullet?linha.replace(/^[-•]\s+/,''):linha
      const partes=conteudo.split(/(\*\*[^*]+\*\*)/g).filter(pt=>pt.length>0).map((pt,pi)=>pt.startsWith('**')&&pt.endsWith('**')?<b key={pi}>{pt.slice(2,-2)}</b>:<span key={pi}>{pt}</span>)
      return <div key={li} style={{display:'flex',gap:6}}>{bullet&&<span>•</span>}<span>{partes}</span></div>
    })
  }

  function montarContexto(){
    const treinosI=(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter(t=>t.status!=='nao_realizado')}catch{return []}})() as any[]
    const leiturasI=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
    const devI=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
    const casaI=(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})() as any[]
    const livroI=(()=>{try{return JSON.parse(localStorage.getItem('dos_livro_atual')||'null')}catch{return null}})() as any
    const agendaLocal=(()=>{try{return JSON.parse(localStorage.getItem('dos_agenda')||'[]')}catch{return []}})() as any[]
    const agendaGoogle=(()=>{try{return JSON.parse(localStorage.getItem('dos_google_events_cache')||'[]')}catch{return []}})() as any[]
    const medicamentosI=(()=>{try{return JSON.parse(localStorage.getItem('dos_medicamentos')||'{}')}catch{return {}}})() as any
    const trabalhoI=(()=>{try{return JSON.parse(localStorage.getItem('dos_trabalho')||'[]')}catch{return []}})() as any[]
    const rotinaItensI=(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'[]')}catch{return []}})() as any[]
    function diasUnicos(entries:any[]):Set<string>{return new Set(entries.map((e:any)=>e.data))}
    function sequencia(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(isoBR(d))){n++;d.setDate(d.getDate()-1)}return n}
    const hojeIso=isoBR(new Date())
    const em7diasIso=isoBR(new Date(Date.now()+7*86400000))
    const contasVencendo=casaI.filter((i:any)=>i.cat==='Contas'&&i.venc&&!i.done&&i.venc>=hojeIso&&i.venc<=em7diasIso)
    const rotinaDoneHoje=(()=>{try{return JSON.parse(localStorage.getItem(`dos_rotina_done_${hojeIso}`)||'[]')}catch{return []}})() as number[]
    const agendaProximos7Dias=[
      ...agendaLocal.map((e:any)=>({data:e.data,hora:e.hora,titulo:e.nome,origem:'app'})),
      ...agendaGoogle.map((ev:any)=>{const dtEv=ev.start?.dateTime?new Date(ev.start.dateTime):null;return{data:(ev.start?.dateTime||ev.start?.date||'').slice(0,10),hora:dtEv?`${String(dtEv.getHours()).padStart(2,'0')}:${String(dtEv.getMinutes()).padStart(2,'0')}`:'',titulo:ev.summary||'(sem titulo)',origem:'google_calendar'}}),
    ].filter(e=>e.data>=hojeIso&&e.data<=em7diasIso).sort((a,b)=>(a.data+a.hora).localeCompare(b.data+b.hora))
    const agendaEditavel=lerEventosAgenda().filter((e:any)=>!e.ehMestre&&e.data>=hojeIso).slice(0,60).map((e:any)=>({id:e.id,nome:e.nome,data:e.data,hora:e.hora,categoria:e.categoria,local:e.local}))
    const aguaLogCtx=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
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
      sequencia_treinos_dias:sequencia(diasUnicos(treinosI)),
      sequencia_leitura_dias:sequencia(diasUnicos(leiturasI)),
      sequencia_devocional_dias:sequencia(diasUnicos(devI)),
      devocional_feito_hoje:devI.some((e:any)=>e.data===hojeIso),
      devocionais_recentes:devI.slice(0,14),
      pedidos_oracao:lerPedidosOracao(),
      planos_leitura_biblica:lerPlanosLeituraBiblia().map((p:any)=>({nome:p.nome,concluidas:p.concluidas,total:p.total,leitura_de_hoje:p.leituraAtual})),
      livro_atual:livroI,
      contas_vencendo_7dias:contasVencendo.map((c:any)=>({nome:c.n,vencimento:c.venc})),
      agenda_proximos_7dias:agendaProximos7Dias,
      agenda_eventos_editaveis_pela_luna:agendaEditavel,
      rotina_de_hoje:rotinaItensI.map((it:any,i:number)=>({horario:it.t,nome:it.n,categoria:it.cat,feito_hoje:rotinaDoneHoje.includes(i)})),
      medicamentos:medicamentosI,
      trabalho_tarefas:trabalhoI,
    }
  }

  function extrairAcaoAgenda(texto:string):{textoLimpo:string,acao:any|null}{
    const m=/```agenda_action\s*([\s\S]*?)```/.exec(texto||'')
    if(!m)return {textoLimpo:texto||'',acao:null}
    let acao=null
    try{acao=JSON.parse(m[1].trim())}catch{}
    const textoLimpo=(texto.slice(0,m.index)+texto.slice(m.index+m[0].length)).trim()
    return {textoLimpo:textoLimpo||'Ok!',acao}
  }

  const [acaoPendente,setAcaoPendente]=React.useState<any>(null)

  async function confirmarAcaoLuna(){
    if(!acaoPendente)return
    try{
      if(acaoPendente.acao==='criar'){
        await criarEventoAgenda(acaoPendente.evento||{})
        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento criado na agenda e sincronizado com o Google Calendar.',at:Date.now()}])
      }else if(acaoPendente.acao==='editar'&&acaoPendente.id){
        await editarEventoAgenda(acaoPendente.id,acaoPendente.evento||{},'este')
        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento atualizado na agenda.',at:Date.now()}])
      }else if(acaoPendente.acao==='excluir'&&acaoPendente.id){
        await excluirEventoAgenda(acaoPendente.id,'este')
        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento excluído da agenda e do Google Calendar.',at:Date.now()}])
      }
    }catch{
      setMsgsAtual(m=>[...m,{me:false,t:'😕 Não consegui concluir essa ação na agenda agora.',at:Date.now()}])
    }
    setAcaoPendente(null)
  }

  function cancelarAcaoLuna(){
    setMsgsAtual(m=>[...m,{me:false,t:'Combinado, não fiz nenhuma alteração na agenda.',at:Date.now()}])
    setAcaoPendente(null)
  }

  async function send(extra?:{audio?:{mediaType:string,base64:string},textoOverride?:string}){
    if(sending)return
    const text=(extra?.textoOverride??inp).trim()
    const img=pendingImg
    const audio=extra?.audio
    if(!text&&!img&&!audio)return
    setSending(true)
    setInp('')
    setPendingImg(null)
    const displayText=text||(img?'📷 Imagem enviada':'🎤 Áudio enviado')
    const historyForApi=[...msgs]
    if(ativaId!==WHATSAPP_THREAD_ID&&conversaAtiva?.titulo==='Nova conversa'){
      const novoTitulo=tituloAPartir(displayText)
      setConversas(prev=>prev.map(c=>c.id===ativaId?{...c,titulo:novoTitulo}:c))
    }
    setMsgsAtual(m=>[...m,{me:true,t:displayText,at:Date.now()}])
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
      const {textoLimpo,acao}=extrairAcaoAgenda(data.reply)
      setMsgsAtual(m=>[...m,{me:false,t:textoLimpo,at:Date.now()}])
      if(acao)setAcaoPendente(acao)
    }catch(err:any){
      setMsgsAtual(m=>[...m,{me:false,t:'😕 '+(err?.message||'Não consegui responder agora. Tenta de novo?'),at:Date.now()}])
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
      setMsgsAtual(m=>[...m,{me:false,t:'Não consegui acessar o microfone. Verifica a permissão de áudio do navegador.',at:Date.now()}])
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

  const insightsBrutosLuna=gerarInsightsLuna(tzSched,tzBalance,periodoLuna)
  const hojeIsoFiltroLuna=isoBR(new Date())
  const insightsVisiveisLuna=insightsBrutosLuna.filter(ins=>{
    if(tiposOcultosLuna[ins.tipo]&&tiposOcultosLuna[ins.tipo]>=hojeIsoFiltroLuna)return false
    if(ignoradosLuna[ins.id]&&ignoradosLuna[ins.id]>=hojeIsoFiltroLuna)return false
    if(categoriaLuna!=='Todos'&&ins.modulo!==categoriaLuna)return false
    if(buscaLuna.trim()&&!ins.titulo.toLowerCase().includes(buscaLuna.trim().toLowerCase()))return false
    return true
  })
  const porTipoLuna={
    atencao:insightsVisiveisLuna.filter(i=>i.tipo==='atencao'),
    padrao:insightsVisiveisLuna.filter(i=>i.tipo==='padrao'),
    progresso:insightsVisiveisLuna.filter(i=>i.tipo==='progresso'),
    sugestao:insightsVisiveisLuna.filter(i=>i.tipo==='sugestao'),
  }
  function MenuInsightLuna({ins}:{ins:LunaInsight}){
    const [aberto,setAberto]=React.useState(false)
    const fb=feedbackLuna[ins.id]
    return(<div style={{position:'relative' as const}}>
      <button onClick={()=>setAberto(v=>!v)} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.4)',fontSize:16,cursor:'pointer',padding:'0 4px'}}>⋯</button>
      {aberto&&<div onMouseLeave={()=>setAberto(false)} style={{position:'absolute' as const,right:0,top:24,background:'#1c1c28',border:`1px solid ${C.line}`,borderRadius:10,padding:6,zIndex:10,minWidth:190,boxShadow:'0 8px 24px rgba(0,0,0,.4)'}}>
        <button onClick={()=>{darFeedbackLuna(ins.id,'util');setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:fb==='util'?C.ok:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>👍 Útil</button>
        <button onClick={()=>{darFeedbackLuna(ins.id,'nao_util');setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:fb==='nao_util'?C.danger:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>👎 Não é útil</button>
        <button onClick={()=>{ignorarInsightLuna(ins.id);setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>Ignorar</button>
        <button onClick={()=>{ocultarTipoLuna(ins.tipo);setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>Não mostrar {LABEL_TIPO_LUNA[ins.tipo].toLowerCase()}</button>
      </div>}
    </div>)
  }
  function badgeAtencaoLuna(ins:LunaInsight):{label:string,cor:string}{
    if(ins.id.startsWith('casa_contas_atrasadas'))return {label:'Atrasada',cor:C.danger}
    if(ins.id.startsWith('casa_contas_hoje'))return {label:'Vence hoje',cor:C.danger}
    if(ins.id.startsWith('casa_manut_alta'))return {label:'Aguardando',cor:C.warn}
    if(ins.id.startsWith('trab_atrasadas'))return {label:'Atrasadas',cor:C.warn}
    if(ins.id.startsWith('fam_aval')){if(ins.periodo==='hoje')return {label:'Hoje',cor:C.danger};if(ins.periodo==='amanhã')return {label:'Amanhã',cor:C.warn};return {label:'Em breve',cor:C.water}}
    if(ins.id.startsWith('saude_tz_estoque_baixo'))return {label:'Estoque baixo',cor:C.warn}
    return {label:'Atenção',cor:C.warn}
  }
  function CardAtencaoLuna({ins}:{ins:LunaInsight}){
    const badge=badgeAtencaoLuna(ins)
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',flexDirection:'column' as const,gap:10}}>
      <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:6}}>
        <span style={{fontSize:11,fontWeight:700,color:badge.cor,background:hexParaRgbaTrab(badge.cor,.15),padding:'3px 9px',borderRadius:20}}>{badge.label}</span>
        <MenuInsightLuna ins={ins}/>
      </div>
      <div style={{fontWeight:700,fontSize:13.5,lineHeight:1.35}}>{ins.titulo}</div>
      <div style={{fontSize:12,color:'rgba(255,255,255,.55)',lineHeight:1.4}}>{ins.conclusao}</div>
      <div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>{ins.modulo}{ins.evidencia?` · ${ins.evidencia}`:''}</div>
      <div style={{display:'flex',gap:8,marginTop:'auto',flexWrap:'wrap' as const}}>
        <button onClick={()=>navigate(ins.rota)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Ver origem</button>
        {ins.acaoPerguntar&&<button onClick={()=>perguntarLuna(ins.acaoPerguntar as string)} style={{background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Perguntar à Luna</button>}
      </div>
    </div>)
  }
  function CardPadraoLuna({ins}:{ins:LunaInsight}){
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',flexDirection:'column' as const,gap:8}}>
      <div style={{width:34,height:34,borderRadius:10,background:hexParaRgbaTrab(COR_TIPO_LUNA[ins.tipo],.14),display:'grid',placeItems:'center',fontSize:16}}>{ICONE_TIPO_LUNA[ins.tipo]}</div>
      <div style={{fontWeight:700,fontSize:13}}>{ins.rotuloCurto||ins.modulo}</div>
      <div style={{fontSize:12.5,color:'rgba(255,255,255,.6)',lineHeight:1.45}}>{ins.conclusao}</div>
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginTop:'auto'}}>
        <span style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>{ins.periodo}</span>
        <button onClick={()=>perguntarLuna(`Por que você está me mostrando isso: "${ins.titulo}"? Me explica com os números que embasam essa conclusão.`)} style={{background:'transparent',border:'none',color:C.acc2,fontSize:11.5,fontWeight:600,cursor:'pointer'}}>Entender</button>
      </div>
    </div>)
  }
  function CardSugestaoLuna({ins}:{ins:LunaInsight}){
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',flexDirection:'column' as const,gap:10}}>
      <div style={{width:34,height:34,borderRadius:10,background:hexParaRgbaTrab(C.warn,.14),display:'grid',placeItems:'center',fontSize:16}}>{ICONE_TIPO_LUNA['sugestao']}</div>
      <div style={{fontSize:12.5,color:'rgba(255,255,255,.75)',lineHeight:1.45}}>{ins.conclusao||ins.titulo}</div>
      <div style={{display:'flex',gap:8,marginTop:'auto'}}>
        <button onClick={()=>ins.acaoPerguntar?perguntarLuna(ins.acaoPerguntar):ignorarInsightLuna(ins.id)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:8,padding:'7px 14px',fontSize:12,fontWeight:700,cursor:'pointer',flex:1}}>{ins.acaoPrimariaLabel||'Ver'}</button>
        <button onClick={()=>ignorarInsightLuna(ins.id)} style={{background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)',borderRadius:8,padding:'7px 12px',fontSize:12,cursor:'pointer'}}>Depois</button>
      </div>
    </div>)
  }
  function TileProgressoLuna({ins}:{ins:LunaInsight}){
    const positivo=(ins.deltaLabel||'').trim().startsWith('+')
    const negativo=(ins.deltaLabel||'').trim().startsWith('-')
    const cor=positivo?C.ok:negativo?C.danger:'rgba(255,255,255,.6)'
    return(<div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'12px 14px'}}>
      <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>{ins.rotuloCurto||ins.modulo}</div>
      <div style={{fontSize:18,fontWeight:800,color:cor}}>{ins.deltaLabel||'—'}</div>
      <div style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginTop:2}}>vs. período anterior</div>
    </div>)
  }
  const MENSAGEM_VAZIO_LUNA:Record<LunaInsight['tipo'],string>={
    atencao:'Nada pedindo atenção agora — sem contas, tarefas ou avaliações pendentes registradas em Casa, Trabalho e Família (ou ainda não há nada cadastrado nesses módulos).',
    padrao:'Ainda não há histórico suficiente pra identificar um padrão real — é preciso um mínimo de registros de água, treino ou proteína ao longo do tempo.',
    progresso:'Ainda não há duas janelas de período pra comparar — é preciso ter registrado proteína, treino, leitura ou devocional em pelo menos dois períodos.',
    sugestao:'Nenhuma sugestão da Luna no momento.',
  }
  function SecaoInsightsLuna({titulo,tipo,itens}:{titulo:string,tipo:LunaInsight['tipo'],itens:LunaInsight[]}){
    const aberta=!!verTodosLuna[tipo]
    const visiveis=aberta?itens:itens.slice(0,3)
    return(<div style={{marginBottom:26}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
        <span style={{fontSize:15}}>{ICONE_TIPO_LUNA[tipo]}</span><span style={{fontWeight:800,fontSize:15}}>{titulo}</span><span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>({itens.length})</span>
      </div>
      {itens.length===0?<div style={{fontSize:12.5,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.03)',border:`1px dashed ${C.line}`,borderRadius:12,padding:'14px 16px'}}>{MENSAGEM_VAZIO_LUNA[tipo]}</div>:<>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:12}}>
        {visiveis.map(ins=>tipo==='atencao'?<CardAtencaoLuna key={ins.id} ins={ins}/>:tipo==='padrao'?<CardPadraoLuna key={ins.id} ins={ins}/>:tipo==='progresso'?<TileProgressoLuna key={ins.id} ins={ins}/>:<CardSugestaoLuna key={ins.id} ins={ins}/>)}
      </div>
      {itens.length>3&&<button onClick={()=>setVerTodosLuna(v=>({...v,[tipo]:!v[tipo]}))} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',marginTop:10,padding:0}}>{aberta?'Ver menos':`Ver todos (${itens.length})`}</button>}
      </>}
    </div>)
  }
  const listaConversasTodasLuna=[{id:WHATSAPP_THREAD_ID,titulo:'WhatsApp',isWhats:true,fixada:true,criadaEm:null as string|null},...conversas.map(c=>({id:c.id,titulo:c.titulo,isWhats:false,fixada:!!c.fixada,criadaEm:(c.criadaEm||null) as string|null}))].filter(c=>!buscaConversaLuna.trim()||c.titulo.toLowerCase().includes(buscaConversaLuna.trim().toLowerCase()))
  const hojeIsoConvLuna=isoBR(new Date())
  const ontemIsoConvLuna=isoBR(new Date(Date.now()-86400000))
  function diaConversaLuna(criadaEm:string|null){if(!criadaEm)return null;try{return isoBR(new Date(criadaEm))}catch{return null}}
  const grupoFixadasConvLuna=listaConversasTodasLuna.filter(c=>c.fixada)
  const naoFixadasConvLuna=listaConversasTodasLuna.filter(c=>!c.fixada)
  const grupoHojeConvLuna=naoFixadasConvLuna.filter(c=>diaConversaLuna(c.criadaEm)===hojeIsoConvLuna)
  const grupoOntemConvLuna=naoFixadasConvLuna.filter(c=>diaConversaLuna(c.criadaEm)===ontemIsoConvLuna)
  const grupoRecentesConvLuna=naoFixadasConvLuna.filter(c=>{const d=diaConversaLuna(c.criadaEm);return d!==hojeIsoConvLuna&&d!==ontemIsoConvLuna})
  function togglePinConversaLuna(id:string){setConversas(prev=>prev.map(c=>c.id===id?{...c,fixada:!c.fixada}:c))}
  function ItemConversaLuna({c}:{c:{id:string,titulo:string,isWhats:boolean,fixada:boolean,criadaEm:string|null}}){
    const horario=c.criadaEm?(()=>{try{return new Date(c.criadaEm as string).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}catch{return ''}})():''
    return(<div onClick={()=>setAtivaId(c.id)} style={{display:'flex',alignItems:'center',gap:6,padding:'9px 10px',borderRadius:10,cursor:'pointer',background:ativaId===c.id?'rgba(139,92,246,.15)':'transparent',color:ativaId===c.id?'#fff':'rgba(255,255,255,.6)'}}>
      <span style={{fontSize:13,flex:1,overflow:'hidden',textOverflow:'ellipsis' as const,whiteSpace:'nowrap' as const}}>{c.isWhats?'💬 ':''}{c.titulo}</span>
      {horario&&<span style={{fontSize:10,color:'rgba(255,255,255,.3)',flexShrink:0}}>{horario}</span>}
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();togglePinConversaLuna(c.id)}} title={c.fixada?'Desafixar':'Fixar'} style={{background:'none',border:'none',color:c.fixada?C.warn:'rgba(255,255,255,.25)',cursor:'pointer',fontSize:12,flexShrink:0}}>📌</button>}
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();excluirConversa(c.id)}} style={{background:'none',border:'none',color:'rgba(255,255,255,.3)',cursor:'pointer',fontSize:12,flexShrink:0}}>✕</button>}
    </div>)
  }
  const chipsContextuaisLuna=(()=>{const base=insightsVisiveisLuna.filter(i=>i.tipo==='atencao'||i.tipo==='sugestao').slice(0,4).map(i=>i.titulo);return base.length>0?base:['Resumo do dia']})()
  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:12,marginBottom:16,flexWrap:'wrap' as const}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>✨ Luna</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Sua inteligência pessoal do Denise OS</p></div>
      <div style={{display:'flex',alignItems:'center',gap:10}}>
        {abaLuna==='conversar'&&<button onClick={novaConversa} style={{background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer',flexShrink:0,whiteSpace:'nowrap' as const}}>+ Nova conversa</button>}
        {buscaLunaAberta?<input autoFocus value={buscaLuna} onChange={e=>setBuscaLuna(e.target.value)} onBlur={()=>{if(!buscaLuna)setBuscaLunaAberta(false)}} placeholder="Buscar insight…" style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:9,padding:'8px 12px',color:'#fff',fontSize:12.5,width:160}}/>:<button onClick={()=>setBuscaLunaAberta(true)} title="Buscar" style={{width:36,height:36,borderRadius:9,background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:14}}>🔎</button>}
        <button title="Notificações" style={{position:'relative' as const,width:36,height:36,borderRadius:9,background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:14}}>🔔{porTipoLuna.atencao.length>0&&<span style={{position:'absolute' as const,top:-4,right:-4,background:C.danger,color:'#fff',borderRadius:20,fontSize:9.5,fontWeight:700,padding:'1px 5px',minWidth:16,textAlign:'center' as const}}>{porTipoLuna.atencao.length}</span>}</button>
        <span title="Tema" style={{width:36,height:36,borderRadius:9,background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.4)',display:'grid',placeItems:'center',fontSize:14}}>🌙</span>
        <div onClick={()=>navigate('/config')} style={{display:'flex',alignItems:'center',gap:8,cursor:'pointer',background:C.s2,border:`1px solid ${C.line}`,borderRadius:9,padding:'5px 10px 5px 5px'}}>
          <Avatar id="denise" label="D" size={26} radius={8}/>
          <span style={{fontSize:12.5,fontWeight:600}}>Denise</span>
          <span style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>▾</span>
        </div>
      </div>
    </div>
    <div style={{display:'inline-flex',gap:4,marginBottom:20,background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:4}}>
      {(['insights','conversar'] as const).map(ab=>(<button key={ab} onClick={()=>setAbaLuna(ab)} style={{background:abaLuna===ab?`linear-gradient(135deg,${C.acc},#7c3aed)`:'transparent',border:'none',borderRadius:9,color:abaLuna===ab?'#fff':'rgba(255,255,255,.5)',fontWeight:700,fontSize:13,padding:'8px 18px',cursor:'pointer'}}>{ab==='insights'?'📊 Insights':'💬 Conversar'}</button>))}
    </div>
    {abaLuna==='insights'?(<div>
      <div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const,alignItems:'center'}}>
        <select value={categoriaLuna} onChange={e=>setCategoriaLuna(e.target.value as any)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}>
          {(['Todos','Saúde','Trabalho','Família','Casa','Desenvolvimento','Espiritual'] as const).map(cat=>(<option key={cat} value={cat}>{cat==='Todos'?'Todos os módulos':cat}</option>))}
        </select>
        <select value={periodoLuna} onChange={e=>setPeriodoLuna(Number(e.target.value) as any)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}>
          {([7,30,90] as const).map(n=>(<option key={n} value={n}>Últimos {n} dias</option>))}
        </select>
      </div>
      <SecaoInsightsLuna titulo="O que merece sua atenção" tipo="atencao" itens={porTipoLuna.atencao}/>
      <SecaoInsightsLuna titulo="Padrões percebidos" tipo="padrao" itens={porTipoLuna.padrao}/>
      <SecaoInsightsLuna titulo="Sugestões da Luna" tipo="sugestao" itens={porTipoLuna.sugestao}/>
      <SecaoInsightsLuna titulo="Mudanças e progresso" tipo="progresso" itens={porTipoLuna.progresso}/>
      {insightsVisiveisLuna.length>0&&<button onClick={()=>setVerTodosLuna({atencao:true,padrao:true,progresso:true,sugestao:true})} style={{background:'transparent',border:'none',color:C.acc2,fontSize:13,fontWeight:600,cursor:'pointer',padding:0,marginTop:4}}>Ver todos os insights →</button>}
    </div>):(
    <div style={{display:'flex',gap:16,height:'60vh'}}>
    <div style={{width:220,flexShrink:0,background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:10,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:4}}>
      <input value={buscaConversaLuna} onChange={e=>setBuscaConversaLuna(e.target.value)} placeholder="🔎 Buscar conversas…" style={{background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:9,padding:'7px 10px',color:'#fff',fontSize:12,marginBottom:6}}/>
      <div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'4px 10px 2px'}}>Fixadas</div>
      {grupoFixadasConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {grupoHojeConvLuna.length>0&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'10px 10px 2px'}}>Hoje</div>}
      {grupoHojeConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {grupoOntemConvLuna.length>0&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'10px 10px 2px'}}>Ontem</div>}
      {grupoOntemConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {grupoRecentesConvLuna.length>0&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'10px 10px 2px'}}>Recentes</div>}
      {grupoRecentesConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {conversas.length===0&&<div style={{fontSize:11,color:'rgba(255,255,255,.3)',padding:'8px 10px'}}>Suas conversas aparecem aqui.</div>}
    </div>
    <div style={{flex:1,minWidth:0,background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const}}>
      <div style={{flex:1,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:12,paddingBottom:12}}>
        {msgs.map((m,i)=>(<div key={i} style={{maxWidth:'80%',display:'flex',flexDirection:'column' as const,alignSelf:m.me?'flex-end':'flex-start'}}>
          <div style={{padding:'11px 14px',borderRadius:14,fontSize:13.5,lineHeight:1.5,background:m.me?`linear-gradient(135deg,${C.acc},#7c3aed)`:'rgba(255,255,255,.06)',border:m.me?'none':`1px solid ${C.line}`}}>{renderMsgLuna(m.t)}</div>
          {m.at&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',marginTop:3,textAlign:m.me?'right' as const:'left' as const}}>{new Date(m.at).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}</div>}
        </div>))}
        {sending&&<div style={{alignSelf:'flex-start',padding:'11px 14px',borderRadius:14,fontSize:13.5,background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)'}}>Luna está digitando…</div>}
        {acaoPendente&&<div style={{alignSelf:'flex-start',maxWidth:'85%',padding:'12px 14px',borderRadius:14,fontSize:13,background:'rgba(139,92,246,.1)',border:`1px solid rgba(139,92,246,.3)`}}>
          <div style={{marginBottom:10,color:'rgba(255,255,255,.8)'}}>Confirma essa ação na agenda ({acaoPendente.acao==='criar'?'criar evento':acaoPendente.acao==='editar'?'editar evento':'excluir evento'}{acaoPendente.evento?.nome?`: "${acaoPendente.evento.nome}"`:''}{acaoPendente.evento?.data?` em ${acaoPendente.evento.data}${acaoPendente.evento?.hora?` às ${acaoPendente.evento.hora}`:''}`:''})?</div>
          <div style={{display:'flex',gap:8}}>
            <button onClick={confirmarAcaoLuna} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'8px 14px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>✓ Confirmar</button>
            <button onClick={cancelarAcaoLuna} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'8px 14px',fontSize:12.5,cursor:'pointer'}}>Cancelar</button>
          </div>
        </div>}
      </div>
      {pendingImg&&<div style={{display:'flex',alignItems:'center',gap:8,margin:'8px 0',background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:10,padding:8}}>
        <img src={pendingImg.preview} style={{width:44,height:44,borderRadius:8,objectFit:'cover' as const}}/>
        <span style={{fontSize:12,color:'rgba(255,255,255,.5)',flex:1}}>Imagem anexada</span>
        <button onClick={()=>setPendingImg(null)} style={{background:'none',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:16}}>✕</button>
      </div>}
      <div style={{display:'flex',flexWrap:'wrap' as const,gap:6,margin:'12px 0'}}>{chipsContextuaisLuna.map(c=>(<button key={c} onClick={()=>setInp(c)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:20,padding:'6px 12px',fontSize:11,color:'rgba(255,255,255,.6)',cursor:'pointer'}}>{c}</button>))}</div>
      <div style={{display:'flex',gap:8,background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:12,padding:'8px 8px 8px 14px',alignItems:'center'}}>
        <input ref={fileRef} type="file" accept="image/*" style={{display:'none'}} onChange={escolherImagem}/>
        <button onClick={()=>fileRef.current?.click()} disabled={sending||recording} title="Anexar imagem" style={{background:'none',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:18,flexShrink:0}}>📷</button>
        <button onClick={recording?pararEEnviarGravacao:iniciarGravacao} disabled={sending} title={recording?'Parar e enviar':'Gravar áudio'} style={{background:'none',border:'none',color:recording?C.danger:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:18,flexShrink:0}}>{recording?'⏹':'🎤'}</button>
        <input value={inp} onChange={e=>setInp(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder={recording?'Gravando áudio…':'Pergunte qualquer coisa…'} disabled={recording} style={{flex:1,background:'none',border:'none',color:'#fff',fontSize:13.5,outline:'none'}}/>
        <button onClick={()=>send()} disabled={sending||recording||(!inp.trim()&&!pendingImg)} style={{width:36,height:36,borderRadius:10,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',cursor:'pointer',fontSize:18,flexShrink:0,opacity:(sending||recording||(!inp.trim()&&!pendingImg))?0.5:1}}>↑</button>
      </div>
      <div style={{display:'flex',gap:8,marginTop:10}}>
        <button onClick={()=>{if(ativaId===WHATSAPP_THREAD_ID){if(conversas.length>0)setAtivaId(conversas[0].id);else novaConversa()}}} style={{background:ativaId!==WHATSAPP_THREAD_ID?'rgba(139,92,246,.15)':'transparent',border:`1px solid ${ativaId!==WHATSAPP_THREAD_ID?'rgba(139,92,246,.3)':C.line}`,color:ativaId!==WHATSAPP_THREAD_ID?C.acc2:'rgba(255,255,255,.4)',borderRadius:8,padding:'6px 14px',fontSize:11.5,fontWeight:600,cursor:'pointer'}}>📱 App</button>
        <button onClick={()=>setAtivaId(WHATSAPP_THREAD_ID)} style={{background:ativaId===WHATSAPP_THREAD_ID?'rgba(34,197,94,.15)':'transparent',border:`1px solid ${ativaId===WHATSAPP_THREAD_ID?'rgba(34,197,94,.3)':C.line}`,color:ativaId===WHATSAPP_THREAD_ID?C.ok:'rgba(255,255,255,.4)',borderRadius:8,padding:'6px 14px',fontSize:11.5,fontWeight:600,cursor:'pointer'}}>💬 WhatsApp</button>
      </div>
    </div>
    </div>
    )}
  </div>)
}
function lerCfg(chave:string,padrao:string):string{try{return localStorage.getItem(chave)??padrao}catch{return padrao}}
function lerCfgBool(chave:string,padrao:boolean):boolean{try{const v=localStorage.getItem(chave);return v===null?padrao:JSON.parse(v)}catch{return padrao}}
function Config(){
  const navigate=useNavigate()
  const [nome,setNome]=React.useState(()=>lerCfg('dos_cfg_nome','Denise'))
  const [fuso,setFuso]=React.useState(()=>lerCfg('dos_cfg_fuso','America/Sao_Paulo'))
  const [formatoData,setFormatoData]=React.useState(()=>lerCfg('dos_cfg_formato','DD/MM/AAAA'))
  const [formatoHora,setFormatoHora]=React.useState(()=>lerCfg('dos_cfg_formato_hora','24h'))
  const [localNomeCfg,setLocalNomeCfg]=React.useState(()=>lerCfg('dos_local_nome',''))
  const [localAuto,setLocalAuto]=React.useState(()=>lerCfgBool('dos_cfg_local_auto',true))
  const [unidadePeso,setUnidadePeso]=React.useState(()=>lerCfg('dos_cfg_unidade_peso','kg'))
  const [unidadeAltura,setUnidadeAltura]=React.useState(()=>lerCfg('dos_cfg_unidade_altura','cm/m/km'))
  const [unidadeTemp,setUnidadeTemp]=React.useState(()=>lerCfg('dos_cfg_unidade_temp','C'))
  const [primeiroDiaSemana,setPrimeiroDiaSemana]=React.useState(()=>lerCfg('dos_cfg_primeiro_dia','segunda'))
  const [notif,setNotif]=React.useState(()=>lerCfgBool('dos_cfg_notif',true))
  const [notifWa,setNotifWa]=React.useState(()=>lerCfgBool('dos_cfg_notif_wa',true))
  const [notifImportantes,setNotifImportantes]=React.useState(()=>lerCfgBool('dos_cfg_notif_importantes',true))
  const [resumoManha,setResumoManha]=React.useState(()=>lerCfgBool('dos_cfg_resumo',true))
  const [resumoManhaHorario,setResumoManhaHorario]=React.useState(()=>lerCfg('dos_cfg_resumo_manha_horario','07:00'))
  const [resumoNoite,setResumoNoite]=React.useState(()=>lerCfgBool('dos_cfg_resumo_noite',true))
  const [resumoNoiteHorario,setResumoNoiteHorario]=React.useState(()=>lerCfg('dos_cfg_resumo_noite_horario','20:00'))
  const [resumoSemanal,setResumoSemanal]=React.useState(()=>lerCfgBool('dos_cfg_resumo_semanal',true))
  const [resumoSemanalDia,setResumoSemanalDia]=React.useState(()=>lerCfg('dos_cfg_resumo_semanal_dia','domingo'))
  const [resumoSemanalHorario,setResumoSemanalHorario]=React.useState(()=>lerCfg('dos_cfg_resumo_semanal_horario','19:00'))
  const [mostrarNotifModulo,setMostrarNotifModulo]=React.useState(false)
  const [lunaCanal,setLunaCanal]=React.useState(()=>lerCfg('dos_cfg_luna_canal','ambos'))
  const [lunaMemoria,setLunaMemoria]=React.useState(()=>lerCfgBool('dos_cfg_luna_memoria',true))
  const [mostrarPermissoesLuna,setMostrarPermissoesLuna]=React.useState(false)
  const [tema,setTema]=React.useState(()=>lerCfg('dos_cfg_tema','escuro'))
  const [densidade]=React.useState(()=>lerCfg('dos_cfg_densidade','confortavel'))
  const [statusSalvo,setStatusSalvo]=React.useState<'salvo'|'alterado'|'salvando'>('salvo')

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
      if(!data.base64&&!data.pairingCode){
        setWaQr(null);setWaPairingCode(null)
        setWaErro(data.message||'Não veio um QR novo agora. Verificando o status atual...')
        await verificarStatusWhatsapp()
      }else{
        setWaQr(data.base64||null)
        setWaPairingCode(data.pairingCode||null)
        setWaState('connecting')
      }
    }catch(err:any){setWaErro(err?.message||'Erro ao conectar.')}
    setWaLoading(false)
  }
  const googleConectadoCfg=(()=>{try{const tk=JSON.parse(localStorage.getItem('dos_google_token')||'null');return !!(tk&&tk.token)}catch{return false}})()
  const googleUltimaSyncCfg=(()=>{try{const cache=JSON.parse(localStorage.getItem('dos_google_events_cache')||'null');return Array.isArray(cache)&&cache.length>0}catch{return false}})()

  function marcarAlterado(){setStatusSalvo('alterado')}
  function salvarConfig(){
    setStatusSalvo('salvando')
    localStorage.setItem('dos_cfg_nome',nome)
    localStorage.setItem('dos_cfg_fuso',fuso)
    localStorage.setItem('dos_cfg_formato',formatoData)
    localStorage.setItem('dos_cfg_formato_hora',formatoHora)
    localStorage.setItem('dos_local_nome',localNomeCfg)
    localStorage.setItem('dos_cfg_local_auto',JSON.stringify(localAuto))
    localStorage.setItem('dos_cfg_unidade_peso',unidadePeso)
    localStorage.setItem('dos_cfg_unidade_altura',unidadeAltura)
    localStorage.setItem('dos_cfg_unidade_temp',unidadeTemp)
    localStorage.setItem('dos_cfg_primeiro_dia',primeiroDiaSemana)
    localStorage.setItem('dos_cfg_notif',JSON.stringify(notif))
    localStorage.setItem('dos_cfg_notif_wa',JSON.stringify(notifWa))
    localStorage.setItem('dos_cfg_notif_importantes',JSON.stringify(notifImportantes))
    localStorage.setItem('dos_cfg_resumo',JSON.stringify(resumoManha))
    localStorage.setItem('dos_cfg_resumo_manha_horario',resumoManhaHorario)
    localStorage.setItem('dos_cfg_resumo_noite',JSON.stringify(resumoNoite))
    localStorage.setItem('dos_cfg_resumo_noite_horario',resumoNoiteHorario)
    localStorage.setItem('dos_cfg_resumo_semanal',JSON.stringify(resumoSemanal))
    localStorage.setItem('dos_cfg_resumo_semanal_dia',resumoSemanalDia)
    localStorage.setItem('dos_cfg_resumo_semanal_horario',resumoSemanalHorario)
    localStorage.setItem('dos_cfg_luna_canal',lunaCanal)
    localStorage.setItem('dos_cfg_luna_memoria',JSON.stringify(lunaMemoria))
    localStorage.setItem('dos_cfg_tema',tema)
    localStorage.setItem('dos_cfg_densidade',densidade)
    setTimeout(()=>setStatusSalvo('salvo'),350)
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
    a.download=`denise-os-dados-${isoBR(new Date())}.json`
    document.body.appendChild(a);a.click();document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  function baixarHistoricoCfg(){
    const CHAVES_HISTORICO=['dos_refs_log','dos_agua_log','dos_treinos','dos_leituras','dos_sessoes_leitura','dos_sessoes_estudo','dos_devocionais','dos_luna_conversas','dos_luna_chat']
    const dados:Record<string,any>={}
    CHAVES_HISTORICO.forEach(k=>{try{dados[k]=JSON.parse(localStorage.getItem(k)||'null')}catch{dados[k]=null}})
    const blob=new Blob([JSON.stringify(dados,null,2)],{type:'application/json'})
    const url=URL.createObjectURL(blob)
    const a=document.createElement('a')
    a.href=url
    a.download=`denise-os-historico-${isoBR(new Date())}.json`
    document.body.appendChild(a);a.click();document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  function limparDadosLocaisCfg(){
    if(!window.confirm('Remover cache e dados armazenados neste dispositivo? Isso não apaga os dados salvos no Supabase.'))return
    localStorage.clear()
    window.location.reload()
  }
  const Toggle=({on,toggle}:{on:boolean,toggle:()=>void})=>(<div onClick={toggle} style={{width:44,height:25,borderRadius:20,background:on?C.acc:'rgba(255,255,255,.1)',position:'relative' as const,cursor:'pointer',transition:'.2s',flexShrink:0}}><div style={{position:'absolute' as const,top:2,left:on?21:2,width:21,height:21,borderRadius:'50%',background:'#fff',transition:'.2s'}}/></div>)
  const CampoCfg=({label,children}:{label:string,children:React.ReactNode})=>(<div><label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>{label}</label>{children}</div>)
  const inputCfgStyle:React.CSSProperties={width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 11px',color:'#fff',fontSize:13.5,colorScheme:'dark' as const}
  const LinhaToggleCfg=({label,desc,on,toggle}:{label:string,desc?:string,on:boolean,toggle:()=>void})=>(<div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}><div style={{flex:1,minWidth:0}}><div style={{fontSize:13}}>{label}</div>{desc&&<div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:2}}>{desc}</div>}</div><Toggle on={on} toggle={toggle}/></div>)

  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:20,flexWrap:'wrap' as const}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Configurações</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Personalize sua experiência e gerencie suas preferências no Denise OS</p></div>
      <div style={{display:'flex',gap:10,alignItems:'center'}}>
        {statusSalvo==='salvo'&&<span style={{display:'inline-flex',alignItems:'center',gap:6,background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',color:C.ok,borderRadius:9,padding:'8px 12px',fontSize:12}}>✓ Todas as alterações salvas</span>}
        {statusSalvo==='alterado'&&<span style={{display:'inline-flex',alignItems:'center',gap:6,background:'rgba(251,191,36,.1)',border:'1px solid rgba(251,191,36,.3)',color:C.warn,borderRadius:9,padding:'8px 12px',fontSize:12}}>Alterações não salvas</span>}
        {statusSalvo==='salvando'&&<span style={{display:'inline-flex',alignItems:'center',gap:6,color:'rgba(255,255,255,.5)',fontSize:12}}>Salvando...</span>}
        <button onClick={salvarConfig} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 18px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Salvar alterações</button>
      </div>
    </div>

    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Perfil">
        <div style={{display:'flex',alignItems:'center',gap:14,marginBottom:14}}>
          <Avatar id="denise" label={(nome||'D')[0]} size={56} radius={14}/>
          <div><div style={{fontWeight:700,fontSize:15}}>{nome||'Denise'}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Toque na foto para alterar</div></div>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
          <CampoCfg label="Nome"><input value={nome} onChange={e=>{setNome(e.target.value);marcarAlterado()}} style={inputCfgStyle}/></CampoCfg>
          <CampoCfg label="Idioma"><select value="pt-BR" disabled style={{...inputCfgStyle,opacity:.7}}><option value="pt-BR">Português (Brasil)</option></select></CampoCfg>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
          <CampoCfg label="Fuso horário"><input value={fuso} onChange={e=>{setFuso(e.target.value);marcarAlterado()}} style={inputCfgStyle}/></CampoCfg>
          <CampoCfg label="Formato de data"><select value={formatoData} onChange={e=>{setFormatoData(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="DD/MM/AAAA">DD/MM/AAAA</option><option value="MM/DD/AAAA">MM/DD/AAAA</option><option value="AAAA-MM-DD">AAAA-MM-DD</option></select></CampoCfg>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
          <CampoCfg label="Formato de hora"><select value={formatoHora} onChange={e=>{setFormatoHora(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="24h">24 horas (14:30)</option><option value="12h">12 horas (2:30 PM)</option></select></CampoCfg>
          <CampoCfg label="Cidade / localização"><input value={localNomeCfg} onChange={e=>{setLocalNomeCfg(e.target.value);marcarAlterado()}} placeholder="Ex: Curitiba, PR" style={inputCfgStyle}/></CampoCfg>
        </div>
      </Card>

      <Card title="Preferências">
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
          <CampoCfg label="Unidade de peso"><select value={unidadePeso} onChange={e=>{setUnidadePeso(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="kg">kg</option><option value="lb">lb</option></select></CampoCfg>
          <CampoCfg label="Altura / distância"><select value={unidadeAltura} onChange={e=>{setUnidadeAltura(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="cm/m/km">cm / m / km</option><option value="in/ft/mi">in / ft / mi</option></select></CampoCfg>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
          <CampoCfg label="Primeiro dia da semana"><select value={primeiroDiaSemana} onChange={e=>{setPrimeiroDiaSemana(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="segunda">Segunda-feira</option><option value="domingo">Domingo</option></select></CampoCfg>
          <CampoCfg label="Temperatura"><select value={unidadeTemp} onChange={e=>{setUnidadeTemp(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="C">°C</option><option value="F">°F</option></select></CampoCfg>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:10,marginBottom:6}}>
          <div><div style={{fontSize:13}}>Usar localização automática</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Permite que o sistema use sua localização atual</div></div>
          <Toggle on={localAuto} toggle={()=>{setLocalAuto(v=>!v);marcarAlterado()}}/>
        </div>
        <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginTop:6}}>A cidade acima é a mesma usada na Home e nas sugestões da Luna — uma única fonte de verdade.</p>
      </Card>

      <Card title="Notificações">
        <div style={{fontSize:11,color:'rgba(255,255,255,.35)',textTransform:'uppercase' as const,letterSpacing:'.5px',marginBottom:6}}>Notificações gerais</div>
        <LinhaToggleCfg label="Lembretes no app" on={notif} toggle={()=>{setNotif(v=>!v);marcarAlterado()}}/>
        <LinhaToggleCfg label="WhatsApp" on={notifWa} toggle={()=>{setNotifWa(v=>!v);marcarAlterado()}}/>
        <LinhaToggleCfg label="Notificações importantes" on={notifImportantes} toggle={()=>{setNotifImportantes(v=>!v);marcarAlterado()}}/>
        <div style={{fontSize:11,color:'rgba(255,255,255,.35)',textTransform:'uppercase' as const,letterSpacing:'.5px',margin:'14px 0 6px'}}>Resumos automáticos</div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
          <span style={{fontSize:13}}>☀️ Resumo da manhã</span>
          <div style={{display:'flex',alignItems:'center',gap:8}}>{resumoManha&&<input type="time" value={resumoManhaHorario} onChange={e=>{setResumoManhaHorario(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:90,padding:'5px 8px',fontSize:12}}/>}<Toggle on={resumoManha} toggle={()=>{setResumoManha(v=>!v);marcarAlterado()}}/></div>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
          <span style={{fontSize:13}}>🌙 Resumo da noite</span>
          <div style={{display:'flex',alignItems:'center',gap:8}}>{resumoNoite&&<input type="time" value={resumoNoiteHorario} onChange={e=>{setResumoNoiteHorario(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:90,padding:'5px 8px',fontSize:12}}/>}<Toggle on={resumoNoite} toggle={()=>{setResumoNoite(v=>!v);marcarAlterado()}}/></div>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 0'}}>
          <span style={{fontSize:13}}>📅 Resumo semanal</span>
          <div style={{display:'flex',alignItems:'center',gap:8}}>{resumoSemanal&&<><select value={resumoSemanalDia} onChange={e=>{setResumoSemanalDia(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:110,padding:'5px 6px',fontSize:11.5}}>{['domingo','segunda','terça','quarta','quinta','sexta','sábado'].map(d=>(<option key={d} value={d}>{d[0].toUpperCase()+d.slice(1)}</option>))}</select><input type="time" value={resumoSemanalHorario} onChange={e=>{setResumoSemanalHorario(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:90,padding:'5px 8px',fontSize:12}}/></>}<Toggle on={resumoSemanal} toggle={()=>{setResumoSemanal(v=>!v);marcarAlterado()}}/></div>
        </div>
        <button onClick={()=>setMostrarNotifModulo(v=>!v)} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'10px 0 0'}}>{mostrarNotifModulo?'Ocultar notificações por módulo ▾':'Configurar notificações por módulo →'}</button>
        {mostrarNotifModulo&&<div style={{marginTop:8,padding:12,background:C.s2,borderRadius:10,fontSize:12,color:'rgba(255,255,255,.5)'}}>Ajuste fino por módulo (Agenda, Saúde, Alimentação, Exercícios, Família, Trabalho, Desenvolvimento, Casa, Espiritual) chega numa próxima etapa — hoje as notificações gerais acima já controlam o comportamento de todos os módulos.</div>}
      </Card>

      <Card title="Luna">
        <div style={{display:'flex',justifyContent:'space-between',padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{color:'rgba(255,255,255,.5)'}}>IA da Luna</span><span style={{color:C.ok,fontWeight:700}}>Ativa</span></div>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{color:'rgba(255,255,255,.5)'}}>Canal preferencial</span><select value={lunaCanal} onChange={e=>{setLunaCanal(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:170}}><option value="app">App</option><option value="whatsapp">WhatsApp</option><option value="ambos">Ambos (App e WhatsApp)</option></select></div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13}}>Memória contextual</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Permite que a Luna use contexto de conversas anteriores quando relevante</div></div>
          <Toggle on={lunaMemoria} toggle={()=>{setLunaMemoria(v=>!v);marcarAlterado()}}/>
        </div>
        <button onClick={()=>setMostrarPermissoesLuna(v=>!v)} style={{display:'block',width:'100%',textAlign:'left' as const,background:'transparent',border:'none',color:'rgba(255,255,255,.7)',fontSize:13,cursor:'pointer',padding:'10px 0'}}>Permissões de ação <span style={{color:'rgba(255,255,255,.35)',fontSize:11.5}}>· Defina quando a Luna pode agir automaticamente</span></button>
        {mostrarPermissoesLuna&&<div style={{padding:12,background:C.s2,borderRadius:10,fontSize:12,color:'rgba(255,255,255,.6)',marginBottom:8}}>
          <div style={{marginBottom:8}}><b style={{color:'#fff'}}>Ações simples</b> — a Luna pode executar direto: registrar água, marcar tarefa concluída, adicionar item no mercado.</div>
          <div><b style={{color:'#fff'}}>Ações importantes</b> — a Luna sempre pede confirmação antes: excluir, cancelar, remarcar, alterar protocolo, marcar conta como paga, alterar estoque.</div>
        </div>}
        <button onClick={()=>navigate('/assistente')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:0}}>Usar horários definidos em Notificações →</button>
      </Card>

      <Card title="Integrações">
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Google Calendar</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>{googleConectadoCfg?(googleUltimaSyncCfg?'Sincronizado':'Conectado'):'Não conectado'}</div></div>
          <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,fontWeight:700,color:googleConectadoCfg?C.ok:'rgba(255,255,255,.4)',background:googleConectadoCfg?'rgba(52,211,153,.12)':'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>{googleConectadoCfg?'Conectado':'Não conectado'}</span><button onClick={()=>navigate('/agenda')} style={{background:'none',border:'none',color:'rgba(255,255,255,.4)',cursor:'pointer',fontSize:13}}>›</button></div>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13,fontWeight:600}}>WhatsApp (Luna)</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>{waState==='open'?'Conectado':waState==='carregando'?'Verificando...':'Não conectado'}</div></div>
          <span style={{fontSize:11,fontWeight:700,color:waState==='open'?C.ok:'rgba(255,255,255,.4)',background:waState==='open'?'rgba(52,211,153,.12)':'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>{waState==='open'?'Conectado':waState==='carregando'?'Verificando':'Em breve'}</span>
        </div>
        {waState==='carregando'?null:<div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          {waState==='open'&&<button onClick={conectarWhatsapp} disabled={waLoading} style={{background:'none',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',borderRadius:9,padding:'6px 12px',fontSize:11.5,fontWeight:600,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Verificando...':'Reconectar (gerar novo QR Code)'}</button>}
          {(waState==='close'||waState==='nao_criada'||waState==='erro')&&<button onClick={conectarWhatsapp} disabled={waLoading} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'8px 14px',fontSize:12,fontWeight:700,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Gerando QR Code...':'Gerar QR Code'}</button>}
          {waState==='connecting'&&<div style={{display:'flex',flexDirection:'column' as const,alignItems:'center',gap:8}}>{waQr&&<img src={waQr.startsWith('data:')?waQr:`data:image/png;base64,${waQr}`} alt="QR Code do WhatsApp" style={{width:140,height:140,borderRadius:10,background:'#fff',padding:6}}/>}{waPairingCode&&<div style={{fontSize:12,color:'rgba(255,255,255,.7)'}}>Código: <strong>{waPairingCode}</strong></div>}</div>}
          {waErro&&<div style={{fontSize:11.5,color:C.danger,marginTop:6}}>{waErro}</div>}
        </div>}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13,fontWeight:600,color:'rgba(255,255,255,.5)'}}>Apple Health</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Em breve</div></div>
          <span style={{fontSize:11,fontWeight:700,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>Em breve</span>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0'}}>
          <div><div style={{fontSize:13,fontWeight:600,color:'rgba(255,255,255,.5)'}}>Apple Watch</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Em breve</div></div>
          <span style={{fontSize:11,fontWeight:700,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>Em breve</span>
        </div>
      </Card>

      <Card title="Privacidade e dados">
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Exportar meus dados (LGPD)</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Baixe um arquivo com todos os seus dados</div></div>
          <button onClick={exportarDados} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer',flexShrink:0}}>Exportar</button>
        </div>
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Baixar histórico</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Baixe seu histórico completo de registros</div></div>
          <button onClick={baixarHistoricoCfg} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer',flexShrink:0}}>Baixar</button>
        </div>
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Limpar dados locais</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Remove cache e dados deste dispositivo. Não afeta seus dados no servidor.</div></div>
          <button onClick={limparDadosLocaisCfg} style={{background:'rgba(248,113,113,.15)',border:'1px solid rgba(248,113,113,.3)',color:C.danger,borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer',flexShrink:0}}>Limpar</button>
        </div>
        <div style={{padding:'10px 0',display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600,color:'rgba(255,255,255,.4)'}}>Excluir meus dados</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Ainda não disponível — essa ação exige um fluxo de confirmação seguro que ainda não existe</div></div>
          <button disabled style={{background:'rgba(255,255,255,.04)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.3)',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'not-allowed',flexShrink:0}}>Em breve</button>
        </div>
      </Card>

      <Card title="Segurança">
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13}}>Conta</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Autenticada via Supabase</div></div>
          <button onClick={()=>supabase.auth.signOut()} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer'}}>Sair</button>
        </div>
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,fontSize:11.5,color:'rgba(255,255,255,.35)'}}>Lista de dispositivos/sessões ativas ainda não implementada nesta versão.</div>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 0'}}>
          <div><div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Autenticação de dois fatores</div></div>
          <span style={{fontSize:11,fontWeight:700,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>Em breve</span>
        </div>
      </Card>

      <Card title="Aparência">
        <div style={{marginBottom:14}}>
          <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:8}}>Tema</label>
          <div style={{display:'flex',gap:8}}>
            {[['escuro','🌙 Escuro',true],['claro','☀️ Claro',false],['sistema','🖥️ Sistema',false]].map(([v,lbl,disp])=>(
              <button key={v as string} onClick={()=>{if(disp){setTema(v as string);marcarAlterado()}}} disabled={!disp} title={disp?'':'Em breve'} style={{flex:1,background:tema===v?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,border:`1px solid ${tema===v?'transparent':C.line}`,color:disp?(tema===v?'#fff':'rgba(255,255,255,.6)'):'rgba(255,255,255,.25)',borderRadius:10,padding:'10px 8px',fontSize:12,cursor:disp?'pointer':'not-allowed'}}>{lbl as string}</button>
            ))}
          </div>
        </div>
        <div>
          <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:8}}>Densidade</label>
          <div style={{display:'flex',gap:8}}>
            {[['confortavel','Confortável'],['compacta','Compacta']].map(([v,lbl])=>(<button key={v} disabled title="Em breve" style={{flex:1,background:densidade===v?'rgba(139,92,246,.15)':C.s2,border:`1px solid ${densidade===v?'rgba(139,92,246,.3)':C.line}`,color:'rgba(255,255,255,.3)',borderRadius:10,padding:'10px 8px',fontSize:12,cursor:'not-allowed'}}>{lbl}</button>))}
          </div>
          <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginTop:8}}>Densidade ainda não implementada — arquitetura preparada para uma próxima etapa.</p>
        </div>
      </Card>
    </div>

    <div style={{marginTop:20,background:'rgba(139,92,246,.06)',border:'1px solid rgba(139,92,246,.15)',borderRadius:12,padding:'12px 16px',fontSize:11.5,color:'rgba(255,255,255,.4)'}}>ⓘ Suas configurações ficam salvas neste dispositivo e são a fonte oficial usada pela Home, Agenda, Relatórios e Luna quando aplicável.</div>
  </div>)
}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><QueryClientProvider client={qc}><AuthGate><PhotoProvider><FamProvider><BrowserRouter><Routes><Route element={<Shell/>}><Route index element={<Home/>}/><Route path="agenda" element={<Agenda/>}/><Route path="espiritual" element={<Espiritual/>}/><Route path="saude" element={<Saude/>}/><Route path="alimentacao" element={<Alimentacao/>}/><Route path="exercicios" element={<Exercicios/>}/><Route path="tirzepatida" element={<Navigate to="/saude" replace/>}/><Route path="familia" element={<Familia/>}/><Route path="trabalho" element={<Trabalho/>}/><Route path="desenvolvimento" element={<Desenvolvimento/>}/><Route path="casa" element={<Casa/>}/><Route path="insights" element={<Navigate to="/assistente" replace/>}/><Route path="relatorios" element={<Relatorios/>}/><Route path="assistente" element={<Assistente/>}/><Route path="config" element={<Config/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Route></Routes></BrowserRouter></FamProvider></PhotoProvider></AuthGate></QueryClientProvider></React.StrictMode>)
