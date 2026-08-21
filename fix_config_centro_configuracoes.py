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

old = """function Config(){
  const [notif,setNotif]=React.useState(()=>{try{return JSON.parse(localStorage.getItem('dos_cfg_notif')||'true')}catch{return true}})
  const [resumo,setResumo]=React.useState(()=>{try{return JSON.parse(localStorage.getItem('dos_cfg_resumo')||'true')}catch{return true}})
  const [fuso,setFuso]=React.useState(()=>localStorage.getItem('dos_cfg_fuso')||'America/Sao_Paulo')
  const [formatoData,setFormatoData]=React.useState(()=>localStorage.getItem('dos_cfg_formato')||'dd/MM/yyyy')
  const [saved,setSaved]=React.useState(false);
  const [waState,setWaState]=React.useState<'carregando'|'nao_criada'|'close'|'connecting'|'open'|'erro'>('carregando')
  const [waQr,setWaQr]=React.useState<string|null>(null)
  const [waPairingCode,setWaPairingCode]=React.useState<string|null>(null)
  const [waLoading,setWaLoading]=React.useState(false)
  const [waErro,setWaErro]=React.useState<string|null>(null)
  async function verificarStatusWhatsapp(){
    try{
      const resp=await fetch('/api/whatsapp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'status'})})
      const data=await resp.json()
      if(!resp.ok){setWaState('erro');setWaErro(data?.error||'Erro ao verificar status.');return}
      setWaState(data.state||'nao_criada')
      if(data.state==='open'){setWaQr(null);setWaPairingCode(null)}
    }catch{setWaState('erro');setWaErro('Não consegui falar com o servidor.')}
  }
  React.useEffect(()=>{verificarStatusWhatsapp()},[])
  React.useEffect(()=>{
    if(waState!=='connecting')return
    const t=setInterval(verificarStatusWhatsapp,4000)
    return()=>clearInterval(t)
  },[waState])
  async function conectarWhatsapp(){
    setWaLoading(true)
    setWaErro(null)
    try{
      const resp=await fetch('/api/whatsapp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'connect'})})
      const data=await resp.json()
      if(!resp.ok)throw new Error(data?.error||'Erro ao conectar.')
      setWaQr(data.base64||null)
      setWaPairingCode(data.pairingCode||null)
      setWaState('connecting')
    }catch(err:any){setWaErro(err?.message||'Erro ao conectar.')}
    setWaLoading(false)
  }
  function salvarConfig(){
    localStorage.setItem('dos_cfg_notif',JSON.stringify(notif))
    localStorage.setItem('dos_cfg_resumo',JSON.stringify(resumo))
    localStorage.setItem('dos_cfg_fuso',fuso)
    localStorage.setItem('dos_cfg_formato',formatoData)
    setSaved(true)
  }
  function exportarDados(){
    const dados:Record<string,any>={}
    for(let i=0;i<localStorage.length;i++){
      const k=localStorage.key(i)
      if(!k)continue
      try{dados[k]=JSON.parse(localStorage.getItem(k)||'null')}catch{dados[k]=localStorage.getItem(k)}
    }
    const blob=new Blob([JSON.stringify(dados,null,2)],{type:'application/json'})
    const url=URL.createObjectURL(blob)
    const a=document.createElement('a')
    a.href=url
    a.download=`denise-os-dados-${isoBR(new Date())}.json`
    document.body.appendChild(a);a.click();document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
const Toggle=({on,toggle}:{on:boolean,toggle:()=>void})=>(<div onClick={toggle} style={{width:44,height:25,borderRadius:20,background:on?C.acc:'rgba(255,255,255,.1)',position:'relative' as const,cursor:'pointer',transition:'.2s',flexShrink:0}}><div style={{position:'absolute' as const,top:2,left:on?21:2,width:21,height:21,borderRadius:'50%',background:'#fff',transition:'.2s'}}/></div>);return(<div style={{padding:'24px 28px'}}><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Configurações</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Perfil, notificações, IA e segurança</p>{saved&&<div style={{background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',borderRadius:10,padding:'10px 16px',fontSize:13,color:C.ok,marginBottom:16}}>✓ Configurações salvas!</div>}<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}><Card title="Perfil"><div style={{display:'flex',alignItems:'center',gap:14,marginBottom:16}}><Avatar id="denise" label="D" size={56} radius={14}/><div><div style={{fontWeight:700,fontSize:15}}>Denise</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)'}}>Toque na foto para alterar</div></div></div><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Fuso horário</label><input value={fuso} onChange={e=>setFuso(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14,marginBottom:12}}/><label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Formato de data</label><input value={formatoData} onChange={e=>setFormatoData(e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'10px 12px',color:'#fff',fontSize:14}}/></Card><Card title="Notificações">{[['Lembretes no app',notif,()=>setNotif((v:boolean)=>!v)],['Resumo diário',resumo,()=>setResumo((v:boolean)=>!v)]].map(([l,v,fn])=>(<div key={String(l)} style={{display:'flex',alignItems:'center',justifyContent:'space-between' as const,padding:'12px 0',borderBottom:`1px solid ${C.line}`}}><span style={{fontSize:13}}>{String(l)}</span><Toggle on={Boolean(v)} toggle={fn as ()=>void}/></div>))}</Card><Card title="Dados"><div style={{padding:'12px 0',borderBottom:`1px solid ${C.line}`}}><div style={{fontSize:13,fontWeight:600,marginBottom:8}}>Exportar meus dados (LGPD)</div><button onClick={exportarDados} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer'}}>Exportar</button></div><div style={{padding:'12px 0'}}><div style={{fontSize:13,fontWeight:600,color:C.danger,marginBottom:8}}>Limpar dados locais</div><button onClick={()=>{localStorage.clear();window.location.reload()}} style={{background:'rgba(248,113,113,.15)',border:'1px solid rgba(248,113,113,.3)',color:C.danger,borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer'}}>Limpar</button></div></Card><Card title="WhatsApp (Luna)"><p style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:14}}>Conecte seu WhatsApp para conversar com a Luna por lá também — o QR Code aparece aqui, sem sair do app.</p>{waState==='carregando'&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Verificando conexão...</div>}{waState==='open'&&<div style={{display:'flex',alignItems:'center',gap:10}}><span style={{width:10,height:10,borderRadius:'50%',background:C.ok,flexShrink:0}}/><span style={{fontSize:13,color:C.ok,fontWeight:600}}>WhatsApp conectado</span></div>}{(waState==='close'||waState==='nao_criada'||waState==='erro')&&<div><div style={{display:'flex',alignItems:'center',gap:10,marginBottom:12}}><span style={{width:10,height:10,borderRadius:'50%',background:'rgba(255,255,255,.25)',flexShrink:0}}/><span style={{fontSize:13,color:'rgba(255,255,255,.5)'}}>WhatsApp não conectado</span></div><button onClick={conectarWhatsapp} disabled={waLoading} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'9px 16px',fontSize:12,fontWeight:700,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Gerando QR Code...':'Gerar QR Code'}</button></div>}{waState==='connecting'&&<div style={{display:'flex',flexDirection:'column' as const,alignItems:'center',gap:10}}>{waQr&&<img src={waQr.startsWith('data:')?waQr:`data:image/png;base64,${waQr}`} alt="QR Code do WhatsApp" style={{width:180,height:180,borderRadius:10,background:'#fff',padding:8}}/>}{waPairingCode&&<div style={{fontSize:13,color:'rgba(255,255,255,.7)'}}>Código: <strong>{waPairingCode}</strong></div>}<div style={{fontSize:12,color:'rgba(255,255,255,.4)',textAlign:'center' as const}}>Abra o WhatsApp {'>'} Aparelhos conectados {'>'} Conectar um aparelho e escaneie o QR Code.</div><button onClick={conectarWhatsapp} disabled={waLoading} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer'}}>Atualizar QR Code</button></div>}{waErro&&<div style={{marginTop:10,fontSize:12,color:C.danger}}>{waErro}</div>}</Card></div><button onClick={salvarConfig} style={{marginTop:20,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:11,padding:'13px 28px',fontSize:14,fontWeight:700,cursor:'pointer'}}>✓ Salvar configurações</button></div>)}"""
new = r'''function lerCfg(chave:string,padrao:string):string{try{return localStorage.getItem(chave)??padrao}catch{return padrao}}
function lerCfgBool(chave:string,padrao:boolean):boolean{try{const v=localStorage.getItem(chave);return v===null?padrao:JSON.parse(v)}catch{return padrao}}
function Config(){
  const navigate=useNavigate()
  const [nome,setNome]=React.useState(()=>lerCfg('dos_cfg_nome','Denise'))
  const [fuso,setFuso]=React.useState(()=>lerCfg('dos_cfg_fuso','America/Sao_Paulo'))
  const [formatoData,setFormatoData]=React.useState(()=>lerCfg('dos_cfg_formato','DD/MM/AAAA'))
  const [formatoHora,setFormatoHora]=React.useState(()=>lerCfg('dos_cfg_formato_hora','24h'))
  const [localNomeCfg,setLocalNomeCfg]=React.useState(()=>lerCfg('dos_local_nome',''))
  const [localAuto,setLocalAuto]=React.useState(()=>lerCfgBool('dos_cfg_local_auto',true))
  const [unidadePeso,setUnidadePeso]=React.useState(()=>lerCfg('dos_cfg_unidade_peso','kg'))
  const [unidadeAltura,setUnidadeAltura]=React.useState(()=>lerCfg('dos_cfg_unidade_altura','cm/m/km'))
  const [unidadeTemp,setUnidadeTemp]=React.useState(()=>lerCfg('dos_cfg_unidade_temp','C'))
  const [primeiroDiaSemana,setPrimeiroDiaSemana]=React.useState(()=>lerCfg('dos_cfg_primeiro_dia','segunda'))
  const [notif,setNotif]=React.useState(()=>lerCfgBool('dos_cfg_notif',true))
  const [notifWa,setNotifWa]=React.useState(()=>lerCfgBool('dos_cfg_notif_wa',true))
  const [notifImportantes,setNotifImportantes]=React.useState(()=>lerCfgBool('dos_cfg_notif_importantes',true))
  const [resumoManha,setResumoManha]=React.useState(()=>lerCfgBool('dos_cfg_resumo',true))
  const [resumoManhaHorario,setResumoManhaHorario]=React.useState(()=>lerCfg('dos_cfg_resumo_manha_horario','07:00'))
  const [resumoNoite,setResumoNoite]=React.useState(()=>lerCfgBool('dos_cfg_resumo_noite',true))
  const [resumoNoiteHorario,setResumoNoiteHorario]=React.useState(()=>lerCfg('dos_cfg_resumo_noite_horario','20:00'))
  const [resumoSemanal,setResumoSemanal]=React.useState(()=>lerCfgBool('dos_cfg_resumo_semanal',true))
  const [resumoSemanalDia,setResumoSemanalDia]=React.useState(()=>lerCfg('dos_cfg_resumo_semanal_dia','domingo'))
  const [resumoSemanalHorario,setResumoSemanalHorario]=React.useState(()=>lerCfg('dos_cfg_resumo_semanal_horario','19:00'))
  const [mostrarNotifModulo,setMostrarNotifModulo]=React.useState(false)
  const [lunaCanal,setLunaCanal]=React.useState(()=>lerCfg('dos_cfg_luna_canal','ambos'))
  const [lunaMemoria,setLunaMemoria]=React.useState(()=>lerCfgBool('dos_cfg_luna_memoria',true))
  const [mostrarPermissoesLuna,setMostrarPermissoesLuna]=React.useState(false)
  const [tema,setTema]=React.useState(()=>lerCfg('dos_cfg_tema','escuro'))
  const [densidade]=React.useState(()=>lerCfg('dos_cfg_densidade','confortavel'))
  const [statusSalvo,setStatusSalvo]=React.useState<'salvo'|'alterado'|'salvando'>('salvo')

  const [waState,setWaState]=React.useState<'carregando'|'nao_criada'|'close'|'connecting'|'open'|'erro'>('carregando')
  const [waQr,setWaQr]=React.useState<string|null>(null)
  const [waPairingCode,setWaPairingCode]=React.useState<string|null>(null)
  const [waLoading,setWaLoading]=React.useState(false)
  const [waErro,setWaErro]=React.useState<string|null>(null)
  async function verificarStatusWhatsapp(){
    try{
      const resp=await fetch('/api/whatsapp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'status'})})
      const data=await resp.json()
      if(!resp.ok){setWaState('erro');setWaErro(data?.error||'Erro ao verificar status.');return}
      setWaState(data.state||'nao_criada')
      if(data.state==='open'){setWaQr(null);setWaPairingCode(null)}
    }catch{setWaState('erro');setWaErro('Não consegui falar com o servidor.')}
  }
  React.useEffect(()=>{verificarStatusWhatsapp()},[])
  React.useEffect(()=>{
    if(waState!=='connecting')return
    const t=setInterval(verificarStatusWhatsapp,4000)
    return()=>clearInterval(t)
  },[waState])
  async function conectarWhatsapp(){
    setWaLoading(true)
    setWaErro(null)
    try{
      const resp=await fetch('/api/whatsapp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'connect'})})
      const data=await resp.json()
      if(!resp.ok)throw new Error(data?.error||'Erro ao conectar.')
      setWaQr(data.base64||null)
      setWaPairingCode(data.pairingCode||null)
      setWaState('connecting')
    }catch(err:any){setWaErro(err?.message||'Erro ao conectar.')}
    setWaLoading(false)
  }
  const googleConectadoCfg=(()=>{try{const tk=JSON.parse(localStorage.getItem('dos_google_token')||'null');return !!(tk&&tk.token)}catch{return false}})()
  const googleUltimaSyncCfg=(()=>{try{const cache=JSON.parse(localStorage.getItem('dos_google_events_cache')||'null');return Array.isArray(cache)&&cache.length>0}catch{return false}})()

  function marcarAlterado(){setStatusSalvo('alterado')}
  function salvarConfig(){
    setStatusSalvo('salvando')
    localStorage.setItem('dos_cfg_nome',nome)
    localStorage.setItem('dos_cfg_fuso',fuso)
    localStorage.setItem('dos_cfg_formato',formatoData)
    localStorage.setItem('dos_cfg_formato_hora',formatoHora)
    localStorage.setItem('dos_local_nome',localNomeCfg)
    localStorage.setItem('dos_cfg_local_auto',JSON.stringify(localAuto))
    localStorage.setItem('dos_cfg_unidade_peso',unidadePeso)
    localStorage.setItem('dos_cfg_unidade_altura',unidadeAltura)
    localStorage.setItem('dos_cfg_unidade_temp',unidadeTemp)
    localStorage.setItem('dos_cfg_primeiro_dia',primeiroDiaSemana)
    localStorage.setItem('dos_cfg_notif',JSON.stringify(notif))
    localStorage.setItem('dos_cfg_notif_wa',JSON.stringify(notifWa))
    localStorage.setItem('dos_cfg_notif_importantes',JSON.stringify(notifImportantes))
    localStorage.setItem('dos_cfg_resumo',JSON.stringify(resumoManha))
    localStorage.setItem('dos_cfg_resumo_manha_horario',resumoManhaHorario)
    localStorage.setItem('dos_cfg_resumo_noite',JSON.stringify(resumoNoite))
    localStorage.setItem('dos_cfg_resumo_noite_horario',resumoNoiteHorario)
    localStorage.setItem('dos_cfg_resumo_semanal',JSON.stringify(resumoSemanal))
    localStorage.setItem('dos_cfg_resumo_semanal_dia',resumoSemanalDia)
    localStorage.setItem('dos_cfg_resumo_semanal_horario',resumoSemanalHorario)
    localStorage.setItem('dos_cfg_luna_canal',lunaCanal)
    localStorage.setItem('dos_cfg_luna_memoria',JSON.stringify(lunaMemoria))
    localStorage.setItem('dos_cfg_tema',tema)
    localStorage.setItem('dos_cfg_densidade',densidade)
    setTimeout(()=>setStatusSalvo('salvo'),350)
  }
  function exportarDados(){
    const dados:Record<string,any>={}
    for(let i=0;i<localStorage.length;i++){
      const k=localStorage.key(i)
      if(!k)continue
      try{dados[k]=JSON.parse(localStorage.getItem(k)||'null')}catch{dados[k]=localStorage.getItem(k)}
    }
    const blob=new Blob([JSON.stringify(dados,null,2)],{type:'application/json'})
    const url=URL.createObjectURL(blob)
    const a=document.createElement('a')
    a.href=url
    a.download=`denise-os-dados-${isoBR(new Date())}.json`
    document.body.appendChild(a);a.click();document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  function baixarHistoricoCfg(){
    const CHAVES_HISTORICO=['dos_refs_log','dos_agua_log','dos_treinos','dos_leituras','dos_sessoes_leitura','dos_sessoes_estudo','dos_devocionais','dos_luna_conversas','dos_luna_chat']
    const dados:Record<string,any>={}
    CHAVES_HISTORICO.forEach(k=>{try{dados[k]=JSON.parse(localStorage.getItem(k)||'null')}catch{dados[k]=null}})
    const blob=new Blob([JSON.stringify(dados,null,2)],{type:'application/json'})
    const url=URL.createObjectURL(blob)
    const a=document.createElement('a')
    a.href=url
    a.download=`denise-os-historico-${isoBR(new Date())}.json`
    document.body.appendChild(a);a.click();document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }
  function limparDadosLocaisCfg(){
    if(!window.confirm('Remover cache e dados armazenados neste dispositivo? Isso não apaga os dados salvos no Supabase.'))return
    localStorage.clear()
    window.location.reload()
  }
  const Toggle=({on,toggle}:{on:boolean,toggle:()=>void})=>(<div onClick={toggle} style={{width:44,height:25,borderRadius:20,background:on?C.acc:'rgba(255,255,255,.1)',position:'relative' as const,cursor:'pointer',transition:'.2s',flexShrink:0}}><div style={{position:'absolute' as const,top:2,left:on?21:2,width:21,height:21,borderRadius:'50%',background:'#fff',transition:'.2s'}}/></div>)
  const CampoCfg=({label,children}:{label:string,children:React.ReactNode})=>(<div><label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>{label}</label>{children}</div>)
  const inputCfgStyle:React.CSSProperties={width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 11px',color:'#fff',fontSize:13.5,colorScheme:'dark' as const}
  const LinhaToggleCfg=({label,desc,on,toggle}:{label:string,desc?:string,on:boolean,toggle:()=>void})=>(<div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}><div style={{flex:1,minWidth:0}}><div style={{fontSize:13}}>{label}</div>{desc&&<div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:2}}>{desc}</div>}</div><Toggle on={on} toggle={toggle}/></div>)

  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:20,flexWrap:'wrap' as const}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Configurações</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Personalize sua experiência e gerencie suas preferências no Denise OS</p></div>
      <div style={{display:'flex',gap:10,alignItems:'center'}}>
        {statusSalvo==='salvo'&&<span style={{display:'inline-flex',alignItems:'center',gap:6,background:'rgba(52,211,153,.1)',border:'1px solid rgba(52,211,153,.3)',color:C.ok,borderRadius:9,padding:'8px 12px',fontSize:12}}>✓ Todas as alterações salvas</span>}
        {statusSalvo==='alterado'&&<span style={{display:'inline-flex',alignItems:'center',gap:6,background:'rgba(251,191,36,.1)',border:'1px solid rgba(251,191,36,.3)',color:C.warn,borderRadius:9,padding:'8px 12px',fontSize:12}}>Alterações não salvas</span>}
        {statusSalvo==='salvando'&&<span style={{display:'inline-flex',alignItems:'center',gap:6,color:'rgba(255,255,255,.5)',fontSize:12}}>Salvando...</span>}
        <button onClick={salvarConfig} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 18px',fontSize:13,fontWeight:700,cursor:'pointer'}}>Salvar alterações</button>
      </div>
    </div>

    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
      <Card title="Perfil">
        <div style={{display:'flex',alignItems:'center',gap:14,marginBottom:14}}>
          <Avatar id="denise" label={(nome||'D')[0]} size={56} radius={14}/>
          <div><div style={{fontWeight:700,fontSize:15}}>{nome||'Denise'}</div><div style={{fontSize:11.5,color:'rgba(255,255,255,.4)'}}>Toque na foto para alterar</div></div>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
          <CampoCfg label="Nome"><input value={nome} onChange={e=>{setNome(e.target.value);marcarAlterado()}} style={inputCfgStyle}/></CampoCfg>
          <CampoCfg label="Idioma"><select value="pt-BR" disabled style={{...inputCfgStyle,opacity:.7}}><option value="pt-BR">Português (Brasil)</option></select></CampoCfg>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
          <CampoCfg label="Fuso horário"><input value={fuso} onChange={e=>{setFuso(e.target.value);marcarAlterado()}} style={inputCfgStyle}/></CampoCfg>
          <CampoCfg label="Formato de data"><select value={formatoData} onChange={e=>{setFormatoData(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="DD/MM/AAAA">DD/MM/AAAA</option><option value="MM/DD/AAAA">MM/DD/AAAA</option><option value="AAAA-MM-DD">AAAA-MM-DD</option></select></CampoCfg>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
          <CampoCfg label="Formato de hora"><select value={formatoHora} onChange={e=>{setFormatoHora(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="24h">24 horas (14:30)</option><option value="12h">12 horas (2:30 PM)</option></select></CampoCfg>
          <CampoCfg label="Cidade / localização"><input value={localNomeCfg} onChange={e=>{setLocalNomeCfg(e.target.value);marcarAlterado()}} placeholder="Ex: Curitiba, PR" style={inputCfgStyle}/></CampoCfg>
        </div>
      </Card>

      <Card title="Preferências">
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:10}}>
          <CampoCfg label="Unidade de peso"><select value={unidadePeso} onChange={e=>{setUnidadePeso(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="kg">kg</option><option value="lb">lb</option></select></CampoCfg>
          <CampoCfg label="Altura / distância"><select value={unidadeAltura} onChange={e=>{setUnidadeAltura(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="cm/m/km">cm / m / km</option><option value="in/ft/mi">in / ft / mi</option></select></CampoCfg>
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
          <CampoCfg label="Primeiro dia da semana"><select value={primeiroDiaSemana} onChange={e=>{setPrimeiroDiaSemana(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="segunda">Segunda-feira</option><option value="domingo">Domingo</option></select></CampoCfg>
          <CampoCfg label="Temperatura"><select value={unidadeTemp} onChange={e=>{setUnidadeTemp(e.target.value);marcarAlterado()}} style={inputCfgStyle}><option value="C">°C</option><option value="F">°F</option></select></CampoCfg>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:10,marginBottom:6}}>
          <div><div style={{fontSize:13}}>Usar localização automática</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Permite que o sistema use sua localização atual</div></div>
          <Toggle on={localAuto} toggle={()=>{setLocalAuto(v=>!v);marcarAlterado()}}/>
        </div>
        <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginTop:6}}>A cidade acima é a mesma usada na Home e nas sugestões da Luna — uma única fonte de verdade.</p>
      </Card>

      <Card title="Notificações">
        <div style={{fontSize:11,color:'rgba(255,255,255,.35)',textTransform:'uppercase' as const,letterSpacing:'.5px',marginBottom:6}}>Notificações gerais</div>
        <LinhaToggleCfg label="Lembretes no app" on={notif} toggle={()=>{setNotif(v=>!v);marcarAlterado()}}/>
        <LinhaToggleCfg label="WhatsApp" on={notifWa} toggle={()=>{setNotifWa(v=>!v);marcarAlterado()}}/>
        <LinhaToggleCfg label="Notificações importantes" on={notifImportantes} toggle={()=>{setNotifImportantes(v=>!v);marcarAlterado()}}/>
        <div style={{fontSize:11,color:'rgba(255,255,255,.35)',textTransform:'uppercase' as const,letterSpacing:'.5px',margin:'14px 0 6px'}}>Resumos automáticos</div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
          <span style={{fontSize:13}}>☀️ Resumo da manhã</span>
          <div style={{display:'flex',alignItems:'center',gap:8}}>{resumoManha&&<input type="time" value={resumoManhaHorario} onChange={e=>{setResumoManhaHorario(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:90,padding:'5px 8px',fontSize:12}}/>}<Toggle on={resumoManha} toggle={()=>{setResumoManha(v=>!v);marcarAlterado()}}/></div>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 0',borderBottom:`1px solid ${C.line}`}}>
          <span style={{fontSize:13}}>🌙 Resumo da noite</span>
          <div style={{display:'flex',alignItems:'center',gap:8}}>{resumoNoite&&<input type="time" value={resumoNoiteHorario} onChange={e=>{setResumoNoiteHorario(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:90,padding:'5px 8px',fontSize:12}}/>}<Toggle on={resumoNoite} toggle={()=>{setResumoNoite(v=>!v);marcarAlterado()}}/></div>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'8px 0'}}>
          <span style={{fontSize:13}}>📅 Resumo semanal</span>
          <div style={{display:'flex',alignItems:'center',gap:8}}>{resumoSemanal&&<><select value={resumoSemanalDia} onChange={e=>{setResumoSemanalDia(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:110,padding:'5px 6px',fontSize:11.5}}>{['domingo','segunda','terça','quarta','quinta','sexta','sábado'].map(d=>(<option key={d} value={d}>{d[0].toUpperCase()+d.slice(1)}</option>))}</select><input type="time" value={resumoSemanalHorario} onChange={e=>{setResumoSemanalHorario(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:90,padding:'5px 8px',fontSize:12}}/></>}<Toggle on={resumoSemanal} toggle={()=>{setResumoSemanal(v=>!v);marcarAlterado()}}/></div>
        </div>
        <button onClick={()=>setMostrarNotifModulo(v=>!v)} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'10px 0 0'}}>{mostrarNotifModulo?'Ocultar notificações por módulo ▾':'Configurar notificações por módulo →'}</button>
        {mostrarNotifModulo&&<div style={{marginTop:8,padding:12,background:C.s2,borderRadius:10,fontSize:12,color:'rgba(255,255,255,.5)'}}>Ajuste fino por módulo (Agenda, Saúde, Alimentação, Exercícios, Família, Trabalho, Desenvolvimento, Casa, Espiritual) chega numa próxima etapa — hoje as notificações gerais acima já controlam o comportamento de todos os módulos.</div>}
      </Card>

      <Card title="Luna">
        <div style={{display:'flex',justifyContent:'space-between',padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{color:'rgba(255,255,255,.5)'}}>IA da Luna</span><span style={{color:C.ok,fontWeight:700}}>Ativa</span></div>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{color:'rgba(255,255,255,.5)'}}>Canal preferencial</span><select value={lunaCanal} onChange={e=>{setLunaCanal(e.target.value);marcarAlterado()}} style={{...inputCfgStyle,width:170}}><option value="app">App</option><option value="whatsapp">WhatsApp</option><option value="ambos">Ambos (App e WhatsApp)</option></select></div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:10,padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13}}>Memória contextual</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Permite que a Luna use contexto de conversas anteriores quando relevante</div></div>
          <Toggle on={lunaMemoria} toggle={()=>{setLunaMemoria(v=>!v);marcarAlterado()}}/>
        </div>
        <button onClick={()=>setMostrarPermissoesLuna(v=>!v)} style={{display:'block',width:'100%',textAlign:'left' as const,background:'transparent',border:'none',color:'rgba(255,255,255,.7)',fontSize:13,cursor:'pointer',padding:'10px 0'}}>Permissões de ação <span style={{color:'rgba(255,255,255,.35)',fontSize:11.5}}>· Defina quando a Luna pode agir automaticamente</span></button>
        {mostrarPermissoesLuna&&<div style={{padding:12,background:C.s2,borderRadius:10,fontSize:12,color:'rgba(255,255,255,.6)',marginBottom:8}}>
          <div style={{marginBottom:8}}><b style={{color:'#fff'}}>Ações simples</b> — a Luna pode executar direto: registrar água, marcar tarefa concluída, adicionar item no mercado.</div>
          <div><b style={{color:'#fff'}}>Ações importantes</b> — a Luna sempre pede confirmação antes: excluir, cancelar, remarcar, alterar protocolo, marcar conta como paga, alterar estoque.</div>
        </div>}
        <button onClick={()=>navigate('/assistente')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:0}}>Usar horários definidos em Notificações →</button>
      </Card>

      <Card title="Integrações">
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Google Calendar</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>{googleConectadoCfg?(googleUltimaSyncCfg?'Sincronizado':'Conectado'):'Não conectado'}</div></div>
          <div style={{display:'flex',alignItems:'center',gap:8}}><span style={{fontSize:11,fontWeight:700,color:googleConectadoCfg?C.ok:'rgba(255,255,255,.4)',background:googleConectadoCfg?'rgba(52,211,153,.12)':'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>{googleConectadoCfg?'Conectado':'Não conectado'}</span><button onClick={()=>navigate('/agenda')} style={{background:'none',border:'none',color:'rgba(255,255,255,.4)',cursor:'pointer',fontSize:13}}>›</button></div>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13,fontWeight:600}}>WhatsApp (Luna)</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>{waState==='open'?'Conectado':waState==='carregando'?'Verificando...':'Não conectado'}</div></div>
          <span style={{fontSize:11,fontWeight:700,color:waState==='open'?C.ok:'rgba(255,255,255,.4)',background:waState==='open'?'rgba(52,211,153,.12)':'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>{waState==='open'?'Conectado':waState==='carregando'?'Verificando':'Em breve'}</span>
        </div>
        {waState==='open'?null:(waState==='carregando'?null:<div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          {(waState==='close'||waState==='nao_criada'||waState==='erro')&&<button onClick={conectarWhatsapp} disabled={waLoading} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'8px 14px',fontSize:12,fontWeight:700,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Gerando QR Code...':'Gerar QR Code'}</button>}
          {waState==='connecting'&&<div style={{display:'flex',flexDirection:'column' as const,alignItems:'center',gap:8}}>{waQr&&<img src={waQr.startsWith('data:')?waQr:`data:image/png;base64,${waQr}`} alt="QR Code do WhatsApp" style={{width:140,height:140,borderRadius:10,background:'#fff',padding:6}}/>}{waPairingCode&&<div style={{fontSize:12,color:'rgba(255,255,255,.7)'}}>Código: <strong>{waPairingCode}</strong></div>}</div>}
          {waErro&&<div style={{fontSize:11.5,color:C.danger,marginTop:6}}>{waErro}</div>}
        </div>)}
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13,fontWeight:600,color:'rgba(255,255,255,.5)'}}>Apple Health</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Em breve</div></div>
          <span style={{fontSize:11,fontWeight:700,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>Em breve</span>
        </div>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 0'}}>
          <div><div style={{fontSize:13,fontWeight:600,color:'rgba(255,255,255,.5)'}}>Apple Watch</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Em breve</div></div>
          <span style={{fontSize:11,fontWeight:700,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>Em breve</span>
        </div>
      </Card>

      <Card title="Privacidade e dados">
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Exportar meus dados (LGPD)</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Baixe um arquivo com todos os seus dados</div></div>
          <button onClick={exportarDados} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer',flexShrink:0}}>Exportar</button>
        </div>
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Baixar histórico</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Baixe seu histórico completo de registros</div></div>
          <button onClick={baixarHistoricoCfg} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer',flexShrink:0}}>Baixar</button>
        </div>
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600}}>Limpar dados locais</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Remove cache e dados deste dispositivo. Não afeta seus dados no servidor.</div></div>
          <button onClick={limparDadosLocaisCfg} style={{background:'rgba(248,113,113,.15)',border:'1px solid rgba(248,113,113,.3)',color:C.danger,borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer',flexShrink:0}}>Limpar</button>
        </div>
        <div style={{padding:'10px 0',display:'flex',alignItems:'center',justifyContent:'space-between',gap:10}}>
          <div><div style={{fontSize:13,fontWeight:600,color:'rgba(255,255,255,.4)'}}>Excluir meus dados</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Ainda não disponível — essa ação exige um fluxo de confirmação seguro que ainda não existe</div></div>
          <button disabled style={{background:'rgba(255,255,255,.04)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.3)',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'not-allowed',flexShrink:0}}>Em breve</button>
        </div>
      </Card>

      <Card title="Segurança">
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          <div><div style={{fontSize:13}}>Conta</div><div style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>Autenticada via Supabase</div></div>
          <button onClick={()=>supabase.auth.signOut()} style={{background:C.s2,border:`1px solid ${C.line}`,color:'#fff',borderRadius:9,padding:'7px 13px',fontSize:12,cursor:'pointer'}}>Sair</button>
        </div>
        <div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`,fontSize:11.5,color:'rgba(255,255,255,.35)'}}>Lista de dispositivos/sessões ativas ainda não implementada nesta versão.</div>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 0'}}>
          <div><div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Autenticação de dois fatores</div></div>
          <span style={{fontSize:11,fontWeight:700,color:'rgba(255,255,255,.35)',background:'rgba(255,255,255,.06)',padding:'3px 9px',borderRadius:20}}>Em breve</span>
        </div>
      </Card>

      <Card title="Aparência">
        <div style={{marginBottom:14}}>
          <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:8}}>Tema</label>
          <div style={{display:'flex',gap:8}}>
            {[['escuro','🌙 Escuro',true],['claro','☀️ Claro',false],['sistema','🖥️ Sistema',false]].map(([v,lbl,disp])=>(
              <button key={v as string} onClick={()=>{if(disp){setTema(v as string);marcarAlterado()}}} disabled={!disp} title={disp?'':'Em breve'} style={{flex:1,background:tema===v?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,border:`1px solid ${tema===v?'transparent':C.line}`,color:disp?(tema===v?'#fff':'rgba(255,255,255,.6)'):'rgba(255,255,255,.25)',borderRadius:10,padding:'10px 8px',fontSize:12,cursor:disp?'pointer':'not-allowed'}}>{lbl as string}</button>
            ))}
          </div>
        </div>
        <div>
          <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:8}}>Densidade</label>
          <div style={{display:'flex',gap:8}}>
            {[['confortavel','Confortável'],['compacta','Compacta']].map(([v,lbl])=>(<button key={v} disabled title="Em breve" style={{flex:1,background:densidade===v?'rgba(139,92,246,.15)':C.s2,border:`1px solid ${densidade===v?'rgba(139,92,246,.3)':C.line}`,color:'rgba(255,255,255,.3)',borderRadius:10,padding:'10px 8px',fontSize:12,cursor:'not-allowed'}}>{lbl}</button>))}
          </div>
          <p style={{fontSize:11,color:'rgba(255,255,255,.3)',marginTop:8}}>Densidade ainda não implementada — arquitetura preparada para uma próxima etapa.</p>
        </div>
      </Card>
    </div>

    <div style={{marginTop:20,background:'rgba(139,92,246,.06)',border:'1px solid rgba(139,92,246,.15)',borderRadius:12,padding:'12px 16px',fontSize:11.5,color:'rgba(255,255,255,.4)'}}>ⓘ Suas configurações ficam salvas neste dispositivo e são a fonte oficial usada pela Home, Agenda, Relatórios e Luna quando aplicável.</div>
  </div>)
}'''
s = replace_once(s, old, new, "reescreve-config")

p.write_text(s)
print("TUDO OK:", applied)
