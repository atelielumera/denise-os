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

# 1) Cor propria por projeto (PixelSAV/SecaVita/Impressoes da Domi/Lumera em cores
#    diferentes, Outros tambem, e qualquer projeto novo cadastrado no futuro cai numa
#    cor consistente pelo nome em vez de tudo ficar roxo igual).
old1 = "const COLS_TRAB=[['pendente','Pendente',C.warn],['andamento','Em andamento',C.acc2],['aguardando','Aguardando',C.water],['concluído','Concluído',C.ok]] as [string,string,string][]"
new1 = '''const COLS_TRAB=[['pendente','Pendente',C.warn],['andamento','Em andamento',C.acc2],['aguardando','Aguardando',C.water],['concluído','Concluído',C.ok]] as [string,string,string][]
const CORES_PROJETO_TRAB:Record<string,string>={'PixelSAV':C.acc2,'SecaVita':C.ok,'Impressões da Domi':C.pink,'Lumera':C.water,'Outros':C.warn}
const PALETA_PROJETO_FALLBACK_TRAB=[C.acc2,C.ok,C.pink,C.water,C.warn,C.teal,'#fb923c']
function hexParaRgbaTrab(hex:string,alpha:number):string{
  const h=hex.replace('#','')
  const r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16)
  return `rgba(${r},${g},${b},${alpha})`
}
function corProjetoTrab(nome:string):string{
  if(CORES_PROJETO_TRAB[nome])return CORES_PROJETO_TRAB[nome]
  let hash=0
  for(let i=0;i<nome.length;i++)hash=(hash*31+nome.charCodeAt(i))>>>0
  return PALETA_PROJETO_FALLBACK_TRAB[hash%PALETA_PROJETO_FALLBACK_TRAB.length]
}'''
s = replace_once(s, old1, new1, "cores-projeto-helper")

# 2) Tag do projeto no card do Kanban.
old2 = "        <span style={{fontSize:11,background:'rgba(139,92,246,.15)',color:C.acc2,padding:'2px 8px',borderRadius:20}}>{tk.p}</span>"
new2 = "        <span style={{fontSize:11,background:hexParaRgbaTrab(corProjetoTrab(tk.p),.15),color:corProjetoTrab(tk.p),padding:'2px 8px',borderRadius:20}}>{tk.p}</span>"
s = replace_once(s, old2, new2, "tag-kanban")

# 3) Tag do projeto no card de "Prioridades de hoje".
old3 = "            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><span style={{fontSize:11,color:C.acc2}}>{tk.p}</span>{pl&&<span style={{fontSize:10.5,color:pl.cor}}>{pl.texto}</span>}</div>"
new3 = "            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><span style={{fontSize:11,color:corProjetoTrab(tk.p),fontWeight:600}}>{tk.p}</span>{pl&&<span style={{fontSize:10.5,color:pl.cor}}>{pl.texto}</span>}</div>"
s = replace_once(s, old3, new3, "tag-prioridades")

p.write_text(s)
print("TUDO OK:", applied)
