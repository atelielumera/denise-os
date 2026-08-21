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

# 1) Motor de insights da Luna (novo), inserido antes de function Assistente(){
old1 = "function Assistente(){"
new1 = '''type CategoriaLuna='Saúde'|'Trabalho'|'Família'|'Casa'|'Desenvolvimento'|'Espiritual'
type LunaInsight={id:string,tipo:'atencao'|'padrao'|'progresso'|'sugestao',titulo:string,conclusao:string,evidencia:string,periodo:string,modulo:CategoriaLuna,rota:string,acaoPerguntar?:string}
const ICONE_TIPO_LUNA:Record<LunaInsight['tipo'],string>={atencao:'⚠️',padrao:'🔎',progresso:'📈',sugestao:'💡'}
const LABEL_TIPO_LUNA:Record<LunaInsight['tipo'],string>={atencao:'Atenção',padrao:'Padrão',progresso:'Progresso',sugestao:'Sugestão'}
const COR_TIPO_LUNA:Record<LunaInsight['tipo'],string>={atencao:C.danger,padrao:C.acc2,progresso:C.ok,sugestao:C.warn}
function gerarInsightsLuna(tzSched:Record<string,{planned_dose_mg:number,interval_days:number,next_application_date:string|null}>,tzBalance:number,periodoDias:number):LunaInsight[]{
  const out:LunaInsight[]=[]
  const hojeG=isoBR(new Date())
  function ultimosNDiasG(n:number):string[]{const arr:string[]=[];for(let i=n-1;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);arr.push(isoBR(d))}return arr}
  function anterioresNDiasG(n:number):string[]{const arr:string[]=[];for(let i=2*n-1;i>=n;i--){const d=new Date();d.setDate(d.getDate()-i);arr.push(isoBR(d))}return arr}
  const ultN=ultimosNDiasG(periodoDias)
  const antN=anterioresNDiasG(periodoDias)

  const casaItensG=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_casa_items')||'[]');return Array.isArray(raw)?raw.map(migrarItemCasa):[]}catch{return []}})() as CasaItem[]
  const contasAtrasadasG=casaItensG.filter(it=>it.cat==='Contas'&&!it.pago&&calcStatusContaCasa(it).atrasada)
  const contasHojeG=casaItensG.filter(it=>it.cat==='Contas'&&!it.pago&&it.venc===hojeG)
  if(contasAtrasadasG.length>0){
    out.push({id:`casa_contas_atrasadas_${contasAtrasadasG.length}`,tipo:'atencao',titulo:`${contasAtrasadasG.length} conta${contasAtrasadasG.length===1?'':'s'} atrasada${contasAtrasadasG.length===1?'':'s'}`,conclusao:`${contasAtrasadasG.map(c=>c.n).join(', ')} — já passou da data de vencimento.`,evidencia:contasAtrasadasG.map(c=>`${c.n}${c.valor?` (R$ ${c.valor.toFixed(2)})`:''}`).join(' · '),periodo:'agora',modulo:'Casa',rota:'/casa',acaoPerguntar:'Quer que eu te ajude a organizar as contas atrasadas da Casa?'})
  }else if(contasHojeG.length>0){
    out.push({id:`casa_contas_hoje_${contasHojeG.length}`,tipo:'atencao',titulo:`${contasHojeG.length} conta${contasHojeG.length===1?'':'s'} vencendo hoje`,conclusao:`${contasHojeG.map(c=>c.n).join(', ')} vence${contasHojeG.length===1?'':'m'} hoje.`,evidencia:contasHojeG.map(c=>`${c.n}${c.valor?` (R$ ${c.valor.toFixed(2)})`:''}`).join(' · '),periodo:'hoje',modulo:'Casa',rota:'/casa'})
  }
  const manutUrgenteG=casaItensG.filter(it=>it.cat==='Manutenção'&&!it.done&&it.prioridade==='alta')
  if(manutUrgenteG.length>0){
    const manutTxtG=manutUrgenteG.length===1?'manutenção de prioridade alta em aberto':'manutenções de prioridade alta em aberto'
    out.push({id:`casa_manut_alta_${manutUrgenteG.length}`,tipo:'atencao',titulo:`${manutUrgenteG.length} ${manutTxtG}`,conclusao:manutUrgenteG.map(m=>m.n).join(', '),evidencia:'Casa · Manutenção',periodo:'agora',modulo:'Casa',rota:'/casa'})
  }

  const tarefasTrabG=(()=>{try{const raw=JSON.parse(localStorage.getItem('dos_trabalho')||'[]');return Array.isArray(raw)?raw.map(migrarTarefaTrab):[]}catch{return []}})() as TarefaTrab[]
  const trabAtrasadasG=tarefasTrabG.filter(t=>t.s!=='concluído'&&calcPrazoLabelTrab(t.prazo)?.atrasada)
  if(trabAtrasadasG.length>0){
    out.push({id:`trab_atrasadas_${trabAtrasadasG.length}`,tipo:'atencao',titulo:`${trabAtrasadasG.length} tarefa${trabAtrasadasG.length===1?'':'s'} do Trabalho atrasada${trabAtrasadasG.length===1?'':'s'}`,conclusao:trabAtrasadasG.slice(0,5).map(t=>t.t).join(', '),evidencia:`Projeto${trabAtrasadasG.length===1?'':'s'}: ${Array.from(new Set(trabAtrasadasG.map(t=>t.p))).join(', ')}`,periodo:'agora',modulo:'Trabalho',rota:'/trabalho',acaoPerguntar:'Quer que eu te ajude a priorizar as tarefas atrasadas do Trabalho?'})
  }

  const avalsFamG=(()=>{try{return JSON.parse(localStorage.getItem('dos_avals')||'{}')}catch{return {}}})() as Record<string,any[]>
  ;(['domi','derick'] as const).forEach(k=>{
    const prox=proximaAvalPendente(avalsFamG[k]||[])
    if(prox&&prox.dias<=2){
      const nome=k==='domi'?'Domi':'Derick'
      out.push({id:`fam_aval_${k}_${prox.aval.data}_${prox.aval.materia}`,tipo:'atencao',titulo:`${nome} tem ${prox.aval.materia} ${prox.dias===0?'hoje':prox.dias===1?'amanhã':`em ${prox.dias} dias`}`,conclusao:`${prox.aval.tipoAvaliacao} de ${prox.aval.materia}, status atual: ${STATUS_AVAL_LABEL[prox.aval.status]}.`,evidencia:`Calendário avaliativo · ${nome}`,periodo:prox.dias===0?'hoje':`em ${prox.dias} dias`,modulo:'Família',rota:'/familia'})
    }
  })

  let autonomiaTzG=0
  if(Object.keys(tzSched).length>0){
    const dDenG=tzSched.denise?.planned_dose_mg||5,dFlaG=tzSched.flavio?.planned_dose_mg||2.5
    const iDenG=tzSched.denise?.interval_days||5,iFlaG=tzSched.flavio?.interval_days||7
    const mgDayG=dDenG/iDenG+dFlaG/iFlaG
    autonomiaTzG=mgDayG>0?Math.floor(tzBalance/mgDayG):0
    if(autonomiaTzG<=14){
      out.push({id:`saude_tz_estoque_baixo_${autonomiaTzG}`,tipo:'atencao',titulo:`Estoque de tirzepatida com autonomia de ~${autonomiaTzG} dias`,conclusao:'O estoque atual está abaixo de 14 dias de autonomia considerando as doses programadas.',evidencia:`Saldo atual: ${tzBalance} mg`,periodo:'agora',modulo:'Saúde',rota:'/saude',acaoPerguntar:'Quer que eu te lembre de repor o estoque de tirzepatida?'})
    }
  }

  const aguaLogG=(()=>{try{return JSON.parse(localStorage.getItem('dos_agua_log')||'{}')}catch{return {}}})() as Record<string,number>
  const aguaPorDiaSemanaG:Record<number,number[]>={}
  Object.keys(aguaLogG).forEach(iso=>{
    const v=Number(aguaLogG[iso]||0)
    if(v<=0)return
    const dw=new Date(iso+'T12:00:00-03:00').getDay()
    if(!aguaPorDiaSemanaG[dw])aguaPorDiaSemanaG[dw]=[]
    aguaPorDiaSemanaG[dw].push(v)
  })
  const DIAS_NOME_G=['domingo','segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado']
  let padraoAguaDiaG:{dw:number,nome:string}|null=null
  const mediasPorDiaG=Object.entries(aguaPorDiaSemanaG).filter(([,vs])=>vs.length>=2).map(([dw,vs])=>({dw:Number(dw),media:vs.reduce((a,b)=>a+b,0)/vs.length,n:vs.length}))
  if(mediasPorDiaG.length>=2){
    const mediaGeralG=mediasPorDiaG.reduce((a,m)=>a+m.media,0)/mediasPorDiaG.length
    const piorDiaG=mediasPorDiaG.reduce((pior,m)=>m.media<pior.media?m:pior)
    if(piorDiaG.media<mediaGeralG*0.85){
      padraoAguaDiaG={dw:piorDiaG.dw,nome:DIAS_NOME_G[piorDiaG.dw]}
      out.push({id:`padrao_agua_dow_${piorDiaG.dw}`,tipo:'padrao',titulo:`Parece haver uma associação entre ${padraoAguaDiaG.nome}s e menor ingestão de água`,conclusao:`Nos registros disponíveis, a ingestão de água às ${padraoAguaDiaG.nome}s tende a ficar abaixo da média dos demais dias.`,evidencia:`Média de ${(piorDiaG.media/1000).toFixed(1).replace('.',',')}L nesse dia vs ${(mediaGeralG/1000).toFixed(1).replace('.',',')}L nos demais dias, com base em ${piorDiaG.n} registros.`,periodo:'baseado no histórico registrado',modulo:'Saúde',rota:'/alimentacao'})
    }
  }

  const treinosConcluidosG=lerTreinos().filter(t=>t.status==='concluido')
  const treinoPorDiaSemanaG:Record<number,number>={}
  treinosConcluidosG.forEach(t=>{const dw=new Date(t.data+'T12:00:00-03:00').getDay();treinoPorDiaSemanaG[dw]=(treinoPorDiaSemanaG[dw]||0)+1})
  const diasComTreinoG=Object.entries(treinoPorDiaSemanaG).filter(([,n])=>n>=2)
  if(treinosConcluidosG.length>=8&&diasComTreinoG.length>=1){
    const melhorDiaG=diasComTreinoG.reduce((a,b)=>b[1]>a[1]?b:a)
    out.push({id:`padrao_treino_dow_${melhorDiaG[0]}`,tipo:'padrao',titulo:`Seus treinos tendem a se concentrar às ${DIAS_NOME_G[Number(melhorDiaG[0])]}s`,conclusao:'Esse é o dia da semana com mais treinos concluídos no seu histórico.',evidencia:`${melhorDiaG[1]} de ${treinosConcluidosG.length} treinos concluídos caíram nesse dia.`,periodo:'baseado no histórico registrado',modulo:'Saúde',rota:'/exercicios'})
  }

  const refsLogG=lerRefsLog()
  const metaProtG=lerMetaProteina()
  function diasComRegistroProtG(dias:string[]){return dias.filter(iso=>(refsLogG[iso]||[]).length>0).length}
  function diasComMetaProtG(dias:string[]){return dias.filter(iso=>{const refs=refsLogG[iso]||[];return refs.reduce((a,r)=>a+(r.prot||0),0)>=metaProtG}).length}
  const regAtualG=diasComRegistroProtG(ultN),regAntG=diasComRegistroProtG(antN)
  if(regAtualG>=3&&regAntG>=3){
    const metaAtualG=diasComMetaProtG(ultN),metaAntG=diasComMetaProtG(antN)
    if(metaAtualG!==metaAntG){
      out.push({id:`progresso_proteina_${periodoDias}_${metaAtualG}_${metaAntG}`,tipo:'progresso',titulo:`Consistência da meta de proteína ${metaAtualG>metaAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Meta batida em ${metaAtualG} de ${ultN.length} dias, contra ${metaAntG} de ${antN.length} dias no período anterior.`,evidencia:`Comparação de ${periodoDias} dias.`,periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/alimentacao'})
    }
  }

  function contarTreinosG(dias:string[]){const set=new Set(dias);return treinosConcluidosG.filter(t=>set.has(t.data)).length}
  const treinoAtualG=contarTreinosG(ultN),treinoAntG=contarTreinosG(antN)
  if(treinosConcluidosG.length>=4&&(treinoAtualG>0||treinoAntG>0)&&treinoAtualG!==treinoAntG){
    out.push({id:`progresso_treino_${periodoDias}_${treinoAtualG}_${treinoAntG}`,tipo:'progresso',titulo:`Frequência de treinos ${treinoAtualG>treinoAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${treinoAtualG} treino${treinoAtualG===1?'':'s'} concluído${treinoAtualG===1?'':'s'} nos últimos ${periodoDias} dias, contra ${treinoAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Exercícios.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Saúde',rota:'/exercicios'})
  }

  const sessoesLeituraG=lerSessoesLeituraDev()
  function minutosLeituraG(dias:string[]){const set=new Set(dias);return sessoesLeituraG.filter(sx=>set.has(sx.data)).reduce((a,sx)=>a+(sx.minutos||0),0)}
  const minAtualG=minutosLeituraG(ultN),minAntG=minutosLeituraG(antN)
  if(sessoesLeituraG.length>=3&&(minAtualG>0||minAntG>0)&&minAtualG!==minAntG){
    out.push({id:`progresso_leitura_${periodoDias}_${minAtualG}_${minAntG}`,tipo:'progresso',titulo:`Tempo de leitura ${minAtualG>minAntG?'aumentou':'diminuiu'} em relação ao período anterior`,conclusao:`${minAtualG} minutos lidos nos últimos ${periodoDias} dias, contra ${minAntG} no período anterior.`,evidencia:'Baseado nas sessões registradas em Desenvolvimento.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Desenvolvimento',rota:'/desenvolvimento'})
  }

  const devEntriesG=(()=>{try{return JSON.parse(localStorage.getItem('dos_devocionais')||'[]')}catch{return []}})() as any[]
  function diasComDevocionalG(dias:string[]){const set=new Set(dias);return devEntriesG.filter((e:any)=>set.has(e.data)).length}
  const devAtualG=diasComDevocionalG(ultN),devAntG=diasComDevocionalG(antN)
  if(devEntriesG.length>=3&&(devAtualG>0||devAntG>0)&&devAtualG!==devAntG){
    out.push({id:`progresso_devocional_${periodoDias}_${devAtualG}_${devAntG}`,tipo:'progresso',titulo:`Consistência do devocional ${devAtualG>devAntG?'melhorou':'caiu'} em relação ao período anterior`,conclusao:`Devocional feito em ${devAtualG} de ${ultN.length} dias, contra ${devAntG} de ${antN.length} dias no período anterior.`,evidencia:'Baseado nos registros de Espiritual.',periodo:`${periodoDias}d vs ${periodoDias}d anteriores`,modulo:'Espiritual',rota:'/espiritual'})
  }

  const metaTreinosSemanaG=lerMetaTreinos()
  const segIsoInsG=isoBR(segundaDaSemanaEx(new Date()))
  const treinosEstaSemanaG=treinosConcluidosG.filter(t=>t.data>=segIsoInsG).length
  if(treinosEstaSemanaG<metaTreinosSemanaG){
    const faltaG=metaTreinosSemanaG-treinosEstaSemanaG
    out.push({id:`sugestao_treino_meta_${faltaG}`,tipo:'sugestao',titulo:'Ajustar o plano de treino desta semana?',conclusao:`Faltam ${faltaG} treino${faltaG===1?'':'s'} para bater a meta semanal de ${metaTreinosSemanaG}.`,evidencia:`${treinosEstaSemanaG} de ${metaTreinosSemanaG} treinos concluídos essa semana.`,periodo:'semana atual',modulo:'Saúde',rota:'/exercicios',acaoPerguntar:'Quer me ajudar a encaixar os treinos que faltam essa semana?'})
  }
  if(padraoAguaDiaG){
    out.push({id:`sugestao_agua_${padraoAguaDiaG.dw}`,tipo:'sugestao',titulo:`Configurar um lembrete extra de água às ${padraoAguaDiaG.nome}s?`,conclusao:'Baseado no padrão percebido de menor ingestão nesse dia da semana.',evidencia:'Ver o padrão em "Padrões percebidos".',periodo:'sugestão',modulo:'Saúde',rota:'/alimentacao',acaoPerguntar:`Quer me ajudar a lembrar de beber mais água às ${padraoAguaDiaG.nome}s?`})
  }
  const leiturasTodasG=(()=>{try{return JSON.parse(localStorage.getItem('dos_leituras')||'[]')}catch{return []}})() as any[]
  function diasUnicosG(entries:any[]):Set<string>{return new Set(entries.map((e:any)=>e.data))}
  function sequenciaG(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(isoBR(d))){n++;d.setDate(d.getDate()-1)}return n}
  const seqLeituraAtualG=sequenciaG(diasUnicosG(leiturasTodasG))
  if(leiturasTodasG.length>=5&&seqLeituraAtualG===0){
    out.push({id:'sugestao_retomar_leitura',tipo:'sugestao',titulo:'Retomar a leitura de hoje?',conclusao:'Você tinha um histórico de leitura frequente e não há registro nos últimos dias.',evidencia:`${leiturasTodasG.length} sessões de leitura registradas ao todo.`,periodo:'agora',modulo:'Desenvolvimento',rota:'/desenvolvimento',acaoPerguntar:'Quer que eu te lembre de retomar a leitura hoje?'})
  }

  return out
}
function Assistente(){'''
s = replace_once(s, old1, new1, "engine-insights-luna")

