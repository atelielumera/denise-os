from pathlib import Path

p = Path("src/main.tsx")
s = p.read_text()
applied = []

def try_replace(s, old, new, label):
    c = s.count(old)
    if c == 1:
        applied.append(label)
        return s.replace(old, new, 1)
    return s

# Este script funciona nos dois cenarios possiveis (caso o script de lista tenha
# sido aplicado ou nao) e sempre termina com Sugestoes em grade de quadros.

# Cenario A: se a versao de LISTA (LinhaSugestaoLuna) estiver presente, volta pra quadro.
old_a1 = """  function LinhaSugestaoLuna({ins}:{ins:LunaInsight}){
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:12,padding:'14px 16px',display:'flex',alignItems:'center',gap:12}}>
      <span style={{color:'rgba(255,255,255,.3)',fontSize:14,flexShrink:0}}>›</span>
      <span style={{flex:1,fontSize:13,color:'rgba(255,255,255,.75)',lineHeight:1.4}}>{ins.conclusao||ins.titulo}</span>
      <div style={{display:'flex',gap:8,flexShrink:0}}>
        <button onClick={()=>ins.acaoPerguntar?perguntarLuna(ins.acaoPerguntar):ignorarInsightLuna(ins.id)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:8,padding:'7px 14px',fontSize:12,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>{ins.acaoPrimariaLabel||'Ver'}</button>
        <button onClick={()=>ignorarInsightLuna(ins.id)} style={{background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)',borderRadius:8,padding:'7px 12px',fontSize:12,cursor:'pointer'}}>Depois</button>
      </div>
    </div>)
  }"""
new_a1 = """  function CardSugestaoLuna({ins}:{ins:LunaInsight}){
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',flexDirection:'column' as const,gap:10}}>
      <div style={{width:34,height:34,borderRadius:10,background:hexParaRgbaTrab(C.warn,.14),display:'grid',placeItems:'center',fontSize:16}}>{ICONE_TIPO_LUNA['sugestao']}</div>
      <div style={{fontSize:12.5,color:'rgba(255,255,255,.75)',lineHeight:1.45}}>{ins.conclusao||ins.titulo}</div>
      <div style={{display:'flex',gap:8,marginTop:'auto'}}>
        <button onClick={()=>ins.acaoPerguntar?perguntarLuna(ins.acaoPerguntar):ignorarInsightLuna(ins.id)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:8,padding:'7px 14px',fontSize:12,fontWeight:700,cursor:'pointer',flex:1}}>{ins.acaoPrimariaLabel||'Ver'}</button>
        <button onClick={()=>ignorarInsightLuna(ins.id)} style={{background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)',borderRadius:8,padding:'7px 12px',fontSize:12,cursor:'pointer'}}>Depois</button>
      </div>
    </div>)
  }"""
s = try_replace(s, old_a1, new_a1, "reverte-linha-para-card")

old_a2 = """    const layout=tipo==='sugestao'?'lista':'grade'
    return(<div style={{marginBottom:26}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
        <span style={{fontSize:15}}>{ICONE_TIPO_LUNA[tipo]}</span><span style={{fontWeight:800,fontSize:15}}>{titulo}</span><span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>({itens.length})</span>
      </div>
      {itens.length===0?<div style={{fontSize:12.5,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.03)',border:`1px dashed ${C.line}`,borderRadius:12,padding:'14px 16px'}}>{MENSAGEM_VAZIO_LUNA[tipo]}</div>:<>
      <div style={layout==='lista'?{display:'flex',flexDirection:'column' as const,gap:10}:{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:12}}>
        {visiveis.map(ins=>tipo==='atencao'?<CardAtencaoLuna key={ins.id} ins={ins}/>:tipo==='padrao'?<CardPadraoLuna key={ins.id} ins={ins}/>:tipo==='progresso'?<TileProgressoLuna key={ins.id} ins={ins}/>:<LinhaSugestaoLuna key={ins.id} ins={ins}/>)}
      </div>"""
new_a2 = """    return(<div style={{marginBottom:26}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
        <span style={{fontSize:15}}>{ICONE_TIPO_LUNA[tipo]}</span><span style={{fontWeight:800,fontSize:15}}>{titulo}</span><span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>({itens.length})</span>
      </div>
      {itens.length===0?<div style={{fontSize:12.5,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.03)',border:`1px dashed ${C.line}`,borderRadius:12,padding:'14px 16px'}}>{MENSAGEM_VAZIO_LUNA[tipo]}</div>:<>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:12}}>
        {visiveis.map(ins=>tipo==='atencao'?<CardAtencaoLuna key={ins.id} ins={ins}/>:tipo==='padrao'?<CardPadraoLuna key={ins.id} ins={ins}/>:tipo==='progresso'?<TileProgressoLuna key={ins.id} ins={ins}/>:<CardSugestaoLuna key={ins.id} ins={ins}/>)}
      </div>"""
s = try_replace(s, old_a2, new_a2, "forca-layout-grade")

p.write_text(s)
if applied:
    print("TUDO OK (revertido para grade):", applied)
else:
    print("TUDO OK: ja estava em grade, nada a fazer.")
