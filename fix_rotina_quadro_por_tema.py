from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_bloco = """          return(<div key={tema} style={{marginBottom:22}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
              <span style={{fontSize:16}}>{icon}</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{tema}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({bloco.length})</span>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(230px,1fr))',gap:10}}>
              {bloco.map(({item,i})=>{
                const feito=done.includes(i)
                return(<div key={i} style={{background:feito?'rgba(52,211,153,.06)':C.s2,border:`1px solid ${feito?'rgba(52,211,153,.25)':C.line}`,borderRadius:14,padding:14}}>
                  <div style={{display:'flex',justifyContent:'space-between' as const,alignItems:'flex-start',marginBottom:10}}>
                    <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:26,height:26,borderRadius:'50%',display:'grid',placeItems:'center',background:feito?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:feito?C.ok:'rgba(255,255,255,.4)',fontSize:12,flexShrink:0,cursor:'pointer'}}>{feito?'✓':'○'}</span>
                    <div style={{display:'flex',gap:4}}>
                      <button onClick={()=>openEdit(i)} style={{width:24,height:24,borderRadius:7,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:11}}>✏️</button>
                      <button onClick={()=>del(i)} style={{width:24,height:24,borderRadius:7,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:11}}>✕</button>
                    </div>
                  </div>
                  <div onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{fontSize:13.5,fontWeight:600,lineHeight:1.4,color:feito?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:feito?'line-through':'none',cursor:'pointer',marginBottom:8}}>{item.n}</div>
                  <div style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>🕐 {item.t}</div>
                </div>)
              })}
            </div>
          </div>)"""
new_bloco = """          return(<div key={tema} style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,marginBottom:16}}>
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
              })}
            </div>
          </div>)"""
s = replace_once(s, old_bloco, new_bloco, "rotina-quadro-por-tema")

main_file.write_text(s)
print("OK - Minha Rotina agora tem UM quadro por tema (igual aos cards da Home: Alimentação,")
print("Saúde, etc.), e dentro de cada quadro os itens ficam em lista, um embaixo do outro,")
print("com check, horário, nome, editar e excluir. Nao tem mais um quadro pra cada item.")
