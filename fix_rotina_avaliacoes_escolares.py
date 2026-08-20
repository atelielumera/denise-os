from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# Erro meu na resposta anterior: eu tinha dito que o "Calendario Avaliativo Escolar" nao
# existia no app, mas ele ja existe (pagina Familia, cadastrado como dos_avals). So nao
# tinha lido o arquivo ate essa parte. Agora os quadros Domi e Derick na Minha Rotina
# tambem mostram as avaliacoes/provas pendentes de cada um (mesmo dado da pagina Familia,
# marcar como feita aqui risca la tambem).

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_state = """  const [casaItens,setCasaItens]=React.useState<{n:string,cat:string,done:boolean,venc?:string}[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})
  const toggleCasa=(item:{n:string,cat:string,done:boolean,venc?:string})=>{const n=casaItens.map(x=>x===item?{...x,done:!x.done}:x);setCasaItens(n);localStorage.setItem('dos_casa_items',JSON.stringify(n))}
  const casaPendentes=casaItens.filter(c=>!c.done)"""
new_state = """  const [casaItens,setCasaItens]=React.useState<{n:string,cat:string,done:boolean,venc?:string}[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})
  const toggleCasa=(item:{n:string,cat:string,done:boolean,venc?:string})=>{const n=casaItens.map(x=>x===item?{...x,done:!x.done}:x);setCasaItens(n);localStorage.setItem('dos_casa_items',JSON.stringify(n))}
  const casaPendentes=casaItens.filter(c=>!c.done)
  const [avals,setAvals]=React.useState<Record<string,{data:string,tipo:string,obs:string,feito:boolean}[]>>(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})
  const toggleAval=(kid:string,item:{data:string,tipo:string,obs:string,feito:boolean})=>{const lista=(avals[kid]||[]).map(x=>x===item?{...x,feito:!x.feito}:x);const n={...avals,[kid]:lista};setAvals(n);localStorage.setItem('dos_avals',JSON.stringify(n))}"""
s = replace_once(s, old_state, new_state, "rotina-avals-estado")

old_badge = """          const itensKid=itemsHoje.filter(({item})=>item.cat==='Família'&&(item.n.includes(nome)||!(item.n.includes('Domi')||item.n.includes('Derick'))))
          return(<div key={kid} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>👧</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{nome}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({itensKid.length+1})</span>
            </div>"""
new_badge = """          const itensKid=itemsHoje.filter(({item})=>item.cat==='Família'&&(item.n.includes(nome)||!(item.n.includes('Domi')||item.n.includes('Derick'))))
          const avalsKid=(avals[kid]||[]).filter(a=>!a.feito).sort((a,b)=>a.data.localeCompare(b.data))
          return(<div key={kid} style={{gridColumn:'span 3',background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:6}}>
              <span style={{fontSize:16}}>👧</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{nome}</span>
              <span style={{fontSize:11,color:'rgba(255,255,255,.3)'}}>({itensKid.length+1+avalsKid.length})</span>
            </div>"""
s = replace_once(s, old_badge, new_badge, "rotina-avals-badge")

old_list = """                  <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
                </div>)
              })}
            </div>
          </div>)
        })}
        </div>
      </>)"""
new_list = """                  <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
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
      </>)"""
s = replace_once(s, old_list, new_list, "rotina-avals-lista")

main_file.write_text(s)
print("OK - Os quadros Domi e Derick na Minha Rotina agora mostram tambem as avaliacoes/provas")
print("pendentes de cada um (mesmo calendario avaliativo cadastrado na pagina Familia).")
print("Marcar como feita ali risca la na pagina Familia tambem - e o mesmo dado.")
