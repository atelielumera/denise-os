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

# 1. Restaura os setters de extras/extrasF (precisamos pra registrar de verdade,
#    nao so "rolar a tela" pra um formulario que nao existe mais).
old1 = "  const [extras]=React.useState<SReg[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_saude_extra')||'[]')}catch{return []}})"
new1 = "  const [extras,setExtras]=React.useState<SReg[]>(()=>{try{return JSON.parse(localStorage.getItem('dos_saude_extra')||'[]')}catch{return []}})"
s = replace_once(s, old1, new1, "restaura-setExtras")

old2 = "  const [extrasF]=React.useState<SReg[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_saude_extra_flavio')||'null');return v||[{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}catch{return [{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}})"
new2 = "  const [extrasF,setExtrasF]=React.useState<SReg[]>(()=>{try{const v=JSON.parse(localStorage.getItem('dos_saude_extra_flavio')||'null');return v||[{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}catch{return [{data:'06/08',peso:95.25,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''},{data:'24/07',peso:95.15,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:''}]}})"
s = replace_once(s, old2, new2, "restaura-setExtrasF")

# 2. Substitui irParaRegistro (que so rolava a tela ate um formulario que ja
#    nao existe mais) por funcoes que registram de verdade, com prompt rapido.
old3 = "function irParaRegistro(pessoa:string){document.getElementById(`card-registrar-${pessoa}`)?.scrollIntoView({behavior:'smooth',block:'center'})}"
new3 = '''type SRegQuick={data:string,peso:number,imc:number,gordura:number,humor:number,energia:number,intestino:string,sint:string,sono?:number}
function registrarCampoRapido(
  pessoa:'denise'|'flavio',
  campo:'peso'|'humor'|'energia'|'intestino'|'sono',
  rotulo:string,
  lista:SRegQuick[],
  setLista:(n:SRegQuick[])=>void,
){
  const valor=window.prompt(rotulo)
  if(valor===null||valor.trim()==='')return
  const chave=pessoa==='denise'?'dos_saude_extra':'dos_saude_extra_flavio'
  const hojeStr=new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})
  const idx=lista.findIndex(r=>r.data===hojeStr)
  const base:SRegQuick=idx>=0?{...lista[idx]}:{data:hojeStr,peso:0,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:'',sono:0}
  if(campo==='peso'){base.peso=Number(valor.replace(',','.'))||0;if(pessoa==='denise')base.imc=Number((base.peso/(1.63**2)).toFixed(1))}
  if(campo==='humor')base.humor=Number(valor)||0
  if(campo==='energia')base.energia=Number(valor)||0
  if(campo==='intestino')base.intestino=valor
  if(campo==='sono')base.sono=Number(valor.replace(',','.'))||0
  const n=idx>=0?lista.map((r,i)=>i===idx?base:r):[base,...lista]
  setLista(n);localStorage.setItem(chave,JSON.stringify(n))
}
function registrarVariosRapido(pessoa:'denise'|'flavio',lista:SRegQuick[],setLista:(n:SRegQuick[])=>void){
  const chave=pessoa==='denise'?'dos_saude_extra':'dos_saude_extra_flavio'
  const hojeStr=new Date().toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})
  const idx=lista.findIndex(r=>r.data===hojeStr)
  const base:SRegQuick=idx>=0?{...lista[idx]}:{data:hojeStr,peso:0,imc:0,gordura:0,humor:0,energia:0,intestino:'',sint:'',sono:0}
  const peso=window.prompt('Peso (kg)? Deixe em branco pra pular.',base.peso?String(base.peso):'')
  if(peso&&peso.trim()){base.peso=Number(peso.replace(',','.'))||0;if(pessoa==='denise')base.imc=Number((base.peso/(1.63**2)).toFixed(1))}
  const gordura=window.prompt('Gordura corporal (%)? Deixe em branco pra pular.',base.gordura?String(base.gordura):'')
  if(gordura&&gordura.trim())base.gordura=Number(gordura.replace(',','.'))||0
  const humor=window.prompt('Humor (1 a 10)? Deixe em branco pra pular.',base.humor?String(base.humor):'')
  if(humor&&humor.trim())base.humor=Number(humor)||0
  const energia=window.prompt('Energia (1 a 10)? Deixe em branco pra pular.',base.energia?String(base.energia):'')
  if(energia&&energia.trim())base.energia=Number(energia)||0
  const intestino=window.prompt('Intestino (Regular/Preso/Solto)? Deixe em branco pra pular.',base.intestino||'')
  if(intestino&&intestino.trim())base.intestino=intestino
  const sono=window.prompt('Sono (horas)? Deixe em branco pra pular.',base.sono?String(base.sono):'')
  if(sono&&sono.trim())base.sono=Number(sono.replace(',','.'))||0
  const sint=window.prompt('Sintomas (opcional)? Deixe em branco pra pular.',base.sint||'')
  if(sint&&sint.trim())base.sint=sint
  const n=idx>=0?lista.map((r,i)=>i===idx?base:r):[base,...lista]
  setLista(n);localStorage.setItem(chave,JSON.stringify(n))
}'''
s = replace_once(s, old3, new3, "adiciona-funcoes-registro-rapido")

