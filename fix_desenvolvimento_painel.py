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

old1 = '''function Desenvolvimento(){
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
    const reg={data:isoBR(new Date()),pag:Number(pag)||0,min:Number(min)||0,apren}
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
  const hojeIso=isoBR(new Date())
  if(!diasComLeitura.has(hojeIso))dcursor.setDate(dcursor.getDate()-1)
  while(diasComLeitura.has(isoBR(dcursor))){sequenciaLeitura++;dcursor.setDate(dcursor.getDate()-1)}
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
</Card></div></div>)}'''

new1 = r'''type StatusLivroDev='quero_ler'|'na_fila'|'lendo'|'pausado'|'concluido'|'abandonado'
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
  </div>)}'''
s = replace_once(s, old1, new1, "reescreve-desenvolvimento")

p.write_text(s)
print("TUDO OK:", applied)
