from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# Bug: a lista EVOLUTION_ALLOWED_NUMBERS era comparada com igualdade exata de string.
# Isso falha em dois casos comuns do WhatsApp brasileiro:
# 1) o remoteJid às vezes vem com sufixo de aparelho, tipo "5541991244639:12@s.whatsapp.net"
#    (o ":12" fica grudado no numero depois do split('@')[0]);
# 2) numeros de celular brasileiros podem chegar com ou sem o "9" extra
#    (5541991244639 vs 554191244639), dependendo de como o WhatsApp normalizou o contato.
# Qualquer um dos dois faz a comparação exata falhar e bloquear ate o proprio numero liberado.
webhook_file = Path("api/whatsapp-webhook.js")
if not webhook_file.exists():
    raise SystemExit("ABORTADO (webhook-nao-encontrado): rode este script na raiz do projeto denise-os.")
w = webhook_file.read_text()

old = """    const number = remoteJid.split('@')[0]

    const allowed = (process.env.EVOLUTION_ALLOWED_NUMBERS || '').split(',').map((s) => s.trim()).filter(Boolean)
    if (allowed.length && !allowed.includes(number)) {
      res.status(200).json({ ok: true })
      return
    }"""
new = """    const number = remoteJid.split('@')[0].split(':')[0]

    function normalizarNumeroBR(n) {
      const d = String(n || '').replace(/\\D/g, '')
      return (d.length === 13 && d.startsWith('55') && d[4] === '9') ? d.slice(0, 4) + d.slice(5) : d
    }
    const allowed = (process.env.EVOLUTION_ALLOWED_NUMBERS || '').split(',').map((s) => s.trim()).filter(Boolean)
    if (allowed.length && !allowed.map(normalizarNumeroBR).includes(normalizarNumeroBR(number))) {
      res.status(200).json({ ok: true })
      return
    }"""
w = replace_once(w, old, new, "webhook-allowlist-normalizada")

webhook_file.write_text(w)
print("OK - api/whatsapp-webhook.js: comparacao do numero liberado agora ignora sufixo de aparelho")
print("e a variacao do 9 dos celulares brasileiros, entao o 5541991244639 volta a ser reconhecido")
print("em qualquer um dos formatos que o WhatsApp mandar.")
