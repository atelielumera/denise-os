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

# Bug: no servidor (roda em UTC), a hora dos eventos do Google Calendar era calculada com
# .toISOString() (UTC), igual ao bug que ja corrigimos no app - so que ali o navegador
# converte sozinho pro fuso local. No servidor precisa converter explicitamente pra
# America/Sao_Paulo, senao todo evento do Google aparece 3h a frente do real (17h virava 20h).
old_import = "import { createClient } from '@supabase/supabase-js'"
new_import = """import { createClient } from '@supabase/supabase-js'

function horaLocalBR(dataISO) {
  const partes = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).formatToParts(new Date(dataISO))
  const h = partes.find((p) => p.type === 'hour')?.value || '00'
  const m = partes.find((p) => p.type === 'minute')?.value || '00'
  return `${h}:${m}`
}"""
c = replace_once(c, old_import, new_import, "cronlib-helper-hora-local-br")

old_hora = "hora: ev.start?.dateTime ? new Date(ev.start.dateTime).toISOString().slice(11, 16) : '',"
new_hora = "hora: ev.start?.dateTime ? horaLocalBR(ev.start.dateTime) : '',"
c = replace_once(c, old_hora, new_hora, "cronlib-agenda-hora-fuso")

cronlib_file.write_text(c)
print("OK - api/_cronlib.js: hora dos eventos do Google Calendar agora convertida para America/Sao_Paulo")
print("no servidor (antes usava UTC direto, mostrando tudo 3h a frente do real).")
