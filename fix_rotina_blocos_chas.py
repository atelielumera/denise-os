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

# 1) Adicionar os 4 chas que estavam no prompt inicial mas nunca entraram na Rotina.
# So adiciona os que ainda nao existem (compara pelo nome), entao roda 1x e nunca duplica.
old_add = "  const addItem=()=>{if(!newItem.n||!newItem.t)return;save([...items,newItem]);setAdding(false);setNewItem({t:'',n:'',cat:'Saúde'})}\n"
new_add = """  const addItem=()=>{if(!newItem.n||!newItem.t)return;save([...items,newItem]);setAdding(false);setNewItem({t:'',n:'',cat:'Saúde'})}
  React.useEffect(()=>{
    const chas:RItem[]=[
      {t:'06:00',n:'Chá verde + gengibre + canela',cat:'Alimentação'},
      {t:'12:00',n:'Chá hortelã + erva-doce (digestivo)',cat:'Alimentação'},
      {t:'15:00',n:'Chá hibisco + cavalinha',cat:'Alimentação'},
      {t:'20:30',n:'Chá camomila + melissa',cat:'Alimentação'},
    ]
    setItems(prev=>{
      const nomes=new Set(prev.map(it=>it.n))
      const faltando=chas.filter(c=>!nomes.has(c.n))
      if(faltando.length===0)return prev
      const n=[...prev,...faltando]
      localStorage.setItem('dos_rotina',JSON.stringify(n))
      return n
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])
"""
s = replace_once(s, old_add, new_add, "rotina-seed-chas")

# 2) Trocar a lista unica e feia por blocos Manha / Tarde / Noite, mantendo tudo editavel
# (marcar feito, editar, excluir, adicionar continuam funcionando exatamente igual).
old_card = """    <Card title={`Hoje — ${done.length} / ${items.length} concluídos (${Math.round(done.length/items.length*100)}%)`}>
      <>{items.map((item,i)=>(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 9px',borderRadius:10,marginBottom:2,background:done.includes(i)?'rgba(52,211,153,.06)':'transparent',border:done.includes(i)?'1px solid rgba(52,211,153,.15)':'1px solid transparent'}}>
        <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:done.includes(i)?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:done.includes(i)?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>{done.includes(i)?'✓':'○'}</span>
        <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,cursor:'pointer'}}>{item.t}</span>
        <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{flex:1,fontSize:13.5,color:done.includes(i)?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:done.includes(i)?'line-through':'none',cursor:'pointer'}}>{item.n}</span>
        <span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:'rgba(139,92,246,.15)',color:C.acc2,flexShrink:0}}>{item.cat}</span>
        <button onClick={()=>openEdit(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:13,flexShrink:0}}>✏️</button>
        <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
      </div>))}</>
    </Card>
  </div>)}"""
new_card = """    <div style={{fontSize:13,color:'rgba(255,255,255,.5)',marginBottom:14}}>Hoje — {done.length} / {items.length} concluídos ({items.length>0?Math.round(done.length/items.length*100):0}%)</div>
    {([['Manhã','☀️','#38bdf8'],['Tarde','🌤️','#fb923c'],['Noite','🌙',C.acc2]] as [string,string,string][]).map(([label,icon,cor])=>{
      const pred=label==='Manhã'?(t:string)=>t<'12:00':label==='Tarde'?(t:string)=>t>='12:00'&&t<'18:00':(t:string)=>t>='18:00'
      const bloco=items.map((item,i)=>({item,i})).filter(({item})=>pred(item.t)).sort((a,b)=>a.item.t.localeCompare(b.item.t))
      if(bloco.length===0)return null
      return(<div key={label} style={{marginBottom:18}}>
        <div style={{display:'flex',alignItems:'center',gap:8,padding:'9px 16px',borderRadius:'14px 14px 0 0',background:`${cor}1f`,border:`1px solid ${cor}44`,borderBottom:'none'}}>
          <span style={{fontSize:16}}>{icon}</span>
          <span style={{fontWeight:800,fontSize:14,color:cor}}>{label}</span>
        </div>
        <div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:'0 0 14px 14px',padding:'2px 16px'}}>
          {bloco.map(({item,i})=>(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
            <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:done.includes(i)?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:done.includes(i)?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>{done.includes(i)?'✓':'○'}</span>
            <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,cursor:'pointer'}}>{item.t}</span>
            <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{flex:1,fontSize:13.5,color:done.includes(i)?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:done.includes(i)?'line-through':'none',cursor:'pointer'}}>{item.n}</span>
            <span style={{fontSize:11,padding:'2px 8px',borderRadius:20,background:'rgba(139,92,246,.15)',color:C.acc2,flexShrink:0}}>{item.cat}</span>
            <button onClick={()=>openEdit(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:13,flexShrink:0}}>✏️</button>
            <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
          </div>))}
        </div>
      </div>)
    })}
  </div>)}"""
s = replace_once(s, old_card, new_card, "rotina-ui-blocos")

main_file.write_text(s)
print("OK - 2 alteracoes aplicadas em src/main.tsx:")
print(" - Minha Rotina agora mostra os itens organizados em blocos Manhã / Tarde / Noite (com cor por bloco),")
print("   igual ao formato das suas imagens. Marcar feito, editar (lapis) e excluir (x) continuam iguais,")
print("   e o botao '+ Novo item' continua funcionando pra adicionar qualquer coisa nova.")
print(" - Os 4 chas do prompt inicial (verde+gengibre+canela as 6h, hortela+erva-doce as 12h,")
print("   hibisco+cavalinha as 15h, camomila+melissa as 20h30) sao adicionados automaticamente")
print("   na sua rotina na primeira vez que voce abrir a tela depois do deploy - sem duplicar")
print("   se voce ja tiver algo com o mesmo nome.")
