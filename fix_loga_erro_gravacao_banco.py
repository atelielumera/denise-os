import pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent
feitos = []

def replace_all_contadas(path, old, new, esperado, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n != esperado:
        print(f"ABORTADO ({label}): esperava {esperado} ocorrencias, encontrei {n}. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new), encoding='utf-8')
    feitos.append(label)

def replace_once(path, old, new, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n != 1:
        print(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new, 1), encoding='utf-8')
    feitos.append(label)

# O fix anterior trocou os upserts por chamadas a merge_app_snapshot(), mas o
# resultado dessas chamadas nunca era checado - se a gravacao no banco falhasse
# (funcao ainda nao visivel pro cache do PostgREST, permissao, o que for), o
# codigo seguia em frente e mandava a confirmacao pra Denise mesmo assim,
# escondendo o erro real. Agora cada gravacao loga o erro (visivel em
# `vercel logs`), pra descobrirmos a causa de verdade se ainda falhar.

replace_all_contadas(
    'api/whatsapp-webhook.js',
    """await supabase.rpc('merge_app_snapshot', { p_id: 'denise', p_patch: d })""",
    """const { error: erroGravarSnap } = await supabase.rpc('merge_app_snapshot', { p_id: 'denise', p_patch: d })
    if (erroGravarSnap) console.error('Erro ao gravar no banco via merge_app_snapshot:', erroGravarSnap)""",
    9,
    'webhook-loga-erro-de-cada-gravacao'
)

replace_once(
    'api/whatsapp-webhook.js',
    """await supabase.rpc('merge_app_snapshot', { p_id: 'denise', p_patch: { ...d, dos_luna_chat: novoHistorico } })""",
    """const { error: erroGravarChat } = await supabase.rpc('merge_app_snapshot', { p_id: 'denise', p_patch: { ...d, dos_luna_chat: novoHistorico } })
      if (erroGravarChat) console.error('Erro ao gravar historico do chat via merge_app_snapshot:', erroGravarChat)""",
    'webhook-loga-erro-gravacao-historico-chat'
)

replace_once(
    'src/main.tsx',
    """        await supabase.rpc('merge_app_snapshot',{p_id:'denise',p_patch:dados})""",
    """        const{error:erroGravarSnapApp}=await supabase.rpc('merge_app_snapshot',{p_id:'denise',p_patch:dados})
        if(erroGravarSnapApp)console.error('Erro ao gravar no banco via merge_app_snapshot:',erroGravarSnapApp)""",
    'main-loga-erro-de-gravacao'
)

print('TUDO OK:', feitos)
