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

# 1) Card de Atencao volta a mostrar a conclusao (o "por que merece atencao"), nao so o modulo/evidencia
old1 = """      <div style={{fontWeight:700,fontSize:13.5,lineHeight:1.35}}>{ins.titulo}</div>
      <div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>{ins.modulo}{ins.evidencia?` · ${ins.evidencia}`:''}</div>
      <div style={{display:'flex',gap:8,marginTop:'auto',flexWrap:'wrap' as const}}>
        <button onClick={()=>navigate(ins.rota)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Ver origem</button>
        {ins.acaoPerguntar&&<button onClick={()=>perguntarLuna(ins.acaoPerguntar as string)} style={{background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Perguntar à Luna</button>}
      </div>
    </div>)
  }"""
new1 = """      <div style={{fontWeight:700,fontSize:13.5,lineHeight:1.35}}>{ins.titulo}</div>
      <div style={{fontSize:12,color:'rgba(255,255,255,.55)',lineHeight:1.4}}>{ins.conclusao}</div>
      <div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>{ins.modulo}{ins.evidencia?` · ${ins.evidencia}`:''}</div>
      <div style={{display:'flex',gap:8,marginTop:'auto',flexWrap:'wrap' as const}}>
        <button onClick={()=>navigate(ins.rota)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Ver origem</button>
        {ins.acaoPerguntar&&<button onClick={()=>perguntarLuna(ins.acaoPerguntar as string)} style={{background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Perguntar à Luna</button>}
      </div>
    </div>)
  }"""
s = replace_once(s, old1, new1, "atencao-mostra-conclusao")

# 2) Ordem das secoes igual a imagem: Atencao, Padroes, Sugestoes, Progresso (Progresso por ultimo)
#    + link "Ver todos os insights" no rodape, que expande as 4 secoes de uma vez
old2 = """      <SecaoInsightsLuna titulo="O que merece sua atenção" tipo="atencao" itens={porTipoLuna.atencao}/>
      <SecaoInsightsLuna titulo="Padrões percebidos" tipo="padrao" itens={porTipoLuna.padrao}/>
      <SecaoInsightsLuna titulo="Mudanças e progresso" tipo="progresso" itens={porTipoLuna.progresso}/>
      <SecaoInsightsLuna titulo="Sugestões da Luna" tipo="sugestao" itens={porTipoLuna.sugestao}/>
    </div>):("""
new2 = """      <SecaoInsightsLuna titulo="O que merece sua atenção" tipo="atencao" itens={porTipoLuna.atencao}/>
      <SecaoInsightsLuna titulo="Padrões percebidos" tipo="padrao" itens={porTipoLuna.padrao}/>
      <SecaoInsightsLuna titulo="Sugestões da Luna" tipo="sugestao" itens={porTipoLuna.sugestao}/>
      <SecaoInsightsLuna titulo="Mudanças e progresso" tipo="progresso" itens={porTipoLuna.progresso}/>
      {insightsVisiveisLuna.length>0&&<button onClick={()=>setVerTodosLuna({atencao:true,padrao:true,progresso:true,sugestao:true})} style={{background:'transparent',border:'none',color:C.acc2,fontSize:13,fontWeight:600,cursor:'pointer',padding:0,marginTop:4}}>Ver todos os insights →</button>}
    </div>):("""
s = replace_once(s, old2, new2, "ordem-secoes-e-ver-todos")

p.write_text(s)
print("TUDO OK:", applied)
