import base64
from pathlib import Path

applied = []

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

# --- 1) Agenda: reconexao silenciosa do Google Calendar ---
old1 = """  React.useEffect(()=>{
    if(gToken)buscarEventosGoogle(gToken)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  function buscarEventosGoogle(token:string){
    setGLoading(true);setGErro('')
    const hoje=new Date()
    const timeMin=new Date(hoje.getFullYear(),hoje.getMonth()-2,1).toISOString()
    const timeMax=new Date(hoje.getFullYear(),hoje.getMonth()+10,1).toISOString()
    fetch(`https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&maxResults=250&singleEvents=true&orderBy=startTime`,{headers:{Authorization:`Bearer ${token}`}})
      .then(r=>r.json())
      .then(data=>{setGEventos(data.items||[]);setGLoading(false)})
      .catch(()=>{setGErro('Erro ao buscar eventos do Google.');setGLoading(false)})
  }

  function conectarGoogle(){
    const g=(window as any).google
    if(!g||!g.accounts||!g.accounts.oauth2){setGErro('Google ainda carregando, tenta de novo em alguns segundos.');return}
    const tokenClient=g.accounts.oauth2.initTokenClient({
      client_id:GOOGLE_CLIENT_ID,
      scope:GOOGLE_SCOPE,
      callback:(resp:any)=>{
        if(resp&&resp.access_token){
          setGToken(resp.access_token)
          const expiresAt=Date.now()+((resp.expires_in||3600)*1000)
          try{localStorage.setItem('dos_google_token',JSON.stringify({token:resp.access_token,expiresAt}))}catch{}
          buscarEventosGoogle(resp.access_token)
        }else{setGErro('Nao foi possivel conectar ao Google.')}
      }
    })
    tokenClient.requestAccessToken()
  }"""
new1 = """  React.useEffect(()=>{
    if(gToken){buscarEventosGoogle(gToken);return}
    tentarReconectarSilencioso()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  function buscarEventosGoogle(token:string){
    setGLoading(true);setGErro('')
    const hoje=new Date()
    const timeMin=new Date(hoje.getFullYear(),hoje.getMonth()-2,1).toISOString()
    const timeMax=new Date(hoje.getFullYear(),hoje.getMonth()+10,1).toISOString()
    fetch(`https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${timeMin}&timeMax=${timeMax}&maxResults=250&singleEvents=true&orderBy=startTime`,{headers:{Authorization:`Bearer ${token}`}})
      .then(r=>r.json())
      .then(data=>{
        const items=data.items||[]
        setGEventos(items)
        setGLoading(false)
        try{localStorage.setItem('dos_google_events_cache',JSON.stringify(items))}catch{}
      })
      .catch(()=>{setGErro('Erro ao buscar eventos do Google.');setGLoading(false)})
  }

  function salvarTokenGoogle(resp:any){
    setGToken(resp.access_token)
    const expiresAt=Date.now()+((resp.expires_in||3600)*1000)
    try{localStorage.setItem('dos_google_token',JSON.stringify({token:resp.access_token,expiresAt}))}catch{}
    buscarEventosGoogle(resp.access_token)
  }

  function tentarReconectarSilencioso(){
    const g=(window as any).google
    if(!g||!g.accounts||!g.accounts.oauth2)return
    const tokenClient=g.accounts.oauth2.initTokenClient({
      client_id:GOOGLE_CLIENT_ID,
      scope:GOOGLE_SCOPE,
      callback:(resp:any)=>{if(resp&&resp.access_token)salvarTokenGoogle(resp)}
    })
    try{tokenClient.requestAccessToken({prompt:''})}catch{}
  }

  function conectarGoogle(){
    const g=(window as any).google
    if(!g||!g.accounts||!g.accounts.oauth2){setGErro('Google ainda carregando, tenta de novo em alguns segundos.');return}
    const tokenClient=g.accounts.oauth2.initTokenClient({
      client_id:GOOGLE_CLIENT_ID,
      scope:GOOGLE_SCOPE,
      callback:(resp:any)=>{
        if(resp&&resp.access_token)salvarTokenGoogle(resp)
        else setGErro('Nao foi possivel conectar ao Google.')
      }
    })
    tokenClient.requestAccessToken()
  }"""
s = replace_once(s, old1, new1, "agenda-google-reconexao-silenciosa")
applied.append("agenda-google-reconexao-silenciosa")

# --- 2) Shell: sincronizar snapshot dos dados locais no Supabase ---
old2 = "function Shell(){return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}>"
new2 = """function Shell(){
  React.useEffect(()=>{
    const EXCLUIR=['dos_google_token','dos_photos','dos_cfg_notif','dos_cfg_resumo','dos_cfg_fuso','dos_cfg_formato']
    function sincronizarSnapshot(){
      const dados:Record<string,any>={}
      for(let i=0;i<localStorage.length;i++){
        const k=localStorage.key(i)
        if(!k||!k.startsWith('dos_')||EXCLUIR.includes(k))continue
        const v=localStorage.getItem(k)
        if(v===null)continue
        try{dados[k]=JSON.parse(v)}catch{dados[k]=v}
      }
      supabase.from('app_snapshot').upsert({id:'denise',data:dados,updated_at:new Date().toISOString()}).then(()=>{})
    }
    sincronizarSnapshot()
    const t=setInterval(sincronizarSnapshot,5*60*1000)
    window.addEventListener('beforeunload',sincronizarSnapshot)
    return()=>{clearInterval(t);window.removeEventListener('beforeunload',sincronizarSnapshot)}
  },[])
  return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}>"""
s = replace_once(s, old2, new2, "shell-snapshot-sync")
applied.append("shell-snapshot-sync")

# --- 3) Assistente: montarContexto com agenda, rotina, medicamentos, trabalho ---
old3 = """  function montarContexto(){
    const treinosI=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]
    const leiturasI=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
    const devI=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
    const casaI=(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})() as any[]
    const livroI=(()=>{try{return JSON.parse(localStorage.getItem('dos_livro_atual')||'null')}catch{return null}})() as any
    function diasUnicos(entries:any[]):Set<string>{return new Set(entries.map((e:any)=>e.data))}
    function sequencia(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(d.toISOString().slice(0,10))){n++;d.setDate(d.getDate()-1)}return n}
    const hojeIso=new Date().toISOString().slice(0,10)
    const em7diasIso=new Date(Date.now()+7*86400000).toISOString().slice(0,10)
    const contasVencendo=casaI.filter((i:any)=>i.cat==='Contas'&&i.venc&&!i.done&&i.venc>=hojeIso&&i.venc<=em7diasIso)
    return {
      data_hoje:hojeIso,
      tirzepatida:Object.keys(tzSched).length>0?{estoque_atual_mg:tzBalance,denise:tzSched.denise||null,flavio:tzSched.flavio||null}:null,
      sequencia_treinos_dias:sequencia(diasUnicos(treinosI)),
      sequencia_leitura_dias:sequencia(diasUnicos(leiturasI)),
      sequencia_devocional_dias:sequencia(diasUnicos(devI)),
      livro_atual:livroI,
      contas_vencendo_7dias:contasVencendo.map((c:any)=>({nome:c.n,vencimento:c.venc})),
    }"""
