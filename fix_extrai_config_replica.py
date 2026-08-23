import pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent
feitos = []

def replace_once(path, old, new, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n != 1:
        print(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new, 1), encoding='utf-8')
    feitos.append(label)

def write_new_file(path, content, label):
    p = BASE / path
    if p.exists():
        print(f"ABORTADO ({label}): {path} ja existe. Nada foi alterado.")
        sys.exit(1)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    feitos.append(label)

# ---------- src/config.ts (novo arquivo) ----------

CONFIG_TS = """// Dados pessoais e padroes desta instancia do sistema.
// Pra replicar pra uma cliente nova: edite so este arquivo com os dados dela
// (rotina, horarios de busca das criancas, localizacao). Nomes das chaves
// "domi"/"derick" continuam fixos no resto do codigo - trocar quem sao as
// pessoas (e nao so os horarios delas) ainda exige editar os componentes
// que usam esses nomes, isso aqui nao resolve sozinho.

export const NOME_RESPONSAVEL_PADRAO: Record<string, string> = { denise: 'Denise', flavio: 'Flávio' }

export const FAMILIA_PADRAO: Record<string, { dropOff: string, pk: Record<number, string>, entrada?: string, responsavel?: string }> = {
  domi: { dropOff: '07:00', pk: { 1: '12:50', 2: '11:40', 3: '12:50', 4: '11:40', 5: '13:00' }, entrada: '07:00', responsavel: 'denise' },
  derick: { dropOff: '07:00', pk: { 1: '17:00', 2: '17:00', 3: '17:00', 4: '17:00', 5: '17:00' }, entrada: '07:00', responsavel: 'flavio' },
}

export const ROTINA_PADRAO = [
  { t: '05:30', n: 'Devocional', cat: 'Espiritual' },
  { t: '06:00', n: 'Acordar · água · humor', cat: 'Saúde' },
  { t: '06:30', n: 'Café · whey · creatina', cat: 'Alimentação' },
  { t: '07:00', n: 'Levar crianças à escola', cat: 'Família' },
  { t: '07:30', n: 'Calistenia', cat: 'Exercícios' },
  { t: '08:20', n: 'Banho · skincare', cat: 'Casa' },
  { t: '08:45', n: 'Planejar o dia · prioridades', cat: 'Trabalho' },
  { t: '09:30', n: 'Lanche da manhã', cat: 'Alimentação' },
  { t: '12:50', n: 'Buscar Domi', cat: 'Família' },
  { t: '15:30', n: 'Whey da tarde', cat: 'Alimentação' },
  { t: '17:00', n: 'Buscar Derick', cat: 'Família' },
  { t: '19:00', n: 'Jantar', cat: 'Alimentação' },
  { t: '20:00', n: 'Célula (Qua) / Aula (Sex)', cat: 'Compromisso' },
  { t: '21:30', n: 'Probióticos', cat: 'Saúde' },
  { t: '22:00', n: 'Leitura · 20 min', cat: 'Desenvolvimento' },
]

// Usada so pro card de clima da Home. Coordenadas da cidade da cliente.
export const LOCALIZACAO_PADRAO = { latitude: -23.55, longitude: -46.63 }
"""

write_new_file('src/config.ts', CONFIG_TS, 'cria-src-config-ts')

# ---------- src/main.tsx: importa e usa o config no lugar dos literais ----------

replace_once(
    'src/main.tsx',
    """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, NavLink, Outlet, Navigate, useNavigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import { supabase } from './lib/supabase'""",
    """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, NavLink, Outlet, Navigate, useNavigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import { supabase } from './lib/supabase'
import { NOME_RESPONSAVEL_PADRAO, FAMILIA_PADRAO, ROTINA_PADRAO, LOCALIZACAO_PADRAO } from './config'""",
    'main-import-config'
)

replace_once(
    'src/main.tsx',
    "const NOME_RESPONSAVEL:Record<string,string>={denise:'Denise',flavio:'Flávio'}",
    "const NOME_RESPONSAVEL:Record<string,string>=NOME_RESPONSAVEL_PADRAO",
    'main-nome-responsavel'
)

