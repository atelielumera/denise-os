from pathlib import Path

p = Path("src/main.tsx")
s = p.read_text()

anchor = "  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''})\n"
c = s.count(anchor)
if c != 1:
    raise SystemExit(f"ABORTADO: esperava 1 ocorrencia do ponto de insercao, encontrei {c}.")

seed_effect = '''  const [novoMed,setNovoMed]=React.useState({nome:'',dosagem:'',frequencia:'',horarios:'',ate:''})
  React.useEffect(()=>{
    // Substitui o registro unico/errado do Derick pelos dados da referencia.
    // Roda so 1 vez (marcador dos_derick_seed_v1) pra nao sobrescrever o que
    // voce registrar depois disso.
    if(localStorage.getItem('dos_derick_seed_v1'))return
    const criancasSeed={...criancas,derick:[
      {data:'20/08',peso:16.75,altura:1.09,obs:'Tudo bem'},
      {data:'20/07',peso:16.55,altura:1.08,obs:'Check-up mensal'},
      {data:'20/06',peso:16.10,altura:1.07,obs:''},
      {data:'20/05',peso:15.90,altura:1.06,obs:''},
    ]}
    setCriancas(criancasSeed);localStorage.setItem('dos_criancas',JSON.stringify(criancasSeed))
    const consulsSeed={...consuls,derick:[
      {tipo:'Pediatria',data:'2026-08-27',obs:'',proximo:''},
      {tipo:'Otorrino',data:'2026-06-12',obs:'',proximo:''},
      {tipo:'Pediatria',data:'2026-05-12',obs:'',proximo:''},
    ]}
    setConsuls(consulsSeed);localStorage.setItem('dos_consuls',JSON.stringify(consulsSeed))
    const medicamentosSeed={...medicamentos,derick:[
      {data:'21/08',nome:'Xarope infantil',dosagem:'5ml',frequencia:'2x ao dia',horarios:'08:00 e 20:00',ate:''},
    ]}
    setMedicamentos(medicamentosSeed);localStorage.setItem('dos_medicamentos',JSON.stringify(medicamentosSeed))
    const tamanhosSeed={...tamanhos,derick:{roupa:'4',calcado:'26',camiseta:'4',calca:'4',atualizadoEm:'29/07'}}
    setTamanhos(tamanhosSeed);localStorage.setItem('dos_tamanhos',JSON.stringify(tamanhosSeed))
    localStorage.setItem('dos_derick_seed_v1','1')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])
'''

s = s.replace(anchor, seed_effect, 1)
p.write_text(s)
print("OK: seed unico do Derick aplicado (substitui o registro errado uma vez, marcador dos_derick_seed_v1 evita rodar de novo).")
