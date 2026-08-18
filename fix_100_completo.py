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

# --- 1) Helpers globais de agua (registro diario de verdade, nao mais um contador que nunca zera) ---
old_c = "const C={bg:'#0a0a0f',s:'#16161f',s2:'#1c1c28',s3:'#22222f',line:'rgba(255,255,255,.07)',acc:'#8b5cf6',acc2:'#a78bfa',ok:'#34d399',water:'#38bdf8',warn:'#fbbf24',danger:'#f87171',pink:'#f472b6',teal:'#2dd4bf'}"
new_c = old_c + """
function hojeIsoAgua(){return new Date().toISOString().slice(0,10)}
function lerAguaHoje(){
  try{
    const iso=hojeIsoAgua()
    const log=JSON.parse(localStorage.getItem('dos_agua_log')||'{}')
    if(typeof log[iso]==='number')return log[iso]
    return Number(localStorage.getItem('dos_wat')||0)
  }catch{return 0}
}
function salvarAguaHoje(ml:number){
  try{
    const iso=hojeIsoAgua()
    const log=JSON.parse(localStorage.getItem('dos_agua_log')||'{}')
    log[iso]=ml
    localStorage.setItem('dos_agua_log',JSON.stringify(log))
  }catch{}
}"""
s = replace_once(s, old_c, new_c, "helpers-agua-globais")
applied.append("Helpers globais de agua criados (dos_agua_log)")

# --- 2) Home(): agua usa o registro diario em vez do contador que nunca reseta ---
old_h1 = "const [wat,setWat]=React.useState(()=>Number(localStorage.getItem('dos_wat')||1800));"
new_h1 = "const [wat,setWat]=React.useState(lerAguaHoje);"
s = replace_once(s, old_h1, new_h1, "home-wat-init")
applied.append("Home(): agua inicial vem do registro diario")

old_h2 = "const addW=(ml:number)=>{const n=Math.min(wat+ml,4000);setWat(n);localStorage.setItem('dos_wat',String(n))};"
new_h2 = "const addW=(ml:number)=>{const n=Math.min(wat+ml,4000);setWat(n);salvarAguaHoje(n)};"
s = replace_once(s, old_h2, new_h2, "home-addW")
applied.append("Home(): addW grava no registro diario")

# --- 3) Home(): card 'Desenvolvimento' mostra o livro atual de verdade, nao mais 45% fixo ---
old_h3 = "  const leituraHoje=leiturasHome.some((l:any)=>l.data===hojeIsoHome)\n  const lembretes:[string,string,string][]=[]"
new_h3 = """  const leituraHoje=leiturasHome.some((l:any)=>l.data===hojeIsoHome)
  const livroAtualHome=(()=>{try{return JSON.parse(localStorage.getItem('dos_livro_atual')||'null')}catch{return null}})() as any
  const livroPctHome=livroAtualHome&&livroAtualHome.totalPaginas>0?Math.min(100,Math.round(livroAtualHome.paginaAtual/livroAtualHome.totalPaginas*100)):0
  const lembretes:[string,string,string][]=[]"""
s = replace_once(s, old_h3, new_h3, "home-livro-const")
applied.append("Home(): const do livro atual adicionada")

old_h4 = "<div style={{fontWeight:700,fontSize:14,marginBottom:4}}>Hábitos Atômicos</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:10}}>James Clear · 45%</div><div style={{height:9,borderRadius:6,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:'45%',borderRadius:6,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div>"
new_h4 = "{livroAtualHome&&livroAtualHome.titulo?<><div style={{fontWeight:700,fontSize:14,marginBottom:4}}>{livroAtualHome.titulo}</div><div style={{fontSize:12,color:'rgba(255,255,255,.4)',marginBottom:10}}>{livroAtualHome.autor||'Autor não informado'} · {livroPctHome}%</div><div style={{height:9,borderRadius:6,background:C.s3,overflow:'hidden'}}><div style={{height:'100%',width:`${livroPctHome}%`,borderRadius:6,background:`linear-gradient(90deg,${C.acc2},${C.acc})`}}/></div></>:<div style={{fontSize:13,color:'rgba(255,255,255,.4)'}}>Nenhum livro em andamento. <NavLink to=\"/desenvolvimento\" style={{color:C.acc2}}>Adicionar</NavLink></div>}"
s = replace_once(s, old_h4, new_h4, "home-livro-card")
applied.append("Home(): card Desenvolvimento mostra o livro atual de verdade")

# --- 4) Alimentacao(): mesma correcao de agua (era um segundo contador que nunca reseta, agora usa o mesmo registro diario) ---
old_a1 = "const [wat,setWat]=React.useState(()=>Number(localStorage.getItem('dos_wat')||0))"
new_a1 = "const [wat,setWat]=React.useState(lerAguaHoje)"
s = replace_once(s, old_a1, new_a1, "alimentacao-wat-init")
applied.append("Alimentacao(): agua inicial vem do registro diario")