replace_once(
    'src/main.tsx',
    "const defaultFam:Record<string,FamData>={domi:{dropOff:'07:00',pk:{1:'12:50',2:'11:40',3:'12:50',4:'11:40',5:'13:00'},entrada:'07:00',responsavel:'denise'},derick:{dropOff:'07:00',pk:{1:'17:00',2:'17:00',3:'17:00',4:'17:00',5:'17:00'},entrada:'07:00',responsavel:'flavio'}}",
    "const defaultFam:Record<string,FamData>=FAMILIA_PADRAO as Record<string,FamData>",
    'main-default-fam'
)

replace_once(
    'src/main.tsx',
    "  const ROTINA_DEF_SHELL=[{t:'05:30',n:'Devocional',cat:'Espiritual'},{t:'06:00',n:'Acordar · água · humor',cat:'Saúde'},{t:'06:30',n:'Café · whey · creatina',cat:'Alimentação'},{t:'07:00',n:'Levar crianças à escola',cat:'Família'},{t:'07:30',n:'Calistenia',cat:'Exercícios'},{t:'08:20',n:'Banho · skincare',cat:'Casa'},{t:'08:45',n:'Planejar o dia · prioridades',cat:'Trabalho'},{t:'09:30',n:'Lanche da manhã',cat:'Alimentação'},{t:'12:50',n:'Buscar Domi',cat:'Família'},{t:'15:30',n:'Whey da tarde',cat:'Alimentação'},{t:'17:00',n:'Buscar Derick',cat:'Família'},{t:'19:00',n:'Jantar',cat:'Alimentação'},{t:'20:00',n:'Célula (Qua) / Aula (Sex)',cat:'Compromisso'},{t:'21:30',n:'Probióticos',cat:'Saúde'},{t:'22:00',n:'Leitura · 20 min',cat:'Desenvolvimento'}]",
    "  const ROTINA_DEF_SHELL=ROTINA_PADRAO",
    'main-rotina-shell'
)

replace_once(
    'src/main.tsx',
    "  const ROTINA_DEF_HOME:RItemHome[]=[{t:'05:30',n:'Devocional',cat:'Espiritual'},{t:'06:00',n:'Acordar · água · humor',cat:'Saúde'},{t:'06:30',n:'Café · whey · creatina',cat:'Alimentação'},{t:'07:00',n:'Levar crianças à escola',cat:'Família'},{t:'07:30',n:'Calistenia',cat:'Exercícios'},{t:'08:20',n:'Banho · skincare',cat:'Casa'},{t:'08:45',n:'Planejar o dia · prioridades',cat:'Trabalho'},{t:'09:30',n:'Lanche da manhã',cat:'Alimentação'},{t:'12:50',n:'Buscar Domi',cat:'Família'},{t:'15:30',n:'Whey da tarde',cat:'Alimentação'},{t:'17:00',n:'Buscar Derick',cat:'Família'},{t:'19:00',n:'Jantar',cat:'Alimentação'},{t:'20:00',n:'Célula (Qua) / Aula (Sex)',cat:'Compromisso'},{t:'21:30',n:'Probióticos',cat:'Saúde'},{t:'22:00',n:'Leitura · 20 min',cat:'Desenvolvimento'}]",
    "  const ROTINA_DEF_HOME:RItemHome[]=ROTINA_PADRAO as RItemHome[]",
    'main-rotina-home'
)

replace_once(
    'src/main.tsx',
    "    fetch('https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current=temperature_2m&timezone=America%2FSao_Paulo')",
    "    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${LOCALIZACAO_PADRAO.latitude}&longitude=${LOCALIZACAO_PADRAO.longitude}&current=temperature_2m&timezone=America%2FSao_Paulo`)",
    'main-clima-localizacao'
)

# Remove os dados de seed pessoais (peso/altura/consultas/remedios reais dos
# seus filhos) que hoje ficam escondidos dentro do codigo como fallback -
# uma cliente nova NAO pode nascer com os dados da Domi e do Derick.
replace_once(
    'src/main.tsx',
    """  React.useEffect(()=>{
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
""",
    "",
    'main-remove-seed-pessoal-criancas'
)

