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

# BUG REAL ENCONTRADO: se a leitura do snapshot remoto falhar (erro de rede,
# permissao, etc.) o codigo nao verificava isso - so tratava como se o
# servidor estivesse vazio ({}), pulava todas as mesclagens, e ainda assim
# subia os dados so-locais por cima do servidor no final (fora do try/catch).
# Isso podia apagar itens que a Luna acabou de gravar via WhatsApp, em
# qualquer navegador, sempre que essa falha de leitura acontecesse antes do
# proximo ciclo de 30s. Agora: se a leitura do servidor falhar, a sincronizacao
# e cancelada nesse ciclo (nao sobrescreve nada), e o upload so acontece se a
# leitura e mesclagem realmente deram certo.
replace_once(
    'src/main.tsx',
    """      try{
        const {data:snap}=await supabase.from('app_snapshot').select('data').eq('id','denise').maybeSingle()
        const remoto=snap?.data||{}""",
    """      try{
        const {data:snap,error:erroLeituraRemota}=await supabase.from('app_snapshot').select('data').eq('id','denise').maybeSingle()
        if(erroLeituraRemota){
          console.error('Sync: falha ao ler snapshot remoto, cancelando esse ciclo pra nao sobrescrever dados com versao desatualizada:',erroLeituraRemota)
          return
        }
        const remoto=snap?.data||{}""",
    'sync-cancela-se-leitura-remota-falhar'
)

replace_once(
    'src/main.tsx',
    """      }catch{}
      supabase.from('app_snapshot').upsert({id:'denise',data:dados,updated_at:new Date().toISOString()}).then(()=>{})
    }""",
    """        await supabase.from('app_snapshot').upsert({id:'denise',data:dados,updated_at:new Date().toISOString()})
      }catch(erroSync){
        console.error('Sync: erro inesperado durante a mesclagem, cancelando esse ciclo pra nao sobrescrever dados:',erroSync)
      }
    }""",
    'sync-upload-so-apos-mesclagem-bem-sucedida'
)

print('TUDO OK:', feitos)
