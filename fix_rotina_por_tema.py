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

# ---------------------------------------------------------------------------
# 1) RItem passa a aceitar um campo opcional "dias" (dias da semana em que o
#    item aparece - 0=Domingo...6=Sabado). Sem esse campo, o item aparece
#    todo santo dia, igual sempre foi.
# ---------------------------------------------------------------------------
old_type = "  type RItem={t:string,n:string,cat:string}"
new_type = "  type RItem={t:string,n:string,cat:string,dias?:number[]}"
s = replace_once(s, old_type, new_type, "ritem-type-dias")

# ---------------------------------------------------------------------------
# 2) Limpa os itens antigos (o "Buscar Domi" original de horario fixo, e as
#    duas versoes com texto combinado de todos os dias que a Denise nao
#    quis) e substitui por itens que so aparecem no(s) dia(s) certo(s), cada
#    um com o produto/horario certo daquele dia - sem lista combinada.
# ---------------------------------------------------------------------------
old_seed = """  React.useEffect(()=>{
    const chas:RItem[]=[
      {t:'06:00',n:'Chá verde + gengibre + canela',cat:'Alimentação'},
      {t:'12:00',n:'Chá hortelã + erva-doce (digestivo)',cat:'Alimentação'},
      {t:'15:00',n:'Chá hibisco + cavalinha',cat:'Alimentação'},
      {t:'20:30',n:'Chá camomila + melissa',cat:'Alimentação'},
      {t:'11:25',n:'Buscar Domi (sair 15 min antes) — Seg/Qua 12:50 · Ter/Qui 11:40 · Sex 13:00',cat:'Família'},
      {t:'08:00',n:'Skincare manhã: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Filtro Solar La Roche-Posay, Cicaplast',cat:'Saúde'},
      {t:'21:00',n:'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Cicaplast + extra do dia — Seg/Qua/Sex: Vitacid · Ter/Qui/Sáb: Effaclar Duo+M · Domingo: sem extra',cat:'Saúde'},
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
  },[])"""
new_seed = """  React.useEffect(()=>{
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
  },[])"""
s = replace_once(s, old_seed, new_seed, "rotina-seed-dias-corretos")

# ---------------------------------------------------------------------------
# 3) Minha Rotina passa a mostrar os itens agrupados por TEMA (categoria),
#    nao mais por Manha/Tarde/Noite. Cada bloco de tema junta os itens
#    daquela categoria que valem hoje (respeitando o campo "dias"), em
#    ordem de horario. Marcar feito, editar e excluir continuam iguais.
# ---------------------------------------------------------------------------
old_render = """    <div style={{fontSize:13,color:'rgba(255,255,255,.5)',marginBottom:14}}>Hoje — {done.length} / {items.length} concluídos ({items.length>0?Math.round(done.length/items.length*100):0}%)</div>
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
    })}"""
new_render = """    {(()=>{
      const hojeDia=new Date(isoBR(new Date())+'T12:00:00-03:00').getDay()
      const itemsHoje=items.map((item,i)=>({item,i})).filter(({item})=>!item.dias||item.dias.includes(hojeDia))
      const doneHoje=itemsHoje.filter(({i})=>done.includes(i))
      const CORES_CAT:Record<string,string>={'Espiritual':C.acc2,'Saúde':C.ok,'Alimentação':C.warn,'Família':C.pink,'Exercícios':C.water,'Casa':C.teal,'Trabalho':C.danger,'Compromisso':C.acc,'Desenvolvimento':'#fb923c'}
      const ICONES_CAT:Record<string,string>={'Espiritual':'🙏','Saúde':'❤️','Alimentação':'🍽️','Família':'👨‍👩‍👧','Exercícios':'💪','Casa':'🏠','Trabalho':'💼','Compromisso':'📅','Desenvolvimento':'📚'}
      return(<>
        <div style={{fontSize:13,color:'rgba(255,255,255,.5)',marginBottom:14}}>Hoje — {doneHoje.length} / {itemsHoje.length} concluídos ({itemsHoje.length>0?Math.round(doneHoje.length/itemsHoje.length*100):0}%)</div>
        {cats.map(tema=>{
          const cor=CORES_CAT[tema]||C.acc2
          const icon=ICONES_CAT[tema]||'📌'
          const bloco=itemsHoje.filter(({item})=>item.cat===tema).sort((a,b)=>a.item.t.localeCompare(b.item.t))
          if(bloco.length===0)return null
          return(<div key={tema} style={{marginBottom:18}}>
            <div style={{display:'flex',alignItems:'center',gap:8,padding:'9px 16px',borderRadius:'14px 14px 0 0',background:`${cor}1f`,border:`1px solid ${cor}44`,borderBottom:'none'}}>
              <span style={{fontSize:16}}>{icon}</span>
              <span style={{fontWeight:800,fontSize:14,color:cor}}>{tema}</span>
            </div>
            <div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:'0 0 14px 14px',padding:'2px 16px'}}>
              {bloco.map(({item,i})=>(<div key={i} style={{display:'flex',alignItems:'center',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
                <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:24,height:24,borderRadius:'50%',display:'grid',placeItems:'center',background:done.includes(i)?'rgba(52,211,153,.2)':'rgba(255,255,255,.07)',color:done.includes(i)?C.ok:'rgba(255,255,255,.4)',fontSize:11,flexShrink:0,cursor:'pointer'}}>{done.includes(i)?'✓':'○'}</span>
                <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{width:42,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0,cursor:'pointer'}}>{item.t}</span>
                <span onClick={()=>setDone(d=>d.includes(i)?d.filter(x=>x!==i):[...d,i])} style={{flex:1,fontSize:13.5,color:done.includes(i)?'rgba(255,255,255,.5)':'#f3f3f8',textDecoration:done.includes(i)?'line-through':'none',cursor:'pointer'}}>{item.n}</span>
                <button onClick={()=>openEdit(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(255,255,255,.06)',border:'none',color:'rgba(255,255,255,.5)',cursor:'pointer',fontSize:13,flexShrink:0}}>✏️</button>
                <button onClick={()=>del(i)} style={{width:28,height:28,borderRadius:8,background:'rgba(248,113,113,.1)',border:'none',color:'#f87171',cursor:'pointer',fontSize:13,flexShrink:0}}>✕</button>
              </div>))}
            </div>
          </div>)
        })}
      </>)
    })()}"""
s = replace_once(s, old_render, new_render, "rotina-blocos-por-tema")

main_file.write_text(s)
print("OK - 3 alteracoes aplicadas em src/main.tsx:")
print(" - Minha Rotina agora agrupa os itens por TEMA (Espiritual, Saúde, Alimentação, Família,")
print("   Exercícios, Casa, Trabalho, Compromisso, Desenvolvimento) em vez de Manhã/Tarde/Noite.")
print(" - Itens podem valer só em certos dias da semana (campo novo, opcional). Sem isso o item")
print("   continua aparecendo todo dia, igual sempre foi.")
print(" - Buscar a Domi e o Skincare da noite: removidos os itens antigos com texto combinado de")
print("   todos os dias, substituídos por versões que só aparecem no dia certo, já com o horário")
print("   ou produto certo daquele dia (sem lista de 'Seg/Qua/Sex: X · Ter/Qui/Sáb: Y' toda vez).")
