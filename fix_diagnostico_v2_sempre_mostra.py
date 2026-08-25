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

# Espiao v2: mostra SEMPRE a mensagem inteira que chega, sem depender de eu ter
# adivinhado certo onde fica a informacao da resposta citada. Assim aparece de
# qualquer jeito, mesmo se o formato real for diferente do que eu imaginei.
replace_once(
    'api/whatsapp-webhook.js',
    """    if (msg.extendedTextMessage?.contextInfo) {
      console.error('DIAGNOSTICO resposta citada:', JSON.stringify(msg.extendedTextMessage.contextInfo))
    }
    const textoCitadoPelaResposta = msg.extendedTextMessage?.contextInfo?.quotedMessage?.conversation || msg.extendedTextMessage?.contextInfo?.quotedMessage?.extendedTextMessage?.text || ''""",
    """    console.error('DIAGNOSTICO mensagem completa:', JSON.stringify({ message: msg, contextInfoNoData: data.contextInfo || null }))
    const textoCitadoPelaResposta = msg.extendedTextMessage?.contextInfo?.quotedMessage?.conversation || msg.extendedTextMessage?.contextInfo?.quotedMessage?.extendedTextMessage?.text || data.contextInfo?.quotedMessage?.conversation || ''""",
    'webhook-diagnostico-v2-sempre-mostra'
)

print('TUDO OK:', feitos)
