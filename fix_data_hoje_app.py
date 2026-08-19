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

# Bug sistemico: em 27 lugares do app, "hoje" era calculado com .toISOString().slice(0,10),
# que sempre retorna a data em UTC - nao no horario de Brasilia. Entre ~21h e meia-noite
# (horario de Brasilia), isso fazia registros de hoje (treino, leitura, devocional, rotina,
# agua, sequencias) serem salvos/contados com a data de amanha por engano.
# Este script adiciona um helper isoBR(data) que converte para data local de Brasilia,
# e substitui todas as 27 ocorrencias, uma a uma, verificando cada uma.

pares = [
  ("hojeIsoAgua-e-helper-isoBR",
   "function hojeIsoAgua(){return new Date().toISOString().slice(0,10)}",
   "function isoBR(d:Date){return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Sao_Paulo'}).format(d)}\nfunction hojeIsoAgua(){return isoBR(new Date())}"),
  ("shell-sequencia-agua-while",
   "    while(dias.has(dt.toISOString().slice(0,10))){n++;dt.setDate(dt.getDate()-1)}",
   "    while(dias.has(isoBR(dt))){n++;dt.setDate(dt.getDate()-1)}"),
  ("shell-sequenciaAguaShell-while",
   "      while((log[dt.toISOString().slice(0,10)]||0)>=2500){n++;dt.setDate(dt.getDate()-1)}",
   "      while((log[isoBR(dt)]||0)>=2500){n++;dt.setDate(dt.getDate()-1)}"),
  ("shell-ultimos7Shell",
   "  const ultimos7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(6-i));return d.toISOString().slice(0,10)})",
   "  const ultimos7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(6-i));return isoBR(d)})"),
  ("shell-anteriores7Shell",
   "  const anteriores7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(13-i));return d.toISOString().slice(0,10)})",
   "  const anteriores7Shell=Array.from({length:7},(_,i)=>{const d=new Date();d.setDate(d.getDate()-(13-i));return isoBR(d)})"),
  ("home-hojeIsoHome",
   "  const hojeIsoHome=new Date().toISOString().slice(0,10)",
   "  const hojeIsoHome=isoBR(new Date())"),
  ("home-devSequencia-while",
   "  while(devDiasSet.has(devDcursor.toISOString().slice(0,10))){devSequencia++;devDcursor.setDate(devDcursor.getDate()-1)}",
   "  while(devDiasSet.has(isoBR(devDcursor))){devSequencia++;devDcursor.setDate(devDcursor.getDate()-1)}"),
  ("home-segIsoHome",
   "  const segIsoHome=segundaDaSemanaHome(new Date()).toISOString().slice(0,10)",
   "  const segIsoHome=isoBR(segundaDaSemanaHome(new Date()))"),
  ("home-rotinaDiaKey",
   "  const rotinaDiaKey=`dos_rotina_done_${new Date().toISOString().slice(0,10)}`",
   "  const rotinaDiaKey=`dos_rotina_done_${isoBR(new Date())}`"),
  ("espiritual-isoHoje",
   "  function isoHoje(){return new Date().toISOString().slice(0,10)}",
   "  function isoHoje(){return isoBR(new Date())}"),
  ("espiritual-sequencia-while",
   "  while(diasComEntrada.has(dcursor.toISOString().slice(0,10))){sequencia++;dcursor.setDate(dcursor.getDate()-1)}",
   "  while(diasComEntrada.has(isoBR(dcursor))){sequencia++;dcursor.setDate(dcursor.getDate()-1)}"),
  ("exercicios-reg-data",
   "    const reg={data:new Date().toISOString().slice(0,10),tipo,duracaoMin:Math.max(1,Math.round(dur/60))}",
   "    const reg={data:isoBR(new Date()),tipo,duracaoMin:Math.max(1,Math.round(dur/60))}"),
  ("exercicios-plano-semana",
   "  const plano=PLANO_SEMANA.map(([d,t],i)=>{const dt=new Date(seg);dt.setDate(seg.getDate()+i);const iso=dt.toISOString().slice(0,10);return [d,t,diasComTreino.has(iso)] as [string,string,boolean]})",
   "  const plano=PLANO_SEMANA.map(([d,t],i)=>{const dt=new Date(seg);dt.setDate(seg.getDate()+i);const iso=isoBR(dt);return [d,t,diasComTreino.has(iso)] as [string,string,boolean]})"),
  ("exercicios-date-state",
   "  const [date,setDate]=React.useState(new Date().toISOString().slice(0,10))",
   "  const [date,setDate]=React.useState(isoBR(new Date()))"),
  ("desenvolvimento-reg-leitura",
   "    const reg={data:new Date().toISOString().slice(0,10),pag:Number(pag)||0,min:Number(min)||0,apren}",
   "    const reg={data:isoBR(new Date()),pag:Number(pag)||0,min:Number(min)||0,apren}"),
  ("desenvolvimento-hojeIso",
   "  const dcursor=new Date()\n  const hojeIso=new Date().toISOString().slice(0,10)\n  if(!diasComLeitura.has(hojeIso))dcursor.setDate(dcursor.getDate()-1)",
   "  const dcursor=new Date()\n  const hojeIso=isoBR(new Date())\n  if(!diasComLeitura.has(hojeIso))dcursor.setDate(dcursor.getDate()-1)"),
  ("desenvolvimento-sequenciaLeitura-while",
   "  while(diasComLeitura.has(dcursor.toISOString().slice(0,10))){sequenciaLeitura++;dcursor.setDate(dcursor.getDate()-1)}",
   "  while(diasComLeitura.has(isoBR(dcursor))){sequenciaLeitura++;dcursor.setDate(dcursor.getDate()-1)}"),
  ("relatorios-sequencia-while",
   "    while(dias.has(d.toISOString().slice(0,10))){n++;d.setDate(d.getDate()-1)}",
   "    while(dias.has(isoBR(d))){n++;d.setDate(d.getDate()-1)}"),
  ("relatorios-treinosSemana",
   "  const treinosSemana=(()=>{const hoje=new Date();const dias=diasUnicos(treinosI);let c=0;for(let i=0;i<7;i++){const d=new Date(hoje);d.setDate(d.getDate()-i);if(dias.has(d.toISOString().slice(0,10)))c++}return c})()",
   "  const treinosSemana=(()=>{const hoje=new Date();const dias=diasUnicos(treinosI);let c=0;for(let i=0;i<7;i++){const d=new Date(hoje);d.setDate(d.getDate()-i);if(dias.has(isoBR(d)))c++}return c})()"),
  ("relatorios-hojeIsoI",
   "  const hojeIsoI=new Date().toISOString().slice(0,10)",
   "  const hojeIsoI=isoBR(new Date())"),
  ("relatorios-em7diasIsoI",
   "  const em7diasIsoI=new Date(Date.now()+7*86400000).toISOString().slice(0,10)",
   "  const em7diasIsoI=isoBR(new Date(Date.now()+7*86400000))"),
  ("relatorios-diasAtivosR-for",
   "    for(let d=0;d<7;d++){const dia=new Date(inicio);dia.setDate(dia.getDate()+d);if(diasAtivosR.has(dia.toISOString().slice(0,10)))ativos++}",
   "    for(let d=0;d<7;d++){const dia=new Date(inicio);dia.setDate(dia.getDate()+d);if(diasAtivosR.has(isoBR(dia)))ativos++}"),
  ("relatorios-hojeIsoR",
   "  const hojeIsoR=new Date().toISOString().slice(0,10)",
   "  const hojeIsoR=isoBR(new Date())"),
  ("assistente-sequencia-oneliner",
   "    function sequencia(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(d.toISOString().slice(0,10))){n++;d.setDate(d.getDate()-1)}return n}",
   "    function sequencia(dias:Set<string>):number{let n=0;const d=new Date();while(dias.has(isoBR(d))){n++;d.setDate(d.getDate()-1)}return n}"),
  ("assistente-hojeIso",
   "    const hojeIso=new Date().toISOString().slice(0,10)",
   "    const hojeIso=isoBR(new Date())"),
  ("assistente-em7diasIso",
   "    const em7diasIso=new Date(Date.now()+7*86400000).toISOString().slice(0,10)",
   "    const em7diasIso=isoBR(new Date(Date.now()+7*86400000))"),
  ("config-exportar-download",
   "    a.download=`denise-os-dados-${new Date().toISOString().slice(0,10)}.json`",
   "    a.download=`denise-os-dados-${isoBR(new Date())}.json`"),
]

for label, old, new in pares:
    s = replace_once(s, old, new, label)
    applied.append(label)

main_file.write_text(s)
print(f"OK - {len(applied)} lugares corrigidos: 'hoje' agora sempre em horario de Brasilia, nao mais UTC.")
for a in applied:
    print(" -", a)