# 2) LunaConversa ganha campo opcional 'fixada' (pin manual, sem quebrar dados existentes)
old2 = "type LunaConversa={id:string,titulo:string,criadaEm:string,msgs:LunaMsg[]}"
new2 = "type LunaConversa={id:string,titulo:string,criadaEm:string,msgs:LunaMsg[],fixada?:boolean}"
s = replace_once(s, old2, new2, "luna-conversa-fixada")

# 3) useNavigate() dentro de Assistente()
old3 = "function Assistente(){\n  const h=new Date().getHours(),g=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite'\n"
new3 = "function Assistente(){\n  const navigate=useNavigate()\n  const h=new Date().getHours(),g=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite'\n"
s = replace_once(s, old3, new3, "navigate-luna")

# 4) Estados novos (aba, filtros, dispensar/ocultar/feedback) antes de novaConversa()
old4 = "  function novaConversa(){"
new4 = '''  const [abaLuna,setAbaLuna]=React.useState<'insights'|'conversar'>('insights')
  const [categoriaLuna,setCategoriaLuna]=React.useState<'Todos'|CategoriaLuna>('Todos')
  const [periodoLuna,setPeriodoLuna]=React.useState<7|30|90>(7)
  const [verTodosLuna,setVerTodosLuna]=React.useState<Record<string,boolean>>({})
  const [ignoradosLuna,setIgnoradosLuna]=React.useState<Record<string,string>>(()=>{try{return JSON.parse(localStorage.getItem('dos_luna_insights_ignorados')||'{}')}catch{return {}}})
  const [tiposOcultosLuna,setTiposOcultosLuna]=React.useState<Record<string,string>>(()=>{try{return JSON.parse(localStorage.getItem('dos_luna_insights_tipos_ocultos')||'{}')}catch{return {}}})
  const [feedbackLuna,setFeedbackLuna]=React.useState<Record<string,'util'|'nao_util'>>(()=>{try{return JSON.parse(localStorage.getItem('dos_luna_insights_feedback')||'{}')}catch{return {}}})
  function ignorarInsightLuna(id:string){const n={...ignoradosLuna,[id]:isoBR(new Date(Date.now()+3*86400000))};setIgnoradosLuna(n);localStorage.setItem('dos_luna_insights_ignorados',JSON.stringify(n))}
  function ocultarTipoLuna(tipo:string){const n={...tiposOcultosLuna,[tipo]:isoBR(new Date(Date.now()+14*86400000))};setTiposOcultosLuna(n);localStorage.setItem('dos_luna_insights_tipos_ocultos',JSON.stringify(n))}
  function darFeedbackLuna(id:string,v:'util'|'nao_util'){const n={...feedbackLuna,[id]:v};setFeedbackLuna(n);localStorage.setItem('dos_luna_insights_feedback',JSON.stringify(n))}
  function perguntarLuna(pergunta:string){setAbaLuna('conversar');send({textoOverride:pergunta})}
  function novaConversa(){'''
