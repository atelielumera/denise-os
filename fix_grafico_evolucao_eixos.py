from pathlib import Path

p = Path("src/main.tsx")
s = p.read_text()

old = '''function LinhaEvolucao({pontos,cor}:{pontos:{iso:string,valor:number}[],cor:string}){
  if(pontos.length===0)return <div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'30px 0',textAlign:'center' as const}}>Nenhum registro no período selecionado.</div>
  if(pontos.length===1)return(<div style={{padding:'20px 0'}}><div style={{fontSize:24,fontWeight:800}}>{pontos[0].valor}kg</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Único registro no período · {new Date(pontos[0].iso+'T12:00:00').toLocaleDateString('pt-BR')}</div></div>)
  const vals=pontos.map(p=>p.valor)
  const mn=Math.min(...vals),mx=Math.max(...vals)
  const range=mx-mn||1
  const W=600,H=150,pad=8
  const xy=pontos.map((p,i)=>{const x=pad+(i/(pontos.length-1))*(W-pad*2);const y=H-pad-((p.valor-mn)/range)*(H-pad*2);return [x,y]})
  return(<div>
    <svg viewBox={`0 0 ${W} ${H}`} style={{width:'100%',height:140,display:'block'}} preserveAspectRatio="none">
      <polyline points={xy.map(([x,y])=>`${x},${y}`).join(' ')} fill="none" stroke={cor} strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round"/>
      {xy.map(([x,y],i)=>(<circle key={i} cx={x} cy={y} r={i===xy.length-1?4:2} fill={cor}/>))}
    </svg>
    <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)',marginTop:6}}>
      <span>{new Date(pontos[0].iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>
      <span>{new Date(pontos[pontos.length-1].iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>
    </div>
  </div>)
}'''

new = '''function LinhaEvolucao({pontos,cor,unidade='kg',rotulo='Peso atual'}:{pontos:{iso:string,valor:number}[],cor:string,unidade?:string,rotulo?:string}){
  if(pontos.length===0)return <div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'30px 0',textAlign:'center' as const}}>Nenhum registro no período selecionado.</div>
  const fmt=(v:number)=>Number.isInteger(v)?String(v):v.toFixed(1).replace('.',',')
  if(pontos.length===1)return(<div style={{padding:'20px 0'}}><div style={{fontSize:24,fontWeight:800}}>{fmt(pontos[0].valor)}{unidade}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Único registro no período · {new Date(pontos[0].iso+'T12:00:00').toLocaleDateString('pt-BR')}</div></div>)
  const vals=pontos.map(p=>p.valor)
  const mnRaw=Math.min(...vals),mxRaw=Math.max(...vals)
  const folga=(mxRaw-mnRaw||1)*0.12
  const mn=mnRaw-folga,mx=mxRaw+folga
  const range=mx-mn||1
  const W=600,H=150,pad=8
  const xy=pontos.map((p,i)=>{const x=pad+(i/(pontos.length-1))*(W-pad*2);const y=H-pad-((p.valor-mn)/range)*(H-pad*2);return [x,y]})
  const atual=pontos[pontos.length-1].valor
  const eixoY=[mx,mn+range*0.75,mn+range*0.5,mn+range*0.25,mn]
  const qtdLabelsX=Math.min(5,pontos.length)
  const idxLabelsX=Array.from({length:qtdLabelsX},(_,i)=>Math.round(i*(pontos.length-1)/(qtdLabelsX-1||1)))
  return(<div>
    <div style={{display:'flex',justifyContent:'flex-end',marginBottom:4}}>
      <div style={{textAlign:'right' as const}}>
        <div style={{fontSize:16,fontWeight:800}}>{fmt(atual)} {unidade}</div>
        <div style={{fontSize:10.5,color:'rgba(255,255,255,.4)'}}>{rotulo}</div>
      </div>
    </div>
    <div style={{display:'flex',gap:6}}>
      <div style={{display:'flex',flexDirection:'column' as const,justifyContent:'space-between',fontSize:10,color:'rgba(255,255,255,.35)',paddingBottom:18,textAlign:'right' as const,minWidth:30}}>
        {eixoY.map((v,i)=>(<span key={i}>{fmt(v)}</span>))}
      </div>
      <div style={{flex:1,minWidth:0}}>
        <svg viewBox={`0 0 ${W} ${H}`} style={{width:'100%',height:140,display:'block'}} preserveAspectRatio="none">
          {[0,0.25,0.5,0.75,1].map((f,i)=>(<line key={i} x1={0} x2={W} y1={H-pad-f*(H-pad*2)} y2={H-pad-f*(H-pad*2)} stroke="rgba(255,255,255,.06)" strokeWidth={1}/>))}
          <polyline points={xy.map(([x,y])=>`${x},${y}`).join(' ')} fill="none" stroke={cor} strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round"/>
          {xy.map(([x,y],i)=>(<circle key={i} cx={x} cy={y} r={i===xy.length-1?4:2} fill={cor}/>))}
        </svg>
        <div style={{display:'flex',justifyContent:'space-between' as const,fontSize:11,color:'rgba(255,255,255,.4)',marginTop:6}}>
          {idxLabelsX.map((idx,i)=>(<span key={i}>{new Date(pontos[idx].iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}</span>))}
        </div>
      </div>
    </div>
    <div style={{textAlign:'center' as const,fontSize:11,color:'rgba(255,255,255,.4)',marginTop:8}}>
      <span style={{display:'inline-flex',alignItems:'center',gap:5}}><span style={{width:14,height:2,background:cor,display:'inline-block'}}/>{rotulo==='Peso atual'?'Peso':rotulo} ({unidade})</span>
    </div>
  </div>)
}'''

c = s.count(old)
if c != 1:
    raise SystemExit(f"ABORTADO (LinhaEvolucao): esperava 1 ocorrencia, encontrei {c}.")
s = s.replace(old, new, 1)

# Ajusta as duas chamadas existentes pra passar unidade/rotulo certos
old_call1 = "            <LinhaEvolucao pontos={serieFiltrada} cor={p.cor}/>"
new_call1 = "            <LinhaEvolucao pontos={serieFiltrada} cor={p.cor} unidade=\"kg\" rotulo=\"Peso atual\"/>"
c1 = s.count(old_call1)
if c1 != 1:
    raise SystemExit(f"ABORTADO (call-adulto): esperava 1 ocorrencia, encontrei {c1}.")
s = s.replace(old_call1, new_call1, 1)

old_call2 = "          <LinhaEvolucao pontos={serieCresc} cor={cor}/>"
new_call2 = "          <LinhaEvolucao pontos={serieCresc} cor={cor} unidade={cresModo==='peso'?'kg':'cm'} rotulo={cresModo==='peso'?'Peso atual':'Altura atual'}/>"
c2 = s.count(old_call2)
if c2 != 1:
    raise SystemExit(f"ABORTADO (call-crianca): esperava 1 ocorrencia, encontrei {c2}.")
s = s.replace(old_call2, new_call2, 1)

p.write_text(s)
print("OK: LinhaEvolucao com eixo Y, valor atual e mais marcacoes no eixo X.")
