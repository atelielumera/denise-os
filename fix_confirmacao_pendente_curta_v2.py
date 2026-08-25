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

def replace_all_flex(path, old, new, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n < 1:
        print(f"ABORTADO ({label}): nao encontrei nenhuma ocorrencia. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new), encoding='utf-8')
    feitos.append(f"{label} ({n}x)")

p_check = BASE / 'api/whatsapp-webhook.js'
if 'confirmaSimPendente' in p_check.read_text(encoding='utf-8'):
    print('TUDO OK: ja aplicado antes, nada a fazer.')
    sys.exit(0)

# ORDEM IMPORTA: primeiro troca todos os usos existentes, so depois insere a
# linha que DEFINE a variavel nova (que tambem contem esse mesmo texto) - senao
# a propria definicao seria trocada por ela mesma e quebraria tudo.
replace_all_flex(
    'api/whatsapp-webhook.js',
    'PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))',
    'confirmaSimPendente',
    'webhook-pendente-usa-confirma-sim'
)

replace_all_flex(
    'api/whatsapp-webhook.js',
    'PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))',
    'confirmaNaoPendente',
    'webhook-pendente-usa-confirma-nao'
)

replace_once(
    'api/whatsapp-webhook.js',
    """      const textoNormalizado = userText.trim().toLowerCase()
      const pendente = d.dos_luna_pendente""",
    """      const textoNormalizado = userText.trim().toLowerCase()
      const ehRespostaCurtaPendente = textoNormalizado.split(/\\s+/).filter(Boolean).length <= 3
      const confirmaSimPendente = ehRespostaCurtaPendente && PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))
      const confirmaNaoPendente = ehRespostaCurtaPendente && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))
      const pendente = d.dos_luna_pendente""",
    'webhook-pendente-flags-resposta-curta'
)

print('TUDO OK:', feitos)
