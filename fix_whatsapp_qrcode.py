from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# --- api/whatsapp.js: pairingCode nao pode cair pro campo "code" (string bruta de conexao do Baileys) ---
api_file = Path("api/whatsapp.js")
if not api_file.exists():
    raise SystemExit("ABORTADO (api-whatsapp-nao-encontrado): rode este script na raiz do projeto denise-os.")
a = api_file.read_text()

old_a = "      const pairingCode = r.data?.pairingCode || r.data?.code || null"
new_a = "      const pairingCode = r.data?.pairingCode || null"
a = replace_once(a, old_a, new_a, "whatsapp-pairingcode-fallback-errado")
api_file.write_text(a)

# --- src/main.tsx: a Evolution API ja devolve o base64 como data URI completo; prefixar de novo quebra a imagem ---
main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_s = "{waQr&&<img src={`data:image/png;base64,${waQr}`} alt=\"QR Code do WhatsApp\" style={{width:180,height:180,borderRadius:10,background:'#fff',padding:8}}/>}"
new_s = "{waQr&&<img src={waQr.startsWith('data:')?waQr:`data:image/png;base64,${waQr}`} alt=\"QR Code do WhatsApp\" style={{width:180,height:180,borderRadius:10,background:'#fff',padding:8}}/>}"
s = replace_once(s, old_s, new_s, "whatsapp-qr-prefixo-duplicado")
main_file.write_text(s)

print("OK - dois bugs do QR Code do WhatsApp corrigidos:")
print(" - api/whatsapp.js: pairingCode nao usa mais 'code' (string bruta de conexao) como fallback")
print(" - src/main.tsx: nao prefixa 'data:image/png;base64,' de novo quando a Evolution API ja manda o data URI completo")
