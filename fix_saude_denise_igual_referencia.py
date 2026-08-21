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

# 1. Remove o bloco antigo da aba Denise que ficava PENDURADO depois do dashboard novo
#    (Registrar hoje / Medidas completas / Registrar novas medidas / Evolucao da cintura /
#    Consultas — Denise / Medicamentos — Denise). A referencia nao tem nada disso: a tela
#    da Denise termina no "Resumo semanal".
start_marker = '      <div id="card-registrar-denise" style={{marginTop:16}}>'
end_marker = "    </div>}\n\n    {aba==='flavio'&&<div>"
start = s.index(start_marker)
end = s.index(end_marker)
if start == -1 or end == -1 or end < start:
    raise SystemExit("ABORTADO (remove-bloco-antigo-denise): marcadores nao encontrados ou fora de ordem.")
removed_len = end - start
s = s[:start] + s[end:]
applied.append(f"remove-bloco-antigo-denise ({removed_len} chars)")

# 2-10. Limpa os states/funcoes/tipos que só existiam para alimentar o bloco removido
#    (sem isso o build quebra com "declared but never used" — nao apaga nenhum dado
#    real, so o formulario antigo que nao aparece mais na tela).
old1 = '''  const MEDIDAS:MReg[]=[
    {data:"11/02",cintura:76,quadril:97,peito:98,coxaE:53,coxaD:54,bracE:27,bracD:28,abdSup:80,abdInf:83},{data:"18/02",cintura:77,quadril:97,peito:97,coxaE:51,coxaD:52,bracE:26,bracD:27,abdSup:82,abdInf:82},{data:"25/02",cintura:73,quadril:93,peito:95,coxaE:50,coxaD:51,bracE:27,bracD:27,abdSup:79,abdInf:81},{data:"04/03",cintura:74,quadril:92.5,peito:92,coxaE:48,coxaD:50,bracE:27,bracD:27,abdSup:78,abdInf:82},{data:"11/03",cintura:73,quadril:91,peito:92,coxaE:51,coxaD:50,bracE:27,bracD:27,abdSup:79,abdInf:82},{data:"18/03",cintura:73,quadril:93,peito:92,coxaE:49,coxaD:49,bracE:24,bracD:24,abdSup:76,abdInf:82},{data:"25/03",cintura:71,quadril:91,peito:92,coxaE:48,coxaD:49.5,bracE:24,bracD:24,abdSup:78,abdInf:80},{data:"29/07",cintura:73,quadril:91.5,peito:91,coxaE:48,coxaD:49,bracE:25,bracD:25.5,abdSup:78,abdInf:81},
  ]
'''
s = replace_once(s, old1, "", "remove-MEDIDAS-orfa")

old2 = "  const [sono,setSono]=React.useState('')\n  const [saved,setSaved]=React.useState(false)\n  const [aba,setAba]=React.useState<'denise'|'flavio'|'domi'|'derick'>('denise')\n"
new2 = "  const [sono,setSono]=React.useState('')\n  const [aba,setAba]=React.useState<'denise'|'flavio'|'domi'|'derick'>('denise')\n"
s = replace_once(s, old2, new2, "remove-saved-orfa")

old3 = "  const [novaMedF,setNovaMedF]=React.useState({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})\n  const [savedMedD,setSavedMedD]=React.useState(false)\n  const [savedMedF,setSavedMedF]=React.useState(false)\n"
new3 = "  const [novaMedF,setNovaMedF]=React.useState({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})\n  const [savedMedF,setSavedMedF]=React.useState(false)\n"
s = replace_once(s, old3, new3, "remove-savedMedD-orfa")

old4 = '''  function salvar(){
    if(!peso&&!humor&&!intestino&&!gorduraIn)return
    const reg:SReg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),peso:Number(peso)||0,imc:peso?Number((Number(peso)/(1.63**2)).toFixed(1)):0,gordura:Number(gorduraIn)||0,humor:Number(humor)||0,energia:Number(energia)||0,intestino,sint,sono:Number(sono)||0}
    const n=[reg,...extras];setExtras(n);localStorage.setItem('dos_saude_extra',JSON.stringify(n))
    setSaved(true);setPeso('');setHumor('');setEnergia('');setIntestino('');setSint('');setSono('');setGorduraIn('')
  }
'''
s = replace_once(s, old4, "", "remove-salvar-orfa")

old5 = '''  function addMedD(){
    const has=Object.values(novaMedD).some(v=>v!=='')
    if(!has)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),pescoco:Number(novaMedD.pescoco)||0,ombro:Number(novaMedD.ombro)||0,peito:Number(novaMedD.peito)||0,cintura:Number(novaMedD.cintura)||0,bracE:Number(novaMedD.bracE)||0,bracD:Number(novaMedD.bracD)||0,antebracoE:Number(novaMedD.antebracoE)||0,antebracoD:Number(novaMedD.antebracoD)||0,abdSup:Number(novaMedD.abdSup)||0,abdInf:Number(novaMedD.abdInf)||0,coxaE:Number(novaMedD.coxaE)||0,coxaD:Number(novaMedD.coxaD)||0,panturE:Number(novaMedD.panturE)||0,panturD:Number(novaMedD.panturD)||0,quadril:Number(novaMedD.quadril)||0}
    const n=[reg,...medD];setMedD(n);localStorage.setItem('dos_medidas_denise',JSON.stringify(n))
    setSavedMedD(true);setNovaMedD({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})
  }
'''
s = replace_once(s, old5, "", "remove-addMedD-orfa")

old6 = "  type MReg={data:string,cintura:number,quadril:number,peito:number,coxaE:number,coxaD:number,bracE:number,bracD:number,abdSup:number,abdInf:number}\n"
s = replace_once(s, old6, "", "remove-MReg-type-orfa")

old7 = "  const [extras,setExtras]=React.useState<SReg[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_saude_extra')||'[]')}catch{return []}})\n  const [peso,setPeso]=React.useState('')\n  const [humor,setHumor]=React.useState('')\n  const [energia,setEnergia]=React.useState('')\n  const [intestino,setIntestino]=React.useState('')\n  const [sint,setSint]=React.useState('')\n  const [sono,setSono]=React.useState('')\n  const [aba,setAba]"
new7 = "  const [extras]=React.useState<SReg[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_saude_extra')||'[]')}catch{return []}})\n  const [aba,setAba]"
s = replace_once(s, old7, new7, "remove-registro-form-states-orfas")

old8 = "  const [medD,setMedD]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_denise')||'null');return v||[{data:'04/06',pescoco:0,ombro:37,peito:91,cintura:73,bracE:25,bracD:25.5,antebracoE:19.5,antebracoD:19,abdSup:78,abdInf:81,coxaE:48,coxaD:49,panturE:31,panturD:33,quadril:91.5}]}catch{return []}})"
new8 = "  const [medD]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_denise')||'null');return v||[{data:'04/06',pescoco:0,ombro:37,peito:91,cintura:73,bracE:25,bracD:25.5,antebracoE:19.5,antebracoD:19,abdSup:78,abdInf:81,coxaE:48,coxaD:49,panturE:31,panturD:33,quadril:91.5}]}catch{return []}})"
s = replace_once(s, old8, new8, "remove-setMedD-orfa")

old9 = "  const [novaMedD,setNovaMedD]=React.useState({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})\n"
s = replace_once(s, old9, "", "remove-novaMedD-orfa")

old10 = "  const [gorduraIn,setGorduraIn]=React.useState('')\n"
s = replace_once(s, old10, "", "remove-gorduraIn-orfa")

p.write_text(s)
print("TUDO OK:", applied)
