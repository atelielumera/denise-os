import pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent
p = BASE / 'api/_cronlib.js'
s = p.read_text(encoding='utf-8')

old = 'gemini-2.0-flash'
new = 'gemini-3.6-flash'
n = s.count(old)
if n == 0:
    print(f"ABORTADO: nenhuma ocorrencia de '{old}' encontrada em api/_cronlib.js. Nada foi alterado.")
    sys.exit(1)

p.write_text(s.replace(old, new), encoding='utf-8')
print(f"TUDO OK: substituidas {n} ocorrencia(s) de '{old}' por '{new}' em api/_cronlib.js")