# Remove a lista real de provas da Domi que ficava escondida como fallback
# sempre que dos_avals.domi estivesse vazio - uma cliente nova nao pode
# nascer com o calendario escolar da sua filha.
replace_once(
    'src/main.tsx',
    """  const [avals,setAvals]=React.useState<Record<string,Aval[]>>(()=>{
    try{
      const stored=JSON.parse(localStorage.getItem('dos_avals')||'{}')
      if(!stored.domi||stored.domi.length===0){
        stored.domi=[
          {data:'11/08',tipo:'📝 Prod. Textual AV1',obs:'Poema de Cordel · peso 10',feito:false},
          {data:'12/08',tipo:'🔬 Ciências AV1',obs:'Mapa mental Sistema Urinário · peso 10',feito:false},
          {data:'14/08',tipo:'🔢 Matemática AV1',obs:'Números decimais · peso 10',feito:false},
          {data:'17/08',tipo:'📖 Português AV1',obs:'Caps 8 e 9 · peso 10',feito:false},
          {data:'17/08',tipo:'🎵 Música AV1',obs:'Parâmetros sonoros · págs 57-60 · peso 10',feito:false},
          {data:'17/08',tipo:'⚽ Ed. Física AV1',obs:'Importância da Atividade Física · peso 10',feito:false},
          {data:'18/08',tipo:'🇬🇧 Inglês AV1',obs:'Routine págs 44-48 · peso 10',feito:false},
          {data:'18/08',tipo:'🎨 Arte AV1',obs:'Colagem figuras geométricas · peso 10',feito:false},
          {data:'19/08',tipo:'📜 História AV1',obs:'Símbolos nacionais · Agência Publicidade · peso 10',feito:false},
          {data:'01/09',tipo:'🔢 Matemática AV3',obs:'Números decimais · lista exercícios · peso 10',feito:false},
          {data:'02/09',tipo:'📖 Português AV3',obs:'Notícia do dia que nasceu · apresentação · peso 10',feito:false},
          {data:'11/09',tipo:'📝 Prod. Textual AV2',obs:'Nossa Turma em Cordel · poema · peso 10',feito:false},
          {data:'14/09',tipo:'📜 História AV2',obs:'Caps 8 e 9 · apostila págs 78-92 · peso 10',feito:false},
          {data:'16/09',tipo:'🔬 Ciências AV2',obs:'Sistema Urinário + Nervoso · págs 129-148 · peso 10',feito:false},
          {data:'17/09',tipo:'📖 Português AV2',obs:'Cordel, rimas, parônimas, conjunções · peso 10',feito:false},
          {data:'18/09',tipo:'🌍 Geografia AV2',obs:'Indústria e Trabalho · caps 8 e 9 · peso 10',feito:false},
          {data:'21/09',tipo:'🔄 Recuperação Prod. Textual',obs:'',feito:false},
          {data:'22/09',tipo:'🔄 Recuperação Português',obs:'',feito:false},
          {data:'28/09',tipo:'🔄 Recuperação Matemática',obs:'',feito:false},
          {data:'29/09',tipo:'🔄 Recuperação Ciências',obs:'',feito:false},
          {data:'30/09',tipo:'🔄 Recuperação História/Geografia',obs:'',feito:false},
        ]
      }
      const migrado:Record<string,Aval[]>={}
      Object.keys(stored).forEach(k=>{migrado[k]=(stored[k]||[]).map(migrarAval)})
      return migrado
    }catch{return {domi:[],derick:[]}}
  })""",
    """  const [avals,setAvals]=React.useState<Record<string,Aval[]>>(()=>{
    try{
      const stored=JSON.parse(localStorage.getItem('dos_avals')||'{}')
      const migrado:Record<string,Aval[]>={}
      Object.keys(stored).forEach(k=>{migrado[k]=(stored[k]||[]).map(migrarAval)})
      return migrado
    }catch{return {domi:[],derick:[]}}
  })""",
    'main-remove-seed-provas-domi'
)

print('TUDO OK:', feitos)