new3 = """  function montarContexto(){
    const treinosI=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]
    const leiturasI=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
    const devI=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
    const casaI=(()=>{try{return JSON.parse(localStorage.getItem('dos_casa_items')||'[]')}catch{return []}})() as any[]
    const livroI=(()=>{try{return JSON.parse(localStorage.getItem('dos_livro_atual')||'null')}catch{return null}})() as any
    const agendaLocal=(()=>{try{return JSON.parse(localStorage.getItem('dos_agenda')||'[]')}catch{return []}})() as any[]
    const agendaGoogle=(()=>{try{return JSON.parse(localStorage.getItem('dos_google_events_cache')||'[]')}catch{return []}})() as any[]
    const medicamentosI=(()=>{try{return JSON.parse(localStorage.getItem('dos_medicamentos')||'{}')}catch{return {}}})() as any
    const trabalhoI=(()=>{try{return JSON.parse(localStorage.getItem('dos_trabalho')||'[]')}catch{return []}})() as any[]
    const rotinaItensI=(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'[]')}catch{return []}})() as any[]
    function diasUnicos(entries:any[]):Set<string>{return new Set(entries.map((e:any)=>e.data))}
    function sequencia(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(d.toISOString().slice(0,10))){n++;d.setDate(d.getDate()-1)}return n}
    const hojeIso=new Date().toISOString().slice(0,10)
    const em7diasIso=new Date(Date.now()+7*86400000).toISOString().slice(0,10)
    const contasVencendo=casaI.filter((i:any)=>i.cat==='Contas'&&i.venc&&!i.done&&i.venc>=hojeIso&&i.venc<=em7diasIso)
    const rotinaDoneHoje=(()=>{try{return JSON.parse(localStorage.getItem(`dos_rotina_done_${hojeIso}`)||'[]')}catch{return []}})() as number[]
    const agendaProximos7Dias=[
      ...agendaLocal.map((e:any)=>({data:e.data,hora:e.hora,titulo:e.nome,origem:'app'})),
      ...agendaGoogle.map((ev:any)=>({data:(ev.start?.dateTime||ev.start?.date||'').slice(0,10),hora:ev.start?.dateTime?new Date(ev.start.dateTime).toISOString().slice(11,16):'',titulo:ev.summary||'(sem titulo)',origem:'google_calendar'})),
    ].filter(e=>e.data>=hojeIso&&e.data<=em7diasIso).sort((a,b)=>(a.data+a.hora).localeCompare(b.data+b.hora))
    return {
      data_hoje:hojeIso,
      tirzepatida:Object.keys(tzSched).length>0?{estoque_atual_mg:tzBalance,denise:tzSched.denise||null,flavio:tzSched.flavio||null}:null,
      sequencia_treinos_dias:sequencia(diasUnicos(treinosI)),
      sequencia_leitura_dias:sequencia(diasUnicos(leiturasI)),
      sequencia_devocional_dias:sequencia(diasUnicos(devI)),
      livro_atual:livroI,
      contas_vencendo_7dias:contasVencendo.map((c:any)=>({nome:c.n,vencimento:c.venc})),
      agenda_proximos_7dias:agendaProximos7Dias,
      rotina_de_hoje:rotinaItensI.map((it:any,i:number)=>({horario:it.t,nome:it.n,categoria:it.cat,feito_hoje:rotinaDoneHoje.includes(i)})),
      medicamentos:medicamentosI,
      trabalho_tarefas:trabalhoI,
    }"""
s = replace_once(s, old3, new3, "assistente-contexto-agenda")
applied.append("assistente-contexto-agenda")

main_file.write_text(s)

