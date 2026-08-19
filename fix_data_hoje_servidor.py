from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (_cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

# Bug: 'hoje' no servidor era calculado em UTC (new Date().toISOString()), nao em horario de
# Brasilia. Entre ~21h e meia-noite (horario de Brasilia), o servidor achava que ja era amanha.
old_import = "import { createClient } from '@supabase/supabase-js'"
new_import = """import { createClient } from '@supabase/supabase-js'

function dataIsoBR(offsetDias = 0) {
  const d = new Date(Date.now() + offsetDias * 86400000)
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(d)
}"""
c = replace_once(c, old_import, new_import, "cronlib-helper-data-iso-br")

old_hoje = """  const hojeIso = new Date().toISOString().slice(0, 10)
  const em7diasIso = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)"""
new_hoje = """  const hojeIso = dataIsoBR(0)
  const em7diasIso = dataIsoBR(7)"""
c = replace_once(c, old_hoje, new_hoje, "cronlib-hoje-fuso-br")

cronlib_file.write_text(c)
print("OK - api/_cronlib.js: 'hoje' agora calculado em horario de Brasilia, nao mais em UTC.")