# 3. Troca os 6 botoes quebrados de "Ações rápidas" (peso/sono/energia/humor/
#    intestino/+Outro registro) de "rolar pra formulario que sumiu" pra
#    registrar de verdade via prompt rapido.
old4 = "                <button onClick={()=>irParaRegistro(p.pessoa)} style={acaoBtnStyle}>⚖️ Registrar peso</button>"
new4 = "                <button onClick={()=>registrarCampoRapido(p.pessoa,'peso','Peso (kg)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>⚖️ Registrar peso</button>"
s = replace_once(s, old4, new4, "botao-registrar-peso")

old5 = "                <button onClick={()=>irParaRegistro(p.pessoa)} style={acaoBtnStyle}>🌙 Registrar sono</button>"
new5 = "                <button onClick={()=>registrarCampoRapido(p.pessoa,'sono','Quantas horas de sono?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>🌙 Registrar sono</button>"
s = replace_once(s, old5, new5, "botao-registrar-sono")

old6 = "                <button onClick={()=>irParaRegistro(p.pessoa)} style={acaoBtnStyle}>⚡ Registrar energia</button>"
new6 = "                <button onClick={()=>registrarCampoRapido(p.pessoa,'energia','Energia (1 a 10)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>⚡ Registrar energia</button>"
s = replace_once(s, old6, new6, "botao-registrar-energia")

old7 = "                <button onClick={()=>irParaRegistro(p.pessoa)} style={acaoBtnStyle}>😊 Registrar humor</button>"
new7 = "                <button onClick={()=>registrarCampoRapido(p.pessoa,'humor','Humor (1 a 10)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>😊 Registrar humor</button>"
s = replace_once(s, old7, new7, "botao-registrar-humor")

old8 = "                <button onClick={()=>irParaRegistro(p.pessoa)} style={acaoBtnStyle}>💚 Registrar intestino</button>"
new8 = "                <button onClick={()=>registrarCampoRapido(p.pessoa,'intestino','Intestino (Regular/Preso/Solto)?',p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={acaoBtnStyle}>💚 Registrar intestino</button>"
s = replace_once(s, old8, new8, "botao-registrar-intestino")

old9 = "              <button onClick={()=>irParaRegistro(p.pessoa)} style={{...acaoBtnStyle,width:'100%',marginTop:8,opacity:diaEhHoje?1:.4,pointerEvents:diaEhHoje?'auto' as const:'none' as const}}>+ Outro registro</button>"
new9 = "              <button onClick={()=>registrarVariosRapido(p.pessoa,p.pessoa==='denise'?extras:extrasF,p.pessoa==='denise'?setExtras:setExtrasF)} style={{...acaoBtnStyle,width:'100%',marginTop:8,opacity:diaEhHoje?1:.4,pointerEvents:diaEhHoje?'auto' as const:'none' as const}}>+ Outro registro</button>"
s = replace_once(s, old9, new9, "botao-outro-registro")

# 4. O botao do cabecalho "+ Novo registro" tambem rolava pra formulario que
#    sumiu quando a aba e Denise/Flavio — agora abre o registro completo.
old10 = "        <button onClick={()=>{if(aba==='denise'||aba==='flavio')irParaRegistro(aba);else document.getElementById(`card-registrar-${aba}`)?.scrollIntoView({behavior:'smooth',block:'center'})}} style={{background:`linear-gradient(135deg,${corAba},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>{aba==='denise'||aba==='flavio'?'+ Novo registro':'+ Nova medida'}</button>"
new10 = "        <button onClick={()=>{if(aba==='denise'||aba==='flavio')registrarVariosRapido(aba,aba==='denise'?extras:extrasF,aba==='denise'?setExtras:setExtrasF);else document.getElementById(`card-registrar-${aba}`)?.scrollIntoView({behavior:'smooth',block:'center'})}} style={{background:`linear-gradient(135deg,${corAba},#7c3aed)`,color:'#fff',border:'none',borderRadius:10,padding:'10px 16px',fontSize:13,fontWeight:700,cursor:'pointer',whiteSpace:'nowrap' as const}}>{aba==='denise'||aba==='flavio'?'+ Novo registro':'+ Nova medida'}</button>"
s = replace_once(s, old10, new10, "botao-header-novo-registro")

p.write_text(s)
print("TUDO OK:", applied)
