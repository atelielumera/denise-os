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

# ---------- api/_cronlib.js ----------

replace_once(
    'api/_cronlib.js',
    """export function diasRestantesAval(dataDDMM) {
  const partes = (dataDDMM || '').split('/')
  if (partes.length < 2) return null
  const ano = new Date().getFullYear()
  const d = new Date(`${ano}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}T12:00:00-03:00`)
  if (isNaN(d.getTime())) return null
  return Math.ceil((d.getTime() - Date.now()) / 86400000)
}""",
    """export function diasRestantesAval(dataDDMM) {
  const partes = (dataDDMM || '').split('/')
  if (partes.length < 2) return null
  const ano = new Date().getFullYear()
  const d = new Date(`${ano}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}T12:00:00-03:00`)
  if (isNaN(d.getTime())) return null
  return Math.ceil((d.getTime() - Date.now()) / 86400000)
}

export function calcularAutonomiaTirzepatida(tzMap, saldoMg) {
  const mgDia = ['denise', 'flavio'].reduce((soma, pessoa) => {
    const sched = tzMap[pessoa]
    if (!sched || !sched.planned_dose_mg || !sched.interval_days) return soma
    return soma + sched.planned_dose_mg / sched.interval_days
  }, 0)
  return mgDia > 0 ? Math.floor(saldoMg / mgDia) : null
}""",
    'cronlib-calcula-autonomia-tirzepatida'
)

replace_once(
    'api/_cronlib.js',
    "    tirzepatida: Object.keys(tzMap).length > 0 ? { estoque_atual_mg: Number(bal?.current_balance_mg ?? 0), denise: tzMap.denise || null, flavio: tzMap.flavio || null } : null,",
    "    tirzepatida: Object.keys(tzMap).length > 0 ? { estoque_atual_mg: Number(bal?.current_balance_mg ?? 0), denise: tzMap.denise || null, flavio: tzMap.flavio || null, autonomia_dias: calcularAutonomiaTirzepatida(tzMap, Number(bal?.current_balance_mg ?? 0)) } : null,",
    'cronlib-contexto-autonomia-tirzepatida'
)

# ---------- api/cron-check.js ----------

replace_once(
    'api/cron-check.js',
    "import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, buscaEfetivaFamiliaPorDia, minutosAntesStr, planoTreinoDoDia, normalizarAval, diasRestantesAval } from './_cronlib.js'",
    "import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, buscaEfetivaFamiliaPorDia, minutosAntesStr, planoTreinoDoDia, normalizarAval, diasRestantesAval, calcularAutonomiaTirzepatida } from './_cronlib.js'",
    'cron-check-import'
)

replace_once(
    'api/cron-check.js',
    """      const pendentes = ['denise', 'flavio'].filter((p) => !jaAplicou.has(p) && doses[p] && proximaData[p] === hojeIso)
      if (pendentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
        const nomes = pendentes.map((p) => `${p === 'denise' ? 'sua' : 'do Flávio'} (${doses[p]}mg)`).join(' e ')
        avisos.push(`💉 Hoje é dia de aplicar a tirzepatida — falta registrar a aplicação ${nomes}. Me avise quando aplicar.`)
      }
    }""",
    """      const pendentes = ['denise', 'flavio'].filter((p) => !jaAplicou.has(p) && doses[p] && proximaData[p] === hojeIso)
      if (pendentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
        const nomes = pendentes.map((p) => `${p === 'denise' ? 'sua' : 'do Flávio'} (${doses[p]}mg)`).join(' e ')
        avisos.push(`💉 Hoje é dia de aplicar a tirzepatida — falta registrar a aplicação ${nomes}. Me avise quando aplicar.`)
      }
    }

    {
      const [{ data: tzSchedRows }, { data: tzBal }] = await Promise.all([
        supabase.from('tirzepatida_schedule').select('person,planned_dose_mg,interval_days'),
        supabase.from('tirzepatida_stock_balance').select('current_balance_mg').maybeSingle()
      ])
      const tzMap = {}
      ;(tzSchedRows || []).forEach((r) => { tzMap[r.person] = { planned_dose_mg: r.planned_dose_mg, interval_days: r.interval_days } })
      const saldoAtualMg = Number(tzBal?.current_balance_mg ?? 0)
      const autonomiaDias = calcularAutonomiaTirzepatida(tzMap, saldoAtualMg)
      if (autonomiaDias !== null && autonomiaDias <= 7 && estaNaJanela('10:00')) {
        avisos.push(`📦 Estoque de tirzepatida acabando: dá pra ~${autonomiaDias} dia${autonomiaDias === 1 ? '' : 's'} no ritmo atual (${saldoAtualMg}mg restantes). Bom repor.`)
      }
    }""",
    'cron-check-alerta-estoque-tirzepatida'
)

print('TUDO OK:', feitos)
