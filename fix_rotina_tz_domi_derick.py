from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# 1) Tirzepatida vira um quadro proprio, sempre visivel (mostra sua dose e a do Flavio com
#    a data, mesmo quando hoje nao e dia de aplicar) - antes so aparecia dentro do quadro
#    Saude e so no dia exato.
# 2) Família vira dois quadros separados: "Domi" e "Derick", cada um com o horario de busca
#    (mesma fonte que a Home usa) e os itens da rotina que mencionam o nome de cada um. Itens
#    genericos (tipo "Levar criancas a escola", que nao citam nome) aparecem nos dois.

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_1 = """  const [tzHoje,setTzHoje]=React.useState<{pessoa:string,dose:number}[]>([])
  React.useEffect(()=>{(async()=>{
    const hoje=isoBR(new Date())
    const [{data:sched},{data:apps}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_applications').select('person,applied_at').order('applied_at',{ascending:false})
    ])
    const aplicadosHoje=new Set((apps||[]).filter((a:any)=>isoBR(new Date(a.applied_at))===hoje).map((a:any)=>a.person))
    const lista=(sched||[]).filter((row:any)=>row.next_application_date===hoje&&!aplicadosHoje.has(row.person)).map((row:any)=>({pessoa:row.person==='denise'?'Você':'Flávio',dose:Number(row.planned_dose_mg)}))
    setTzHoje(lista)
  })()},[])"""
new_1 = """  const {fam}=React.useContext(FamCtx)
  const [tzSchedAll,setTzSchedAll]=React.useState<Record<string,{dose:number,next:string|null}>>({})
  React.useEffect(()=>{(async()=>{
    const {data:sched}=await supabase.from('tirzepatida_schedule').select('*')
    const map:Record<string,{dose:number,next:string|null}>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={dose:Number(row.planned_dose_mg),next:row.next_application_date}})
    setTzSchedAll(map)
  })()},[])"""
s = replace_once(s, old_1, new_1, "rotina-tz-estado")

old_2 = """        {cats.map(tema=>{
          const cor=CORES_CAT[tema]||C.acc2
          const icon=ICONES_CAT[tema]||'📌'
          const bloco=itemsHoje.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
          const extraTz=tema==='Saúde'?tzHoje:[]
          const extraCasa=tema==='Casa'?casaPendentes:[]
          if(bloco.length===0&&extraTz.length===0&&extraCasa.length===0)return null
          return(<div key={tema} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>{icon}</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{tema}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({bloco.length+extraTz.length+extraCasa.length})</span>
            </div>"""
new_2 = """        {cats.filter(tema=>tema!=='Família').map(tema=>{
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
            </div>"""
s = replace_once(s, old_2, new_2, "rotina-loop-sem-familia")

old_3 = """              {extraTz.map((t,ti)=>(<div key={'tz'+ti} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:'rgba(139,92,246,.15)',color:C.acc2,fontSize:11,flexShrink:0}}>💉</span>
                <span style={{flex:1,fontSize:13.5,color:'#f3f3f8'}}>Tirzepatida · {t.pessoa} ({t.dose} mg)</span>
                <NavLink to="/tirzepatida" style={{fontSize:11,color:C.acc2,textDecoration:'none',flexShrink:0}}>Registrar →</NavLink>
              </div>))}
              {extraCasa.map((c,ci)=>(<div key={'casa'+ci} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>"""
new_3 = """              {extraCasa.map((c,ci)=>(<div key={'casa'+ci} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>"""
s = replace_once(s, old_3, new_3, "rotina-tira-extratz")

old_4 = """            </div>
          </div>)
        })}
        </div>
      </>)
    })()}
  </div>)}
function Agenda(){"""
new_4 = """            </div>
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
            <div>
              {pessoas.map(p=>{
                const info=tzSchedAll[p]
                const dueToday=info.next===hojeIsoTz
                const overdue=!!info.next&&info.next<hojeIsoTz
                return(<div key={p} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                  <span style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:dueToday||overdue?'rgba(139,92,246,.2)':'rgba(255,255,255,.07)',color:dueToday||overdue?C.acc2:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0}}>💉</span>
                  <span style={{flex:1,fontSize:13.5,color:'#f3f3f8'}}>{p==='denise'?'Você':'Flávio'} · {info.dose} mg · {info.next?new Date(info.next+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}):'—'}{dueToday?' (hoje)':overdue?' (atrasada)':''}</span>
                  <NavLink to="/tirzepatida" style={{fontSize:11,color:C.acc2,textDecoration:'none',flexShrink:0}}>Registrar →</NavLink>
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
          return(<div key={kid} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>👧</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{nome}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({itensKid.length+1})</span>
            </div>
            <div>
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
            </div>
          </div>)
        })}
        </div>
      </>)
    })()}
  </div>)}
function Agenda(){"""
s = replace_once(s, old_4, new_4, "rotina-adiciona-tz-domi-derick")

main_file.write_text(s)
print("OK:")
print(" - Tirzepatida agora e um quadro proprio, sempre visivel, mostrando sua dose e a do")
print("   Flavio com a data (marca 'hoje' ou 'atrasada' quando for o caso).")
print(" - Familia virou dois quadros: Domi e Derick, cada um com o horario de busca certo do")
print("   dia (mesmo dado que a Home usa) e os itens da rotina que citam o nome de cada um.")
