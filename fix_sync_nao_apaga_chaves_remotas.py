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

# BUG REAL DE VERDADE, CONFIRMADO OLHANDO O BANCO DE DADOS: o upload final da
# sincronizacao mandava so "dados" (construido A PARTIR DO QUE ESSE NAVEGADOR
# TEM SALVO LOCALMENTE) como o valor INTEIRO da coluna no servidor. Isso
# SUBSTITUI o JSON inteiro - nao faz merge no banco. Entao qualquer campo que
# exista no servidor mas nao exista no localStorage desse navegador especifico
# (por qualquer motivo: navegador novo, cache limpo, etc.) e APAGADO do
# servidor na proxima sincronizacao - foi isso que apagou dos_casa_items depois
# que a Luna escreveu via WhatsApp. Agora o upload manda remoto+dados (local
# por cima do que veio do servidor), preservando qualquer campo que o servidor
# tenha e esse navegador nao conheça.
replace_once(
    'src/main.tsx',
    """        await supabase.from('app_snapshot').upsert({id:'denise',data:dados,updated_at:new Date().toISOString()})""",
    """        await supabase.from('app_snapshot').upsert({id:'denise',data:{...remoto,...dados},updated_at:new Date().toISOString()})""",
    'sync-upload-preserva-campos-so-do-servidor'
)

print('TUDO OK:', feitos)
