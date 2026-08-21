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

old1 = '''function Casa(){
  type CasaItem={n:string,cat:string,done:boolean,venc?:string}
  const [items,setItems]=React.useState<CasaItem[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'null')||[{n:'Iogurte proteico sem lactose',cat:'Mercado',done:false},{n:'Whey isolado',cat:'Mercado',done:false},{n:'Frango',cat:'Mercado',done:false},{n:'Limpar casa',cat:'Doméstico',done:false},{n:'Pagar energia',cat:'Contas',done:false}]}catch{return []}})
  const [nova,setNova]=React.useState('')
  const [cat,setCat]=React.useState('Mercado')
  const [novoVenc,setNovoVenc]=React.useState('')
  const [editando,setEditando]=React.useState<CasaItem|null>(null)
  const [editNome,setEditNome]=React.useState('')
  const [editVenc,setEditVenc]=React.useState('')
  const cats=['Mercado','Doméstico','Manutenção','Contas']
  function salvarItems(n:CasaItem[]){setItems(n);localStorage.setItem('dos_casa_items',JSON.stringify(n))}
  function addItem(){if(!nova)return;const item:CasaItem={n:nova,cat,done:false};if(cat==='Contas'&&novoVenc)item.venc=novoVenc;salvarItems([item,...items]);setNova('');setNovoVenc('')}
  function toggleItem(item:CasaItem){salvarItems(items.map(x=>x===item?{...x,done:!x.done}:x))}
  function delItem(item:CasaItem){salvarItems(items.filter(x=>x!==item))}
  function iniciarEdicao(item:CasaItem){setEditando(item);setEditNome(item.n);setEditVenc(item.venc||'')}
  function salvarEdicao(){
    if(!editando)return
    if(!editNome){setEditando(null);return}
    salvarItems(items.map(x=>x===editando?{...x,n:editNome,venc:editando.cat==='Contas'?(editVenc||undefined):x.venc}:x))
    setEditando(null)
  }
  function cancelarEdicao(){setEditando(null)}
  function fmtVenc(v:string){return new Date(v+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}
  function diasVenc(v:string){const hoje=new Date();hoje.setHours(0,0,0,0);const d=new Date(v+'T00:00:00');return Math.round((d.getTime()-hoje.getTime())/86400000)}
  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Casa</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Compras, tarefas, manutenção e contas</p>
    <div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const}}>
      <input value={nova} onChange={e=>setNova(e.target.value)} onKeyDown={e=>e.key==='Enter'&&addItem()} placeholder="Adicionar item…" style={{flex:1,minWidth:200,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14}}/>
      <select value={cat} onChange={e=>setCat(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14,colorScheme:'dark'}}>{cats.map(c=>(<option key={c}>{c}</option>))}</select>
      {cat==='Contas'&&<input type="date" value={novoVenc} onChange={e=>setNovoVenc(e.target.value)} title="Data de vencimento" style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 14px',color:'#fff',fontSize:14,colorScheme:'dark'}}/>}
      <button onClick={addItem} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Adicionar</button>
    </div>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>{cats.map(c=>(<div key={c}><Card title={c}>{items.filter(i=>i.cat===c).map((item,idx)=>{
      const dv=item.venc?diasVenc(item.venc):null
      const urgente=dv!==null&&dv<=3
      const passada=dv!==null&&dv<0
      const emEdicao=editando===item
      if(emEdicao){
        return(<div key={idx} style={{display:'flex',alignItems:'center',gap:8,padding:'9px 0',borderBottom:`1px solid ${C.line}`,flexWrap:'wrap' as const}}>
          <input value={editNome} onChange={e=>setEditNome(e.target.value)} onKeyDown={e=>e.key==='Enter'&&salvarEdicao()} autoFocus style={{flex:1,minWidth:120,background:C.bg,border:`1px solid ${C.line}`,borderRadius:8,padding:'6px 9px',color:'#fff',fontSize:13}}/>
          {item.cat==='Contas'&&<input type="date" value={editVenc} onChange={e=>setEditVenc(e.target.value)} style={{background:C.bg,border:`1px solid ${C.line}`,borderRadius:8,padding:'6px 9px',color:'#fff',fontSize:13,colorScheme:'dark'}}/>}
          <button onClick={salvarEdicao} style={{background:C.ok,border:'none',color:'#04231a',borderRadius:6,padding:'5px 10px',fontSize:11,fontWeight:700,cursor:'pointer',flexShrink:0}}>✓</button>
          <button onClick={cancelarEdicao} style={{background:'rgba(255,255,255,.08)',border:'none',color:'#fff',borderRadius:6,padding:'5px 10px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button>
        </div>)
      }
      return(<div key={idx} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`,opacity:item.done?0.5:1}}><span onClick={()=>toggleItem(item)} style={{width:22,height:22,borderRadius:6,border:`2px solid ${item.done?C.ok:'rgba(255,255,255,.2)'}`,background:item.done?'rgba(52,211,153,.2)':'transparent',display:'grid',placeItems:'center',color:C.ok,fontSize:12,flexShrink:0,cursor:'pointer'}}>{item.done&&'✓'}</span><span onClick={()=>toggleItem(item)} style={{flex:1,fontSize:13,textDecoration:item.done?'line-through':'none',color:item.done?'rgba(255,255,255,.4)':'#fff',cursor:'pointer'}}>{item.n}</span>{item.venc&&!item.done&&<span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:urgente?'rgba(248,113,113,.15)':'rgba(251,191,36,.12)',color:urgente?C.danger:C.warn,flexShrink:0,whiteSpace:'nowrap' as const}}>{passada?`venceu ${fmtVenc(item.venc)}`:dv===0?'vence hoje!':dv===1?'vence amanhã!':`${fmtVenc(item.venc)} · ${dv}d`}</span>}<button onClick={()=>iniciarEdicao(item)} style={{background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.6)',borderRadius:6,padding:'3px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✎</button><button onClick={()=>delItem(item)} style={{background:'rgba(248,113,113,.1)',border:'none',color:C.danger,borderRadius:6,padding:'3px 8px',fontSize:11,cursor:'pointer',flexShrink:0}}>✕</button></div>)
    })}{items.filter(i=>i.cat===c).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum item</div>}</Card></div>))}</div>
  </div>)}'''

new1 = r'''type PrioridadeCasa='baixa'|'media'|'alta'
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
  </div>)}'''
s = replace_once(s, old1, new1, "reescreve-casa")

p.write_text(s)
print("TUDO OK:", applied)
