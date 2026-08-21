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

# 1) FamData ganha entrada (horario de entrada na escola) e responsavel padrao (quem
#    normalmente busca) - sem quebrar o que ja existe (dropOff/pk continuam iguais).
#    Acrescenta o sistema de excecoes por data (responsavel diferente so naquele dia,
#    ou sem aula naquele dia) sem alterar a rotina recorrente.
old1 = "type FamData={dropOff:string,pk:{[k:number]:string}}\nconst defaultFam:Record<string,FamData>={domi:{dropOff:'07:00',pk:{1:'12:50',2:'11:40',3:'12:50',4:'11:40',5:'13:00'}},derick:{dropOff:'07:00',pk:{1:'17:00',2:'17:00',3:'17:00',4:'17:00',5:'17:00'}}}"
new1 = '''type FamData={dropOff:string,pk:{[k:number]:string},entrada?:string,responsavel?:string}
const defaultFam:Record<string,FamData>={domi:{dropOff:'07:00',pk:{1:'12:50',2:'11:40',3:'12:50',4:'11:40',5:'13:00'},entrada:'07:00',responsavel:'denise'},derick:{dropOff:'07:00',pk:{1:'17:00',2:'17:00',3:'17:00',4:'17:00',5:'17:00'},entrada:'07:00',responsavel:'flavio'}}
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
const NOME_RESPONSAVEL:Record<string,string>={denise:'Denise',flavio:'Flávio'}
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
}'''
s = replace_once(s, old1, new1, "familia-tipos-e-excecoes")

# 2) Home: card "Familia" (dentro do bloco 'Ações rápidas'/quadros) passa a usar a busca
#    efetiva (considerando excecao de hoje) e mostra a proxima avaliacao pendente de cada
#    crianca - mesma fonte de dados do modulo Familia, sem duplicar logica.
old2 = "          {(['domi','derick'] as const).map(k=>{const nome=k==='domi'?'Domi':'Derick';const pk=fam[k]?.pk?.[sd]||'—';return(<div key={k} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`}}><Avatar id={k} label={nome[0]} size={30} radius={9}/><div style={{flex:1}}><div style={{fontWeight:700,fontSize:13}}>{nome}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>Buscar · {pk}</div></div></div>)})}"
new2 = '''          {(['domi','derick'] as const).map(k=>{
            const nome=k==='domi'?'Domi':'Derick'
            const efet=buscaEfetivaFam(fam,k,isoBR(new Date()),sd)
            const avalsK=(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})() as Record<string,any[]>
            const proxAval=proximaAvalPendente(avalsK[k]||[])
            return(<div key={k} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`}}><Avatar id={k} label={nome[0]} size={30} radius={9}/><div style={{flex:1}}><div style={{fontWeight:700,fontSize:13}}>{nome}</div><div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{efet.semAula?'Sem aula hoje':`Buscar · ${efet.horario} · ${NOME_RESPONSAVEL[efet.responsavel]||efet.responsavel}`}</div>{proxAval&&<div style={{fontSize:10.5,color:C.warn,marginTop:2}}>{proxAval.aval.materia} · {proxAval.dias===0?'hoje':proxAval.dias===1?'amanhã':`em ${proxAval.dias} dias`}</div>}</div></div>)
          })}'''
s = replace_once(s, old2, new2, "home-familia-busca-efetiva")

# 3) Reescreve o modulo Familia: rotina escolar com entrada/sair de casa/buscar/responsavel
#    (config real, nada hardcoded), excecao pontual por data sem alterar a recorrencia,
#    calendario avaliativo com filtros/status/preview de importacao de PDF antes de salvar.
old3 = '''function Familia(){
  const {fam,setFam}=React.useContext(FamCtx)
  const [showEdit,setShowEdit]=React.useState(false)
  const [editKey,setEditKey]=React.useState<'domi'|'derick'|null>(null)
  const [local,setLocal]=React.useState(JSON.parse(JSON.stringify(fam)))
  const days:[number,string][]=[[1,'Seg'],[2,'Ter'],[3,'Qua'],[4,'Qui'],[5,'Sex']]
  const membros=[{id:'denise',nome:'Denise',papel:'Você · mãe',cor:'#8b5cf6'},{id:'flavio',nome:'Flávio',papel:'Pai',cor:'#38bdf8'},{id:'domi',nome:'Domi',papel:'Filha · escola',cor:'#f472b6'},{id:'derick',nome:'Derick',papel:'Filho · escola',cor:'#34d399'}]
  const [eventosFam]=React.useState<any[]>(()=>lerEventosAgenda())
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
      const resp=await fetch('/api/parse-calendar',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({pdfBase64:base64})
      })
      const data=await resp.json()
      if(!resp.ok) throw new Error(data?.error||'Falha ao processar o PDF.')
      const extracted:Aval[]=data.avaliacoes
      saveAvals(kid,[...(avals[kid]||[]),...extracted].sort((a,b)=>a.data.localeCompare(b.data)))
      setMsg(`✓ ${extracted.length} avaliações importadas!`)
    }catch(e:any){setMsg(`❌ ${e?.message||'Erro ao ler PDF. Tente novamente.'}`)}
    setLoading(false);setTimeout(()=>setMsg(''),6000)
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
    <Card title="📅 Próximos compromissos da família">
      {compromissosFamilia.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum compromisso de família nos próximos dias.</div>}
      {compromissosFamilia.map((e:any,i:number)=>(<div key={i} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:i<compromissosFamilia.length-1?`1px solid ${C.line}`:'none',alignItems:'center'}}>
        <span style={{width:80,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.data}{e.hora?` · ${e.hora}`:''}</span>
        <span style={{width:4,height:20,borderRadius:2,background:e.cor,flexShrink:0}}/>
        <span style={{fontSize:13.5,flex:1}}>{e.nome}</span>
        {e.pessoa&&<span style={{fontSize:11,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.pessoa==='domi'?'Domi':'Derick'}</span>}
      </div>))}
    </Card>
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
  </div>)}'''

new3 = r'''function Familia(){
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
  const [eventosFam]=React.useState<any[]>(()=>lerEventosAgenda())
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
    <Card title="📅 Próximos compromissos da família">
      {compromissosFamilia.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum compromisso de família nos próximos dias.</div>}
      {compromissosFamilia.map((e:any,i:number)=>(<div key={i} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:i<compromissosFamilia.length-1?`1px solid ${C.line}`:'none',alignItems:'center'}}>
        <span style={{width:80,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.data}{e.hora?` · ${e.hora}`:''}</span>
        <span style={{width:4,height:20,borderRadius:2,background:e.cor,flexShrink:0}}/>
        <span style={{fontSize:13.5,flex:1}}>{e.nome}</span>
        {e.pessoa&&<span style={{fontSize:11,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.pessoa==='domi'?'Domi':'Derick'}</span>}
      </div>))}
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
  </div>)}'''
s = replace_once(s, old3, new3, "reescreve-familia")

p.write_text(s)
print("TUDO OK:", applied)