s = replace_once(s, old4, new4, "estados-insights-luna")

# 5) send() aceita textoOverride (usado por "Perguntar à Luna")
old5 = "  async function send(extra?:{audio?:{mediaType:string,base64:string}}){\n    if(sending)return\n    const text=inp.trim()"
new5 = "  async function send(extra?:{audio?:{mediaType:string,base64:string},textoOverride?:string}){\n    if(sending)return\n    const text=(extra?.textoOverride??inp).trim()"
s = replace_once(s, old5, new5, "send-textoOverride")

# 6) Cabeçalho + abrir bloco de retorno: adiciona tabs Insights/Conversar
old6 = """  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:20}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Luna</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Sua assistente pessoal — entende texto, áudio e imagem.</p></div>
      <button onClick={novaConversa} style={{background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer',flexShrink:0,whiteSpace:'nowrap' as const}}>+ Nova conversa</button>
    </div>
    <div style={{display:'flex',gap:16,height:'60vh'}}>
"""
new6 = """  const insightsBrutosLuna=gerarInsightsLuna(tzSched,tzBalance,periodoLuna)
  const hojeIsoFiltroLuna=isoBR(new Date())
  const insightsVisiveisLuna=insightsBrutosLuna.filter(ins=>{
    if(tiposOcultosLuna[ins.tipo]&&tiposOcultosLuna[ins.tipo]>=hojeIsoFiltroLuna)return false
    if(ignoradosLuna[ins.id]&&ignoradosLuna[ins.id]>=hojeIsoFiltroLuna)return false
    if(categoriaLuna!=='Todos'&&ins.modulo!==categoriaLuna)return false
    return true
  })
  const porTipoLuna={
    atencao:insightsVisiveisLuna.filter(i=>i.tipo==='atencao'),
    padrao:insightsVisiveisLuna.filter(i=>i.tipo==='padrao'),
    progresso:insightsVisiveisLuna.filter(i=>i.tipo==='progresso'),
    sugestao:insightsVisiveisLuna.filter(i=>i.tipo==='sugestao'),
  }
  function CardInsightLuna({ins}:{ins:LunaInsight}){
    const fb=feedbackLuna[ins.id]
    return(<div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderLeft:`3px solid ${COR_TIPO_LUNA[ins.tipo]}`,borderRadius:12,padding:16}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:8,flexWrap:'wrap' as const}}>
        <span style={{fontSize:14}}>{ICONE_TIPO_LUNA[ins.tipo]}</span>
        <span style={{fontSize:11,fontWeight:700,color:COR_TIPO_LUNA[ins.tipo],textTransform:'uppercase' as const,letterSpacing:'.4px'}}>{LABEL_TIPO_LUNA[ins.tipo]}</span>
        <span style={{fontSize:11,background:'rgba(255,255,255,.06)',color:'rgba(255,255,255,.5)',padding:'2px 8px',borderRadius:20}}>{ins.modulo}</span>
        <span style={{fontSize:11,color:'rgba(255,255,255,.35)',marginLeft:'auto'}}>{ins.periodo}</span>
      </div>
      <div style={{fontWeight:700,fontSize:14,marginBottom:5}}>{ins.titulo}</div>
      <div style={{fontSize:13,color:'rgba(255,255,255,.65)',lineHeight:1.5,marginBottom:6}}>{ins.conclusao}</div>
      <div style={{fontSize:11.5,color:'rgba(255,255,255,.4)',marginBottom:10}}>{ins.evidencia}</div>
      <div style={{display:'flex',gap:8,flexWrap:'wrap' as const,alignItems:'center'}}>
        <button onClick={()=>navigate(ins.rota)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Ver origem</button>
        {ins.acaoPerguntar&&<button onClick={()=>perguntarLuna(ins.acaoPerguntar as string)} style={{background:'rgba(139,92,246,.12)',border:'1px solid rgba(139,92,246,.3)',color:C.acc2,borderRadius:8,padding:'6px 12px',fontSize:11.5,cursor:'pointer'}}>Perguntar à Luna</button>}
        <button onClick={()=>ignorarInsightLuna(ins.id)} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.35)',fontSize:11.5,cursor:'pointer'}}>Ignorar</button>
        <button onClick={()=>ocultarTipoLuna(ins.tipo)} style={{background:'transparent',border:'none',color:'rgba(255,255,255,.3)',fontSize:11,cursor:'pointer'}}>Não mostrar {LABEL_TIPO_LUNA[ins.tipo].toLowerCase()} por enquanto</button>
        <span style={{marginLeft:'auto',display:'flex',gap:6}}>
          <button onClick={()=>darFeedbackLuna(ins.id,'util')} title="Útil" style={{background:'none',border:'none',cursor:'pointer',fontSize:13,opacity:fb==='util'?1:.35}}>👍</button>
          <button onClick={()=>darFeedbackLuna(ins.id,'nao_util')} title="Não é útil" style={{background:'none',border:'none',cursor:'pointer',fontSize:13,opacity:fb==='nao_util'?1:.35}}>👎</button>
        </span>
      </div>
    </div>)
  }
  function SecaoInsightsLuna({titulo,tipo,itens}:{titulo:string,tipo:LunaInsight['tipo'],itens:LunaInsight[]}){
    if(itens.length===0)return null
    const aberta=!!verTodosLuna[tipo]
    const visiveis=aberta?itens:itens.slice(0,3)
    return(<div style={{marginBottom:22}}>
      <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
        <span style={{fontSize:15}}>{ICONE_TIPO_LUNA[tipo]}</span><span style={{fontWeight:800,fontSize:15}}>{titulo}</span><span style={{fontSize:11,color:'rgba(255,255,255,.35)'}}>({itens.length})</span>
      </div>
      <div style={{display:'flex',flexDirection:'column' as const,gap:10}}>
        {visiveis.map(ins=><CardInsightLuna key={ins.id} ins={ins}/>)}
      </div>
      {itens.length>3&&<button onClick={()=>setVerTodosLuna(v=>({...v,[tipo]:!v[tipo]}))} style={{background:'transparent',border:'none',color:C.acc2,fontSize:12,cursor:'pointer',marginTop:8,padding:0}}>{aberta?'Ver menos':`Ver todos (${itens.length})`}</button>}
    </div>)
  }
  const listaConversasTodasLuna=[{id:WHATSAPP_THREAD_ID,titulo:'WhatsApp',isWhats:true,fixada:true,criadaEm:null as string|null},...conversas.map(c=>({id:c.id,titulo:c.titulo,isWhats:false,fixada:!!c.fixada,criadaEm:(c.criadaEm||null) as string|null}))]
  const hojeIsoConvLuna=isoBR(new Date())
  const ontemIsoConvLuna=isoBR(new Date(Date.now()-86400000))
  function diaConversaLuna(criadaEm:string|null){if(!criadaEm)return null;try{return isoBR(new Date(criadaEm))}catch{return null}}
  const grupoFixadasConvLuna=listaConversasTodasLuna.filter(c=>c.fixada)
  const naoFixadasConvLuna=listaConversasTodasLuna.filter(c=>!c.fixada)
  const grupoHojeConvLuna=naoFixadasConvLuna.filter(c=>diaConversaLuna(c.criadaEm)===hojeIsoConvLuna)
  const grupoOntemConvLuna=naoFixadasConvLuna.filter(c=>diaConversaLuna(c.criadaEm)===ontemIsoConvLuna)
  const grupoRecentesConvLuna=naoFixadasConvLuna.filter(c=>{const d=diaConversaLuna(c.criadaEm);return d!==hojeIsoConvLuna&&d!==ontemIsoConvLuna})
  function togglePinConversaLuna(id:string){setConversas(prev=>prev.map(c=>c.id===id?{...c,fixada:!c.fixada}:c))}
  function ItemConversaLuna({c}:{c:{id:string,titulo:string,isWhats:boolean,fixada:boolean}}){
    return(<div onClick={()=>setAtivaId(c.id)} style={{display:'flex',alignItems:'center',gap:6,padding:'9px 10px',borderRadius:10,cursor:'pointer',background:ativaId===c.id?'rgba(139,92,246,.15)':'transparent',color:ativaId===c.id?'#fff':'rgba(255,255,255,.6)'}}>
      <span style={{fontSize:13,flex:1,overflow:'hidden',textOverflow:'ellipsis' as const,whiteSpace:'nowrap' as const}}>{c.isWhats?'💬 ':''}{c.titulo}</span>
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();togglePinConversaLuna(c.id)}} title={c.fixada?'Desafixar':'Fixar'} style={{background:'none',border:'none',color:c.fixada?C.warn:'rgba(255,255,255,.25)',cursor:'pointer',fontSize:12,flexShrink:0}}>📌</button>}
      {!c.isWhats&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();excluirConversa(c.id)}} style={{background:'none',border:'none',color:'rgba(255,255,255,.3)',cursor:'pointer',fontSize:12,flexShrink:0}}>✕</button>}
    </div>)
  }
  const chipsContextuaisLuna=(()=>{const base=insightsVisiveisLuna.filter(i=>i.tipo==='atencao'||i.tipo==='sugestao').slice(0,4).map(i=>i.titulo);return base.length>0?base:['Resumo do dia']})()
  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:16}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Luna</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Sua assistente pessoal — entende texto, áudio e imagem.</p></div>
      {abaLuna==='conversar'&&<button onClick={novaConversa} style={{background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer',flexShrink:0,whiteSpace:'nowrap' as const}}>+ Nova conversa</button>}
    </div>
    <div style={{display:'flex',gap:6,marginBottom:20,borderBottom:`1px solid ${C.line}`}}>
      {(['insights','conversar'] as const).map(ab=>(<button key={ab} onClick={()=>setAbaLuna(ab)} style={{background:'none',border:'none',borderBottom:`2px solid ${abaLuna===ab?C.acc2:'transparent'}`,color:abaLuna===ab?'#fff':'rgba(255,255,255,.4)',fontWeight:abaLuna===ab?700:500,fontSize:13.5,padding:'0 4px 10px',marginRight:14,cursor:'pointer'}}>{ab==='insights'?'📊 Insights':'💬 Conversar'}</button>))}
    </div>
    {abaLuna==='insights'?(<div>
      <div style={{display:'flex',gap:8,flexWrap:'wrap' as const,marginBottom:10}}>
        {(['Todos','Saúde','Trabalho','Família','Casa','Desenvolvimento','Espiritual'] as const).map(cat=>(<button key={cat} onClick={()=>setCategoriaLuna(cat)} style={{background:categoriaLuna===cat?`linear-gradient(135deg,${C.acc},#7c3aed)`:C.s2,color:'#fff',border:`1px solid ${categoriaLuna===cat?'transparent':C.line}`,borderRadius:20,padding:'6px 13px',fontSize:12,fontWeight:600,cursor:'pointer'}}>{cat}</button>))}
      </div>
      <div style={{display:'flex',gap:8,marginBottom:20}}>
        {([7,30,90] as const).map(n=>(<button key={n} onClick={()=>setPeriodoLuna(n)} style={{background:periodoLuna===n?'rgba(139,92,246,.15)':'transparent',color:periodoLuna===n?C.acc2:'rgba(255,255,255,.4)',border:`1px solid ${periodoLuna===n?'rgba(139,92,246,.3)':C.line}`,borderRadius:20,padding:'5px 12px',fontSize:11.5,cursor:'pointer'}}>{n} dias</button>))}
      </div>
      {insightsVisiveisLuna.length===0&&<div style={{fontSize:13,color:'rgba(255,255,255,.4)',padding:'20px 0'}}>Ainda não há insights relevantes com esses filtros. Continue registrando seus dados pelo app.</div>}
      <SecaoInsightsLuna titulo="O que merece sua atenção" tipo="atencao" itens={porTipoLuna.atencao}/>
      <SecaoInsightsLuna titulo="Padrões percebidos" tipo="padrao" itens={porTipoLuna.padrao}/>
      <SecaoInsightsLuna titulo="Mudanças e progresso" tipo="progresso" itens={porTipoLuna.progresso}/>
      <SecaoInsightsLuna titulo="Sugestões da Luna" tipo="sugestao" itens={porTipoLuna.sugestao}/>
    </div>):(
    <div style={{display:'flex',gap:16,height:'60vh'}}>
"""
s = replace_once(s, old6, new6, "cabecalho-tabs-luna")

