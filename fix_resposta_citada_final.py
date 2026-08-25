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

# Versao final: cobre todos os lugares onde a Evolution API/Baileys costuma
# guardar a mensagem citada (varia dependendo da versao e do tipo de mensagem
# original), em vez de depender de um unico formato adivinhado. Remove o log
# de diagnostico temporario, que nao e mais necessario.
replace_once(
    'api/whatsapp-webhook.js',
    """    console.error('DIAGNOSTICO mensagem completa:', JSON.stringify({ message: msg, contextInfoNoData: data.contextInfo || null }))
    const textoCitadoPelaResposta = msg.extendedTextMessage?.contextInfo?.quotedMessage?.conversation || msg.extendedTextMessage?.contextInfo?.quotedMessage?.extendedTextMessage?.text || data.contextInfo?.quotedMessage?.conversation || ''""",
    """    const contextInfoCitacao = msg.extendedTextMessage?.contextInfo || msg.contextInfo || data.contextInfo || null
    const quotedMsgCitacao = contextInfoCitacao?.quotedMessage || null
    const textoCitadoPelaResposta = quotedMsgCitacao
      ? (quotedMsgCitacao.conversation || quotedMsgCitacao.extendedTextMessage?.text || quotedMsgCitacao.imageMessage?.caption || quotedMsgCitacao.videoMessage?.caption || '')
      : ''""",
    'webhook-resposta-citada-final-todos-formatos'
)

print('TUDO OK:', feitos)