# --- 4) Novos arquivos api/*.js (lib compartilhada + 4 crons) ---
files_b64 = {
    "api/_cronlib.js": "aW1wb3J0IHsgY3JlYXRlQ2xpZW50IH0gZnJvbSAnQHN1cGFiYXNlL3N1cGFiYXNlLWpzJwoKZXhwb3J0IGZ1bmN0aW9uIGdldEV2b0NvbmZpZygpIHsKICBjb25zdCBiYXNlVXJsID0gKHByb2Nlc3MuZW52LkVWT0xVVElPTl9BUElfVVJMIHx8ICcnKS5yZXBsYWNlKC9cLyskLywgJycpCiAgY29uc3QgYXBpS2V5ID0gcHJvY2Vzcy5lbnYuRVZPTFVUSU9OX0FQSV9LRVkKICBjb25zdCBpbnN0YW5jZSA9IHByb2Nlc3MuZW52LkVWT0xVVElPTl9JTlNUQU5DRSB8fCAnZGVuaXNlLW9zJwogIHJldHVybiB7IGJhc2VVcmwsIGFwaUtleSwgaW5zdGFuY2UgfQp9CgpleHBvcnQgYXN5bmMgZnVuY3Rpb24gc2VuZFdoYXRzYXBwVGV4dChudW1iZXIsIHRleHQpIHsKICBjb25zdCB7IGJhc2VVcmwsIGFwaUtleSwgaW5zdGFuY2UgfSA9IGdldEV2b0NvbmZpZygpCiAgaWYgKCFiYXNlVXJsIHx8ICFhcGlLZXkpIHRocm93IG5ldyBFcnJvcignRXZvbHV0aW9uIEFQSSBuYW8gY29uZmlndXJhZGEuJykKICBhd2FpdCBmZXRjaChgJHtiYXNlVXJsfS9tZXNzYWdlL3NlbmRUZXh0LyR7aW5zdGFuY2V9YCwgewogICAgbWV0aG9kOiAnUE9TVCcsCiAgICBoZWFkZXJzOiB7ICdjb250ZW50LXR5cGUnOiAnYXBwbGljYXRpb24vanNvbicsIGFwaWtleTogYXBpS2V5IH0sCiAgICBib2R5OiBKU09OLnN0cmluZ2lmeSh7IG51bWJlciwgdGV4dCB9KQogIH0pCn0KCmV4cG9ydCBhc3luYyBmdW5jdGlvbiB0cmFuc2NyaWJlQXVkaW8oYmFzZTY0LCBtZWRpYVR5cGUpIHsKICBjb25zdCBnZW1pbmlLZXkgPSBwcm9jZXNzLmVudi5HRU1JTklfQVBJX0tFWQogIGlmICghZ2VtaW5pS2V5KSB0aHJvdyBuZXcgRXJyb3IoJ0dFTUlOSV9BUElfS0VZIG5hbyBjb25maWd1cmFkYS4nKQogIGNvbnN0IGdlbWluaVJlc3AgPSBhd2FpdCBmZXRjaCgKICAgICdodHRwczovL2dlbmVyYXRpdmVsYW5ndWFnZS5nb29nbGVhcGlzLmNvbS92MWJldGEvbW9kZWxzL2dlbWluaS0yLjAtZmxhc2g6Z2VuZXJhdGVDb250ZW50P2tleT0nICsgZ2VtaW5pS2V5LAogICAgewogICAgICBtZXRob2Q6ICdQT1NUJywKICAgICAgaGVhZGVyczogeyAnY29udGVudC10eXBlJzogJ2FwcGxpY2F0aW9uL2pzb24nIH0sCiAgICAgIGJvZHk6IEpTT04uc3RyaW5naWZ5KHsKICAgICAgICBjb250ZW50czogW3sKICAgICAgICAgIHBhcnRzOiBbCiAgICAgICAgICAgIHsgdGV4dDogJ1RyYW5zY3JldmEgZXN0ZSBhdWRpbyBlbSBwb3J0dWd1ZXMgZG8gQnJhc2lsLiBSZXNwb25kYSBhcGVuYXMgY29tIG8gdGV4dG8gdHJhbnNjcml0bywgc2VtIGNvbWVudGFyaW9zLicgfSwKICAgICAgICAgICAgeyBpbmxpbmVfZGF0YTogeyBtaW1lX3R5cGU6IG1lZGlhVHlwZSB8fCAnYXVkaW8vb2dnJywgZGF0YTogYmFzZTY0IH0gfQogICAgICAgICAgXQogICAgICAgIH1dCiAgICAgIH0pCiAgICB9CiAgKQogIGNvbnN0IGdlbWluaURhdGEgPSBhd2FpdCBnZW1pbmlSZXNwLmpzb24oKQogIGlmICghZ2VtaW5pUmVzcC5vaykgdGhyb3cgbmV3IEVycm9yKGdlbWluaURhdGE/LmVycm9yPy5tZXNzYWdlIHx8ICdFcnJvIGFvIHRyYW5zY3JldmVyIGF1ZGlvLicpCiAgcmV0dXJuIChnZW1pbmlEYXRhLmNhbmRpZGF0ZXM/LlswXT8uY29udGVudD8ucGFydHM/LlswXT8udGV4dCB8fCAnJykudHJpbSgpCn0KCmV4cG9ydCBhc3luYyBmdW5jdGlvbiBhc2tMdW5hKHN5c3RlbVByb21wdCwgdXNlckNvbnRlbnQpIHsKICBjb25zdCBhcGlLZXkgPSBwcm9jZXNzLmVudi5BTlRIUk9QSUNfQVBJX0tFWQogIGlmICghYXBpS2V5KSB0aHJvdyBuZXcgRXJyb3IoJ0FOVEhST1BJQ19BUElfS0VZIG5hbyBjb25maWd1cmFkYS4nKQogIGNvbnN0IGFudGhyb3BpY1Jlc3AgPSBhd2FpdCBmZXRjaCgnaHR0cHM6Ly9hcGkuYW50aHJvcGljLmNvbS92MS9tZXNzYWdlcycsIHsKICAgIG1ldGhvZDogJ1BPU1QnLAogICAgaGVhZGVyczogeyAnY29udGVudC10eXBlJzogJ2FwcGxpY2F0aW9uL2pzb24nLCAneC1hcGkta2V5JzogYXBpS2V5LCAnYW50aHJvcGljLXZlcnNpb24nOiAnMjAyMy0wNi0wMScgfSwKICAgIGJvZHk6IEpTT04uc3RyaW5naWZ5KHsKICAgICAgbW9kZWw6ICdjbGF1ZGUtc29ubmV0LTUnLAogICAgICBtYXhfdG9rZW5zOiA4MDAsCiAgICAgIHN5c3RlbTogc3lzdGVtUHJvbXB0LAogICAgICBtZXNzYWdlczogW3sgcm9sZTogJ3VzZXInLCBjb250ZW50OiB1c2VyQ29udGVudCB9XQogICAgfSkKICB9KQogIGNvbnN0IGRhdGEgPSBhd2FpdCBhbnRocm9waWNSZXNwLmpzb24oKQogIGlmICghYW50aHJvcGljUmVzcC5vaykgdGhyb3cgbmV3IEVycm9yKGRhdGE/LmVycm9yPy5tZXNzYWdlIHx8ICdFcnJvIGFvIGNvbnN1bHRhciBhIElBLicpCiAgcmV0dXJuIGRhdGEuY29udGVudD8uZmluZCgoYikgPT4gYi50eXBlID09PSAndGV4dCcpPy50ZXh0IHx8ICdEZXNjdWxwYSwgbsOjbyBjb25zZWd1aSBnZXJhciBpc3NvIGFnb3JhLicKfQoKZnVuY3Rpb24gZ2V0U3VwYWJhc2VBZG1pbigpIHsKICBjb25zdCB1cmwgPSBwcm9jZXNzLmVudi5WSVRFX1NVUEFCQVNFX1VSTAogIGNvbnN0IHNlcnZpY2VLZXkgPSBwcm9jZXNzLmVudi5TVVBBQkFTRV9TRVJWSUNFX1JPTEVfS0VZCiAgaWYgKCF1cmwgfHwgIXNlcnZpY2VLZXkpIHJldHVybiBudWxsCiAgcmV0dXJuIGNyZWF0ZUNsaWVudCh1cmwsIHNlcnZpY2VLZXkpCn0KCmV4cG9ydCBhc3luYyBmdW5jdGlvbiBidWlsZEx1bmFDb250ZXh0KCkgewogIGNvbnN0IGhvamVJc28gPSBuZXcgRGF0ZSgpLnRvSVNPU3RyaW5nKCkuc2xpY2UoMCwgMTApCiAgY29uc3QgZW03ZGlhc0lzbyA9IG5ldyBEYXRlKERhdGUubm93KCkgKyA3ICogODY0MDAwMDApLnRvSVNPU3RyaW5nKCkuc2xpY2UoMCwgMTApCiAgY29uc3Qgc3VwYWJhc2UgPSBnZXRTdXBhYmFzZUFkbWluKCkKICBpZiAoIXN1cGFiYXNlKSByZXR1cm4geyBkYXRhX2hvamU6IGhvamVJc28sIHRpcnplcGF0aWRhOiBudWxsIH0KCiAgY29uc3QgW3sgZGF0YTogc2NoZWQgfSwgeyBkYXRhOiBiYWwgfSwgeyBkYXRhOiBzbmFwIH1dID0gYXdhaXQgUHJvbWlzZS5hbGwoWwogICAgc3VwYWJhc2UuZnJvbSgndGlyemVwYXRpZGFfc2NoZWR1bGUnKS5zZWxlY3QoJyonKSwKICAgIHN1cGFiYXNlLmZyb20oJ3RpcnplcGF0aWRhX3N0b2NrX2JhbGFuY2UnKS5zZWxlY3QoJyonKS5tYXliZVNpbmdsZSgpLAogICAgc3VwYWJhc2UuZnJvbSgnYXBwX3NuYXBzaG90Jykuc2VsZWN0KCdkYXRhJykuZXEoJ2lkJywgJ2RlbmlzZScpLm1heWJlU2luZ2xlKCkKICBdKQoKICBjb25zdCB0ek1hcCA9IHt9CiAgOyhzY2hlZCB8fCBbXSkuZm9yRWFjaCgocm93KSA9PiB7CiAgICB0ek1hcFtyb3cucGVyc29uXSA9IHsgcGxhbm5lZF9kb3NlX21nOiBOdW1iZXIocm93LnBsYW5uZWRfZG9zZV9tZyksIGludGVydmFsX2RheXM6IHJvdy5pbnRlcnZhbF9kYXlzLCBuZXh0X2FwcGxpY2F0aW9uX2RhdGU6IHJvdy5uZXh0X2FwcGxpY2F0aW9uX2RhdGUgfQogIH0pCgogIGNvbnN0IGQgPSBzbmFwPy5kYXRhIHx8IHt9CiAgY29uc3QgYWdlbmRhTG9jYWwgPSBBcnJheS5pc0FycmF5KGQuZG9zX2FnZW5kYSkgPyBkLmRvc19hZ2VuZGEgOiBbXQogIGNvbnN0IGFnZW5kYUdvb2dsZSA9IEFycmF5LmlzQXJyYXkoZC5kb3NfZ29vZ2xlX2V2ZW50c19jYWNoZSkgPyBkLmRvc19nb29nbGVfZXZlbnRzX2NhY2hlIDogW10KICBjb25zdCByb3RpbmFJdGVucyA9IEFycmF5LmlzQXJyYXkoZC5kb3Nfcm90aW5hKSA/IGQuZG9zX3JvdGluYSA6IFtdCiAgY29uc3Qgcm90aW5hRG9uZUhvamUgPSBBcnJheS5pc0FycmF5KGRbYGRvc19yb3RpbmFfZG9uZV8ke2hvamVJc299YF0pID8gZFtgZG9zX3JvdGluYV9kb25lXyR7aG9qZUlzb31gXSA6IFtdCiAgY29uc3QgY2FzYUl0ZW5zID0gQXJyYXkuaXNBcnJheShkLmRvc19jYXNhX2l0ZW1zKSA/IGQuZG9zX2Nhc2FfaXRlbXMgOiBbXQogIGNvbnN0IHRyZWlub3MgPSBBcnJheS5pc0FycmF5KGQuZG9zX3RyZWlub3MpID8gZC5kb3NfdHJlaW5vcyA6IFtdCiAgY29uc3QgbGVpdHVyYXMgPSBBcnJheS5pc0FycmF5KGQuZG9zX2xlaXR1cmFzKSA/IGQuZG9zX2xlaXR1cmFzIDogW10KICBjb25zdCBkZXZvY2lvbmFpcyA9IEFycmF5LmlzQXJyYXkoZC5kb3NfZGV2b2Npb25haXMpID8gZC5kb3NfZGV2b2Npb25haXMgOiBbXQoKICBmdW5jdGlvbiBkaWFzVW5pY29zKGVudHJpZXMpIHsgcmV0dXJuIG5ldyBTZXQoZW50cmllcy5tYXAoKGUpID0+IGUuZGF0YSkpIH0KICBmdW5jdGlvbiBzZXF1ZW5jaWEoZGlhcykgewogICAgbGV0IG4gPSAwCiAgICBjb25zdCBkdCA9IG5ldyBEYXRlKCkKICAgIHdoaWxlIChkaWFzLmhhcyhkdC50b0lTT1N0cmluZygpLnNsaWNlKDAsIDEwKSkpIHsgbisrOyBkdC5zZXREYXRlKGR0LmdldERhdGUoKSAtIDEpIH0KICAgIHJldHVybiBuCiAgfQoKICBjb25zdCBhZ2VuZGFQcm94aW1vczdEaWFzID0gWwogICAgLi4uYWdlbmRhTG9jYWwubWFwKChlKSA9PiAoeyBkYXRhOiBlLmRhdGEsIGhvcmE6IGUuaG9yYSwgdGl0dWxvOiBlLm5vbWUsIG9yaWdlbTogJ2FwcCcgfSkpLAogICAgLi4uYWdlbmRhR29vZ2xlLm1hcCgoZXYpID0+ICh7CiAgICAgIGRhdGE6IChldi5zdGFydD8uZGF0ZVRpbWUgfHwgZXYuc3RhcnQ/LmRhdGUgfHwgJycpLnNsaWNlKDAsIDEwKSwKICAgICAgaG9yYTogZXYuc3RhcnQ/LmRhdGVUaW1lID8gbmV3IERhdGUoZXYuc3RhcnQuZGF0ZVRpbWUpLnRvSVNPU3RyaW5nKCkuc2xpY2UoMTEsIDE2KSA6ICcnLAogICAgICB0aXR1bG86IGV2LnN1bW1hcnkgfHwgJyhzZW0gdGl0dWxvKScsCiAgICAgIG9yaWdlbTogJ2dvb2dsZV9jYWxlbmRhcicKICAgIH0pKQogIF0uZmlsdGVyKChlKSA9PiBlLmRhdGEgPj0gaG9qZUlzbyAmJiBlLmRhdGEgPD0gZW03ZGlhc0lzbykuc29ydCgoYSwgYikgPT4gKGEuZGF0YSArIGEuaG9yYSkubG9jYWxlQ29tcGFyZShiLmRhdGEgKyBiLmhvcmEpKQoKICBjb25zdCBjb250YXNWZW5jZW5kbyA9IGNhc2FJdGVucy5maWx0ZXIoKGkpID0+IGkuY2F0ID09PSAnQ29udGFzJyAmJiBpLnZlbmMgJiYgIWkuZG9uZSAmJiBpLnZlbmMgPj0gaG9qZUlzbyAmJiBpLnZlbmMgPD0gZW03ZGlhc0lzbykKCiAgcmV0dXJuIHsKICAgIGRhdGFfaG9qZTogaG9qZUlzbywKICAgIHVsdGltYV9zaW5jcm9uaXphY2FvX2RvX2FwcDogc25hcD8uZGF0YSA/IGQuX191cGRhdGVkX2F0IHx8IG51bGwgOiBudWxsLAogICAgdGlyemVwYXRpZGE6IE9iamVjdC5rZXlzKHR6TWFwKS5sZW5ndGggPiAwID8geyBlc3RvcXVlX2F0dWFsX21nOiBOdW1iZXIoYmFsPy5jdXJyZW50X2JhbGFuY2VfbWcgPz8gMCksIGRlbmlzZTogdHpNYXAuZGVuaXNlIHx8IG51bGwsIGZsYXZpbzogdHpNYXAuZmxhdmlvIHx8IG51bGwgfSA6IG51bGwsCiAgICBzZXF1ZW5jaWFfdHJlaW5vc19kaWFzOiBzZXF1ZW5jaWEoZGlhc1VuaWNvcyh0cmVpbm9zKSksCiAgICBzZXF1ZW5jaWFfbGVpdHVyYV9kaWFzOiBzZXF1ZW5jaWEoZGlhc1VuaWNvcyhsZWl0dXJhcykpLAogICAgc2VxdWVuY2lhX2Rldm9jaW9uYWxfZGlhczogc2VxdWVuY2lhKGRpYXNVbmljb3MoZGV2b2Npb25haXMpKSwKICAgIGxpdnJvX2F0dWFsOiBkLmRvc19saXZyb19hdHVhbCB8fCBudWxsLAogICAgY29udGFzX3ZlbmNlbmRvXzdkaWFzOiBjb250YXNWZW5jZW5kby5tYXAoKGMpID0+ICh7IG5vbWU6IGMubiwgdmVuY2ltZW50bzogYy52ZW5jIH0pKSwKICAgIGFnZW5kYV9wcm94aW1vc183ZGlhczogYWdlbmRhUHJveGltb3M3RGlhcywKICAgIHJvdGluYV9kZV9ob2plOiByb3RpbmFJdGVucy5tYXAoKGl0LCBpKSA9PiAoeyBob3JhcmlvOiBpdC50LCBub21lOiBpdC5uLCBjYXRlZ29yaWE6IGl0LmNhdCwgZmVpdG9faG9qZTogcm90aW5hRG9uZUhvamUuaW5jbHVkZXMoaSkgfSkpLAogICAgbWVkaWNhbWVudG9zOiBkLmRvc19tZWRpY2FtZW50b3MgfHwge30sCiAgICB0cmFiYWxob190YXJlZmFzOiBkLmRvc190cmFiYWxobyB8fCBbXSwKICAgIHRyZWlub3NfcmVjZW50ZXM6IHRyZWlub3Muc2xpY2UoMCwgMTApLAogICAgbGVpdHVyYXNfcmVjZW50ZXM6IGxlaXR1cmFzLnNsaWNlKDAsIDEwKQogIH0KfQoKZXhwb3J0IGZ1bmN0aW9uIHZlcmlmaWNhckNyb24ocmVxKSB7CiAgY29uc3Qgc2VjcmV0ID0gcHJvY2Vzcy5lbnYuQ1JPTl9TRUNSRVQKICBpZiAoIXNlY3JldCkgcmV0dXJuIHRydWUKICByZXR1cm4gcmVxLmhlYWRlcnMuYXV0aG9yaXphdGlvbiA9PT0gYEJlYXJlciAke3NlY3JldH1gCn0KCmV4cG9ydCBmdW5jdGlvbiBnZXREZW5pc2VOdW1iZXIoKSB7CiAgcmV0dXJuIHByb2Nlc3MuZW52LkRFTklTRV9XSEFUU0FQUF9OVU1CRVIgfHwgJycKfQoKZXhwb3J0IGZ1bmN0aW9uIGx1bmFTeXN0ZW1Qcm9tcHQoZXh0cmEpIHsKICByZXR1cm4gJ1ZvY8OqIMOpIGEgTHVuYSwgYXNzaXN0ZW50ZSBwZXNzb2FsIGRhIERlbmlzZSBkZW50cm8gZG8gRGVuaXNlIE9TLiBTZWphIGRpcmV0YSwgYWNvbGhlZG9yYSBlIHNlbSBqdWxnYW1lbnRvLCBlbSBwb3J0dWd1w6pzIGRvIEJyYXNpbC4gVXNlIEFQRU5BUyBvcyBkYWRvcyByZWFpcyBmb3JuZWNpZG9zIG5vIGNvbnRleHRvIGFiYWl4byAtIG51bmNhIGludmVudGUgbsO6bWVyb3MsIGRhdGFzIG91IGZhdG9zIHF1ZSBuw6NvIGVzdMOjbyBhbGkuIFNlIHVtIGRhZG8gbsOjbyBlc3RpdmVyIG5vIGNvbnRleHRvLCBkaWdhIGNvbSBuYXR1cmFsaWRhZGUgcXVlIGVsZSBhaW5kYSBuw6NvIGZvaSByZWdpc3RyYWRvIG5vIGFwcC4gJyArIChleHRyYSB8fCAnJykKfQo=",
    "api/cron-morning.js": "aW1wb3J0IHsgdmVyaWZpY2FyQ3JvbiwgZ2V0RGVuaXNlTnVtYmVyLCBidWlsZEx1bmFDb250ZXh0LCBhc2tMdW5hLCBzZW5kV2hhdHNhcHBUZXh0LCBsdW5hU3lzdGVtUHJvbXB0IH0gZnJvbSAnLi9fY3JvbmxpYi5qcycKCmV4cG9ydCBkZWZhdWx0IGFzeW5jIGZ1bmN0aW9uIGhhbmRsZXIocmVxLCByZXMpIHsKICBpZiAoIXZlcmlmaWNhckNyb24ocmVxKSkgewogICAgcmVzLnN0YXR1cyg0MDEpLmpzb24oeyBlcnJvcjogJ05hbyBhdXRvcml6YWRvLicgfSkKICAgIHJldHVybgogIH0KICBjb25zdCBudW1lcm8gPSBnZXREZW5pc2VOdW1iZXIoKQogIGlmICghbnVtZXJvKSB7CiAgICByZXMuc3RhdHVzKDUwMCkuanNvbih7IGVycm9yOiAnREVOSVNFX1dIQVRTQVBQX05VTUJFUiBuYW8gY29uZmlndXJhZGEuJyB9KQogICAgcmV0dXJuCiAgfQogIHRyeSB7CiAgICBjb25zdCBjb250ZXh0ID0gYXdhaXQgYnVpbGRMdW5hQ29udGV4dCgpCiAgICBjb25zdCBzeXN0ZW1Qcm9tcHQgPSBsdW5hU3lzdGVtUHJvbXB0KCdWb2PDqiBlc3TDoSBlbnZpYW5kbyBvIHJlc3VtbyBkYSBtYW5ow6MgKDA2OjAwKSBwZWxvIFdoYXRzQXBwLicpICsgJ1xuXG5Db250ZXh0byBhdHVhbCAoZGFkb3MgcmVhaXMgZGEgRGVuaXNlLCBhZ29yYSk6XG4nICsgSlNPTi5zdHJpbmdpZnkoY29udGV4dCwgbnVsbCwgMikKICAgIGNvbnN0IHBlZGlkbyA9ICdFc2NyZXZhIGEgbWVuc2FnZW0gZGUgYm9tIGRpYSBkYSBEZW5pc2UuIENvbWVjZSBjb20gIkJvbSBkaWEsIERlbmlzZSEg4piA77iPIiBlIGxpc3RlLCBkZSBmb3JtYSBvcmdhbml6YWRhIGUgY3VydGEsIHR1ZG8gcXVlIGVsYSB0ZW0gcGFyYSBmYXplciBob2plOiBpdGVucyBkYSByb3RpbmEgZGUgaG9qZSBhaW5kYSBuw6NvIGZlaXRvcywgY29tcHJvbWlzc29zIGRhIGFnZW5kYSBkZSBob2plLCB0aXJ6ZXBhdGlkYSBzZSBmb3IgaG9qZSBvIGRpYSBkZSBhcGxpY2FyLCBtZWRpY2FtZW50b3MgZGUgaG9qZSwgZSB0YXJlZmFzIGRlIHRyYWJhbGhvIHBlbmRlbnRlcyBzZSBob3V2ZXIuIFNlIHVtYSBkZXNzYXMgY2F0ZWdvcmlhcyBlc3RpdmVyIHZhemlhIG91IHNlbSBkYWRvLCBuw6NvIG1lbmNpb25lIGVsYSAobsOjbyBkaWdhICJuYWRhIHJlZ2lzdHJhZG8iKS4gVGVybWluZSBjb20gdW1hIGZyYXNlIGN1cnRhIGRlIGluY2VudGl2by4gRm9ybWF0byBkZSBXaGF0c0FwcCwgdXNlIGVtb2ppcyBjb20gbW9kZXJhw6fDo28sIHNlbSBtYXJrZG93biBkZSBuZWdyaXRvLicKICAgIGNvbnN0IHRleHRvID0gYXdhaXQgYXNrTHVuYShzeXN0ZW1Qcm9tcHQsIFt7IHR5cGU6ICd0ZXh0JywgdGV4dDogcGVkaWRvIH1dKQogICAgYXdhaXQgc2VuZFdoYXRzYXBwVGV4dChudW1lcm8sIHRleHRvKQogICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogIH0gY2F0Y2ggKGVycikgewogICAgcmVzLnN0YXR1cyg1MDApLmpzb24oeyBlcnJvcjogZXJyPy5tZXNzYWdlIHx8ICdlcnJvIGRlc2NvbmhlY2lkbycgfSkKICB9Cn0K",
    "api/cron-evening.js": "aW1wb3J0IHsgdmVyaWZpY2FyQ3JvbiwgZ2V0RGVuaXNlTnVtYmVyLCBidWlsZEx1bmFDb250ZXh0LCBhc2tMdW5hLCBzZW5kV2hhdHNhcHBUZXh0LCBsdW5hU3lzdGVtUHJvbXB0IH0gZnJvbSAnLi9fY3JvbmxpYi5qcycKCmV4cG9ydCBkZWZhdWx0IGFzeW5jIGZ1bmN0aW9uIGhhbmRsZXIocmVxLCByZXMpIHsKICBpZiAoIXZlcmlmaWNhckNyb24ocmVxKSkgewogICAgcmVzLnN0YXR1cyg0MDEpLmpzb24oeyBlcnJvcjogJ05hbyBhdXRvcml6YWRvLicgfSkKICAgIHJldHVybgogIH0KICBjb25zdCBudW1lcm8gPSBnZXREZW5pc2VOdW1iZXIoKQogIGlmICghbnVtZXJvKSB7CiAgICByZXMuc3RhdHVzKDUwMCkuanNvbih7IGVycm9yOiAnREVOSVNFX1dIQVRTQVBQX05VTUJFUiBuYW8gY29uZmlndXJhZGEuJyB9KQogICAgcmV0dXJuCiAgfQogIHRyeSB7CiAgICBjb25zdCBjb250ZXh0ID0gYXdhaXQgYnVpbGRMdW5hQ29udGV4dCgpCiAgICBjb25zdCBzeXN0ZW1Qcm9tcHQgPSBsdW5hU3lzdGVtUHJvbXB0KCdWb2PDqiBlc3TDoSBlbnZpYW5kbyBvIHJlc3VtbyBkYSBub2l0ZSAoMjA6MDApIHBlbG8gV2hhdHNBcHAuJykgKyAnXG5cbkNvbnRleHRvIGF0dWFsIChkYWRvcyByZWFpcyBkYSBEZW5pc2UsIGFnb3JhKTpcbicgKyBKU09OLnN0cmluZ2lmeShjb250ZXh0LCBudWxsLCAyKQogICAgY29uc3QgcGVkaWRvID0gJ0VzY3JldmEgYSBtZW5zYWdlbSBkZSBlbmNlcnJhbWVudG8gZG8gZGlhIGRhIERlbmlzZS4gQ29tZWNlIGNvbSAiQm9hIG5vaXRlLCBEZW5pc2Ug8J+MmSIgZSBtb3N0cmU6IG8gcXVlIGZvaSBmZWl0byBob2plIChpdGVucyBkYSByb3RpbmEgbWFyY2Fkb3MgY29tbyBmZWl0byBob2plLCB0cmVpbm8vbGVpdHVyYS9kZXZvY2lvbmFsIHNlIGhvdXZlciByZWdpc3RybyBkZSBob2plKSwgZSBvIHF1ZSBmaWNhIHBlbmRlbnRlIHBhcmEgYW1hbmjDoyAoaXRlbnMgZGEgYWdlbmRhIGRlIGFtYW5ow6MsIGl0ZW5zIGRhIHJvdGluYSBkZSBob2plIHF1ZSBuw6NvIGZvcmFtIGZlaXRvcykuIFNlIHVtYSBjYXRlZ29yaWEgZXN0aXZlciB2YXppYSwgbsOjbyBtZW5jaW9uZSBlbGEuIFRlcm1pbmUgY29tIHVtYSBmcmFzZSBjdXJ0YSBlIGFjb2xoZWRvcmEuIEZvcm1hdG8gZGUgV2hhdHNBcHAsIGVtb2ppcyBjb20gbW9kZXJhw6fDo28sIHNlbSBtYXJrZG93biBkZSBuZWdyaXRvLicKICAgIGNvbnN0IHRleHRvID0gYXdhaXQgYXNrTHVuYShzeXN0ZW1Qcm9tcHQsIFt7IHR5cGU6ICd0ZXh0JywgdGV4dDogcGVkaWRvIH1dKQogICAgYXdhaXQgc2VuZFdoYXRzYXBwVGV4dChudW1lcm8sIHRleHRvKQogICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogIH0gY2F0Y2ggKGVycikgewogICAgcmVzLnN0YXR1cyg1MDApLmpzb24oeyBlcnJvcjogZXJyPy5tZXNzYWdlIHx8ICdlcnJvIGRlc2NvbmhlY2lkbycgfSkKICB9Cn0K",
    "api/cron-weekly.js": "aW1wb3J0IHsgdmVyaWZpY2FyQ3JvbiwgZ2V0RGVuaXNlTnVtYmVyLCBidWlsZEx1bmFDb250ZXh0LCBhc2tMdW5hLCBzZW5kV2hhdHNhcHBUZXh0LCBsdW5hU3lzdGVtUHJvbXB0IH0gZnJvbSAnLi9fY3JvbmxpYi5qcycKCmV4cG9ydCBkZWZhdWx0IGFzeW5jIGZ1bmN0aW9uIGhhbmRsZXIocmVxLCByZXMpIHsKICBpZiAoIXZlcmlmaWNhckNyb24ocmVxKSkgewogICAgcmVzLnN0YXR1cyg0MDEpLmpzb24oeyBlcnJvcjogJ05hbyBhdXRvcml6YWRvLicgfSkKICAgIHJldHVybgogIH0KICBjb25zdCBudW1lcm8gPSBnZXREZW5pc2VOdW1iZXIoKQogIGlmICghbnVtZXJvKSB7CiAgICByZXMuc3RhdHVzKDUwMCkuanNvbih7IGVycm9yOiAnREVOSVNFX1dIQVRTQVBQX05VTUJFUiBuYW8gY29uZmlndXJhZGEuJyB9KQogICAgcmV0dXJuCiAgfQogIHRyeSB7CiAgICBjb25zdCBjb250ZXh0ID0gYXdhaXQgYnVpbGRMdW5hQ29udGV4dCgpCiAgICBjb25zdCBzeXN0ZW1Qcm9tcHQgPSBsdW5hU3lzdGVtUHJvbXB0KCdWb2PDqiBlc3TDoSBlbnZpYW5kbyBvIHJlc3VtbyBzZW1hbmFsIChzZXh0YS1mZWlyYSkgcGVsbyBXaGF0c0FwcC4nKSArICdcblxuQ29udGV4dG8gYXR1YWwgKGRhZG9zIHJlYWlzIGRhIERlbmlzZSwgYWdvcmEpOlxuJyArIEpTT04uc3RyaW5naWZ5KGNvbnRleHQsIG51bGwsIDIpCiAgICBjb25zdCBwZWRpZG8gPSAnRXNjcmV2YSBvIHJlc3VtbyBkYSBzZW1hbmEgZGEgRGVuaXNlLiBDb21lY2UgY29tICJSZXN1bW8gZGEgc2VtYW5hIPCfk4oiIGUgdXNlIGFzIHNlcXXDqm5jaWFzIGRpc3BvbsOtdmVpcyAodHJlaW5vcywgbGVpdHVyYSwgZGV2b2Npb25hbCkgZSBvcyB0cmVpbm9zL2xlaXR1cmFzIHJlY2VudGVzIHBhcmEgY29tZW50YXIgY29tbyBmb2kgYSBzZW1hbmEgLSBzZW0gaW52ZW50YXIgbsO6bWVyb3MgcXVlIG7Do28gZXN0w6NvIG5vIGNvbnRleHRvLiBTZSBuw6NvIGhvdXZlciBkYWRvIHN1ZmljaWVudGUgcGFyYSB1bSB0w7NwaWNvLCBuw6NvIG1lbmNpb25lIGVsZS4gVGVybWluZSBjb20gdW1hIGZyYXNlIGN1cnRhIGRlIHJlY29uaGVjaW1lbnRvIHBlbG8gZXNmb3LDp28gZGEgc2VtYW5hLiBGb3JtYXRvIGRlIFdoYXRzQXBwLCBlbW9qaXMgY29tIG1vZGVyYcOnw6NvLCBzZW0gbWFya2Rvd24gZGUgbmVncml0by4nCiAgICBjb25zdCB0ZXh0byA9IGF3YWl0IGFza0x1bmEoc3lzdGVtUHJvbXB0LCBbeyB0eXBlOiAndGV4dCcsIHRleHQ6IHBlZGlkbyB9XSkKICAgIGF3YWl0IHNlbmRXaGF0c2FwcFRleHQobnVtZXJvLCB0ZXh0bykKICAgIHJlcy5zdGF0dXMoMjAwKS5qc29uKHsgb2s6IHRydWUgfSkKICB9IGNhdGNoIChlcnIpIHsKICAgIHJlcy5zdGF0dXMoNTAwKS5qc29uKHsgZXJyb3I6IGVycj8ubWVzc2FnZSB8fCAnZXJybyBkZXNjb25oZWNpZG8nIH0pCiAgfQp9Cg==",
    "api/cron-nextweek.js": "aW1wb3J0IHsgdmVyaWZpY2FyQ3JvbiwgZ2V0RGVuaXNlTnVtYmVyLCBidWlsZEx1bmFDb250ZXh0LCBhc2tMdW5hLCBzZW5kV2hhdHNhcHBUZXh0LCBsdW5hU3lzdGVtUHJvbXB0IH0gZnJvbSAnLi9fY3JvbmxpYi5qcycKCmV4cG9ydCBkZWZhdWx0IGFzeW5jIGZ1bmN0aW9uIGhhbmRsZXIocmVxLCByZXMpIHsKICBpZiAoIXZlcmlmaWNhckNyb24ocmVxKSkgewogICAgcmVzLnN0YXR1cyg0MDEpLmpzb24oeyBlcnJvcjogJ05hbyBhdXRvcml6YWRvLicgfSkKICAgIHJldHVybgogIH0KICBjb25zdCBudW1lcm8gPSBnZXREZW5pc2VOdW1iZXIoKQogIGlmICghbnVtZXJvKSB7CiAgICByZXMuc3RhdHVzKDUwMCkuanNvbih7IGVycm9yOiAnREVOSVNFX1dIQVRTQVBQX05VTUJFUiBuYW8gY29uZmlndXJhZGEuJyB9KQogICAgcmV0dXJuCiAgfQogIHRyeSB7CiAgICBjb25zdCBjb250ZXh0ID0gYXdhaXQgYnVpbGRMdW5hQ29udGV4dCgpCiAgICBjb25zdCBzeXN0ZW1Qcm9tcHQgPSBsdW5hU3lzdGVtUHJvbXB0KCdWb2PDqiBlc3TDoSBlbnZpYW5kbyBvIHJlc3VtbyBkYSBwcsOzeGltYSBzZW1hbmEgKGRvbWluZ28gMjA6MDApIHBlbG8gV2hhdHNBcHAuJykgKyAnXG5cbkNvbnRleHRvIGF0dWFsIChkYWRvcyByZWFpcyBkYSBEZW5pc2UsIGFnb3JhKTpcbicgKyBKU09OLnN0cmluZ2lmeShjb250ZXh0LCBudWxsLCAyKQogICAgY29uc3QgcGVkaWRvID0gJ0VzY3JldmEgYSBtZW5zYWdlbSBkZSBwcmVwYXJhw6fDo28gcGFyYSBhIHByw7N4aW1hIHNlbWFuYSBkYSBEZW5pc2UuIENvbWVjZSBjb20gIlNlIHByZXBhcmFuZG8gcGFyYSBhIHNlbWFuYSDwn5eT77iPIiBlIGxpc3RlIG9zIGNvbXByb21pc3NvcyBkYSBhZ2VuZGFfcHJveGltb3NfN2RpYXMsIGNvbnRhcyBhIHZlbmNlciwgZSBhIHByw7N4aW1hIGFwbGljYcOnw6NvIGRlIHRpcnplcGF0aWRhIHNlIGNhaXIgbm9zIHByw7N4aW1vcyA3IGRpYXMuIFNlIG7Do28gaG91dmVyIG5lbmh1bSBjb21wcm9taXNzbyByZWdpc3RyYWRvLCBkaWdhIGlzc28gY29tIG5hdHVyYWxpZGFkZS4gVGVybWluZSBjb20gdW1hIGZyYXNlIGN1cnRhIGRlIGluY2VudGl2byBwYXJhIGEgc2VtYW5hIHF1ZSB2ZW0uIEZvcm1hdG8gZGUgV2hhdHNBcHAsIGVtb2ppcyBjb20gbW9kZXJhw6fDo28sIHNlbSBtYXJrZG93biBkZSBuZWdyaXRvLicKICAgIGNvbnN0IHRleHRvID0gYXdhaXQgYXNrTHVuYShzeXN0ZW1Qcm9tcHQsIFt7IHR5cGU6ICd0ZXh0JywgdGV4dDogcGVkaWRvIH1dKQogICAgYXdhaXQgc2VuZFdoYXRzYXBwVGV4dChudW1lcm8sIHRleHRvKQogICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogIH0gY2F0Y2ggKGVycikgewogICAgcmVzLnN0YXR1cyg1MDApLmpzb24oeyBlcnJvcjogZXJyPy5tZXNzYWdlIHx8ICdlcnJvIGRlc2NvbmhlY2lkbycgfSkKICB9Cn0K",
}