# 7) Sidebar de conversas agrupada (Fixadas/Hoje/Ontem/Recentes)
old7 = """    <div style={{width:220,flexShrink:0,background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:10,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:4}}>
      {[{id:WHATSAPP_THREAD_ID,titulo:'WhatsApp',fixa:true},...conversas.map(c=>({id:c.id,titulo:c.titulo,fixa:false}))].map(c=>(
        <div key={c.id} onClick={()=>setAtivaId(c.id)} style={{display:'flex',alignItems:'center',gap:6,padding:'9px 10px',borderRadius:10,cursor:'pointer',background:ativaId===c.id?'rgba(139,92,246,.15)':'transparent',color:ativaId===c.id?'#fff':'rgba(255,255,255,.6)'}}>
          <span style={{fontSize:13,flex:1,overflow:'hidden',textOverflow:'ellipsis' as const,whiteSpace:'nowrap' as const}}>{c.fixa?'💬 ':''}{c.titulo}</span>
          {!c.fixa&&<button onClick={(e:React.MouseEvent)=>{e.stopPropagation();excluirConversa(c.id)}} style={{background:'none',border:'none',color:'rgba(255,255,255,.3)',cursor:'pointer',fontSize:12,flexShrink:0}}>✕</button>}
        </div>
      ))}
      {conversas.length===0&&<div style={{fontSize:11,color:'rgba(255,255,255,.3)',padding:'8px 10px'}}>Suas conversas aparecem aqui.</div>}
    </div>"""
