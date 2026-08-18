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

# --- Shell(): calcular score da semana e sequencias com dados reais em vez de numeros fixos ---
old_insert = """  },[])
  return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}>"""
new_insert = """  },[])
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
  function sequenciaRotinaShell(){
    let n=0
    const dt=new Date()
    while(pctDiaShell(dt.toISOString().slice(0,10))>=1){n++;dt.setDate(dt.getDate()-1)}
    return n
  }
  const devEntriesShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  const treinosShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_treinos')||'[]')}catch{return []}})() as any[]
  const leiturasShell=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  const seqEspiritual=sequenciaShell(diasUnicosShell(devEntriesShell))
  const seqTreino=sequenciaShell(diasUnicosShell(treinosShell))
  const seqLeitura=sequenciaShell(diasUnicosShell(leiturasShell))
  const seqRotina=sequenciaRotinaShell()
  const ultimos7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(6-i));return d.toISOString().slice(0,10)})
  const anteriores7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(13-i));return d.toISOString().slice(0,10)})
  const pctSemanaAtual=ultimos7Shell.map(pctDiaShell)
  const pctSemanaAnterior=anteriores7Shell.map(pctDiaShell)
  const mediaAtual=Math.round(pctSemanaAtual.reduce((a,b)=>a+b,0)/7*100)
  const mediaAnterior=Math.round(pctSemanaAnterior.reduce((a,b)=>a+b,0)/7*100)
  const deltaSemana=mediaAtual-mediaAnterior
  return(<div style={{display:'flex',minHeight:'100vh',background:C.bg,color:'#f3f3f8'}}>"""
s = replace_once(s, old_insert, new_insert, "shell-calc-real-data")
applied.append("Shell(): calculo real de score/sequencias adicionado")

old_score = """<span style={{fontSize:28,fontWeight:800}}>92%</span><span style={{fontSize:11,color:C.ok,fontWeight:700}}>▲ 8%</span>"""
new_score = """<span style={{fontSize:28,fontWeight:800}}>{mediaAtual}%</span><span style={{fontSize:11,color:deltaSemana>=0?C.ok:C.danger,fontWeight:700}}>{deltaSemana>=0?'▲':'▼'} {Math.abs(deltaSemana)}%</span>"""
s = replace_once(s, old_score, new_score, "shell-score-percent")
applied.append("Shell(): % do score da semana com dado real")

old_bars = """{[60,80,70,90,75,85,40].map((h,i)=><span key={i} style={{flex:1,borderRadius:'3px 3px 2px 2px',height:`${h}%`,background:i<3?`linear-gradient(180deg,${C.ok},#15803d)`:`linear-gradient(180deg,${C.acc2},#6d28d9)`}}/>)}"""
new_bars = """{pctSemanaAtual.map((p,i)=><span key={i} style={{flex:1,borderRadius:'3px 3px 2px 2px',height:`${Math.max(Math.round(p*100),3)}%`,background:i===6?`linear-gradient(180deg,${C.ok},#15803d)`:`linear-gradient(180deg,${C.acc2},#6d28d9)`}}/>)}"""
s = replace_once(s, old_bars, new_bars, "shell-score-bars")
applied.append("Shell(): barras do grafico semanal com dado real")

old_streak = """{[{n:12,l:'Espiritual',c:C.pink},{n:8,l:'Treino',c:C.ok},{n:10,l:'Leitura',c:C.warn},{n:7,l:'Água',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}"""
new_streak = """{[{n:seqEspiritual,l:'Espiritual',c:C.pink},{n:seqTreino,l:'Treino',c:C.ok},{n:seqLeitura,l:'Leitura',c:C.warn},{n:seqRotina,l:'Rotina',c:C.water}].map(s=>(<div key={s.l} style={{display:'flex',flexDirection:'column',alignItems:'center',gap:4}}><div style={{width:40,height:40,borderRadius:'50%',display:'grid',placeItems:'center',fontWeight:800,fontSize:13,boxShadow:`inset 0 0 0 2px ${s.c}`,color:s.c}}>{s.n}</div><small style={{fontSize:9,color:'#7d7d90'}}>{s.l}</small></div>))}"""
s = replace_once(s, old_streak, new_streak, "shell-sequencia-real")
applied.append("Shell(): sequencias (Espiritual/Treino/Leitura/Rotina) com dado real")

main_file.write_text(s)
print("OK - alteracoes aplicadas:")
for a in applied:
    print(" -", a)
print()
print("Observacao: o anel 'Agua' virou 'Rotina' (% de dias com a rotina 100% concluida),")
print("porque a agua nao tem um historico diario salvo hoje - so o total do dia atual.")
print("Se quiser um streak real de agua, preciso adicionar um registro diario de consumo primeiro.")
