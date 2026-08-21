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

# 1) Remove o aviso generico (fica redundante agora que cada secao explica a propria ausencia)
old1 = "      {insightsVisiveisLuna.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)',padding:'20px 0'}}>Ainda não há insights relevantes com esses filtros. Continue registrando seus dados pelo app.</div>}\n"
new1 = ""
s = replace_once(s, old1, new1, "remove-aviso-generico")

# 2) Cada secao (Atencao/Padroes/Progresso/Sugestoes) explica por que esta vazia, em vez de
#    sumir sem dizer nada quando ainda nao ha dado real suficiente pra gerar aquele insight.
old2 = """  function SecaoInsightsLuna({titulo,tipo,itens}:{titulo:string,tipo:LunaInsight['tipo'],itens:LunaInsight[]}){
    if(itens.length===0)return null
    const aberta=!!verTodosLuna[tipo]
    const visiveis=aberta?itens:itens.slice(0,3)
    const layout=tipo==='sugestao'?'lista':'grade'
    return(<div style={{marginBottom:26}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
        <span style={{fontSize:15}}>{ICONE_TIPO_LUNA[tipo]}</span><span style={{fontWeight:800,fontSize:15}}>{titulo}</span><span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>({itens.length})</span>
      </div>
      <div style={layout==='lista'?{display:'flex',flexDirection:'column' as const,gap:10}:{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:12}}>
        {visiveis.map(ins=>tipo==='atencao'?<CardAtencaoLuna key={ins.id} ins={ins}/>:tipo==='padrao'?<CardPadraoLuna key={ins.id} ins={ins}/>:tipo==='progresso'?<TileProgressoLuna key={ins.id} ins={ins}/>:<LinhaSugestaoLuna key={ins.id} ins={ins}/>)}
      </div>
      {itens.length>3&&<button onClick={()=>setVerTodosLuna(v=>({...v,[tipo]:!v[tipo]}))} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',marginTop:10,padding:0}}>{aberta?'Ver menos':`Ver todos (${itens.length})`}</button>}
    </div>)
  }"""
new2 = """  const MENSAGEM_VAZIO_LUNA:Record<LunaInsight['tipo'],string>={
    atencao:'Nada pedindo atenção agora — sem contas, tarefas ou avaliações pendentes registradas em Casa, Trabalho e Família (ou ainda não há nada cadastrado nesses módulos).',
    padrao:'Ainda não há histórico suficiente pra identificar um padrão real — é preciso um mínimo de registros de água, treino ou proteína ao longo do tempo.',
    progresso:'Ainda não há duas janelas de período pra comparar — é preciso ter registrado proteína, treino, leitura ou devocional em pelo menos dois períodos.',
    sugestao:'Nenhuma sugestão da Luna no momento.',
  }
  function SecaoInsightsLuna({titulo,tipo,itens}:{titulo:string,tipo:LunaInsight['tipo'],itens:LunaInsight[]}){
    const aberta=!!verTodosLuna[tipo]
    const visiveis=aberta?itens:itens.slice(0,3)
    const layout=tipo==='sugestao'?'lista':'grade'
    return(<div style={{marginBottom:26}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
        <span style={{fontSize:15}}>{ICONE_TIPO_LUNA[tipo]}</span><span style={{fontWeight:800,fontSize:15}}>{titulo}</span><span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>({itens.length})</span>
      </div>
      {itens.length===0?<div style={{fontSize:12.5,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.03)',border:`1px dashed ${C.line}`,borderRadius:12,padding:'14px 16px'}}>{MENSAGEM_VAZIO_LUNA[tipo]}</div>:<>
      <div style={layout==='lista'?{display:'flex',flexDirection:'column' as const,gap:10}:{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))',gap:12}}>
        {visiveis.map(ins=>tipo==='atencao'?<CardAtencaoLuna key={ins.id} ins={ins}/>:tipo==='padrao'?<CardPadraoLuna key={ins.id} ins={ins}/>:tipo==='progresso'?<TileProgressoLuna key={ins.id} ins={ins}/>:<LinhaSugestaoLuna key={ins.id} ins={ins}/>)}
      </div>
      {itens.length>3&&<button onClick={()=>setVerTodosLuna(v=>({...v,[tipo]:!v[tipo]}))} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',marginTop:10,padding:0}}>{aberta?'Ver menos':`Ver todos (${itens.length})`}</button>}
      </>}
    </div>)
  }"""
s = replace_once(s, old2, new2, "estados-vazios-por-secao")

p.write_text(s)
print("TUDO OK:", applied)
