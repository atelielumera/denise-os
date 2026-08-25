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

def replace_all_checked(path, old, new, expected_count, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n != expected_count:
        print(f"ABORTADO ({label}): esperava {expected_count} ocorrencias, encontrei {n}. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new), encoding='utf-8')
    feitos.append(label)

# Bug real: uma pergunta pendente da Luna (ex: "ja fez o treino?") fica valendo
# por 30 minutos. Se a Denise mandar QUALQUER outra mensagem nesse meio tempo
# contendo a palavra "sim" ou "nao" em qualquer lugar de uma frase sobre outro
# assunto (ex: "Nao tomei o cha de hortela"), o sistema casava errado com a
# pergunta pendente antiga (treino, evento, boleto) em vez do assunto real.
# Agora so conta como resposta sim/nao pra pergunta pendente quando a mensagem
# for curta mesmo (ate 3 palavras) - uma frase longa sobre outro assunto nao
# ativa mais essa logica por engano.
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

replace_all_checked(
    'api/whatsapp-webhook.js',
    'PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))',
    'confirmaSimPendente',
    4,
    'webhook-pendente-usa-confirma-sim'
)

replace_all_checked(
    'api/whatsapp-webhook.js',
    'PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))',
    'confirmaNaoPendente',
    3,
    'webhook-pendente-usa-confirma-nao'
)

print('TUDO OK:', feitos)
