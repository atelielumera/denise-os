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

# 1) Reescreve Relatorios() por completo: visao historica/comparativa real, com filtro de
#    periodo (semana/30d/90d/ano/personalizado), filtro de area, comparacao automatica com
#    o periodo anterior de mesma duracao, grafico reaproveitando LinhaEvolucao, destaques
#    reais e integracao "Perguntar a Luna sobre este relatorio".
old = """function Relatorios(){
  const [tzSched,setTzSched]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [tzBalance,setTzBalance]=React.useState(0)
  const [tzApps,setTzApps]=React.useState<any[]>([])
  React.useEffect(()=>{(async()=>{
    const [{data:sched},{data:bal},{data:apps}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
      supabase.from('tirzepatida_applications').select('*').order('applied_at',{ascending:false}),
    ])
    const map:Record<string,any>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={planned_dose_mg:Number(row.planned_dose_mg),interval_days:row.interval_days,next_application_date:row.next_application_date}})
    setTzSched(map)
    setTzBalance(Number(bal?.current_balance_mg??0))
    setTzApps(apps||[])
  })()},[])
  function fmtIsoR(iso:string|null|undefined){if(!iso)return '—';return new Date(iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric'})}
  const tzAutonomyR=(()=>{const dDen=tzSched.denise?.planned_dose_mg||5;const dFla=tzSched.flavio?.planned_dose_mg||2.5;const iDen=tzSched.denise?.interval_days||5;const iFla=tzSched.flavio?.interval_days||7;const mgDay=dDen/iDen+dFla/iFla;return mgDay>0?Math.floor(tzBalance/mgDay):0})()
  function segRel(d:Date){const x=new Date(d);const day=x.getDay();const diff=(day===0?-6:1-day);x.setDate(x.getDate()+diff);x.setHours(0,0,0,0);return x}
  const segAtualR=segRel(new Date())
  const treinosR=(()=>{try{return (JSON.parse(localStorage.getItem('dos_treinos')||'[]') as any[]).filter(t=>t.status!=='nao_realizado')}catch{return []}})() as any[]
  const leiturasR=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  const devR=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  const diasAtivosR=new Set<string>([...treinosR.map((t:any)=>t.data),...leiturasR.map((l:any)=>l.data),...devR.map((e:any)=>e.data)])
  const semanasScore=Array.from({length:7},(_,i)=>{
    const inicio=new Date(segAtualR);inicio.setDate(inicio.getDate()-(6-i)*7)
    let ativos=0
    for(let d=0;d<7;d++){const dia=new Date(inicio);dia.setDate(dia.getDate()+d);if(diasAtivosR.has(isoBR(dia)))ativos++}
    return {s:`${String(inicio.getDate()).padStart(2,'0')}/${String(inicio.getMonth()+1).padStart(2,'0')}`,v:Math.round(ativos/7*100)}
  })
  function diasComEntradaUltimos(entries:any[],dias:number){
    const limite=new Date();limite.setDate(limite.getDate()-dias)
    return new Set(entries.filter((e:any)=>new Date(e.data+'T00:00:00')>=limite).map((e:any)=>e.data)).size
  }
  const periodoDias=30
  const espDiasR=diasComEntradaUltimos(devR,periodoDias)
  const exDiasR=diasComEntradaUltimos(treinosR,periodoDias)
  const espPctR=Math.min(100,Math.round(espDiasR/periodoDias*100))
  const exPctR=Math.min(100,Math.round(exDiasR/periodoDias*100))
  const hojeIsoR=isoBR(new Date())
  const watR=lerAguaHoje()
  const protR=totalProteinaDia(hojeIsoR)
  const hidPctR=Math.min(100,Math.round(watR/Number(localStorage.getItem('dos_meta_agua_ml')||2500)*100))
  const aliPctR=Math.min(100,Math.round(protR/lerMetaProteina()*100))
  const pessoasSchedR=Object.keys(tzSched)
  const emDiaR=pessoasSchedR.filter(pid=>{const nd=tzSched[pid].next_application_date;return nd&&nd>=hojeIsoR}).length
  const tzPctR=pessoasSchedR.length>0?Math.round(emDiaR/pessoasSchedR.length*100):0
  const refsLogR=lerRefsLog()
  const diasPeriodoR=Array.from({length:periodoDias},(_,i)=>{const d=new Date();d.setDate(d.getDate()-i);return isoBR(d)})
  const diasComMetaProtR=diasPeriodoR.filter(iso=>{const refs=refsLogR[iso]||[];return refs.reduce((a,r)=>a+(r.prot||0),0)>=lerMetaProteina()}).length
  const pctMetaProtR=Math.round(diasComMetaProtR/periodoDias*100)
  const mediaRefeicoesR=(diasPeriodoR.reduce((a,iso)=>a+((refsLogR[iso]||[]).length),0)/periodoDias).toFixed(1)
  const resumoPeriodo:[string,string,string][]=[
    ['Espiritual',`${espPctR}%`,C.acc2],
    ['Exercícios',`${exPctR}%`,C.ok],
    ['Alimentação (hoje)',`${aliPctR}%`,C.warn],
    ['Hidratação (hoje)',`${hidPctR}%`,C.warn],
    ['Refeições/dia (média)',mediaRefeicoesR,C.warn],
    ['Meta de proteína batida',`${pctMetaProtR}%`,C.ok],
    ['Tirzepatida',pessoasSchedR.length>0?`${tzPctR}%`:'—',C.ok],
  ]
  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Relatórios</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Consistência das últimas 7 semanas · resumo dos últimos {periodoDias} dias</p>
    <Card title="Consistência semanal (dias com treino, leitura ou devocional)">
      <div style={{display:'flex',alignItems:'flex-end' as const,gap:10,height:130,padding:'10px 0'}}>{semanasScore.map(b=>(<div key={b.s} style={{flex:1,display:'flex',flexDirection:'column' as const,alignItems:'center',gap:6}}><div style={{flex:1,width:'100%',display:'flex',alignItems:'flex-end' as const}}><div style={{width:'100%',borderRadius:'5px 5px 2px 2px',background:`linear-gradient(180deg,${C.acc2},#6d28d9)`,height:`${b.v}%`}}/></div><span style={{fontSize:11,color:'rgba(255,255,255,.4)'}}>{b.s}</span></div>))}</div>
    </Card>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginTop:16}}>
      <Card title={`Resumo dos últimos ${periodoDias} dias`}>{resumoPeriodo.map(([lbl,v,c])=>(<div key={lbl} style={{display:'flex',alignItems:'center',gap:10,padding:'9px 0',borderBottom:`1px solid ${C.line}`}}><span style={{flex:1,fontSize:13}}>{lbl}</span><span style={{fontWeight:700,color:c}}>{v}</span></div>))}</Card>
      <Card title="Tirzepatida">{[['Aplicações',String(tzApps.length)],['Estoque atual',`${tzBalance} mg`],['Autonomia',`~${tzAutonomyR} dias`],['Sua próxima',fmtIsoR(tzSched.denise?.next_application_date)],['Flávio',fmtIsoR(tzSched.flavio?.next_application_date)]].map(([lbl,v])=>(<div key={lbl} style={{display:'flex',justifyContent:'space-between' as const,padding:'9px 0',borderBottom:`1px solid ${C.line}`,fontSize:13}}><span style={{color:'rgba(255,255,255,.6)'}}>{lbl}</span><span style={{fontWeight:600}}>{v}</span></div>))}</Card>
    </div>
  </div>)
}"""
new = r'''type AreaRel='geral'|'saude'|'alimentacao'|'exercicios'|'espiritual'|'familia'|'trabalho'|'desenvolvimento'|'casa'
const AREAS_REL_INFO:{key:AreaRel,nome:string,icone:string,rota:string}[]=[
  {key:'geral',nome:'Visão geral',icone:'📊',rota:'/relatorios'},
  {key:'saude',nome:'Saúde',icone:'❤️',rota:'/saude'},
  {key:'alimentacao',nome:'Alimentação',icone:'🍽️',rota:'/alimentacao'},
  {key:'exercicios',nome:'Exercícios',icone:'💪',rota:'/exercicios'},
  {key:'espiritual',nome:'Espiritual',icone:'📖',rota:'/espiritual'},
  {key:'familia',nome:'Família',icone:'👨‍👩‍👧',rota:'/familia'},
  {key:'trabalho',nome:'Trabalho',icone:'💼',rota:'/trabalho'},
  {key:'desenvolvimento',nome:'Desenvolvimento',icone:'📈',rota:'/desenvolvimento'},
  {key:'casa',nome:'Casa',icone:'🏡',rota:'/casa'},
]
function diasIntervaloRel(inicioIso:string,fimIso:string):string[]{
  const out:string[]=[]
  let d=new Date(inicioIso+'T12:00:00')
  const fim=new Date(fimIso+'T12:00:00')
  let guarda=0
  while(d.getTime()<=fim.getTime()&&guarda<3660){out.push(isoBR(d));d.setDate(d.getDate()+1);guarda++}
  return out
}
function calcularJanelaRel(periodo:'semana'|'30d'|'90d'|'ano'|'personalizado',ini:string,fim:string){
  const hoje=isoBR(new Date())
  let inicioIso=hoje,fimIso=hoje
  if(periodo==='semana'){const d=new Date();const dw=d.getDay();const diff=(dw===0?-6:1-dw);const seg=new Date(d);seg.setDate(seg.getDate()+diff);inicioIso=isoBR(seg);fimIso=hoje}
  else if(periodo==='30d'){const d=new Date();d.setDate(d.getDate()-29);inicioIso=isoBR(d);fimIso=hoje}
  else if(periodo==='90d'){const d=new Date();d.setDate(d.getDate()-89);inicioIso=isoBR(d);fimIso=hoje}
  else if(periodo==='ano'){inicioIso=`${new Date().getFullYear()}-01-01`;fimIso=hoje}
  else{inicioIso=ini||(()=>{const d=new Date();d.setDate(d.getDate()-29);return isoBR(d)})();fimIso=fim||hoje}
  const diasAtual=diasIntervaloRel(inicioIso,fimIso)
  const n=diasAtual.length||1
  const antFim=new Date(inicioIso+'T12:00:00');antFim.setDate(antFim.getDate()-1)
  const antIni=new Date(antFim);antIni.setDate(antIni.getDate()-(n-1))
  return {inicioIso,fimIso,diasAtual,inicioAntIso:isoBR(antIni),fimAntIso:isoBR(antFim)}
}
function sequenciaMaximaNoPeriodo(diasAtivos:Set<string>,periodo:string[]):number{
  let max=0,atual=0
  for(const iso of periodo){if(diasAtivos.has(iso)){atual++;max=Math.max(max,atual)}else atual=0}
  return max
}
function Relatorios(){
  const navigate=useNavigate()
  const [tzSched,setTzSched]=React.useState<Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>>({})
  const [tzBalance,setTzBalance]=React.useState(0)
  const [tzApps,setTzApps]=React.useState<any[]>([])
  React.useEffect(()=>{(async()=>{
    const [{data:sched},{data:bal},{data:apps}]=await Promise.all([
      supabase.from('tirzepatida_schedule').select('*'),
      supabase.from('tirzepatida_stock_balance').select('*').maybeSingle(),
      supabase.from('tirzepatida_applications').select('*').order('applied_at',{ascending:false}),
    ])
    const map:Record<string,any>={}
    ;(sched||[]).forEach((row:any)=>{map[row.person]={planned_dose_mg:Number(row.planned_dose_mg),interval_days:row.interval_days,next_application_date:row.next_application_date}})
    setTzSched(map)
    setTzBalance(Number(bal?.current_balance_mg??0))
    setTzApps(apps||[])
  })()},[])
  const [periodoRel,setPeriodoRel]=React.useState<'semana'|'30d'|'90d'|'ano'|'personalizado'>('30d')
  const [personalizadoIniRel,setPersonalizadoIniRel]=React.useState('')
  const [personalizadoFimRel,setPersonalizadoFimRel]=React.useState('')
  const [areaRel,setAreaRel]=React.useState<AreaRel>('geral')
  const [granularidadeRel,setGranularidadeRel]=React.useState<'dia'|'semana'|'mes'>('semana')

  const janela=calcularJanelaRel(periodoRel,personalizadoIniRel,personalizadoFimRel)
  const diasAtualRel=janela.diasAtual
  const diasAnteriorRel=diasIntervaloRel(janela.inicioAntIso,janela.fimAntIso)

  const devRel=lerDevocionais()
  const treinosRel=lerTreinos().filter(t=>t.status==='concluido')
  const sessoesLeituraRel=lerSessoesLeituraDev()
  const sessoesEstudoRel=lerSessoesEstudoDev()
  const refsLogRel=lerRefsLog()
  const aguaLogRel=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
  const metaAguaRel=Number(localStorage.getItem('dos_meta_agua_ml')||2500)
  const metaProteinaRel=lerMetaProteina()
  const casaItensRel=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_casa_items')||'[]');return Array.isArray(raw)?raw.map(migrarItemCasa):[]}catch{return []}})() as CasaItem[]
  const trabalhoItensRel=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_trabalho')||'[]');return Array.isArray(raw)?raw.map(migrarTarefaTrab):[]}catch{return []}})() as TarefaTrab[]
  const avalsFamRel=(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})() as Record<string,any[]>

  const diasEspiritualRel=new Set(devRel.map((d:any)=>d.data))
  const diasExerciciosRel=new Set(treinosRel.map(t=>t.data))
  const diasDesenvolvimentoRel=new Set([...sessoesLeituraRel.map(s=>s.data),...sessoesEstudoRel.map(s=>s.data)])
  const diasAlimentacaoRel=new Set(Object.keys(refsLogRel).filter(iso=>(refsLogRel[iso]||[]).length>0))
  const diasSaudeRel=new Set(Object.keys(aguaLogRel).filter(iso=>Number(aguaLogRel[iso]||0)>0))
  const diasTrabalhoRel=new Set(trabalhoItensRel.filter(t=>t.concluidaEm).map(t=>String(t.concluidaEm).slice(0,10)))
  const diasCasaRel=new Set(casaItensRel.flatMap(it=>[it.compradoEm,it.concluidaEm,it.pagoEm].filter(Boolean).map(d=>String(d).slice(0,10))))

  const AREAS_SCORE_REL:{chave:AreaRel,nome:string,set:Set<string>}[]=[
    {chave:'saude',nome:'Saúde',set:diasSaudeRel},
    {chave:'exercicios',nome:'Exercícios',set:diasExerciciosRel},
    {chave:'desenvolvimento',nome:'Desenvolvimento',set:diasDesenvolvimentoRel},
    {chave:'espiritual',nome:'Espiritual',set:diasEspiritualRel},
    {chave:'alimentacao',nome:'Alimentação',set:diasAlimentacaoRel},
    {chave:'casa',nome:'Casa',set:diasCasaRel},
    {chave:'trabalho',nome:'Trabalho',set:diasTrabalhoRel},
  ]
  function scoreAreaRel(set:Set<string>,dias:string[]):number{if(dias.length===0)return 0;const ativos=dias.filter(d=>set.has(d)).length;return Math.round(ativos/dias.length*100)}
  const consistenciaPorArea=AREAS_SCORE_REL.map(a=>({nome:a.nome,chave:a.chave,atual:scoreAreaRel(a.set,diasAtualRel),anterior:scoreAreaRel(a.set,diasAnteriorRel)}))
  const temAlgumDadoRel=diasAtualRel.some(d=>AREAS_SCORE_REL.some(a=>a.set.has(d)))||diasAnteriorRel.some(d=>AREAS_SCORE_REL.some(a=>a.set.has(d)))

  const scorePeriodoAtual=Math.round(consistenciaPorArea.reduce((a,c)=>a+c.atual,0)/consistenciaPorArea.length)
  const scorePeriodoAnterior=Math.round(consistenciaPorArea.reduce((a,c)=>a+c.anterior,0)/consistenciaPorArea.length)
  const deltaScorePeriodo=scorePeriodoAtual-scorePeriodoAnterior
  const melhorAreaRel=[...consistenciaPorArea].sort((a,b)=>b.atual-a.atual)[0]
  const piorAreaRel=[...consistenciaPorArea].sort((a,b)=>a.atual-b.atual)[0]
  const diasAtivosUniaoRel=diasAtualRel.filter(d=>AREAS_SCORE_REL.some(a=>a.set.has(d))).length
  function labelScoreRel(v:number){if(v>=80)return 'Ótimo';if(v>=60)return 'Bom';if(v>=40)return 'Regular';return 'Baixo'}

  function agregarPontosRel(set:Set<string>|null,dias:string[],granularidade:'dia'|'semana'|'mes'){
    function scoreDiaUniao(iso:string){return Math.round(AREAS_SCORE_REL.filter(a=>a.set.has(iso)).length/AREAS_SCORE_REL.length*100)}
    function valorDia(iso:string){return set?(set.has(iso)?100:0):scoreDiaUniao(iso)}
    if(granularidade==='dia')return dias.map(iso=>({iso,valor:valorDia(iso)}))
    const grupos=new Map<string,{soma:number,n:number,iso:string}>()
    dias.forEach(iso=>{
      let chave=iso
      if(granularidade==='semana'){const d=new Date(iso+'T12:00:00');const dw=d.getDay();const diff=(dw===0?-6:1-dw);const seg=new Date(d);seg.setDate(seg.getDate()+diff);chave=isoBR(seg)}
      else{chave=iso.slice(0,7)+'-01'}
      const atual=grupos.get(chave)||{soma:0,n:0,iso:chave}
      atual.soma+=valorDia(iso);atual.n+=1
      grupos.set(chave,atual)
    })
    return Array.from(grupos.values()).sort((a,b)=>a.iso.localeCompare(b.iso)).map(g=>({iso:g.iso,valor:Math.round(g.soma/g.n)}))
  }
  const areaSelecionadaInfo=AREAS_SCORE_REL.find(a=>a.chave===areaRel)||null
  const pontosGraficoRel=agregarPontosRel(areaSelecionadaInfo?areaSelecionadaInfo.set:null,diasAtualRel,granularidadeRel)

  function somaAguaPeriodoRel(dias:string[]){return dias.reduce((a,iso)=>a+Number(aguaLogRel[iso]||0),0)}
  const aguaMediaAtualRel=diasAtualRel.length?somaAguaPeriodoRel(diasAtualRel)/diasAtualRel.length:0
  const aguaMediaAnteriorRel=diasAnteriorRel.length?somaAguaPeriodoRel(diasAnteriorRel)/diasAnteriorRel.length:0
  const treinosAtualNRel=treinosRel.filter(t=>diasAtualRel.includes(t.data)).length
  const treinosAnteriorNRel=treinosRel.filter(t=>diasAnteriorRel.includes(t.data)).length
  const minLeituraAtualRel=sessoesLeituraRel.filter(sx=>diasAtualRel.includes(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)
  const minLeituraAnteriorRel=sessoesLeituraRel.filter(sx=>diasAnteriorRel.includes(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)
  const minEstudoAtualRel=sessoesEstudoRel.filter(sx=>diasAtualRel.includes(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)
  const tarefasConcluidasAtualRel=trabalhoItensRel.filter(t=>t.concluidaEm&&diasAtualRel.includes(String(t.concluidaEm).slice(0,10))).length
  const tarefasConcluidasAnteriorRel=trabalhoItensRel.filter(t=>t.concluidaEm&&diasAnteriorRel.includes(String(t.concluidaEm).slice(0,10))).length
  const tarefasAtrasadasRel=trabalhoItensRel.filter(t=>t.s!=='concluído'&&calcPrazoLabelTrab(t.prazo)?.atrasada).length
  const tarefasAguardandoRel=trabalhoItensRel.filter(t=>t.s==='aguardando').length
  const proteinaMediaRel=diasAtualRel.length?diasAtualRel.reduce((a,iso)=>a+((refsLogRel[iso]||[]).reduce((x,r)=>x+(r.prot||0),0)),0)/diasAtualRel.length:0
  const diasComMetaProtRel=diasAtualRel.filter(iso=>(refsLogRel[iso]||[]).reduce((a,r)=>a+(r.prot||0),0)>=metaProteinaRel).length
  const mediaRefeicoesRel=diasAtualRel.length?(diasAtualRel.reduce((a,iso)=>a+((refsLogRel[iso]||[]).length),0)/diasAtualRel.length):0

  const seqLeituraPeriodoRel=sequenciaMaximaNoPeriodo(new Set(sessoesLeituraRel.map(sx=>sx.data)),diasAtualRel)
  const contasPeriodoRel=casaItensRel.filter(it=>it.cat==='Contas'&&it.pago&&it.pagoEm&&diasAtualRel.includes(String(it.pagoEm).slice(0,10)))
  const contasNoPrazoRel=contasPeriodoRel.filter(it=>!it.venc||String(it.pagoEm).slice(0,10)<=(it.venc as string)).length
  const contasAtrasadasAgoraRel=casaItensRel.filter(it=>it.cat==='Contas'&&!it.pago&&calcStatusContaCasa(it).atrasada).length
  const pixelsavConcluidasRel=trabalhoItensRel.filter(t=>t.p==='PixelSAV'&&t.s==='concluído'&&t.concluidaEm&&diasAtualRel.includes(String(t.concluidaEm).slice(0,10))).length
  const mercadoConcluidoRel=casaItensRel.filter(it=>it.cat==='Mercado'&&it.done&&it.compradoEm&&diasAtualRel.includes(String(it.compradoEm).slice(0,10))).length
  const destaquesRel:string[]=[]
  if(seqLeituraPeriodoRel>=2)destaquesRel.push(`Maior sequência de leitura do período: ${seqLeituraPeriodoRel} dias`)
  if(treinosAtualNRel>0)destaquesRel.push(`${treinosAtualNRel} treino${treinosAtualNRel===1?'':'s'} realizado${treinosAtualNRel===1?'':'s'} no período`)
  if(tarefasConcluidasAtualRel>0)destaquesRel.push(`${tarefasConcluidasAtualRel} tarefa${tarefasConcluidasAtualRel===1?'':'s'} concluída${tarefasConcluidasAtualRel===1?'':'s'} no período`)
  if(pixelsavConcluidasRel>0)destaquesRel.push(`${pixelsavConcluidasRel} tarefa${pixelsavConcluidasRel===1?'':'s'} da PixelSAV concluída${pixelsavConcluidasRel===1?'':'s'} no período`)
  if(contasPeriodoRel.length>0)destaquesRel.push(contasNoPrazoRel===contasPeriodoRel.length?`Todas as ${contasPeriodoRel.length} contas pagas no período estavam em dia`:`${contasNoPrazoRel} de ${contasPeriodoRel.length} contas pagas no prazo`)
  if(contasAtrasadasAgoraRel===0)destaquesRel.push('Nenhuma conta em atraso no momento')
  if(mercadoConcluidoRel>0)destaquesRel.push(`${mercadoConcluidoRel} item${mercadoConcluidoRel===1?'':'ns'} de mercado resolvido${mercadoConcluidoRel===1?'':'s'} no período`)

  const comparacoesRel:[string,string,string,number|null][]=[
    ['Score geral',`${scorePeriodoAtual}%`,`${scorePeriodoAnterior}%`,deltaScorePeriodo],
    ['Água média',`${(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia`,`${(aguaMediaAnteriorRel/1000).toFixed(1).replace('.',',')} L/dia`,Math.round(aguaMediaAtualRel-aguaMediaAnteriorRel)],
    ['Treinos realizados',String(treinosAtualNRel),String(treinosAnteriorNRel),treinosAtualNRel-treinosAnteriorNRel],
    ['Minutos de leitura',String(minLeituraAtualRel),String(minLeituraAnteriorRel),minLeituraAtualRel-minLeituraAnteriorRel],
    ['Tarefas concluídas',String(tarefasConcluidasAtualRel),String(tarefasConcluidasAnteriorRel),tarefasConcluidasAtualRel-tarefasConcluidasAnteriorRel],
  ]

  function perguntarLunaSobreRelatorio(){
    const areaNome=AREAS_REL_INFO.find(a=>a.key===areaRel)?.nome||'Visão geral'
    const periodoTxt=periodoRel==='semana'?'esta semana':periodoRel==='30d'?'os últimos 30 dias':periodoRel==='90d'?'os últimos 90 dias':periodoRel==='ano'?'este ano':`de ${janela.inicioIso} a ${janela.fimIso}`
    const pergunta=`Analisando o relatório de "${areaNome}" em ${periodoTxt}: o score está em ${scorePeriodoAtual}% (era ${scorePeriodoAnterior}% no período anterior). O que mais chama atenção nesses números?`
    try{localStorage.setItem('dos_luna_pergunta_pendente',pergunta)}catch{}
    navigate('/assistente')
  }
  function exportarRelatorioRel(){window.print()}

  const CardResumoRel=({icone,titulo,valor,sub,cor}:{icone:string,titulo:string,valor:string,sub?:React.ReactNode,cor?:string})=>(
    <div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:14,padding:16}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:8}}><span style={{fontSize:16}}>{icone}</span><span style={{fontSize:12,color:'rgba(255,255,255,.5)'}}>{titulo}</span></div>
      <div style={{fontSize:20,fontWeight:800,color:cor||'#fff'}}>{valor}</div>
      {sub&&<div style={{fontSize:11,color:'rgba(255,255,255,.4)',marginTop:4}}>{sub}</div>}
    </div>
  )
  const Seta=({delta}:{delta:number|null})=>delta===null?null:(<span style={{color:delta>0?C.ok:delta<0?C.danger:'rgba(255,255,255,.4)',fontWeight:700}}>{delta>0?'▲':delta<0?'▼':'—'} {Math.abs(delta)}%</span>)

  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:6,flexWrap:'wrap' as const}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Relatórios</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Acompanhe sua evolução ao longo do tempo</p></div>
      <div style={{display:'flex',gap:10,flexWrap:'wrap' as const}}>
        <button onClick={perguntarLunaSobreRelatorio} style={{display:'inline-flex',alignItems:'center',gap:7,background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:10,padding:'9px 14px',fontSize:12.5,fontWeight:600,cursor:'pointer'}}>🌙 Perguntar à Luna sobre este relatório</button>
        <button onClick={exportarRelatorioRel} style={{display:'inline-flex',alignItems:'center',gap:7,background:`linear-gradient(135deg,${C.acc},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'9px 16px',fontSize:12.5,fontWeight:700,cursor:'pointer'}}>⬇ Exportar relatório</button>
      </div>
    </div>

    <div style={{display:'flex',gap:10,marginBottom:14,flexWrap:'wrap' as const,alignItems:'center'}}>
      <select value={periodoRel} onChange={e=>setPeriodoRel(e.target.value as any)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}>
        <option value="semana">Esta semana</option><option value="30d">Últimos 30 dias</option><option value="90d">Últimos 90 dias</option><option value="ano">Este ano</option><option value="personalizado">Personalizado</option>
      </select>
      {periodoRel==='personalizado'&&<>
        <input type="date" value={personalizadoIniRel} onChange={e=>setPersonalizadoIniRel(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}/>
        <span style={{color:'rgba(255,255,255,.3)',fontSize:12}}>até</span>
        <input type="date" value={personalizadoFimRel} onChange={e=>setPersonalizadoFimRel(e.target.value)} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 10px',color:'#fff',fontSize:12.5,colorScheme:'dark' as const}}/>
      </>}
      <div style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'8px 12px',color:'rgba(255,255,255,.5)',fontSize:12.5}}>Comparando com: {diasAtualRel.length} dia{diasAtualRel.length===1?'':'s'} anteriores</div>
      <div style={{flex:1}}/>
      <div style={{display:'flex',gap:4,background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:4,flexWrap:'wrap' as const}}>
        {AREAS_REL_INFO.map(a=>(<button key={a.key} onClick={()=>setAreaRel(a.key)} title={a.nome} style={{background:areaRel===a.key?`linear-gradient(135deg,${C.acc},#7c3aed)`:'transparent',border:'none',borderRadius:8,color:areaRel===a.key?'#fff':'rgba(255,255,255,.5)',fontSize:13,padding:'6px 9px',cursor:'pointer'}}>{a.icone}{areaRel===a.key?` ${a.nome}`:''}</button>))}
      </div>
    </div>

    {!temAlgumDadoRel&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)',background:'rgba(255,255,255,.03)',border:`1px dashed ${C.line}`,borderRadius:12,padding:'16px 18px',marginBottom:16}}>Sem dados suficientes neste período. Continue registrando pelo app para os relatórios ganharem forma.</div>}

    {areaRel==='geral'&&<>
      <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:12,marginBottom:16}}>
        <CardResumoRel icone="💜" titulo="Score do período" valor={`${scorePeriodoAtual}%`} cor={C.acc2} sub={<span>{labelScoreRel(scorePeriodoAtual)} · <Seta delta={deltaScorePeriodo}/></span>}/>
        <CardResumoRel icone="🏆" titulo="Melhor área" valor={melhorAreaRel?melhorAreaRel.nome:'—'} cor={C.ok} sub={melhorAreaRel?`${melhorAreaRel.atual}% no período`:''}/>
        <CardResumoRel icone="⚠️" titulo="Área com menor consistência" valor={piorAreaRel?piorAreaRel.nome:'—'} cor={C.warn} sub={piorAreaRel?`${piorAreaRel.atual}% no período`:''}/>
        <CardResumoRel icone="📅" titulo="Dias ativos" valor={`${diasAtivosUniaoRel} de ${diasAtualRel.length}`} sub={`${Math.round(diasAtivosUniaoRel/(diasAtualRel.length||1)*100)}% dos dias`}/>
        <CardResumoRel icone="📈" titulo="Média geral" valor={`${(scorePeriodoAtual/10).toFixed(1)} / 10`} sub={<span>{(scorePeriodoAnterior/10).toFixed(1)} anterior · <Seta delta={deltaScorePeriodo}/></span>}/>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1.7fr 1fr',gap:16,marginBottom:16}}>
        <Card title="Evolução do período" action={<div style={{display:'flex',gap:4}}>{(['dia','semana','mes'] as const).map(g=>(<button key={g} onClick={()=>setGranularidadeRel(g)} style={{background:granularidadeRel===g?'rgba(139,92,246,.15)':'transparent',border:`1px solid ${granularidadeRel===g?'rgba(139,92,246,.3)':C.line}`,color:granularidadeRel===g?C.acc2:'rgba(255,255,255,.4)',borderRadius:8,padding:'5px 10px',fontSize:11.5,cursor:'pointer'}}>{g==='dia'?'Dia':g==='semana'?'Semana':'Mês'}</button>))}</div>}>
          <LinhaEvolucao pontos={pontosGraficoRel} cor={C.acc2} unidade="%" rotulo="Score geral"/>
        </Card>
        <Card title="Consistência por área">
          <div style={{maxHeight:280,overflowY:'auto' as const}}>
            <div style={{display:'grid',gridTemplateColumns:'1.3fr .7fr .7fr .7fr',gap:6,fontSize:11,color:'rgba(255,255,255,.35)',padding:'0 0 8px'}}><span>Área</span><span>Atual</span><span>Anterior</span><span>Variação</span></div>
            {consistenciaPorArea.map(a=>(<div key={a.chave} onClick={()=>setAreaRel(a.chave)} style={{display:'grid',gridTemplateColumns:'1.3fr .7fr .7fr .7fr',gap:6,padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5,cursor:'pointer'}}>
              <span>{a.nome}</span><span style={{fontWeight:700}}>{a.atual}%</span><span style={{color:'rgba(255,255,255,.5)'}}>{a.anterior}%</span><Seta delta={a.atual-a.anterior}/>
            </div>))}
          </div>
          <button onClick={()=>setAreaRel(piorAreaRel?piorAreaRel.chave:'saude')} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'8px 0 0'}}>Ver relatório completo por área →</button>
        </Card>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1.7fr 1fr',gap:16,marginBottom:16}}>
        <Card title="Destaques do período">
          {destaquesRel.length===0?<div style={{fontSize:12.5,color:'rgba(255,255,255,.35)'}}>Sem destaques suficientes neste período.</div>:
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))',gap:10}}>
            {destaquesRel.map((d,i)=>(<div key={i} style={{background:C.s2,border:`1px solid ${C.line}`,borderRadius:10,padding:'10px 12px',fontSize:12.5,color:'rgba(255,255,255,.8)'}}>{d}</div>))}
          </div>}
        </Card>
        <Card title="Comparação com período anterior">
          <div style={{maxHeight:220,overflowY:'auto' as const}}>
            {comparacoesRel.map(([lbl,atual,anterior,delta])=>(<div key={lbl} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'8px 0',borderBottom:`1px solid ${C.line}`,fontSize:12.5}}>
              <span style={{color:'rgba(255,255,255,.6)'}}>{lbl}</span>
              <span style={{display:'flex',gap:8,alignItems:'center'}}><b>{atual}</b><span style={{color:'rgba(255,255,255,.35)',fontSize:11}}>{anterior}</span><Seta delta={delta}/></span>
            </div>))}
          </div>
          <button onClick={()=>{}} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'8px 0 0'}}>Ver todas as comparações →</button>
        </Card>
      </div>

      <Card title="Resumo rápido por área">
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(190px,1fr))',gap:12}}>
          <div onClick={()=>setAreaRel('saude')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.pink}}>❤️ Saúde</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Água média</span><b>{(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
          </div>
          <div onClick={()=>setAreaRel('alimentacao')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.warn}}>🍽️ Alimentação</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Proteína média</span><b>{Math.round(proteinaMediaRel)} g/dia</b></div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Refeições/dia</span><b>{mediaRefeicoesRel.toFixed(1)}</b></div>
          </div>
          <div onClick={()=>setAreaRel('exercicios')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.ok}}>💪 Exercícios</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Treinos</span><b>{treinosAtualNRel}</b></div>
          </div>
          <div onClick={()=>setAreaRel('trabalho')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:C.danger}}>💼 Trabalho</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Concluídas</span><b>{tarefasConcluidasAtualRel}</b></div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Atrasadas</span><b>{tarefasAtrasadasRel}</b></div>
          </div>
          <div onClick={()=>setAreaRel('desenvolvimento')} style={{cursor:'pointer'}}><div style={{fontWeight:700,fontSize:12.5,marginBottom:6,color:'#fb923c'}}>📈 Desenvolvimento</div>
            <div style={{fontSize:11.5,color:'rgba(255,255,255,.6)',display:'flex',justifyContent:'space-between'}}><span>Leitura</span><b>{minLeituraAtualRel} min</b></div>
          </div>
        </div>
        <button onClick={()=>{}} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',padding:'10px 0 0'}}>Ver todos os indicadores · Explore todos os dados detalhados por área →</button>
      </Card>
    </>}

    {areaRel!=='geral'&&<>
      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12,marginBottom:16}}>
        {areaSelecionadaInfo?<>
          <CardResumoRel icone="💜" titulo="Score da área" valor={`${consistenciaPorArea.find(a=>a.chave===areaRel)?.atual??0}%`} cor={C.acc2}/>
          <CardResumoRel icone="📅" titulo="Dias ativos" valor={`${diasAtualRel.filter(d=>areaSelecionadaInfo.set.has(d)).length} de ${diasAtualRel.length}`}/>
          <CardResumoRel icone="↕️" titulo="Vs. período anterior" valor={`${consistenciaPorArea.find(a=>a.chave===areaRel)?.anterior??0}%`} sub={<Seta delta={(consistenciaPorArea.find(a=>a.chave===areaRel)?.atual??0)-(consistenciaPorArea.find(a=>a.chave===areaRel)?.anterior??0)}/>}/>
        </>:<CardResumoRel icone="👨‍👩‍👧" titulo="Família" valor="Sem score" sub="Família não recebe pontuação — só indicadores."/>}
      </div>
      <div style={{display:'grid',gridTemplateColumns:'1.7fr 1fr',gap:16,marginBottom:16}}>
        <Card title="Evolução do período">
          {areaSelecionadaInfo?<LinhaEvolucao pontos={pontosGraficoRel} cor={C.acc2} unidade="%" rotulo={AREAS_REL_INFO.find(a=>a.key===areaRel)?.nome||''}/>:<div style={{fontSize:13,color:'rgba(255,255,255,.3)',padding:'30px 0',textAlign:'center' as const}}>Família não tem gráfico de consistência (não é pontuada).</div>}
        </Card>
        <Card title={`Indicadores · ${AREAS_REL_INFO.find(a=>a.key===areaRel)?.nome}`}>
          <div style={{maxHeight:280,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:8,fontSize:12.5}}>
            {areaRel==='saude'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Água média</span><b>{(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Meta de água</span><b>{(metaAguaRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Tirzepatida · estoque</span><b>{Object.keys(tzSched).length>0?`${tzBalance} mg`:'—'}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Aplicações registradas</span><b>{tzApps.length}</b></div>
              <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:6}}>Peso, sono e humor detalhados por pessoa ficam na Etapa 2 deste relatório — hoje eles moram em Saúde.</div>
            </>}
            {areaRel==='alimentacao'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Proteína média</span><b>{Math.round(proteinaMediaRel)} g/dia</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Dias com meta batida</span><b>{diasComMetaProtRel} de {diasAtualRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Refeições/dia (média)</span><b>{mediaRefeicoesRel.toFixed(1)}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Água média</span><b>{(aguaMediaAtualRel/1000).toFixed(1).replace('.',',')} L/dia</b></div>
            </>}
            {areaRel==='exercicios'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Treinos realizados</span><b>{treinosAtualNRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Meta semanal</span><b>{lerMetaTreinos()}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Vs. período anterior</span><Seta delta={treinosAtualNRel-treinosAnteriorNRel}/></div>
            </>}
            {areaRel==='espiritual'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Dias com devocional</span><b>{diasAtualRel.filter(d=>diasEspiritualRel.has(d)).length} de {diasAtualRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Sequência atual</span><b>{calcularSequenciaDevocional(devRel)} dias</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Pedidos de oração</span><b>{(()=>{try{return lerPedidosOracao().filter((p:any)=>!p.respondido).length}catch{return 0}})()} em aberto</b></div>
            </>}
            {areaRel==='trabalho'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Concluídas no período</span><b>{tarefasConcluidasAtualRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Atrasadas agora</span><b style={{color:tarefasAtrasadasRel>0?C.danger:'#fff'}}>{tarefasAtrasadasRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Aguardando</span><b>{tarefasAguardandoRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>PixelSAV concluídas</span><b>{pixelsavConcluidasRel}</b></div>
            </>}
            {areaRel==='desenvolvimento'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Minutos de leitura</span><b>{minLeituraAtualRel} min</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Minutos de estudo</span><b>{minEstudoAtualRel} min</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Maior sequência de leitura</span><b>{seqLeituraPeriodoRel} dias</b></div>
            </>}
            {areaRel==='casa'&&<>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Itens de mercado resolvidos</span><b>{mercadoConcluidoRel}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Contas pagas no período</span><b>{contasPeriodoRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Pagas no prazo</span><b>{contasNoPrazoRel} de {contasPeriodoRel.length}</b></div>
              <div style={{display:'flex',justifyContent:'space-between'}}><span>Atrasadas agora</span><b style={{color:contasAtrasadasAgoraRel>0?C.danger:'#fff'}}>{contasAtrasadasAgoraRel}</b></div>
            </>}
            {areaRel==='familia'&&<>
              {(['domi','derick'] as const).map(k=>{
                const lista=(avalsFamRel[k]||[]).map(migrarAval)
                const noPeriodo=lista.length
                const realizadas=lista.filter((a:any)=>a.status==='realizado').length
                return(<div key={k} style={{display:'flex',justifyContent:'space-between'}}><span>Avaliações · {k==='domi'?'Domi':'Derick'}</span><b>{realizadas} de {noPeriodo} realizadas</b></div>)
              })}
              <div style={{fontSize:11,color:'rgba(255,255,255,.35)',marginTop:6}}>Sem score de família — só indicadores objetivos, como pedido.</div>
            </>}
          </div>
        </Card>
      </div>
    </>}
  </div>)
}'''
s = replace_once(s, old, new, "reescreve-relatorios")

# 2) Luna: se houver pergunta pendente vinda de "Perguntar a Luna sobre este relatorio",
#    abre a aba Conversar ja com a pergunta enviada, sem duplicar o fluxo de perguntarLuna().
old2 = """  const [abaLuna,setAbaLuna]=React.useState<'insights'|'conversar'>('insights')"""
new2 = """  const [abaLuna,setAbaLuna]=React.useState<'insights'|'conversar'>('insights')
  React.useEffect(()=>{
    let perguntaPendente:string|null=null
    try{perguntaPendente=localStorage.getItem('dos_luna_pergunta_pendente')}catch{}
    if(!perguntaPendente)return
    try{localStorage.removeItem('dos_luna_pergunta_pendente')}catch{}
    setAbaLuna('conversar')
    send({textoOverride:perguntaPendente})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])"""
s = replace_once(s, old2, new2, "luna-pega-pergunta-pendente-relatorios")

p.write_text(s)
print("TUDO OK:", applied)
