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

# 1) eventosFam precisa de setter pra card atualizar sozinho depois de adicionar um
#    compromisso (antes so tinha getter, o valor nunca mudava depois do primeiro load).
old1 = "  const [eventosFam]=React.useState<any[]>(()=>lerEventosAgenda())"
new1 = '''  const [eventosFam,setEventosFam]=React.useState<any[]>(()=>lerEventosAgenda())
  const [showNovoComp,setShowNovoComp]=React.useState(false)
  const [novoCompNome,setNovoCompNome]=React.useState('')
  const [novoCompData,setNovoCompData]=React.useState(isoBR(new Date()))
  const [novoCompHora,setNovoCompHora]=React.useState('')
  const [novoCompPessoa,setNovoCompPessoa]=React.useState<'geral'|'domi'|'derick'>('geral')
  async function salvarNovoCompromisso(){
    if(!novoCompNome||!novoCompData)return
    await criarEventoAgenda({nome:novoCompNome,data:novoCompData,hora:novoCompHora,categoria:'familia',pessoa:novoCompPessoa==='geral'?undefined:novoCompPessoa})
    setEventosFam(lerEventosAgenda())
    setNovoCompNome('');setNovoCompHora('');setNovoCompPessoa('geral');setShowNovoComp(false)
  }'''
s = replace_once(s, old1, new1, "eventosFam-setter-e-form-novo-compromisso")

# 2) Botao "+ Novo compromisso" no card, com um formulario compacto que some depois de
#    salvar. Usa a mesma criarEventoAgenda que ja sincroniza com o Google Calendar,
#    categoria "familia" (que ja existia no dropdown da Agenda, so faltava um atalho
#    direto aqui na tela Familia).
old2 = '''    <Card title="📅 Próximos compromissos da família">
      {compromissosFamilia.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum compromisso de família nos próximos dias.</div>}
      {compromissosFamilia.map((e:any,i:number)=>(<div key={i} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:i<compromissosFamilia.length-1?`1px solid ${C.line}`:'none',alignItems:'center'}}>
        <span style={{width:80,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.data}{e.hora?` · ${e.hora}`:''}</span>
        <span style={{width:4,height:20,borderRadius:2,background:e.cor,flexShrink:0}}/>
        <span style={{fontSize:13.5,flex:1}}>{e.nome}</span>
        {e.pessoa&&<span style={{fontSize:11,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.pessoa==='domi'?'Domi':'Derick'}</span>}
      </div>))}
    </Card>'''
new2 = '''    <Card title="📅 Próximos compromissos da família" action={<button onClick={()=>setShowNovoComp(v=>!v)} style={{fontSize:12,color:C.acc2,background:'rgba(139,92,246,.1)',border:'1px solid rgba(139,92,246,.2)',padding:'5px 10px',borderRadius:9,cursor:'pointer',fontWeight:600}}>{showNovoComp?'✕ Cancelar':'+ Novo compromisso'}</button>}>
      {showNovoComp&&<div style={{display:'grid',gridTemplateColumns:'1.6fr .9fr .7fr .9fr auto',gap:8,marginBottom:14,alignItems:'end'}}>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Nome</label><input value={novoCompNome} onChange={e=>setNovoCompNome(e.target.value)} placeholder="Ex: Reunião escolar" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novoCompData} onChange={e=>setNovoCompData(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Hora</label><input type="time" value={novoCompHora} onChange={e=>setNovoCompHora(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}/></div>
        <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Quem</label><select value={novoCompPessoa} onChange={e=>setNovoCompPessoa(e.target.value as 'geral'|'domi'|'derick')} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark' as const}}><option value="geral">Família toda</option><option value="domi">Domi</option><option value="derick">Derick</option></select></div>
        <button onClick={salvarNovoCompromisso} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 14px',fontSize:13,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>+ Adicionar</button>
      </div>}
      {compromissosFamilia.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'10px 0'}}>Nenhum compromisso de família nos próximos dias.</div>}
      {compromissosFamilia.map((e:any,i:number)=>(<div key={i} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:i<compromissosFamilia.length-1?`1px solid ${C.line}`:'none',alignItems:'center'}}>
        <span style={{width:80,fontSize:12,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.data}{e.hora?` · ${e.hora}`:''}</span>
        <span style={{width:4,height:20,borderRadius:2,background:e.cor,flexShrink:0}}/>
        <span style={{fontSize:13.5,flex:1}}>{e.nome}</span>
        {e.pessoa&&<span style={{fontSize:11,color:'rgba(255,255,255,.4)',flexShrink:0}}>{e.pessoa==='domi'?'Domi':'Derick'}</span>}
      </div>))}
      <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:8}}>Compromissos também podem ser criados direto na Agenda, com categoria "Família".</div>
    </Card>'''
s = replace_once(s, old2, new2, "botao-novo-compromisso-familia")

p.write_text(s)
print("TUDO OK:", applied)
