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

# --- Card de Consultas + Medicamentos para Denise ---
old_denise = """          <span>{medD[medD.length-1].data}: {medD[medD.length-1].cintura}cm</span><span>atual: {medD[0].cintura}cm</span>
        </div>
      </Card>
    </div>}

    {aba==='flavio'&&<div>"""
new_denise = """          <span>{medD[medD.length-1].data}: {medD[medD.length-1].cintura}cm</span><span>atual: {medD[0].cintura}cm</span>
        </div>
      </Card>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginTop:16}}>
        <Card title="Consultas — Denise">
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Tipo</label>
            <select value={novaConsulta.tipo} onChange={e=>setNovaConsulta(p=>({...p,tipo:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}>
              <option value="">Selecionar</option><option>Clínico Geral</option><option>Ginecologia</option><option>Dentista</option><option>Nutrição</option><option>Exame</option><option>Outro</option>
            </select></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novaConsulta.data} onChange={e=>setNovaConsulta(p=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
          </div>
          <input value={novaConsulta.obs} onChange={e=>setNovaConsulta(p=>({...p,obs:e.target.value}))} placeholder="Observações / diagnóstico" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:8}}/>
          <input value={novaConsulta.proximo} onChange={e=>setNovaConsulta(p=>({...p,proximo:e.target.value}))} placeholder="Próxima consulta" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
          <button onClick={()=>addConsulta('denise')} style={{width:'100%',background:`linear-gradient(135deg,${C.acc2},#6d28d9)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar consulta</button>
          {(consuls.denise||[]).length>0&&<div style={{marginTop:12}}>
            {(consuls.denise||[]).map((c,i)=>(<div key={i} style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
              <div style={{display:'flex',justifyContent:'space-between' as const,marginBottom:3}}><span style={{fontWeight:700,fontSize:13,color:C.acc2}}>{c.tipo}</span><span style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'flex',alignItems:'center',gap:8}}>{c.data}<button onClick={()=>delConsulta('denise',i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></span></div>
              {c.obs&&<div style={{fontSize:12,color:'rgba(255,255,255,.6)'}}>{c.obs}</div>}
              {c.proximo&&<div style={{fontSize:11,color:C.warn,marginTop:3}}>📅 Próxima: {c.proximo}</div>}
            </div>))}
          </div>}
          {(consuls.denise||[]).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma consulta registrada.</div>}
        </Card>
        <Card title="Medicamentos — Denise">
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Medicamento</label><input value={novoMed.nome} onChange={e=>setNovoMed(p=>({...p,nome:e.target.value}))} placeholder="Ex: Losartana" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Dosagem</label><input value={novoMed.dosagem} onChange={e=>setNovoMed(p=>({...p,dosagem:e.target.value}))} placeholder="Ex: 50mg" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Frequência</label><input value={novoMed.frequencia} onChange={e=>setNovoMed(p=>({...p,frequencia:e.target.value}))} placeholder="Ex: 1x ao dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Horários</label><input value={novoMed.horarios} onChange={e=>setNovoMed(p=>({...p,horarios:e.target.value}))} placeholder="Ex: 08:00" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
          </div>
          <p style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginBottom:10}}>Preenchendo os horários, o medicamento aparece todo dia na Agenda automaticamente.</p>
          <button onClick={()=>addMedicamento('denise')} style={{width:'100%',background:`linear-gradient(135deg,${C.acc2},#6d28d9)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar medicamento</button>
          {(medicamentos.denise||[]).length>0&&<div style={{marginTop:12}}>
            {(medicamentos.denise||[]).map((m:any,i:number)=>(<div key={i} style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
              <div><span style={{fontWeight:700,fontSize:13,color:C.acc2}}>{m.nome}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)',marginLeft:8}}>{m.dosagem}{m.frequencia?` - ${m.frequencia}`:''}{m.horarios?` - ${m.horarios}`:''}</span></div>
              <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{m.data}</span><button onClick={()=>delMedicamento('denise',i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></div>
            </div>))}
          </div>}
          {(medicamentos.denise||[]).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum medicamento registrado.</div>}
        </Card>
      </div>
    </div>}

    {aba==='flavio'&&<div>"""
s = replace_once(s, old_denise, new_denise, "saude-consultas-med-denise")

# --- Card de Consultas + Medicamentos para Flavio ---
old_flavio = """          <span>{medF[medF.length-1].data}: {medF[medF.length-1].cintura}cm</span><span>atual: {medF[0].cintura}cm</span>
        </div>
      </Card>
    </div>}

    {(aba==='domi'||aba==='derick')&&<div>"""
