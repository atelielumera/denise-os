from pathlib import Path

p = Path("src/main.tsx")
s = p.read_text()

anchor = "  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''})\n"
c = s.count(anchor)
if c != 1:
    raise SystemExit(f"ABORTADO: esperava 1 ocorrencia do ponto de insercao, encontrei {c}.")

seed_effect = '''  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''})
  React.useEffect(()=>{
    if((criancas.domi||[]).length>0)return
    const criancasSeed={...criancas,domi:[
      {data:'20/08',peso:34.20,altura:1.32,obs:'Tudo bem'},
      {data:'20/07',peso:33.90,altura:1.315,obs:'Check-up mensal'},
      {data:'20/06',peso:33.40,altura:1.310,obs:''},
      {data:'20/05',peso:32.80,altura:1.300,obs:''},
    ]}
    setCriancas(criancasSeed);localStorage.setItem('dos_criancas',JSON.stringify(criancasSeed))
    const consulsSeed={...consuls,domi:[
      {tipo:'Pediatria',data:'2026-08-27',obs:'',proximo:''},
      {tipo:'Dermatologia',data:'2026-07-10',obs:'',proximo:''},
      {tipo:'Pediatria',data:'2026-05-10',obs:'',proximo:''},
    ]}
    setConsuls(consulsSeed);localStorage.setItem('dos_consuls',JSON.stringify(consulsSeed))
    const medicamentosSeed={...medicamentos,domi:[
      {data:'21/08',nome:'Vitamina D',dosagem:'2 gotas',frequencia:'1x ao dia',horarios:'07:00',ate:''},
    ]}
    setMedicamentos(medicamentosSeed);localStorage.setItem('dos_medicamentos',JSON.stringify(medicamentosSeed))
    const tamanhosSeed={...tamanhos,domi:{roupa:'10',calcado:'33',camiseta:'10',calca:'10',atualizadoEm:'29/07'}}
    setTamanhos(tamanhosSeed);localStorage.setItem('dos_tamanhos',JSON.stringify(tamanhosSeed))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])
'''

s = s.replace(anchor, seed_effect, 1)
p.write_text(s)
print("OK: seed unico da Domi aplicado (so roda se criancas.domi estiver vazio, nao duplica nem sobrescreve o que ja existir).")
