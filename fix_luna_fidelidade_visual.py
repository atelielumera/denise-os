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

# 1) LunaMsg ganha horario opcional (usado nos balões e na lista de conversas)
old = "type LunaMsg={me:boolean,t:string}"
new = "type LunaMsg={me:boolean,t:string,at?:number}"
s = replace_once(s, old, new, "lunamsg-at")

old = "const saudacaoInicial=():LunaMsg[]=>[{me:false,t:`${g}, Denise! Sou a Luna 💜 Pode falar comigo por texto, áudio ou mandar uma foto. Como posso ajudar?`}]"
new = "const saudacaoInicial=():LunaMsg[]=>[{me:false,t:`${g}, Denise! Sou a Luna 💜 Pode falar comigo por texto, áudio ou mandar uma foto. Como posso ajudar?`,at:Date.now()}]"
s = replace_once(s, old, new, "saudacao-at")

# 2) LunaInsight ganha campos opcionais usados nos novos formatos de card (badge/tile/sugestao)
old = "type LunaInsight={id:string,tipo:'atencao'|'padrao'|'progresso'|'sugestao',titulo:string,conclusao:string,evidencia:string,periodo:string,modulo:CategoriaLuna,rota:string,acaoPerguntar?:string}"
new = "type LunaInsight={id:string,tipo:'atencao'|'padrao'|'progresso'|'sugestao',titulo:string,conclusao:string,evidencia:string,periodo:string,modulo:CategoriaLuna,rota:string,acaoPerguntar?:string,deltaLabel?:string,rotuloCurto?:string,acaoPrimariaLabel?:string}"
s = replace_once(s, old, new, "lunainsight-campos-extra")

# 3) Progresso: rotulo curto + delta pra virar tile compacto
old = "out.push({id:`progresso_proteina_${periodoDias}_${metaAtualG}_${metaAntG}`,tipo:'progresso',titulo:`Consistência da meta de proteína ${metaAtualG>metaAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Meta batida em ${metaAtualG} de ${ultN.length} dias, contra ${metaAntG} de ${antN.length} dias no período anterior.`,evidencia:`Comparação de ${periodoDias} dias.`,periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/alimentacao'})"
new = "out.push({id:`progresso_proteina_${periodoDias}_${metaAtualG}_${metaAntG}`,tipo:'progresso',titulo:`Consistência da meta de proteína ${metaAtualG>metaAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Meta batida em ${metaAtualG} de ${ultN.length} dias, contra ${metaAntG} de ${antN.length} dias no período anterior.`,evidencia:`Comparação de ${periodoDias} dias.`,periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/alimentacao',rotuloCurto:'Proteína',deltaLabel:`${metaAtualG-metaAntG>=0?'+':''}${metaAtualG-metaAntG}`})"
s = replace_once(s, old, new, "progresso-proteina-tile")

old = "out.push({id:`progresso_treino_${periodoDias}_${treinoAtualG}_${treinoAntG}`,tipo:'progresso',titulo:`Frequência de treinos ${treinoAtualG>treinoAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${treinoAtualG} treino${treinoAtualG===1?'':'s'} concluído${treinoAtualG===1?'':'s'} nos últimos ${periodoDias} dias, contra ${treinoAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Exercícios.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/exercicios'})"
new = "out.push({id:`progresso_treino_${periodoDias}_${treinoAtualG}_${treinoAntG}`,tipo:'progresso',titulo:`Frequência de treinos ${treinoAtualG>treinoAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${treinoAtualG} treino${treinoAtualG===1?'':'s'} concluído${treinoAtualG===1?'':'s'} nos últimos ${periodoDias} dias, contra ${treinoAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Exercícios.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/exercicios',rotuloCurto:'Treinos',deltaLabel:`${treinoAtualG-treinoAntG>=0?'+':''}${treinoAtualG-treinoAntG}`})"
s = replace_once(s, old, new, "progresso-treino-tile")

old = "out.push({id:`progresso_leitura_${periodoDias}_${minAtualG}_${minAntG}`,tipo:'progresso',titulo:`Tempo de leitura ${minAtualG>minAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${minAtualG} minutos lidos nos últimos ${periodoDias} dias, contra ${minAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Desenvolvimento.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Desenvolvimento',rota:'/desenvolvimento'})"
new = "out.push({id:`progresso_leitura_${periodoDias}_${minAtualG}_${minAntG}`,tipo:'progresso',titulo:`Tempo de leitura ${minAtualG>minAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${minAtualG} minutos lidos nos últimos ${periodoDias} dias, contra ${minAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Desenvolvimento.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Desenvolvimento',rota:'/desenvolvimento',rotuloCurto:'Leitura',deltaLabel:`${minAtualG-minAntG>=0?'+':''}${minAtualG-minAntG} min`})"
s = replace_once(s, old, new, "progresso-leitura-tile")

