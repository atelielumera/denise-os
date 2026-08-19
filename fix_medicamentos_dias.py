from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# --- api/_cronlib.js: calcular ha quantos dias cada medicamento foi registrado ---
cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (_cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_import = "import { createClient } from '@supabase/supabase-js'"
new_import = """import { createClient } from '@supabase/supabase-js'

function diasDesdeRegistroBR(dataBR) {
  const m = /^(\\d{2})\\/(\\d{2})$/.exec(dataBR || '')
  if (!m) return null
  const hoje = new Date()
  const anoAtual = hoje.getFullYear()
  let dataReg = new Date(Date.UTC(anoAtual, Number(m[2]) - 1, Number(m[1])))
  if (dataReg.getTime() > hoje.getTime() + 86400000) dataReg = new Date(Date.UTC(anoAtual - 1, Number(m[2]) - 1, Number(m[1])))
  return Math.floor((hoje.getTime() - dataReg.getTime()) / 86400000)
}"""
c = replace_once(c, old_import, new_import, "cronlib-helper-dias-desde-registro")

old_med = "    medicamentos: d.dos_medicamentos || {},"
new_med = """    medicamentos: (() => {
      const bruto = d.dos_medicamentos || {}
      const comDias = {}
      Object.keys(bruto).forEach((kid) => {
        comDias[kid] = (bruto[kid] || []).map((m) => ({ ...m, dias_desde_registro: diasDesdeRegistroBR(m.data) }))
      })
      return comDias
    })(),"""
c = replace_once(c, old_med, new_med, "cronlib-medicamentos-com-dias")

cronlib_file.write_text(c)

# --- api/cron-morning.js: instruir a IA a considerar medicamento "de hoje" mesmo se o registro nao for de hoje ---
morning_file = Path("api/cron-morning.js")
if not morning_file.exists():
    raise SystemExit("ABORTADO (cron-morning-nao-encontrado): rode este script na raiz do projeto denise-os.")
m = morning_file.read_text()
old_prompt = "medicamentos de hoje, e tarefas de trabalho pendentes se houver."
new_prompt = "medicamentos em curso hoje (considere em curso qualquer medicamento com \\'horarios\\' preenchido cujo \\'dias_desde_registro\\' seja 10 ou menos, mesmo que a data de registro nao seja hoje), e tarefas de trabalho pendentes se houver."
m = replace_once(m, old_prompt, new_prompt, "cron-morning-prompt-medicamentos")
morning_file.write_text(m)

print("OK - Luna agora recebe 'dias_desde_registro' de cada medicamento e o resumo da manha")
print("passa a considerar tratamentos em curso (nao so os registrados no mesmo dia).")
