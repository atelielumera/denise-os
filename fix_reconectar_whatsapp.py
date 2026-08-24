import pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent
feitos = []

def replace_once(path, old, new, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n != 1:
        print(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new, 1), encoding='utf-8')
    feitos.append(label)

replace_once(
    'src/main.tsx',
    """  async function conectarWhatsapp(){
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
  }""",
    """  async function conectarWhatsapp(){
    setWaLoading(true)
    setWaErro(null)
    try{
      const resp=await fetch('/api/whatsapp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'connect'})})
      const data=await resp.json()
      if(!resp.ok)throw new Error(data?.error||'Erro ao conectar.')
      if(!data.base64&&!data.pairingCode){
        setWaQr(null);setWaPairingCode(null)
        setWaErro(data.message||'Não veio um QR novo agora. Verificando o status atual...')
        await verificarStatusWhatsapp()
      }else{
        setWaQr(data.base64||null)
        setWaPairingCode(data.pairingCode||null)
        setWaState('connecting')
      }
    }catch(err:any){setWaErro(err?.message||'Erro ao conectar.')}
    setWaLoading(false)
  }""",
    'main-conectarWhatsapp-lida-sem-qr'
)

replace_once(
    'src/main.tsx',
    """        {waState==='open'?null:(waState==='carregando'?null:<div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          {(waState==='close'||waState==='nao_criada'||waState==='erro')&&<button onClick={conectarWhatsapp} disabled={waLoading} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'8px 14px',fontSize:12,fontWeight:700,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Gerando QR Code...':'Gerar QR Code'}</button>}
          {waState==='connecting'&&<div style={{display:'flex',flexDirection:'column' as const,alignItems:'center',gap:8}}>{waQr&&<img src={waQr.startsWith('data:')?waQr:`data:image/png;base64,${waQr}`} alt="QR Code do WhatsApp" style={{width:140,height:140,borderRadius:10,background:'#fff',padding:6}}/>}{waPairingCode&&<div style={{fontSize:12,color:'rgba(255,255,255,.7)'}}>Código: <strong>{waPairingCode}</strong></div>}</div>}
          {waErro&&<div style={{fontSize:11.5,color:C.danger,marginTop:6}}>{waErro}</div>}
        </div>)}""",
    """        {waState==='carregando'?null:<div style={{padding:'10px 0',borderBottom:`1px solid ${C.line}`}}>
          {waState==='open'&&<button onClick={conectarWhatsapp} disabled={waLoading} style={{background:'none',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.6)',borderRadius:9,padding:'6px 12px',fontSize:11.5,fontWeight:600,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Verificando...':'Reconectar (gerar novo QR Code)'}</button>}
          {(waState==='close'||waState==='nao_criada'||waState==='erro')&&<button onClick={conectarWhatsapp} disabled={waLoading} style={{background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:9,padding:'8px 14px',fontSize:12,fontWeight:700,cursor:'pointer',opacity:waLoading?.6:1}}>{waLoading?'Gerando QR Code...':'Gerar QR Code'}</button>}
          {waState==='connecting'&&<div style={{display:'flex',flexDirection:'column' as const,alignItems:'center',gap:8}}>{waQr&&<img src={waQr.startsWith('data:')?waQr:`data:image/png;base64,${waQr}`} alt="QR Code do WhatsApp" style={{width:140,height:140,borderRadius:10,background:'#fff',padding:6}}/>}{waPairingCode&&<div style={{fontSize:12,color:'rgba(255,255,255,.7)'}}>Código: <strong>{waPairingCode}</strong></div>}</div>}
          {waErro&&<div style={{fontSize:11.5,color:C.danger,marginTop:6}}>{waErro}</div>}
        </div>}""",
    'main-botao-reconectar-sempre-visivel'
)

print('TUDO OK:', feitos)
