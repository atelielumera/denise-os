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

old_wrap_open = """      return(<>
        <div style={{fontSize:13,color:'rgba(255,255,255,.5)',marginBottom:14}}>Hoje — {doneHoje.length} / {itemsHoje.length} concluídos ({itemsHoje.length>0?Math.round(doneHoje.length/itemsHoje.length*100):0}%)</div>
        {cats.map(tema=>{
          const cor=CORES_CAT[tema]||C.acc2
          const icon=ICONES_CAT[tema]||'📌'
          const bloco=itemsHoje.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
          if(bloco.length===0)return null
          return(<div key={tema} style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,marginBottom:16}}>"""
new_wrap_open = """      return(<>
        <div style={{fontSize:13,color:'rgba(255,255,255,.5)',marginBottom:14}}>Hoje — {doneHoje.length} / {itemsHoje.length} concluídos ({itemsHoje.length>0?Math.round(doneHoje.length/itemsHoje.length*100):0}%)</div>
        <div style={{display:'grid',gridTemplateColumns:'repeat(12,1fr)',gap:14}}>
        {cats.map(tema=>{
          const cor=CORES_CAT[tema]||C.acc2
          const icon=ICONES_CAT[tema]||'📌'
          const bloco=itemsHoje.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
          if(bloco.length===0)return null
          return(<div key={tema} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>"""
s = replace_once(s, old_wrap_open, new_wrap_open, "rotina-grid-abre")

old_wrap_close = """          </div>)
        })}
      </>)
    })()}"""
new_wrap_close = """          </div>)
        })}
        </div>
      </>)
    })()}"""
s = replace_once(s, old_wrap_close, new_wrap_close, "rotina-grid-fecha")

main_file.write_text(s)
print("OK - Minha Rotina agora fica em grade de 4 colunas, cada tema um quadro dentro da")
print("grade (igual ao layout de cards da Home: Alimentação, Saúde, Exercícios lado a lado),")
print("com a lista de itens dentro de cada quadro.")
