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

# TEMPORARIO, sem interromper nada: a Luna continua respondendo normalmente
# (fluido, como sempre). So quando a mensagem for uma resposta citada, um
# pedacinho de info tecnica e colado no final da resposta dela mesma, pra eu
# ver o que realmente foi capturado. Sera removido assim que confirmarmos.
replace_once(
    'api/whatsapp-webhook.js',
    """    if (textoCitadoPelaResposta && userText) {
      userText = `(Denise respondeu usando a funcao "Responder" do WhatsApp a esta mensagem sua: "${textoCitadoPelaResposta.trim()}") ${userText}`
    }""",
    """    if (textoCitadoPelaResposta && userText) {
      userText = `(Denise respondeu usando a funcao "Responder" do WhatsApp a esta mensagem sua: "${textoCitadoPelaResposta.trim()}") ${userText}`
    }
    const debugSufixoCitacao = contextInfoCitacao ? ('\\n\\n[DEBUG citacao]: ' + JSON.stringify({ textoCitadoPelaResposta, temContextInfo: !!contextInfoCitacao, temQuotedMessage: !!quotedMsgCitacao }).slice(0, 500)) : ''""",
    'webhook-debug-sufixo-variavel'
)

replace_once(
    'api/whatsapp-webhook.js',
    """      if (mensagemAcao) {
        await sendWhatsappText(number, mensagemAcao)
        res.status(200).json({ ok: true })
        return
      }""",
    """      if (mensagemAcao) {
        await sendWhatsappText(number, mensagemAcao + debugSufixoCitacao)
        res.status(200).json({ ok: true })
        return
      }""",
    'webhook-debug-sufixo-mensagemacao'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    const reply = await askLuna(systemPrompt, userContent, historyMsgs)
    await sendWhatsappText(number, reply)""",
    """    const reply = await askLuna(systemPrompt, userContent, historyMsgs)
    await sendWhatsappText(number, reply + debugSufixoCitacao)""",
    'webhook-debug-sufixo-reply'
)

print('TUDO OK:', feitos)