api_dir = Path("api")
api_dir.mkdir(exist_ok=True)
for rel, b64 in files_b64.items():
    p = Path(rel)
    if p.exists():
        raise SystemExit(f"ABORTADO ({rel}-existe): o arquivo {rel} ja existe. Nada foi alterado.")
    p.write_bytes(base64.b64decode(b64))
    applied.append(f"create-{rel}")

# --- 5) Sobrescreve api/whatsapp-webhook.js (versao anterior, agora usando a lib compartilhada) ---
webhook_b64 = "aW1wb3J0IHsgc2VuZFdoYXRzYXBwVGV4dCwgdHJhbnNjcmliZUF1ZGlvLCBhc2tMdW5hLCBidWlsZEx1bmFDb250ZXh0LCBsdW5hU3lzdGVtUHJvbXB0IH0gZnJvbSAnLi9fY3JvbmxpYi5qcycKCmV4cG9ydCBkZWZhdWx0IGFzeW5jIGZ1bmN0aW9uIGhhbmRsZXIocmVxLCByZXMpIHsKICBpZiAocmVxLm1ldGhvZCAhPT0gJ1BPU1QnKSB7CiAgICByZXMuc3RhdHVzKDIwMCkuanNvbih7IG9rOiB0cnVlIH0pCiAgICByZXR1cm4KICB9CiAgdHJ5IHsKICAgIGNvbnN0IGJvZHkgPSByZXEuYm9keSB8fCB7fQogICAgY29uc3QgZXZlbnQgPSBib2R5LmV2ZW50IHx8ICcnCiAgICBpZiAoZXZlbnQgJiYgIS9tZXNzYWdlc1wuP3Vwc2VydC9pLnRlc3QoZXZlbnQpKSB7CiAgICAgIHJlcy5zdGF0dXMoMjAwKS5qc29uKHsgb2s6IHRydWUgfSkKICAgICAgcmV0dXJuCiAgICB9CgogICAgY29uc3QgZGF0YSA9IGJvZHkuZGF0YSB8fCB7fQogICAgY29uc3Qga2V5ID0gZGF0YS5rZXkgfHwge30KICAgIGlmIChrZXkuZnJvbU1lKSB7CiAgICAgIHJlcy5zdGF0dXMoMjAwKS5qc29uKHsgb2s6IHRydWUgfSkKICAgICAgcmV0dXJuCiAgICB9CiAgICBjb25zdCByZW1vdGVKaWQgPSBrZXkucmVtb3RlSmlkIHx8ICcnCiAgICBpZiAoIXJlbW90ZUppZCB8fCByZW1vdGVKaWQuZW5kc1dpdGgoJ0BnLnVzJykpIHsKICAgICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogICAgICByZXR1cm4KICAgIH0KICAgIGNvbnN0IG51bWJlciA9IHJlbW90ZUppZC5zcGxpdCgnQCcpWzBdCgogICAgY29uc3QgYWxsb3dlZCA9IChwcm9jZXNzLmVudi5FVk9MVVRJT05fQUxMT1dFRF9OVU1CRVJTIHx8ICcnKS5zcGxpdCgnLCcpLm1hcCgocykgPT4gcy50cmltKCkpLmZpbHRlcihCb29sZWFuKQogICAgaWYgKGFsbG93ZWQubGVuZ3RoICYmICFhbGxvd2VkLmluY2x1ZGVzKG51bWJlcikpIHsKICAgICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogICAgICByZXR1cm4KICAgIH0KCiAgICBjb25zdCBtc2cgPSBkYXRhLm1lc3NhZ2UgfHwge30KICAgIGxldCB1c2VyVGV4dCA9IChtc2cuY29udmVyc2F0aW9uIHx8IG1zZy5leHRlbmRlZFRleHRNZXNzYWdlPy50ZXh0IHx8ICcnKS50cmltKCkKCiAgICBpZiAobXNnLmF1ZGlvTWVzc2FnZSAmJiBkYXRhLm1lc3NhZ2UuYmFzZTY0KSB7CiAgICAgIHRyeSB7CiAgICAgICAgY29uc3QgdHJhbnNjcmlwdCA9IGF3YWl0IHRyYW5zY3JpYmVBdWRpbyhkYXRhLm1lc3NhZ2UuYmFzZTY0LCBtc2cuYXVkaW9NZXNzYWdlLm1pbWV0eXBlIHx8ICdhdWRpby9vZ2cnKQogICAgICAgIHVzZXJUZXh0ID0gdXNlclRleHQgPyAodXNlclRleHQgKyAnXG5cbihhdWRpbyB0cmFuc2NyaXRvKTogJyArIHRyYW5zY3JpcHQpIDogdHJhbnNjcmlwdAogICAgICB9IGNhdGNoIHsKICAgICAgICBhd2FpdCBzZW5kV2hhdHNhcHBUZXh0KG51bWJlciwgJ1JlY2ViaSBzZXUgw6F1ZGlvIG1hcyBuw6NvIGNvbnNlZ3VpIGVudGVuZGVyIGFnb3JhLiBQb2RlIHRlbnRhciBkZSBub3ZvIG91IGVzY3JldmVyPycpCiAgICAgICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogICAgICAgIHJldHVybgogICAgICB9CiAgICB9CgogICAgY29uc3QgdXNlckNvbnRlbnQgPSBbXQogICAgaWYgKG1zZy5pbWFnZU1lc3NhZ2UgJiYgZGF0YS5tZXNzYWdlLmJhc2U2NCkgewogICAgICB1c2VyQ29udGVudC5wdXNoKHsgdHlwZTogJ2ltYWdlJywgc291cmNlOiB7IHR5cGU6ICdiYXNlNjQnLCBtZWRpYV90eXBlOiBtc2cuaW1hZ2VNZXNzYWdlLm1pbWV0eXBlIHx8ICdpbWFnZS9qcGVnJywgZGF0YTogZGF0YS5tZXNzYWdlLmJhc2U2NCB9IH0pCiAgICB9CgogICAgaWYgKCF1c2VyVGV4dCAmJiB1c2VyQ29udGVudC5sZW5ndGggPT09IDApIHsKICAgICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogICAgICByZXR1cm4KICAgIH0KICAgIHVzZXJDb250ZW50LnB1c2goeyB0eXBlOiAndGV4dCcsIHRleHQ6IHVzZXJUZXh0IHx8ICdBIERlbmlzZSBlbnZpb3UgdW1hIGltYWdlbSBzZW0gbGVnZW5kYSBwZWxvIFdoYXRzQXBwLiBDb21lbnRlIG8gcXVlIHZvY8OqIHbDqiBlIHBlcmd1bnRlIG5vIHF1ZSBwb2RlIGFqdWRhci4nIH0pCgogICAgY29uc3QgY29udGV4dCA9IGF3YWl0IGJ1aWxkTHVuYUNvbnRleHQoKQogICAgY29uc3Qgc3lzdGVtUHJvbXB0ID0gbHVuYVN5c3RlbVByb21wdCgnVm9jw6ogZXN0w6EgcmVzcG9uZGVuZG8gYWdvcmEgcGVsbyBXaGF0c0FwcCwgY29tIHJlc3Bvc3RhcyBjdXJ0YXMgKDIgYSA1IGZyYXNlcykuJykgKyAnXG5cbkNvbnRleHRvIGF0dWFsIChkYWRvcyByZWFpcyBkYSBEZW5pc2UsIGFnb3JhKTpcbicgKyBKU09OLnN0cmluZ2lmeShjb250ZXh0LCBudWxsLCAyKQoKICAgIGNvbnN0IHJlcGx5ID0gYXdhaXQgYXNrTHVuYShzeXN0ZW1Qcm9tcHQsIHVzZXJDb250ZW50KQogICAgYXdhaXQgc2VuZFdoYXRzYXBwVGV4dChudW1iZXIsIHJlcGx5KQogICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogIH0gY2F0Y2ggewogICAgcmVzLnN0YXR1cygyMDApLmpzb24oeyBvazogdHJ1ZSB9KQogIH0KfQo="
Path("api/whatsapp-webhook.js").write_bytes(base64.b64decode(webhook_b64))
applied.append("update-api-whatsapp-webhook")

