from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# A Minha Rotina so mostrava os itens cadastrados dentro dela mesma (dos_rotina). Agora o
# quadro "Saude" tambem puxa a Tirzepatida (sua e do Flavio) quando hoje e dia de aplicar e
# ainda nao foi registrada, com um botao "Registrar" que leva pra pagina de Tirzepatida. E o
# quadro "Casa" tambem puxa os itens pendentes da pagina Casa (compras, contas, manutencao),
# e marcar como feito ali risca la na pagina Casa tambem (mesmo dado, mesmo lugar).

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_state = """  const cats=['Espiritual','Saúde','Alimentação','Família','Exercícios','Casa','Trabalho','Compromisso','Desenvolvimento']
  const save=(it:RItem[])=>{setItems(it);localStorage.setItem('dos_rotina',JSON.stringify(it))}"""
new_state = """  const cats=['Espiritual','Saúde','Alimentação','Família','Exercícios','Casa','Trabalho','Compromisso','Desenvolvimento']
  const [tzHoje,setTzHoje]=React.useState<{pessoa:string,dose:number}[]>([])
  React.useEffect(()=>{(async()=>{
    const hoje=isoBR(new Date())
    const [{data:sched},{data:apps}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_applications').select('person,applied_at').order('applied_at',{ascending:false})
    ])
    const aplicadosHoje=new Set((apps||[]).filter((a:any)=>isoBR(new Date(a.applied_at))===hoje).map((a:any)=>a.person))
    const lista=(sched||[]).filter((row:any)=>row.next_application_date===hoje&&!aplicadosHoje.has(row.person)).map((row:any)=>({pessoa:row.person==='denise'?'Você':'Flávio',dose:Number(row.planned_dose_mg)}))
    setTzHoje(lista)
  })()},[])
  const [casaItens,setCasaItens]=React.useState<{n:string,cat:string,done:boolean,venc?:string}[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})
  const toggleCasa=(item:{n:string,cat:string,done:boolean,venc?:string})=>{const n=casaItens.map(x=>x===item?{...x,done:!x.done}:x);setCasaItens(n);localStorage.setItem('dos_casa_items',JSON.stringify(n))}
  const casaPendentes=casaItens.filter(c=>!c.done)
  const save=(it:RItem[])=>{setItems(it);localStorage.setItem('dos_rotina',JSON.stringify(it))}"""
s = replace_once(s, old_state, new_state, "rotina-estado-tz-casa")

old_bloco = """          const bloco=itemsHoje.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
          if(bloco.length===0)return null
          return(<div key={tema} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>{icon}</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{tema}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({bloco.length})</span>
            </div>
            <div>
              {bloco.map(({item,i})=>{
                const feito=done.includes(i)
                return(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:feito?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:feito?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>{feito?'✓':'○'}</span>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,cursor:'pointer'}}>{item.t}</span>
                  <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{flex:1,fontSize:13.5,color:feito?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:feito?'line-through':'none',cursor:'pointer'}}>{item.n}</span>
                  <button onClick={()=>openEdit(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:13,flexShrink:0}}>✏️</button>
                  <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
                </div>)
              })}"""
new_bloco = """          const bloco=itemsHoje.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
          const extraTz=tema==='Saúde'?tzHoje:[]
          const extraCasa=tema==='Casa'?casaPendentes:[]
          if(bloco.length===0&&extraTz.length===0&&extraCasa.length===0)return null
          return(<div key={tema} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>{icon}</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{tema}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({bloco.length+extraTz.length+extraCasa.length})</span>
            </div>
            <div>
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
              {extraTz.map((t,ti)=>(<div key={'tz'+ti} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:'rgba(139,92,246,.15)',color:C.acc2,fontSize:11,flexShrink:0}}>💉</span>
                <span style={{flex:1,fontSize:13.5,color:'#f3f3f8'}}>Tirzepatida · {t.pessoa} ({t.dose} mg)</span>
                <NavLink to="/tirzepatida" style={{fontSize:11,color:C.acc2,textDecoration:'none',flexShrink:0}}>Registrar →</NavLink>
              </div>))}
              {extraCasa.map((c,ci)=>(<div key={'casa'+ci} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                <span onClick={()=>toggleCasa(c)} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:'rgba(255,255,255,.07)',color:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>○</span>
                <span style={{width:42,fontSize:9.5,color:'rgba(255,255,255,.35)',flexShrink:0}}>{c.cat}</span>
                <span onClick={()=>toggleCasa(c)} style={{flex:1,fontSize:13.5,color:'#f3f3f8',cursor:'pointer'}}>{c.n}</span>
              </div>))}"""
s = replace_once(s, old_bloco, new_bloco, "rotina-render-tz-casa")

main_file.write_text(s)
print("OK - Minha Rotina agora puxa:")
print(" - Tirzepatida (sua e do Flavio) no quadro Saude, so quando hoje e dia de aplicar e")
print("   ainda nao foi registrada, com botao Registrar.")
print(" - Itens pendentes da pagina Casa (compras, contas, manutencao) no quadro Casa -")
print("   marcar como feito ali ja risca na pagina Casa tambem.")