new_flavio = """          <span>{medF[medF.length-1].data}: {medF[medF.length-1].cintura}cm</span><span>atual: {medF[0].cintura}cm</span>
        </div>
      </Card>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginTop:16}}>
        <Card title="Consultas — Flávio">
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Tipo</label>
            <select value={novaConsulta.tipo} onChange={e=>setNovaConsulta(p=>({...p,tipo:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}>
              <option value="">Selecionar</option><option>Clínico Geral</option><option>Urologia</option><option>Dentista</option><option>Nutrição</option><option>Exame</option><option>Outro</option>
            </select></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Data</label><input type="date" value={novaConsulta.data} onChange={e=>setNovaConsulta(p=>({...p,data:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>
          </div>
          <input value={novaConsulta.obs} onChange={e=>setNovaConsulta(p=>({...p,obs:e.target.value}))} placeholder="Observações / diagnóstico" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:8}}/>
          <input value={novaConsulta.proximo} onChange={e=>setNovaConsulta(p=>({...p,proximo:e.target.value}))} placeholder="Próxima consulta" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,marginBottom:10}}/>
          <button onClick={()=>addConsulta('flavio')} style={{width:'100%',background:`linear-gradient(135deg,${C.water},#0369a1)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar consulta</button>
          {(consuls.flavio||[]).length>0&&<div style={{marginTop:12}}>
            {(consuls.flavio||[]).map((c,i)=>(<div key={i} style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
              <div style={{display:'flex',justifyContent:'space-between' as const,marginBottom:3}}><span style={{fontWeight:700,fontSize:13,color:C.water}}>{c.tipo}</span><span style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'flex',alignItems:'center',gap:8}}>{c.data}<button onClick={()=>delConsulta('flavio',i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></span></div>
              {c.obs&&<div style={{fontSize:12,color:'rgba(255,255,255,.6)'}}>{c.obs}</div>}
              {c.proximo&&<div style={{fontSize:11,color:C.warn,marginTop:3}}>📅 Próxima: {c.proximo}</div>}
            </div>))}
          </div>}
          {(consuls.flavio||[]).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhuma consulta registrada.</div>}
        </Card>
        <Card title="Medicamentos — Flávio">
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Medicamento</label><input value={novoMed.nome} onChange={e=>setNovoMed(p=>({...p,nome:e.target.value}))} placeholder="Ex: Losartana" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Dosagem</label><input value={novoMed.dosagem} onChange={e=>setNovoMed(p=>({...p,dosagem:e.target.value}))} placeholder="Ex: 50mg" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Frequência</label><input value={novoMed.frequencia} onChange={e=>setNovoMed(p=>({...p,frequencia:e.target.value}))} placeholder="Ex: 1x ao dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Horários</label><input value={novoMed.horarios} onChange={e=>setNovoMed(p=>({...p,horarios:e.target.value}))} placeholder="Ex: 08:00" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
          </div>
          <p style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginBottom:10}}>Preenchendo os horários, o medicamento aparece todo dia na Agenda automaticamente.</p>
          <button onClick={()=>addMedicamento('flavio')} style={{width:'100%',background:`linear-gradient(135deg,${C.water},#0369a1)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar medicamento</button>
          {(medicamentos.flavio||[]).length>0&&<div style={{marginTop:12}}>
            {(medicamentos.flavio||[]).map((m:any,i:number)=>(<div key={i} style={{display:'flex',justifyContent:'space-between' as const,alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
              <div><span style={{fontWeight:700,fontSize:13,color:C.water}}>{m.nome}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)',marginLeft:8}}>{m.dosagem}{m.frequencia?` - ${m.frequencia}`:''}{m.horarios?` - ${m.horarios}`:''}</span></div>
              <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{m.data}</span><button onClick={()=>delMedicamento('flavio',i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></div>
            </div>))}
          </div>}
          {(medicamentos.flavio||[]).length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'20px 0',textAlign:'center' as const}}>Nenhum medicamento registrado.</div>}
        </Card>
      </div>
    </div>}

    {(aba==='domi'||aba==='derick')&&<div>"""
s = replace_once(s, old_flavio, new_flavio, "saude-consultas-med-flavio")

main_file.write_text(s)
print("OK - cards de Consultas e Medicamentos adicionados nas abas Denise e Flavio da tela Saude.")
print("Usam as mesmas funcoes/dados que ja existiam para Domi/Derick (nada duplicado, so a tela nova).")