# --- 6) vercel.json com os crons ---
vercel_b64 = "ewogICJyZXdyaXRlcyI6IFt7ICJzb3VyY2UiOiAiLygoPyFhcGkvKS4qKSIsICJkZXN0aW5hdGlvbiI6ICIvIiB9XSwKICAiY3JvbnMiOiBbCiAgICB7ICJwYXRoIjogIi9hcGkvY3Jvbi1tb3JuaW5nIiwgInNjaGVkdWxlIjogIjAgOSAqICogKiIgfSwKICAgIHsgInBhdGgiOiAiL2FwaS9jcm9uLWV2ZW5pbmciLCAic2NoZWR1bGUiOiAiMCAyMyAqICogKiIgfSwKICAgIHsgInBhdGgiOiAiL2FwaS9jcm9uLXdlZWtseSIsICJzY2hlZHVsZSI6ICI1IDIzICogKiA1IiB9LAogICAgeyAicGF0aCI6ICIvYXBpL2Nyb24tbmV4dHdlZWsiLCAic2NoZWR1bGUiOiAiMTAgMjMgKiAqIDAiIH0KICBdCn0K"
Path("vercel.json").write_bytes(base64.b64decode(vercel_b64))
applied.append("update-vercel-json-crons")

print("TUDO OK:", applied)
