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

def replace_all_contadas(path, old, new, esperado, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n != esperado:
        print(f"ABORTADO ({label}): esperava {esperado} ocorrencias, encontrei {n}. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new), encoding='utf-8')
    feitos.append(label)

# CAUSA RAIZ DE VERDADE: tanto o app (a cada 30s) quanto a Luna (via WhatsApp)
# faziam "ler o servidor -> esperar -> escrever tudo de volta" (upsert). Se os
# dois aconteciam perto um do outro, quem escrevia por ultimo apagava o que o
# outro tinha acabado de gravar, mesmo com os merges parciais que ja existiam,
# porque o merge so considerava o que o servidor tinha NO MOMENTO DA LEITURA,
# nao o que foi escrito depois, durante a espera. Agora os dois lados usam a
# funcao merge_app_snapshot() do banco (criada via SQL, uma vez so), que faz a
# mesclagem de forma atomica dentro do proprio Postgres - sem essa janela de
# corrida. Precisa ter rodado o SQL da funcao no Supabase antes de usar isso.

# --- app (src/main.tsx): upload final da sincronizacao ---
replace_once(
    'src/main.tsx',
    """        await supabase.from('app_snapshot').upsert({id:'denise',data:{...remoto,...dados},updated_at:new Date().toISOString()})""",
    """        await supabase.rpc('merge_app_snapshot',{p_id:'denise',p_patch:dados})""",
    'main-upload-usa-merge-atomico-do-banco'
)

# --- app (src/main.tsx): compromissos recorrentes (dos_rotina) tambem somem,
# pois nao tem id e nenhum merge cobria isso ainda ---
replace_once(
    'src/main.tsx',
    """        mesclarArrayPorId('dos_agenda')
        mesclarArrayPorId('dos_treinos')
        mesclarArrayPorId('dos_trabalho')""",
    """        mesclarArrayPorId('dos_agenda')
        mesclarArrayPorId('dos_treinos')
        mesclarArrayPorId('dos_trabalho')
        function mesclarRotina(){
          const remotos=Array.isArray(remoto.dos_rotina)?remoto.dos_rotina:[]
          if(remotos.length===0)return
          const locais=Array.isArray(dados.dos_rotina)?dados.dos_rotina:[]
          const chaveItem=(it:any)=>`${it?.n}|${it?.t}|${JSON.stringify(it?.dias||[])}`
          const chavesLocais=new Set(locais.map(chaveItem))
          const novosDoRemoto=remotos.filter((it:any)=>it&&!chavesLocais.has(chaveItem(it)))
          if(novosDoRemoto.length===0)return
          const unidos=[...locais,...novosDoRemoto]
          dados.dos_rotina=unidos
          localStorage.setItem('dos_rotina',JSON.stringify(unidos))
        }
        mesclarRotina()""",
    'main-mescla-rotina-recorrente'
)

# --- webhook (api/whatsapp-webhook.js): todos os pontos que gravavam com
# "data: d" (o objeto inteiro construido no inicio da requisicao) agora usam
# o merge atomico do banco em vez de sobrescrever a coluna inteira ---
replace_all_contadas(
    'api/whatsapp-webhook.js',
    """await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })""",
    """await supabase.rpc('merge_app_snapshot', { p_id: 'denise', p_patch: d })""",
    9,
    'webhook-todos-os-upserts-usam-merge-atomico'
)

# --- webhook: o ponto que grava o historico de chat (data: {...d, dos_luna_chat}) ---
replace_once(
    'api/whatsapp-webhook.js',
    """await supabase.from('app_snapshot').upsert({ id: 'denise', data: { ...d, dos_luna_chat: novoHistorico }, updated_at: new Date().toISOString() })""",
    """await supabase.rpc('merge_app_snapshot', { p_id: 'denise', p_patch: { ...d, dos_luna_chat: novoHistorico } })""",
    'webhook-historico-chat-usa-merge-atomico'
)

print('TUDO OK:', feitos)
