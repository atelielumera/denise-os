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

# Manda todos os avisos da leva em paralelo, nao um por um - evita que o ultimo item
# saia com o carimbo de horario do WhatsApp um ou mais minutos depois do primeiro.
replace_once(
    'api/cron-check.js',
    """    for (const aviso of avisos) {
      await sendWhatsappText(numero, aviso).catch(() => null)
    }""",
    """    await Promise.all(avisos.map((aviso) => sendWhatsappText(numero, aviso).catch(() => null)))""",
    'cron-check-envia-avisos-em-paralelo'
)

print('TUDO OK:', feitos)