old = "out.push({id:`progresso_devocional_${periodoDias}_${devAtualG}_${devAntG}`,tipo:'progresso',titulo:`Consistência do devocional ${devAtualG>devAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Devocional feito em ${devAtualG} de ${ultN.length} dias, contra ${devAntG} de ${antN.length} dias no período anterior.`,evidencia:'Baseado nos registros de Espiritual.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Espiritual',rota:'/espiritual'})"
new = "out.push({id:`progresso_devocional_${periodoDias}_${devAtualG}_${devAntG}`,tipo:'progresso',titulo:`Consistência do devocional ${devAtualG>devAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Devocional feito em ${devAtualG} de ${ultN.length} dias, contra ${devAntG} de ${antN.length} dias no período anterior.`,evidencia:'Baseado nos registros de Espiritual.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Espiritual',rota:'/espiritual',rotuloCurto:'Devocional',deltaLabel:`${devAtualG-devAntG>=0?'+':''}${devAtualG-devAntG}`})"
s = replace_once(s, old, new, "progresso-devocional-tile")

# 4) Sugestoes: rotulo do botao primario (verbo especifico por sugestao)
old = "out.push({id:`sugestao_treino_meta_${faltaG}`,tipo:'sugestao',titulo:'Ajustar o plano de treino desta semana?',conclusao:`Faltam ${faltaG} treino${faltaG===1?'':'s'} para bater a meta semanal de ${metaTreinosSemanaG}.`,evidencia:`${treinosEstaSemanaG} de ${metaTreinosSemanaG} treinos concluídos essa semana.`,periodo:'semana atual',modulo:'Saúde',rota:'/exercicios',acaoPerguntar:'Quer me ajudar a encaixar os treinos que faltam essa semana?'})"
new = "out.push({id:`sugestao_treino_meta_${faltaG}`,tipo:'sugestao',titulo:'Ajustar o plano de treino desta semana?',conclusao:`Faltam ${faltaG} treino${faltaG===1?'':'s'} para bater a meta semanal de ${metaTreinosSemanaG}.`,evidencia:`${treinosEstaSemanaG} de ${metaTreinosSemanaG} treinos concluídos essa semana.`,periodo:'semana atual',modulo:'Saúde',rota:'/exercicios',acaoPerguntar:'Quer me ajudar a encaixar os treinos que faltam essa semana?',acaoPrimariaLabel:'Organizar agora'})"
s = replace_once(s, old, new, "sugestao-treino-label")

old = "out.push({id:`sugestao_agua_${padraoAguaDiaG.dw}`,tipo:'sugestao',titulo:`Configurar um lembrete extra de água às ${padraoAguaDiaG.nome}s?`,conclusao:'Baseado no padrão percebido de menor ingestão nesse dia da semana.',evidencia:'Ver o padrão em \"Padrões percebidos\".',periodo:'sugestão',modulo:'Saúde',rota:'/alimentacao',acaoPerguntar:`Quer me ajudar a lembrar de beber mais água às ${padraoAguaDiaG.nome}s?`})"
new = "out.push({id:`sugestao_agua_${padraoAguaDiaG.dw}`,tipo:'sugestao',titulo:`Configurar um lembrete extra de água às ${padraoAguaDiaG.nome}s?`,conclusao:'Baseado no padrão percebido de menor ingestão nesse dia da semana.',evidencia:'Ver o padrão em \"Padrões percebidos\".',periodo:'sugestão',modulo:'Saúde',rota:'/alimentacao',acaoPerguntar:`Quer me ajudar a lembrar de beber mais água às ${padraoAguaDiaG.nome}s?`,acaoPrimariaLabel:'Configurar lembrete'})"
s = replace_once(s, old, new, "sugestao-agua-label")

old = "out.push({id:'sugestao_retomar_leitura',tipo:'sugestao',titulo:'Retomar a leitura de hoje?',conclusao:'Você tinha um histórico de leitura frequente e não há registro nos últimos dias.',evidencia:`${leiturasTodasG.length} sessões de leitura registradas ao todo.`,periodo:'agora',modulo:'Desenvolvimento',rota:'/desenvolvimento',acaoPerguntar:'Quer que eu te lembre de retomar a leitura hoje?'})"
new = "out.push({id:'sugestao_retomar_leitura',tipo:'sugestao',titulo:'Retomar a leitura de hoje?',conclusao:'Você tinha um histórico de leitura frequente e não há registro nos últimos dias.',evidencia:`${leiturasTodasG.length} sessões de leitura registradas ao todo.`,periodo:'agora',modulo:'Desenvolvimento',rota:'/desenvolvimento',acaoPerguntar:'Quer que eu te lembre de retomar a leitura hoje?',acaoPrimariaLabel:'Manter'})"
s = replace_once(s, old, new, "sugestao-leitura-label")

# 5) Novos estados: busca de insights (com o icone de lupa do cabecalho) e busca de conversas
old = "  const [verTodosLuna,setVerTodosLuna]=React.useState<Record<string,boolean>>({})"
new = """  const [verTodosLuna,setVerTodosLuna]=React.useState<Record<string,boolean>>({})
  const [buscaLuna,setBuscaLuna]=React.useState('')
  const [buscaLunaAberta,setBuscaLunaAberta]=React.useState(false)
  const [buscaConversaLuna,setBuscaConversaLuna]=React.useState('')"""
