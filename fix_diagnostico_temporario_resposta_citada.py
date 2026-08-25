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

# Espiao temporario: mostra no log o formato real da mensagem quando ela e uma
# resposta citada, pra eu conseguir ver o nome certo do campo. Vai ser removido
# depois que a gente confirmar o formato.
replace_once(
    'api/whatsapp-webhook.js',
    """    const textoCitadoPelaResposta = msg.extendedTextMessage?.contextInfo?.quotedMessage?.conversation || msg.extendedTextMessage?.contextInfo?.quotedMessage?.extendedTextMessage?.text || ''""",
    """    if (msg.extendedTextMessage?.contextInfo) {
      console.error('DIAGNOSTICO resposta citada:', JSON.stringify(msg.extendedTextMessage.contextInfo))
    }
    const textoCitadoPelaResposta = msg.extendedTextMessage?.contextInfo?.quotedMessage?.conversation || msg.extendedTextMessage?.contextInfo?.quotedMessage?.extendedTextMessage?.text || ''""",
    'webhook-diagnostico-contextinfo'
)

print('TUDO OK:', feitos)
