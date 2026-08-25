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

# Quando a Denise usa a funcao "Responder" do WhatsApp (swipe/segurar e responder
# a uma mensagem especifica), o WhatsApp manda o texto da mensagem citada dentro
# de contextInfo.quotedMessage - mas o webhook nunca lia isso, entao a Luna nao
# tinha ideia de qual pergunta estava sendo respondida. Agora, se a mensagem for
# uma resposta citada, o texto da pergunta original e incluido junto, dando
# contexto real pra Luna entender - tanto pro fluxo de confirmacao pendente
# (dos_luna_pendente) quanto pro chat livre.
replace_once(
    'api/whatsapp-webhook.js',
    """    const msg = data.message || {}
    let userText = (msg.conversation || msg.extendedTextMessage?.text || '').trim()

    if (msg.audioMessage && data.message.base64) {""",
    """    const msg = data.message || {}
    let userText = (msg.conversation || msg.extendedTextMessage?.text || '').trim()

    const textoCitadoPelaResposta = msg.extendedTextMessage?.contextInfo?.quotedMessage?.conversation || msg.extendedTextMessage?.contextInfo?.quotedMessage?.extendedTextMessage?.text || ''
    if (textoCitadoPelaResposta && userText) {
      userText = `(Denise respondeu usando a funcao "Responder" do WhatsApp a esta mensagem sua: "${textoCitadoPelaResposta.trim()}") ${userText}`
    }

    if (msg.audioMessage && data.message.base64) {""",
    'webhook-le-mensagem-citada-na-resposta'
)

print('TUDO OK:', feitos)