s = replace_once(s, old, new, "estados-busca-luna")

# 6) Filtro de insights passa a considerar a busca por titulo
old = """  const insightsVisiveisLuna=insightsBrutosLuna.filter(ins=>{
    if(tiposOcultosLuna[ins.tipo]&&tiposOcultosLuna[ins.tipo]>=hojeIsoFiltroLuna)return false
    if(ignoradosLuna[ins.id]&&ignoradosLuna[ins.id]>=hojeIsoFiltroLuna)return false
    if(categoriaLuna!=='Todos'&&ins.modulo!==categoriaLuna)return false
    return true
  })"""
new = """  const insightsVisiveisLuna=insightsBrutosLuna.filter(ins=>{
    if(tiposOcultosLuna[ins.tipo]&&tiposOcultosLuna[ins.tipo]>=hojeIsoFiltroLuna)return false
    if(ignoradosLuna[ins.id]&&ignoradosLuna[ins.id]>=hojeIsoFiltroLuna)return false
    if(categoriaLuna!=='Todos'&&ins.modulo!==categoriaLuna)return false
    if(buscaLuna.trim()&&!ins.titulo.toLowerCase().includes(buscaLuna.trim().toLowerCase()))return false
    return true
  })"""
s = replace_once(s, old, new, "filtro-busca-insights")

# 7) Substitui CardInsightLuna generico + SecaoInsightsLuna por formatos distintos por categoria
#    (grade com selo pra Atencao, icone+"Entender" pra Padroes, lista de duas acoes pra Sugestoes, tiles pra Progresso)
old = """  function CardInsightLuna({ins}:{ins:LunaInsight}){
    const fb=feedbackLuna[ins.id]
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderLeft:`3px solid ${COR_TIPO_LUNA[ins.tipo]}`,borderRadius:12,padding:16}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:8,flexWrap:'wrap' as const}}>
        <span style={{fontSize:14}}>{ICONE_TIPO_LUNA[ins.tipo]}</span>
        <span style={{fontSize:11,fontWeight:700,color:COR_TIPO_LUNA[ins.tipo],textTransform:'uppercase' as const,letterSpacing:'.4px'}}>{LABEL_TIPO_LUNA[ins.tipo]}</span>
        <span style={{fontSize:11,background:'rgba(255,255,255,.06)',color:'rgba(255,255,255,.5)',padding:'2px 8px',borderRadius:20}}>{ins.modulo}</span>
        <span style={{fontSize:11,color:'rgba(255,255,255,.35)',marginLeft:'auto'}}>{ins.periodo}</span>
      </div>
      <div style={{fontWeight:700,fontSize:14,marginBottom:5}}>{ins.titulo}</div>
      <div style={{fontSize:13,color:'rgba(255,255,255,.65)',lineHeight:1.5,marginBottom:6}}>{ins.conclusao}</div>
      <div style={{fontSize:11.5,color:'rgba(255,255,255,.4)',marginBottom:10}}>{ins.evidencia}</div>
      <div style={{display:'flex',gap:8,flexWrap:'wrap' as const,alignItems:'center'}}>
        <button onClick={()=>navigate(ins.rota)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Ver origem</button>
        {ins.acaoPerguntar&&<button onClick={()=>perguntarLuna(ins.acaoPerguntar as string)} style={{background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Perguntar à Luna</button>}
        <button onClick={()=>ignorarInsightLuna(ins.id)} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.35)',fontSize:11.5,cursor:'pointer'}}>Ignorar</button>
        <button onClick={()=>ocultarTipoLuna(ins.tipo)} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.3)',fontSize:11,cursor:'pointer'}}>Não mostrar {LABEL_TIPO_LUNA[ins.tipo].toLowerCase()} por enquanto</button>
        <span style={{marginLeft:'auto',display:'flex',gap:6}}>
          <button onClick={()=>darFeedbackLuna(ins.id,'util')} title="Útil" style={{background:'none',border:'none',cursor:'pointer',fontSize:13,opacity:fb==='util'?1:.35}}>👍</button>
          <button onClick={()=>darFeedbackLuna(ins.id,'nao_util')} title="Não é útil" style={{background:'none',border:'none',cursor:'pointer',fontSize:13,opacity:fb==='nao_util'?1:.35}}>👎</button>
        </span>
      </div>
    </div>)
  }
  function SecaoInsightsLuna({titulo,tipo,itens}:{titulo:string,tipo:LunaInsight['tipo'],itens:LunaInsight[]}){
    if(itens.length===0)return null
    const aberta=!!verTodosLuna[tipo]
    const visiveis=aberta?itens:itens.slice(0,3)
    return(<div style={{marginBottom:22}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
        <span style={{fontSize:15}}>{ICONE_TIPO_LUNA[tipo]}</span><span style={{fontWeight:800,fontSize:15}}>{titulo}</span><span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>({itens.length})</span>
      </div>
      <div style={{display:'flex',flexDirection:'column' as const,gap:10}}>
        {visiveis.map(ins=><CardInsightLuna key={ins.id} ins={ins}/>)}
      </div>
      {itens.length>3&&<button onClick={()=>setVerTodosLuna(v=>({...v,[tipo]:!v[tipo]}))} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',marginTop:8,padding:0}}>{aberta?'Ver menos':`Ver todos (${itens.length})`}</button>}
    </div>)
  }"""
