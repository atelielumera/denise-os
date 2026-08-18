from pathlib import Path
import os

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

# --- 0) limpar o script anterior que ficou parado no repo sem efeito (abortou antes de mudar nada) ---
old_script = Path("fix_100_completo.py")
if old_script.exists():
    old_script.unlink()
    applied.append("fix_100_completo.py removido (tinha abortado sem alterar nada)")

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

# --- 4) Alimentacao(): mesma correcao de agua ---
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

# --- 6) Shell(): o anel 'Rotina' (adicionado no ultimo script) volta a ser 'Agua', agora com dado de verdade ---
old_seq_fn = """function sequenciaRotinaShell(){
    let n=0
    const dt=new Date()
    while(pctDiaShell(dt.toISOString().slice(0,10))>=1){n++;dt.setDate(dt.getDate()-1)}
    return n
  }
  """
new_seq_fn = """function sequenciaAguaShell(){
    let n=0
    const dt=new Date()
    try{
      const log=JSON.parse(localStorage.getItem('dos_agua_log')||'{}')
      while((log[dt.toISOString().slice(0,10)]||0)>=2500){n++;dt.setDate(dt.getDate()-1)}
    }catch{}
    return n
  }
  """
s = replace_once(s, old_seq_fn, new_seq_fn, "shell-sequencia-agua-fn")
applied.append("Shell(): funcao de sequencia de agua adicionada")

old_seq_call = "  const seqRotina=sequenciaRotinaShell()\n"
new_seq_call = "  const seqAgua=sequenciaAguaShell()\n"
s = replace_once(s, old_seq_call, new_seq_call, "shell-sequencia-agua-call")
applied.append("Shell(): sequencia de agua calculada")

old_streak = "{[{n:seqEspiritual,l:'Espiritual',c:C.pink},{n:seqTreino,l:'Treino',c:C.ok},{n:seqLeitura,l:'Leitura',c:C.warn},{n:seqRotina,l:'Rotina',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}"
new_streak = "{[{n:seqEspiritual,l:'Espiritual',c:C.pink},{n:seqTreino,l:'Treino',c:C.ok},{n:seqLeitura,l:'Leitura',c:C.warn},{n:seqAgua,l:'Água',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}"
s = replace_once(s, old_streak, new_streak, "shell-sequencia-jsx")
applied.append("Shell(): anel volta a mostrar 'Água' com sequencia real")

# --- 7) Shell(): sincronizacao quase em tempo real (poucos segundos) em vez de a cada 5 minutos ---
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