old_a2 = "const addW=(ml:number)=>{const n=Math.min(wat+ml,6000);setWat(n);localStorage.setItem('dos_wat',String(n))}"
new_a2 = "const addW=(ml:number)=>{const n=Math.min(wat+ml,6000);setWat(n);salvarAguaHoje(n)}"
s = replace_once(s, old_a2, new_a2, "alimentacao-addW")
applied.append("Alimentacao(): addW grava no registro diario")

old_a3 = "localStorage.removeItem('dos_refs');localStorage.removeItem('dos_wat');localStorage.removeItem('dos_prot')"
new_a3 = "localStorage.removeItem('dos_refs');salvarAguaHoje(0);localStorage.removeItem('dos_prot')"
s = replace_once(s, old_a3, new_a3, "alimentacao-limpar-dia")
applied.append("Alimentacao(): 'Limpar dia' zera o registro diario certo")

# --- 5) Relatorios: agua do relatorio vem do mesmo registro diario ---
old_r1 = "const watR=Number(localStorage.getItem('dos_wat')||0)"
new_r1 = "const watR=lerAguaHoje()"
s = replace_once(s, old_r1, new_r1, "relatorios-watR")
applied.append("Relatorios(): agua do dia vem do registro diario")

# --- 6) Shell(): sincronizacao quase em tempo real (poucos segundos) em vez de a cada 5 minutos ---
old_sync = """  },[])
  return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}>"""
new_sync_and_score = """  },[])
  const ROTINA_DEF_SHELL=[{t:'05:30',n:'Devocional',cat:'Espiritual'},{t:'06:00',n:'Acordar · água · humor',cat:'Saúde'},{t:'06:30',n:'Café · whey · creatina',cat:'Alimentação'},{t:'07:00',n:'Levar crianças à escola',cat:'Família'},{t:'07:30',n:'Calistenia',cat:'Exercícios'},{t:'08:20',n:'Banho · skincare',cat:'Casa'},{t:'08:45',n:'Planejar o dia · prioridades',cat:'Trabalho'},{t:'09:30',n:'Lanche da manhã',cat:'Alimentação'},{t:'12:50',n:'Buscar Domi',cat:'Família'},{t:'15:30',n:'Whey da tarde',cat:'Alimentação'},{t:'17:00',n:'Buscar Derick',cat:'Família'},{t:'19:00',n:'Jantar',cat:'Alimentação'},{t:'20:00',n:'Célula (Qua) / Aula (Sex)',cat:'Compromisso'},{t:'21:30',n:'Probióticos',cat:'Saúde'},{t:'22:00',n:'Leitura · 20 min',cat:'Desenvolvimento'}]
  const rotinaItensShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_rotina')||'null')||ROTINA_DEF_SHELL}catch{return ROTINA_DEF_SHELL}})() as any[]
  function diasUnicosShell(entries:any[]){return new Set(entries.map((e:any)=>e.data))}
  function sequenciaShell(dias:Set<string>){
    let n=0
    const dt=new Date()
    while(dias.has(dt.toISOString().slice(0,10))){n++;dt.setDate(dt.getDate()-1)}
    return n
  }
  function pctDiaShell(iso:string){
    try{
      const done=JSON.parse(localStorage.getItem(`dos_rotina_done_${iso}`)||'[]')
      return rotinaItensShell.length>0?done.length/rotinaItensShell.length:0
    }catch{return 0}
  }
  function sequenciaAguaShell(){
    let n=0
    const dt=new Date()
    try{
      const log=JSON.parse(localStorage.getItem('dos_agua_log')||'{}')
      while((log[dt.toISOString().slice(0,10)]||0)>=2500){n++;dt.setDate(dt.getDate()-1)}
    }catch{}
    return n
  }
  const devEntriesShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  const treinosShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]
  const leiturasShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  const seqEspiritual=sequenciaShell(diasUnicosShell(devEntriesShell))
  const seqTreino=sequenciaShell(diasUnicosShell(treinosShell))
  const seqLeitura=sequenciaShell(diasUnicosShell(leiturasShell))
  const seqAgua=sequenciaAguaShell()
  const ultimos7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(6-i));return d.toISOString().slice(0,10)})
  const anteriores7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(13-i));return d.toISOString().slice(0,10)})
  const pctSemanaAtual=ultimos7Shell.map(pctDiaShell)
  const pctSemanaAnterior=anteriores7Shell.map(pctDiaShell)
  const mediaAtual=Math.round(pctSemanaAtual.reduce((a,b)=>a+b,0)/7*100)
  const mediaAnterior=Math.round(pctSemanaAnterior.reduce((a,b)=>a+b,0)/7*100)
  const deltaSemana=mediaAtual-mediaAnterior
  return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}>"""