new = """  function MenuInsightLuna({ins}:{ins:LunaInsight}){
    const [aberto,setAberto]=React.useState(false)
    const fb=feedbackLuna[ins.id]
    return(<div style={{position:'relative' as const}}>
      <button onClick={()=>setAberto(v=>!v)} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.4)',fontSize:16,cursor:'pointer',padding:'0 4px'}}>⋯</button>
      {aberto&&<div onMouseLeave={()=>setAberto(false)} style={{position:'absolute' as const,right:0,top:24,background:'#1c1c28',border:`1px solid ${C.line}`,borderRadius:10,padding:6,zIndex:10,minWidth:190,boxShadow:'0 8px 24px rgba(0,0,0,.4)'}}>
        <button onClick={()=>{darFeedbackLuna(ins.id,'util');setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:fb==='util'?C.ok:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>👍 Útil</button>
        <button onClick={()=>{darFeedbackLuna(ins.id,'nao_util');setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:fb==='nao_util'?C.danger:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>👎 Não é útil</button>
        <button onClick={()=>{ignorarInsightLuna(ins.id);setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>Ignorar</button>
        <button onClick={()=>{ocultarTipoLuna(ins.tipo);setAberto(false)}} style={{display:'block',width:'100%',textAlign:'left' as const,background:'none',border:'none',color:'rgba(255,255,255,.7)',fontSize:12,padding:'7px 8px',cursor:'pointer',borderRadius:6}}>Não mostrar {LABEL_TIPO_LUNA[ins.tipo].toLowerCase()}</button>
      </div>}
    </div>)
  }
  function badgeAtencaoLuna(ins:LunaInsight):{label:string,cor:string}{
    if(ins.id.startsWith('casa_contas_atrasadas'))return {label:'Atrasada',cor:C.danger}
    if(ins.id.startsWith('casa_contas_hoje'))return {label:'Vence hoje',cor:C.danger}
    if(ins.id.startsWith('casa_manut_alta'))return {label:'Aguardando',cor:C.warn}
    if(ins.id.startsWith('trab_atrasadas'))return {label:'Atrasadas',cor:C.warn}
    if(ins.id.startsWith('fam_aval')){if(ins.periodo==='hoje')return {label:'Hoje',cor:C.danger};if(ins.periodo==='amanhã')return {label:'Amanhã',cor:C.warn};return {label:'Em breve',cor:C.water}}
    if(ins.id.startsWith('saude_tz_estoque_baixo'))return {label:'Estoque baixo',cor:C.warn}
    return {label:'Atenção',cor:C.warn}
  }
  function CardAtencaoLuna({ins}:{ins:LunaInsight}){
    const badge=badgeAtencaoLuna(ins)
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',flexDirection:'column' as const,gap:10}}>
      <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:6}}>
        <span style={{fontSize:11,fontWeight:700,color:badge.cor,background:hexParaRgbaTrab(badge.cor,.15),padding:'3px 9px',borderRadius:20}}>{badge.label}</span>
        <MenuInsightLuna ins={ins}/>
      </div>
      <div style={{fontWeight:700,fontSize:13.5,lineHeight:1.35}}>{ins.titulo}</div>
      <div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>{ins.modulo}{ins.evidencia?` · ${ins.evidencia}`:''}</div>
      <div style={{display:'flex',gap:8,marginTop:'auto',flexWrap:'wrap' as const}}>
        <button onClick={()=>navigate(ins.rota)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Ver origem</button>
        {ins.acaoPerguntar&&<button onClick={()=>perguntarLuna(ins.acaoPerguntar as string)} style={{background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Perguntar à Luna</button>}
      </div>
    </div>)
  }
  function CardPadraoLuna({ins}:{ins:LunaInsight}){
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16,display:'flex',flexDirection:'column' as const,gap:8}}>
      <div style={{width:34,height:34,borderRadius:10,background:hexParaRgbaTrab(COR_TIPO_LUNA[ins.tipo],.14),display:'grid',placeItems:'center',fontSize:16}}>{ICONE_TIPO_LUNA[ins.tipo]}</div>
      <div style={{fontWeight:700,fontSize:13}}>{ins.rotuloCurto||ins.modulo}</div>
      <div style={{fontSize:12.5,color:'rgba(255,255,255,.6)',lineHeight:1.45}}>{ins.conclusao}</div>
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginTop:'auto'}}>
        <span style={{fontSize:10.5,color:'rgba(255,255,255,.35)'}}>{ins.periodo}</span>
        <button onClick={()=>perguntarLuna(`Por que você está me mostrando isso: \"${ins.titulo}\"? Me explica com os números que embasam essa conclusão.`)} style={{background:'transparent',border:'none',color:C.acc2,fontSize:11.5,fontWeight:600,cursor:'pointer'}}>Entender</button>
      </div>
    </div>)
  }
  function LinhaSugestaoLuna({ins}:{ins:LunaInsight}){
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:12,padding:'14px 16px',display:'flex',alignItems:'center',gap:12}}>
      <span style={{color:'rgba(255,255,255,.3)',fontSize:14}}>›</span>
      <span style={{flex:1,fontSize:13,color:'rgba(255,255,255,.75)',lineHeight:1.4}}>{ins.conclusao||ins.titulo}</span>
      <div style={{display:'flex',gap:8,flexShrink:0}}>
        <button onClick={()=>ins.acaoPerguntar?perguntarLuna(ins.acaoPerguntar):ignorarInsightLuna(ins.id)} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:8,padding:'7px 14px',fontSize:12,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>{ins.acaoPrimariaLabel||'Ver'}</button>
        <button onClick={()=>ignorarInsightLuna(ins.id)} style={{background:'transparent',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.5)',borderRadius:8,padding:'7px 12px',fontSize:12,cursor:'pointer'}}>Depois</button>
      </div>
    </div>)
  }
  function TileProgressoLuna({ins}:{ins:LunaInsight}){
    const positivo=(ins.deltaLabel||'').trim().startsWith('+')
    const negativo=(ins.deltaLabel||'').trim().startsWith('-')
    const cor=positivo?C.ok:negativo?C.danger:'rgba(255,255,255,.6)'
    return(<div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:'12px 14px'}}>
      <div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginBottom:4}}>{ins.rotuloCurto||ins.modulo}</div>
      <div style={{fontSize:18,fontWeight:800,color:cor}}>{ins.deltaLabel||'—'}</div>
      <div style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginTop:2}}>vs. período anterior</div>
    </div>)
  }
  function SecaoInsightsLuna({titulo,tipo,itens}:{titulo:string,tipo:LunaInsight['tipo'],itens:LunaInsight[]}){
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
s = replace_once(s, old, new, "cards-por-categoria")

# 8) Lista de conversas: item ganha horario (criadaEm) alem do pin/excluir
old = """  function ItemConversaLuna({c}:{c:{id:string,titulo:string,isWhats:boolean,fixada:boolean}}){
    return(<div onClick={()=>setAtivaId(c.id)} style={{display:'flex',alignItems:'center',gap:6,padding:'9px 10px',borderRadius:10,cursor:'pointer',background:ativaId===c.id?'rgba(139,92,246,.15)':'transparent',color:ativaId===c.id?'#fff':'rgba(255,255,255,.6)'}}>
      <span style={{fontSize:13,flex:1,overflow:'hidden',textOverflow:'ellipsis' as const,whiteSpace:'nowrap' as const}}>{c.isWhats?'💬 ':''}{c.titulo}</span>
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();togglePinConversaLuna(c.id)}} title={c.fixada?'Desafixar':'Fixar'} style={{background:'none',border:'none',color:c.fixada?C.warn:'rgba(255,255,255,.25)',cursor:'pointer',fontSize:12,flexShrink:0}}>📌</button>}
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();excluirConversa(c.id)}} style={{background:'none',border:'none',color:'rgba(255,255,255,.3)',cursor:'pointer',fontSize:12,flexShrink:0}}>✕</button>}
    </div>)
  }"""
new = """  function ItemConversaLuna({c}:{c:{id:string,titulo:string,isWhats:boolean,fixada:boolean,criadaEm:string|null}}){
    const horario=c.criadaEm?(()=>{try{return new Date(c.criadaEm as string).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}catch{return ''}})():''
    return(<div onClick={()=>setAtivaId(c.id)} style={{display:'flex',alignItems:'center',gap:6,padding:'9px 10px',borderRadius:10,cursor:'pointer',background:ativaId===c.id?'rgba(139,92,246,.15)':'transparent',color:ativaId===c.id?'#fff':'rgba(255,255,255,.6)'}}>
      <span style={{fontSize:13,flex:1,overflow:'hidden',textOverflow:'ellipsis' as const,whiteSpace:'nowrap' as const}}>{c.isWhats?'💬 ':''}{c.titulo}</span>
      {horario&&<span style={{fontSize:10,color:'rgba(255,255,255,.3)',flexShrink:0}}>{horario}</span>}
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();togglePinConversaLuna(c.id)}} title={c.fixada?'Desafixar':'Fixar'} style={{background:'none',border:'none',color:c.fixada?C.warn:'rgba(255,255,255,.25)',cursor:'pointer',fontSize:12,flexShrink:0}}>📌</button>}
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();excluirConversa(c.id)}} style={{background:'none',border:'none',color:'rgba(255,255,255,.3)',cursor:'pointer',fontSize:12,flexShrink:0}}>✕</button>}
    </div>)
  }"""
s = replace_once(s, old, new, "item-conversa-horario")

# 9) Filtra a lista de conversas pela busca
old = "  const listaConversasTodasLuna=[{id:WHATSAPP_THREAD_ID,titulo:'WhatsApp',isWhats:true,fixada:true,criadaEm:null as string|null},...conversas.map(c=>({id:c.id,titulo:c.titulo,isWhats:false,fixada:!!c.fixada,criadaEm:(c.criadaEm||null) as string|null}))]"
new = "  const listaConversasTodasLuna=[{id:WHATSAPP_THREAD_ID,titulo:'WhatsApp',isWhats:true,fixada:true,criadaEm:null as string|null},...conversas.map(c=>({id:c.id,titulo:c.titulo,isWhats:false,fixada:!!c.fixada,criadaEm:(c.criadaEm||null) as string|null}))].filter(c=>!buscaConversaLuna.trim()||c.titulo.toLowerCase().includes(buscaConversaLuna.trim().toLowerCase()))"
s = replace_once(s, old, new, "filtro-busca-conversas")

# 10) Renderizador leve de markdown (negrito **texto** e listas com -) pros balões da Luna
old = "  function toBase64(blob:Blob):Promise<string>{return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(String(r.result).split(',')[1]||'');r.onerror=rej;r.readAsDataURL(blob)})}"
new = """  function toBase64(blob:Blob):Promise<string>{return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(String(r.result).split(',')[1]||'');r.onerror=rej;r.readAsDataURL(blob)})}
  function renderMsgLuna(t:string){
    return t.split('\\n').map((linha,li)=>{
      const bullet=/^[-•]\\s+/.test(linha)
      const conteudo=bullet?linha.replace(/^[-•]\\s+/,''):linha
      const partes=conteudo.split(/(\\*\\*[^*]+\\*\\*)/g).filter(pt=>pt.length>0).map((pt,pi)=>pt.startsWith('**')&&pt.endsWith('**')?<b key={pi}>{pt.slice(2,-2)}</b>:<span key={pi}>{pt}</span>)
      return <div key={li} style={{display:'flex',gap:6}}>{bullet&&<span>•</span>}<span>{partes}</span></div>
    })
  }"""
s = replace_once(s, old, new, "renderizador-markdown-leve")

# 11) Cabecalho da Luna: titulo/subtitulo iguais a referencia + busca/sino/tema/perfil, e abas viram pilulas
old = """  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:16}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Luna</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Sua assistente pessoal — entende texto, áudio e imagem.</p></div>
      {abaLuna==='conversar'&&<button onClick={novaConversa} style={{background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer',flexShrink:0,whiteSpace:'nowrap' as const}}>+ Nova conversa</button>}
    </div>
    <div style={{display:'flex',gap:6,marginBottom:20,borderBottom:`1px solid ${C.line}`}}>
      {(['insights','conversar'] as const).map(ab=>(<button key={ab} onClick={()=>setAbaLuna(ab)} style={{background:'none',border:'none',borderBottom:`2px solid ${abaLuna===ab?C.acc2:'transparent'}`,color:abaLuna===ab?'#fff':'rgba(255,255,255,.4)',fontWeight:abaLuna===ab?700:500,fontSize:13.5,padding:'0 4px 10px',marginRight:14,cursor:'pointer'}}>{ab==='insights'?'📊 Insights':'💬 Conversar'}</button>))}
    </div>"""
new = """  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:12,marginBottom:16,flexWrap:'wrap' as const}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>✨ Luna</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Sua inteligência pessoal do Denise OS</p></div>
      <div style={{display:'flex',alignItems:'center',gap:10}}>
        {abaLuna==='conversar'&&<button onClick={novaConversa} style={{background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer',flexShrink:0,whiteSpace:'nowrap' as const}}>+ Nova conversa</button>}
        {buscaLunaAberta?<input autoFocus value={buscaLuna} onChange={e=>setBuscaLuna(e.target.value)} onBlur={()=>{if(!buscaLuna)setBuscaLunaAberta(false)}} placeholder="Buscar insight…" style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:9,padding:'8px 12px',color:'#fff',fontSize:12.5,width:160}}/>:<button onClick={()=>setBuscaLunaAberta(true)} title="Buscar" style={{width:36,height:36,borderRadius:9,background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:14}}>🔎</button>}
        <button title="Notificações" style={{position:'relative' as const,width:36,height:36,borderRadius:9,background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',cursor:'pointer',fontSize:14}}>🔔{porTipoLuna.atencao.length>0&&<span style={{position:'absolute' as const,top:-4,right:-4,background:C.danger,color:'#fff',borderRadius:20,fontSize:9.5,fontWeight:700,padding:'1px 5px',minWidth:16,textAlign:'center' as const}}>{porTipoLuna.atencao.length}</span>}</button>
        <span title="Tema" style={{width:36,height:36,borderRadius:9,background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.4)',display:'grid',placeItems:'center',fontSize:14}}>🌙</span>
        <div onClick={()=>navigate('/config')} style={{display:'flex',alignItems:'center',gap:8,cursor:'pointer',background:C.s2,border:`1px solid ${C.line}`,borderRadius:9,padding:'5px 10px 5px 5px'}}>
          <Avatar id="denise" label="D" size={26} radius={8}/>
          <span style={{fontSize:12.5,fontWeight:600}}>Denise</span>
          <span style={{fontSize:10,color:'rgba(255,255,255,.4)'}}>▾</span>
        </div>
      </div>
    </div>
    <div style={{display:'inline-flex',gap:4,marginBottom:20,background:C.s2,border:`1px solid ${C.line}`,borderRadius:12,padding:4}}>
      {(['insights','conversar'] as const).map(ab=>(<button key={ab} onClick={()=>setAbaLuna(ab)} style={{background:abaLuna===ab?`linear-gradient(135deg,${C.acc},#7c3aed)`:'transparent',border:'none',borderRadius:9,color:abaLuna===ab?'#fff':'rgba(255,255,255,.5)',fontWeight:700,fontSize:13,padding:'8px 18px',cursor:'pointer'}}>{ab==='insights'?'📊 Insights':'💬 Conversar'}</button>))}
    </div>"""
s = replace_once(s, old, new, "cabecalho-e-pilulas")

# 12) Filtros: chips viram dois dropdowns (modulo / periodo), igual a referencia
old = """      <div style={{display:'flex',gap:8,flexWrap:'wrap' as const,marginBottom:10}}>
        {(['Todos','Saúde','Trabalho','Família','Casa','Desenvolvimento','Espiritual'] as const).map(cat=>(<button key={cat} onClick={()=>setCategoriaLuna(cat)} style={{background:categoriaLuna===cat?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,color:'#fff',border:`1px solid ${categoriaLuna===cat?'transparent':C.line}`,borderRadius:20,padding:'6px 13px',fontSize:12,fontWeight:600,cursor:'pointer'}}>{cat}</button>))}
      </div>
      <div style={{display:'flex',gap:8,marginBottom:20}}>
        {([7,30,90] as const).map(n=>(<button key={n} onClick={()=>setPeriodoLuna(n)} style={{background:periodoLuna===n?'rgba(139,92,246,.15)':'transparent',color:periodoLuna===n?C.acc2:'rgba(255,255,255,.4)',border:`1px solid ${periodoLuna===n?'rgba(139,92,246,.3)':C.line}`,borderRadius:20,padding:'5px 12px',fontSize:11.5,cursor:'pointer'}}>{n} dias</button>))}
      </div>"""
new = """      <div style={{display:'flex',gap:10,marginBottom:20,flexWrap:'wrap' as const,alignItems:'center'}}>
        <select value={categoriaLuna} onChange={e=>setCategoriaLuna(e.target.value as any)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}>
          {(['Todos','Saúde','Trabalho','Família','Casa','Desenvolvimento','Espiritual'] as const).map(cat=>(<option key={cat} value={cat}>{cat==='Todos'?'Todos os módulos':cat}</option>))}
        </select>
        <select value={periodoLuna} onChange={e=>setPeriodoLuna(Number(e.target.value) as any)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}>
          {([7,30,90] as const).map(n=>(<option key={n} value={n}>Últimos {n} dias</option>))}
        </select>
      </div>"""
s = replace_once(s, old, new, "filtros-dropdown")

# 13) Sidebar de conversas ganha campo de busca antes do grupo "Fixadas"
old = """    <div style={{width:220,flexShrink:0,background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:10,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:4}}>
      <div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'4px 10px 2px'}}>Fixadas</div>"""
new = """    <div style={{width:220,flexShrink:0,background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:10,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:4}}>
      <input value={buscaConversaLuna} onChange={e=>setBuscaConversaLuna(e.target.value)} placeholder="🔎 Buscar conversas…" style={{background:'rgba(255,255,255,.05)',border:`1px solid ${C.line}`,borderRadius:9,padding:'7px 10px',color:'#fff',fontSize:12,marginBottom:6}}/>
      <div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'4px 10px 2px'}}>Fixadas</div>"""
s = replace_once(s, old, new, "busca-conversas-ui")

# 14) Baloes de mensagem: formatacao leve + horario
old = "        {msgs.map((m,i)=>(<div key={i} style={{maxWidth:'80%',padding:'11px 14px',borderRadius:14,fontSize:13.5,lineHeight:1.5,alignSelf:m.me?'flex-end':'flex-start',background:m.me?`linear-gradient(135deg,${C.acc},#7c3aed)`:'rgba(255,255,255,.06)',border:m.me?'none':`1px solid ${C.line}`,whiteSpace:'pre-wrap' as const}}>{m.t}</div>))}"
new = """        {msgs.map((m,i)=>(<div key={i} style={{maxWidth:'80%',display:'flex',flexDirection:'column' as const,alignSelf:m.me?'flex-end':'flex-start'}}>
          <div style={{padding:'11px 14px',borderRadius:14,fontSize:13.5,lineHeight:1.5,background:m.me?`linear-gradient(135deg,${C.acc},#7c3aed)`:'rgba(255,255,255,.06)',border:m.me?'none':`1px solid ${C.line}`}}>{renderMsgLuna(m.t)}</div>
          {m.at&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',marginTop:3,textAlign:m.me?'right' as const:'left' as const}}>{new Date(m.at).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}</div>}
        </div>))}"""
s = replace_once(s, old, new, "baloes-horario-formatacao")

# 15) Timestamp nas mensagens que o app cria (usuario, respostas da Luna e confirmacoes de agenda)
old = "    setMsgsAtual(m=>[...m,{me:true,t:displayText}])"
new = "    setMsgsAtual(m=>[...m,{me:true,t:displayText,at:Date.now()}])"
s = replace_once(s, old, new, "at-mensagem-usuario")

old = "      setMsgsAtual(m=>[...m,{me:false,t:textoLimpo}])"
new = "      setMsgsAtual(m=>[...m,{me:false,t:textoLimpo,at:Date.now()}])"
s = replace_once(s, old, new, "at-resposta-luna")

old = "      setMsgsAtual(m=>[...m,{me:false,t:'😕 '+(err?.message||'Não consegui responder agora. Tenta de novo?')}])"
new = "      setMsgsAtual(m=>[...m,{me:false,t:'😕 '+(err?.message||'Não consegui responder agora. Tenta de novo?'),at:Date.now()}])"
s = replace_once(s, old, new, "at-erro-send")

old = "        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento criado na agenda e sincronizado com o Google Calendar.'}])"
new = "        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento criado na agenda e sincronizado com o Google Calendar.',at:Date.now()}])"
s = replace_once(s, old, new, "at-evento-criado")

old = "        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento atualizado na agenda.'}])"
new = "        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento atualizado na agenda.',at:Date.now()}])"
s = replace_once(s, old, new, "at-evento-atualizado")

old = "        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento excluído da agenda e do Google Calendar.'}])"
new = "        setMsgsAtual(m=>[...m,{me:false,t:'✅ Evento excluído da agenda e do Google Calendar.',at:Date.now()}])"
s = replace_once(s, old, new, "at-evento-excluido")

old = "      setMsgsAtual(m=>[...m,{me:false,t:'😕 Não consegui concluir essa ação na agenda agora.'}])"
new = "      setMsgsAtual(m=>[...m,{me:false,t:'😕 Não consegui concluir essa ação na agenda agora.',at:Date.now()}])"
s = replace_once(s, old, new, "at-erro-acao-agenda")

old = "    setMsgsAtual(m=>[...m,{me:false,t:'Combinado, não fiz nenhuma alteração na agenda.'}])"
new = "    setMsgsAtual(m=>[...m,{me:false,t:'Combinado, não fiz nenhuma alteração na agenda.',at:Date.now()}])"
s = replace_once(s, old, new, "at-cancelar-acao")

old = "      setMsgsAtual(m=>[...m,{me:false,t:'Não consegui acessar o microfone. Verifica a permissão de áudio do navegador.'}])"
new = "      setMsgsAtual(m=>[...m,{me:false,t:'Não consegui acessar o microfone. Verifica a permissão de áudio do navegador.',at:Date.now()}])"
s = replace_once(s, old, new, "at-erro-microfone")

# 16) Alternador rapido de canal (App/WhatsApp) abaixo do campo de digitar
old = """        <button onClick={()=>send()} disabled={sending||recording||(!inp.trim()&&!pendingImg)} style={{width:36,height:36,borderRadius:10,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',cursor:'pointer',fontSize:18,flexShrink:0,opacity:(sending||recording||(!inp.trim()&&!pendingImg))?0.5:1}}>↑</button>
      </div>
    </div>
    </div>"""
new = """        <button onClick={()=>send()} disabled={sending||recording||(!inp.trim()&&!pendingImg)} style={{width:36,height:36,borderRadius:10,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,border:'none',color:'#fff',cursor:'pointer',fontSize:18,flexShrink:0,opacity:(sending||recording||(!inp.trim()&&!pendingImg))?0.5:1}}>↑</button>
      </div>
      <div style={{display:'flex',gap:8,marginTop:10}}>
        <button onClick={()=>{if(ativaId===WHATSAPP_THREAD_ID){if(conversas.length>0)setAtivaId(conversas[0].id);else novaConversa()}}} style={{background:ativaId!==WHATSAPP_THREAD_ID?'rgba(139,92,246,.15)':'transparent',border:`1px solid ${ativaId!==WHATSAPP_THREAD_ID?'rgba(139,92,246,.3)':C.line}`,color:ativaId!==WHATSAPP_THREAD_ID?C.acc2:'rgba(255,255,255,.4)',borderRadius:8,padding:'6px 14px',fontSize:11.5,fontWeight:600,cursor:'pointer'}}>📱 App</button>
        <button onClick={()=>setAtivaId(WHATSAPP_THREAD_ID)} style={{background:ativaId===WHATSAPP_THREAD_ID?'rgba(34,197,94,.15)':'transparent',border:`1px solid ${ativaId===WHATSAPP_THREAD_ID?'rgba(34,197,94,.3)':C.line}`,color:ativaId===WHATSAPP_THREAD_ID?C.ok:'rgba(255,255,255,.4)',borderRadius:8,padding:'6px 14px',fontSize:11.5,fontWeight:600,cursor:'pointer'}}>💬 WhatsApp</button>
      </div>
    </div>
    </div>"""
s = replace_once(s, old, new, "alternador-canal")

p.write_text(s)
print("TUDO OK:", applied)
