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

# 1. Remove o bloco antigo da aba Flavio pendurado depois do dashboard novo
#    (Registrar hoje - Flavio / Medidas iniciais completas / Registrar novas medidas /
#    Evolucao da cintura / Consultas — Flávio / Medicamentos — Flávio), igual foi
#    feito na aba da Denise. A referencia termina no "Resumo semanal".
start_marker = '      <div id="card-registrar-flavio" style={{marginTop:16}}>'
end_marker = "    </div>}\n\n    {aba==='domi'&&<div>"
start = s.index(start_marker)
end = s.index(end_marker)
if start == -1 or end == -1 or end < start:
    raise SystemExit("ABORTADO (remove-bloco-antigo-flavio): marcadores nao encontrados ou fora de ordem.")
removed_len = end - start
s = s[:start] + s[end:]
applied.append(f"remove-bloco-antigo-flavio ({removed_len} chars)")

# 2-11. Limpa states/funcoes que so existiam pra alimentar o bloco removido
#    (sem isso o build quebra com "declared but never used"). Nao apaga dado
#    real nenhum, so o formulario antigo que nao aparece mais na tela.
old2 = "  const [pesoF,setPesoF]=React.useState('')\n  const [savedF,setSavedF]=React.useState(false)\n  const [humorF,setHumorF]=React.useState('')\n  const [energiaF,setEnergiaF]=React.useState('')\n  const [intestinoF,setIntestinoF]=React.useState('')\n  const [sintF,setSintF]=React.useState('')\n  const [sonoF,setSonoF]=React.useState('')\n"
s = replace_once(s, old2, "", "remove-states-registro-flavio-orfaos")

old3 = "  const [medF,setMedF]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_flavio')||'null');return v||[{data:'29/07',pescoco:41,ombro:42,peito:99,cintura:100,bracE:33,bracD:33,antebracoE:28,antebracoD:29,abdSup:96,abdInf:103,coxaE:56,coxaD:55,panturE:42,panturD:42,quadril:108}]}catch{return []}})"
new3 = "  const [medF]=React.useState<any[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_medidas_flavio')||'null');return v||[{data:'29/07',pescoco:41,ombro:42,peito:99,cintura:100,bracE:33,bracD:33,antebracoE:28,antebracoD:29,abdSup:96,abdInf:103,coxaE:56,coxaD:55,panturE:42,panturD:42,quadril:108}]}catch{return []}})"
s = replace_once(s, old3, new3, "remove-setMedF-orfa")

old4 = "  const [novaMedF,setNovaMedF]=React.useState({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})\n  const [savedMedF,setSavedMedF]=React.useState(false)\n"
s = replace_once(s, old4, "", "remove-novaMedF-savedMedF-orfaos")

old5 = "  const [gorduraInF,setGorduraInF]=React.useState('')\n"
s = replace_once(s, old5, "", "remove-gorduraInF-orfa")

old6 = '''  function salvarFlavio(){
    if(!pesoF&&!gorduraInF)return
    const reg:SReg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),peso:Number(pesoF)||0,imc:0,gordura:Number(gorduraInF)||0,humor:Number(humorF)||0,energia:Number(energiaF)||0,intestino:intestinoF,sint:sintF,sono:Number(sonoF)||0}
    const n=[reg,...extrasF];setExtrasF(n);localStorage.setItem('dos_saude_extra_flavio',JSON.stringify(n))
    setSavedF(true);setPesoF('');setHumorF('');setEnergiaF('');setIntestinoF('');setSintF('');setGorduraInF('');setSonoF('')
  }
'''
s = replace_once(s, old6, "", "remove-salvarFlavio-orfa")

old7 = '''  function addMedF(){
    const has=Object.values(novaMedF).some(v=>v!=='')
    if(!has)return
    const reg={data:new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'}),pescoco:Number(novaMedF.pescoco)||0,ombro:Number(novaMedF.ombro)||0,peito:Number(novaMedF.peito)||0,cintura:Number(novaMedF.cintura)||0,bracE:Number(novaMedF.bracE)||0,bracD:Number(novaMedF.bracD)||0,antebracoE:Number(novaMedF.antebracoE)||0,antebracoD:Number(novaMedF.antebracoD)||0,abdSup:Number(novaMedF.abdSup)||0,abdInf:Number(novaMedF.abdInf)||0,coxaE:Number(novaMedF.coxaE)||0,coxaD:Number(novaMedF.coxaD)||0,panturE:Number(novaMedF.panturE)||0,panturD:Number(novaMedF.panturD)||0,quadril:Number(novaMedF.quadril)||0}
    const n=[reg,...medF];setMedF(n);localStorage.setItem('dos_medidas_flavio',JSON.stringify(n))
    setSavedMedF(true);setNovaMedF({pescoco:'',ombro:'',peito:'',cintura:'',bracE:'',bracD:'',antebracoE:'',antebracoD:'',abdSup:'',abdInf:'',coxaE:'',coxaD:'',panturE:'',panturD:'',quadril:''})
  }
'''
s = replace_once(s, old7, "", "remove-addMedF-orfa")

old8 = "  const [extrasF,setExtrasF]=React.useState<SReg[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_saude_extra_flavio')||'null');return v||[{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}catch{return [{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}})"
new8 = "  const [extrasF]=React.useState<SReg[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_saude_extra_flavio')||'null');return v||[{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}catch{return [{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}})"
s = replace_once(s, old8, new8, "remove-setExtrasF-orfa")

p.write_text(s)
print("TUDO OK:", applied)