s = replace_once(s, old_sync, new_sync_and_score, "shell-score-real")
applied.append("Shell(): score da semana e sequencias (Espiritual/Treino/Leitura/Agua) com dado real")

old_score = "<span style={{fontSize:28,fontWeight:800}}>92%</span><span style={{fontSize:11,color:C.ok,fontWeight:700}}>▲ 8%</span>"
new_score = "<span style={{fontSize:28,fontWeight:800}}>{mediaAtual}%</span><span style={{fontSize:11,color:deltaSemana>=0?C.ok:C.danger,fontWeight:700}}>{deltaSemana>=0?'▲':'▼'} {Math.abs(deltaSemana)}%</span>"
s = replace_once(s, old_score, new_score, "shell-score-percent")
applied.append("Shell(): % do score da semana com dado real")

old_bars = "{[60,80,70,90,75,85,40].map((h,i)=><span key={i} style={{flex:1,borderRadius:'3px 3px 2px 2px',height:`${h}%`,background:i<3?`linear-gradient(180deg,${C.ok},#15803d)`:`linear-gradient(180deg,${C.acc2},#6d28d9)`}}/>)}"
new_bars = "{pctSemanaAtual.map((p,i)=><span key={i} style={{flex:1,borderRadius:'3px 3px 2px 2px',height:`${Math.max(Math.round(p*100),3)}%`,background:i===6?`linear-gradient(180deg,${C.ok},#15803d)`:`linear-gradient(180deg,${C.acc2},#6d28d9)`}}/>)}"
s = replace_once(s, old_bars, new_bars, "shell-score-bars")
applied.append("Shell(): barras do grafico semanal com dado real")

old_streak = "{[{n:12,l:'Espiritual',c:C.pink},{n:8,l:'Treino',c:C.ok},{n:10,l:'Leitura',c:C.warn},{n:7,l:'Água',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}"
new_streak = "{[{n:seqEspiritual,l:'Espiritual',c:C.pink},{n:seqTreino,l:'Treino',c:C.ok},{n:seqLeitura,l:'Leitura',c:C.warn},{n:seqAgua,l:'Água',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}"
s = replace_once(s, old_streak, new_streak, "shell-sequencia-real")
applied.append("Shell(): sequencias (Espiritual/Treino/Leitura/Agua) com dado real")

old_interval = """    sincronizarSnapshot()
    const t=setInterval(sincronizarSnapshot,5*60*1000)
    window.addEventListener('beforeunload',sincronizarSnapshot)
    return()=>{clearInterval(t);window.removeEventListener('beforeunload',sincronizarSnapshot)}
  },[])"""
new_interval = """    sincronizarSnapshot()
    const t=setInterval(sincronizarSnapshot,30*1000)
    let debounceSync:any=null
    const origSetItem=localStorage.setItem.bind(localStorage)
    localStorage.setItem=function(key:string,value:string){
      origSetItem(key,value)
      if(key.startsWith('dos_')){
        if(debounceSync)clearTimeout(debounceSync)
        debounceSync=setTimeout(sincronizarSnapshot,4000)
      }
    }
    function sincronizarSeEscondeu(){if(document.hidden)sincronizarSnapshot()}
    window.addEventListener('beforeunload',sincronizarSnapshot)
    document.addEventListener('visibilitychange',sincronizarSeEscondeu)
    return()=>{
      clearInterval(t)
      if(debounceSync)clearTimeout(debounceSync)
      localStorage.setItem=origSetItem
      window.removeEventListener('beforeunload',sincronizarSnapshot)
      document.removeEventListener('visibilitychange',sincronizarSeEscondeu)
    }
  },[])"""
s = replace_once(s, old_interval, new_interval, "shell-sync-realtime")
applied.append("Shell(): sincronizacao quase em tempo real (poucos segundos, nao mais 5 min)")

main_file.write_text(s)
print("OK - alteracoes aplicadas:")
for a in applied:
    print(" -", a)
print()
print("IMPORTANTE - rode esta SQL no Supabase SQL Editor (fecha uma brecha de seguranca):")
print("""
alter policy "app_snapshot_all" on app_snapshot using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
alter policy "google_tokens_all" on google_tokens using (auth.role() = 'authenticated') with check (auth.role() = 'authenticated');
""")
print("Isso impede que alguem com a chave publica do site (que fica visivel no navegador) leia ou")
print("escreva nessas 2 tabelas sem estar logada. As outras tabelas (tirzepatida_*, etc.) foram criadas")
print("antes desta conversa - se quiser, me manda a lista de policies delas (Supabase > Authentication >")
print("Policies) que eu reviso e mando a correcao junto.")