new7 = """    <div style={{width:220,flexShrink:0,background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:10,overflowY:'auto' as const,display:'flex',flexDirection:'column' as const,gap:4}}>
      <div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'4px 10px 2px'}}>Fixadas</div>
      {grupoFixadasConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {grupoHojeConvLuna.length>0&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'10px 10px 2px'}}>Hoje</div>}
      {grupoHojeConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {grupoOntemConvLuna.length>0&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'10px 10px 2px'}}>Ontem</div>}
      {grupoOntemConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {grupoRecentesConvLuna.length>0&&<div style={{fontSize:10,color:'rgba(255,255,255,.3)',textTransform:'uppercase' as const,letterSpacing:'.5px',padding:'10px 10px 2px'}}>Recentes</div>}
      {grupoRecentesConvLuna.map(c=><ItemConversaLuna key={c.id} c={c}/>)}
      {conversas.length===0&&<div style={{fontSize:11,color:'rgba(255,255,255,.3)',padding:'8px 10px'}}>Suas conversas aparecem aqui.</div>}
    </div>"""
s = replace_once(s, old7, new7, "sidebar-conversas-agrupada")

# 8) Chips de sugestão contextuais no lugar dos fixos
old8 = "      <div style={{display:'flex',flexWrap:'wrap' as const,gap:6,margin:'12px 0'}}>{['Resumo do dia','Estoque tirzepatida','Contas a vencer','Sequência de leitura'].map(c=>(<button key={c} onClick={()=>setInp(c)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:20,padding:'6px 12px',fontSize:11,color:'rgba(255,255,255,.6)',cursor:'pointer'}}>{c}</button>))}</div>"
new8 = "      <div style={{display:'flex',flexWrap:'wrap' as const,gap:6,margin:'12px 0'}}>{chipsContextuaisLuna.map(c=>(<button key={c} onClick={()=>setInp(c)} style={{background:'rgba(255,255,255,.06)',border:`1px solid ${C.line}`,borderRadius:20,padding:'6px 12px',fontSize:11,color:'rgba(255,255,255,.6)',cursor:'pointer'}}>{c}</button>))}</div>"
s = replace_once(s, old8, new8, "chips-contextuais")

# 9) Fecha o ternario aberto no passo 6 (aba Conversar) antes do fechamento da função
old9 = """    </div>
    </div>
  </div>)
}
function Config(){"""
new9 = """    </div>
    </div>
    )}
  </div>)
}
function Config(){"""
s = replace_once(s, old9, new9, "fecha-ternario-luna")

p.write_text(s)
print("TUDO OK:", applied)
