from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

applied = []

# ===========================================================================
# PARTE 1 - api/_cronlib.js: WhatsApp parava de avisar em silencio quando o
# envio falhava (ex: sessao do WhatsApp caida) - a Vercel achava que tinha
# dado tudo certo. Agora ela checa de verdade se o envio funcionou.
# Tambem: medicamento com data de validade vencida sai sozinho do contexto
# da Luna (sem precisar apagar na mao).
# ===========================================================================

cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (_cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_send = """export async function sendWhatsappText(number, text) {
  const { baseUrl, apiKey, instance } = getEvoConfig()
  if (!baseUrl || !apiKey) throw new Error('Evolution API nao configurada.')
  await fetch(`${baseUrl}/message/sendText/${instance}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', apikey: apiKey },
    body: JSON.stringify({ number, text })
  })
}"""
new_send = """export async function sendWhatsappText(number, text) {
  const { baseUrl, apiKey, instance } = getEvoConfig()
  if (!baseUrl || !apiKey) throw new Error('Evolution API nao configurada.')
  const resp = await fetch(`${baseUrl}/message/sendText/${instance}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', apikey: apiKey },
    body: JSON.stringify({ number, text })
  })
  if (!resp.ok) {
    const corpo = await resp.text().catch(() => '')
    throw new Error(`Falha ao enviar WhatsApp (status ${resp.status}): ${corpo.slice(0, 300)}`)
  }
}"""
c = replace_once(c, old_send, new_send, "sendWhatsappText-checa-falha")
applied.append("sendWhatsappText-checa-falha")

old_meds = """    medicamentos: (() => {
      const bruto = d.dos_medicamentos || {}
      const comDias = {}
      Object.keys(bruto).forEach((kid) => {
        comDias[kid] = (bruto[kid] || []).map((m) => ({ ...m, dias_desde_registro: diasDesdeRegistroBR(m.data) }))
      })
      return comDias
    })(),"""
new_meds = """    medicamentos: (() => {
      const bruto = d.dos_medicamentos || {}
      const comDias = {}
      Object.keys(bruto).forEach((kid) => {
        comDias[kid] = (bruto[kid] || [])
          .filter((m) => !m.ate || m.ate >= hojeIso)
          .map((m) => ({ ...m, dias_desde_registro: diasDesdeRegistroBR(m.data) }))
      })
      return comDias
    })(),"""
c = replace_once(c, old_meds, new_meds, "cronlib-medicamentos-filtra-validade")
applied.append("cronlib-medicamentos-filtra-validade")

cronlib_file.write_text(c)

# ===========================================================================
# PARTE 2 - api/whatsapp-webhook.js: se algo desse errado ao responder no
# WhatsApp (ex: erro da IA, erro de rede), o erro sumia sem deixar rastro
# nenhum nos logs da Vercel. Agora pelo menos fica registrado.
# ===========================================================================

webhook_file = Path("api/whatsapp-webhook.js")
if not webhook_file.exists():
    raise SystemExit("ABORTADO (webhook-nao-encontrado): rode este script na raiz do projeto denise-os.")
w = webhook_file.read_text()

old_catch = """  } catch {
    res.status(200).json({ ok: true })
  }
}"""
new_catch = """  } catch (err) {
    console.error('Erro no webhook do WhatsApp:', err)
    res.status(200).json({ ok: true })
  }
}"""
w = replace_once(w, old_catch, new_catch, "webhook-loga-erro")
applied.append("webhook-loga-erro")
webhook_file.write_text(w)

# ===========================================================================
# PARTE 3 - src/main.tsx: campo novo "Repetir ate" (opcional) no cadastro de
# medicamento. Remedios de tratamento curto (tipo antibiotico) agora podem
# ter uma data final - depois dela, o medicamento some sozinho do resumo da
# Luna, sem precisar apagar na mao. Se deixar em branco, continua igual a
# hoje (considerado em curso ate voce apagar).
# ===========================================================================

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_state = "  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:''})\n"
new_state = "  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''})\n"
s = replace_once(s, old_state, new_state, "novoMed-state-com-ate")
applied.append("novoMed-state-com-ate")

old_add = """  function addMedicamento(kid:string){
    if(!novoMed.nome||!novoMed.dosagem)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),nome:novoMed.nome,dosagem:novoMed.dosagem,frequencia:novoMed.frequencia,horarios:novoMed.horarios}
    const n={...medicamentos,[kid]:[reg,...(medicamentos[kid]||[])]}
    setMedicamentos(n);localStorage.setItem('dos_medicamentos',JSON.stringify(n))
    setNovoMed({nome:'',dosagem:'',frequencia:'',horarios:''});setSavedMed(true)
  }"""
new_add = """  function addMedicamento(kid:string){
    if(!novoMed.nome||!novoMed.dosagem)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),nome:novoMed.nome,dosagem:novoMed.dosagem,frequencia:novoMed.frequencia,horarios:novoMed.horarios,ate:novoMed.ate}
    const n={...medicamentos,[kid]:[reg,...(medicamentos[kid]||[])]}
    setMedicamentos(n);localStorage.setItem('dos_medicamentos',JSON.stringify(n))
    setNovoMed({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''});setSavedMed(true)
  }"""
s = replace_once(s, old_add, new_add, "addMedicamento-grava-ate")
applied.append("addMedicamento-grava-ate")

CAMPO_ATE = "\n            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Repetir até (opcional)</label><input type=\"date\" value={novoMed.ate} onChange={e=>setNovoMed(p=>({...p,ate:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>"

# --- Bloco Denise ---
old_denise = """          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Medicamento</label><input value={novoMed.nome} onChange={e=>setNovoMed(p=>({...p,nome:e.target.value}))} placeholder="Ex: Losartana" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Dosagem</label><input value={novoMed.dosagem} onChange={e=>setNovoMed(p=>({...p,dosagem:e.target.value}))} placeholder="Ex: 50mg" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Frequência</label><input value={novoMed.frequencia} onChange={e=>setNovoMed(p=>({...p,frequencia:e.target.value}))} placeholder="Ex: 1x ao dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Horários</label><input value={novoMed.horarios} onChange={e=>setNovoMed(p=>({...p,horarios:e.target.value}))} placeholder="Ex: 08:00" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
          </div>
          <p style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginBottom:10}}>Preenchendo os horários, o medicamento aparece todo dia na Agenda automaticamente.</p>
          <button onClick={()=>addMedicamento('denise')} style={{width:'100%',background:`linear-gradient(135deg,${C.acc2},#6d28d9)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar medicamento</button>"""
new_denise = old_denise.replace(
    '</div>\n          <p style={{fontSize:10.5',
    CAMPO_ATE + "\n          </div>\n          <p style={{fontSize:10.5",
    1
)
s = replace_once(s, old_denise, new_denise, "medicamentos-denise-campo-ate")
applied.append("medicamentos-denise-campo-ate")

old_denise_row = "              <div><span style={{fontWeight:700,fontSize:13,color:C.acc2}}>{m.nome}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)',marginLeft:8}}>{m.dosagem}{m.frequencia?` - ${m.frequencia}`:''}{m.horarios?` - ${m.horarios}`:''}</span></div>\n              <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{m.data}</span><button onClick={()=>delMedicamento('denise',i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></div>"
new_denise_row = old_denise_row.replace(
    "{m.horarios?` - ${m.horarios}`:''}</span></div>",
    "{m.horarios?` - ${m.horarios}`:''}{m.ate?` · até ${m.ate.slice(8,10)}/${m.ate.slice(5,7)}`:''}</span></div>",
    1
)
s = replace_once(s, old_denise_row, new_denise_row, "medicamentos-denise-mostra-ate")
applied.append("medicamentos-denise-mostra-ate")

# --- Bloco Flavio ---
old_flavio = """          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:10}}>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Medicamento</label><input value={novoMed.nome} onChange={e=>setNovoMed(p=>({...p,nome:e.target.value}))} placeholder="Ex: Losartana" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Dosagem</label><input value={novoMed.dosagem} onChange={e=>setNovoMed(p=>({...p,dosagem:e.target.value}))} placeholder="Ex: 50mg" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Frequência</label><input value={novoMed.frequencia} onChange={e=>setNovoMed(p=>({...p,frequencia:e.target.value}))} placeholder="Ex: 1x ao dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
            <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Horários</label><input value={novoMed.horarios} onChange={e=>setNovoMed(p=>({...p,horarios:e.target.value}))} placeholder="Ex: 08:00" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
          </div>
          <p style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginBottom:10}}>Preenchendo os horários, o medicamento aparece todo dia na Agenda automaticamente.</p>
          <button onClick={()=>addMedicamento('flavio')} style={{width:'100%',background:`linear-gradient(135deg,${C.water},#0369a1)`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar medicamento</button>"""
new_flavio = old_flavio.replace(
    '</div>\n          <p style={{fontSize:10.5',
    CAMPO_ATE + "\n          </div>\n          <p style={{fontSize:10.5",
    1
)
s = replace_once(s, old_flavio, new_flavio, "medicamentos-flavio-campo-ate")
applied.append("medicamentos-flavio-campo-ate")

old_flavio_row = "              <div><span style={{fontWeight:700,fontSize:13,color:C.water}}>{m.nome}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)',marginLeft:8}}>{m.dosagem}{m.frequencia?` - ${m.frequencia}`:''}{m.horarios?` - ${m.horarios}`:''}</span></div>\n              <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{m.data}</span><button onClick={()=>delMedicamento('flavio',i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></div>"
new_flavio_row = old_flavio_row.replace(
    "{m.horarios?` - ${m.horarios}`:''}</span></div>",
    "{m.horarios?` - ${m.horarios}`:''}{m.ate?` · até ${m.ate.slice(8,10)}/${m.ate.slice(5,7)}`:''}</span></div>",
    1
)
s = replace_once(s, old_flavio_row, new_flavio_row, "medicamentos-flavio-mostra-ate")
applied.append("medicamentos-flavio-mostra-ate")

# --- Bloco Domi/Derick (compartilhado) ---
old_kids = """              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr 1fr',gap:8,marginBottom:10}}>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Medicamento</label><input value={novoMed.nome} onChange={e=>setNovoMed(p=>({...p,nome:e.target.value}))} placeholder="Ex: Amoxicilina" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Dosagem</label><input value={novoMed.dosagem} onChange={e=>setNovoMed(p=>({...p,dosagem:e.target.value}))} placeholder="Ex: 5ml" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Frequencia</label><input value={novoMed.frequencia} onChange={e=>setNovoMed(p=>({...p,frequencia:e.target.value}))} placeholder="Ex: 2x ao dia" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Horarios</label><input value={novoMed.horarios} onChange={e=>setNovoMed(p=>({...p,horarios:e.target.value}))} placeholder="Ex: 08:00, 20:00" style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13}}/></div>
              </div>
              <p style={{fontSize:10.5,color:'rgba(255,255,255,.35)',marginBottom:10}}>Preenchendo os horarios, o medicamento aparece todo dia na Agenda automaticamente.</p>
              <button onClick={()=>addMedicamento(kid)} style={{width:'100%',background:`linear-gradient(135deg,${cor},${kid==='domi'?'#9d174d':'#15803d'})`,color:'#fff',border:'none',borderRadius:10,padding:'11px',fontSize:13,fontWeight:700,cursor:'pointer'}}>+ Registrar medicamento</button>"""
new_kids = old_kids.replace(
    "gridTemplateColumns:'1fr 1fr 1fr 1fr'",
    "gridTemplateColumns:'repeat(5,1fr)'",
    1
).replace(
    '</div>\n              <p style={{fontSize:10.5',
    "\n                <div><label style={{fontSize:11,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>Repetir até (opcional)</label><input type=\"date\" value={novoMed.ate} onChange={e=>setNovoMed(p=>({...p,ate:e.target.value}))} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 10px',color:'#fff',fontSize:13,colorScheme:'dark'}}/></div>"
    + "\n              </div>\n              <p style={{fontSize:10.5",
    1
)
s = replace_once(s, old_kids, new_kids, "medicamentos-kids-campo-ate")
applied.append("medicamentos-kids-campo-ate")

old_kids_row = "                  <div><span style={{fontWeight:700,fontSize:13,color:cor}}>{m.nome}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)',marginLeft:8}}>{m.dosagem}{m.frequencia?` - ${m.frequencia}`:''}{m.horarios?` - ${m.horarios}`:''}</span></div>\n                  <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{m.data}</span><button onClick={()=>delMedicamento(kid,i)} style={{background:'rgba(248,113,113,.15)',border:'none',color:C.danger,borderRadius:6,padding:'2px 7px',fontSize:11,cursor:'pointer'}}>&times;</button></div>"
new_kids_row = old_kids_row.replace(
    "{m.horarios?` - ${m.horarios}`:''}</span></div>",
    "{m.horarios?` - ${m.horarios}`:''}{m.ate?` · até ${m.ate.slice(8,10)}/${m.ate.slice(5,7)}`:''}</span></div>",
    1
)
s = replace_once(s, old_kids_row, new_kids_row, "medicamentos-kids-mostra-ate")
applied.append("medicamentos-kids-mostra-ate")

main_file.write_text(s)

print("TUDO OK:", applied)
print("")
print("Resumo:")
print(" - api/_cronlib.js: envio de WhatsApp agora verifica se realmente funcionou (erros de")
print("   conexao/instancia caida deixam de ser engolidos em silencio).")
print(" - api/whatsapp-webhook.js: erros no webhook agora ficam registrados nos logs da Vercel.")
print(" - Medicamentos (Denise, Flávio, Domi, Derick): novo campo opcional 'Repetir até'.")
print("   Preenchendo, o remedio some sozinho da Luna depois dessa data - nao precisa mais")
print("   apagar na mao quando o tratamento (tipo antibiotico) terminar.")
print("")
print("IMPORTANTE sobre o remedio da Domi que ja esta cadastrado: como ele foi criado antes")
print("desse campo existir, ele nao tem data de repeticao (vai continuar aparecendo todo dia,")
print("igual hoje). Se quiser que ele pare sozinho em 20/08, precisa apagar o registro atual")
print("(no x) e cadastrar de novo com 'Repetir até' = 20/08/2026.")
