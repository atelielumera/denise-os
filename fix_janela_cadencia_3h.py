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

# 1) Janela de checagem igual ao intervalo do cron (15 min) -> acaba com o disparo duplicado
replace_once(
    'api/cron-check.js',
    'const JANELA_MIN = 30',
    'const JANELA_MIN = 15',
    'cron-check-janela-15min'
)

# 2) lembraOuCobra passa a cobrar a cada 3h (padrao) em vez de de hora em hora
replace_once(
    'api/cron-check.js',
    """    // Lembrete uma vez no horario, depois cobranca de hora em hora ate o corte (se ainda nao feito).
    function lembraOuCobra(hhmm, corteMin) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      if (agoraMin < min || agoraMin >= corteMin) return false
      return (agoraMin - min) % 60 < JANELA_MIN
    }""",
    """    // Lembrete uma vez no horario, depois cobranca a cada `cadenciaMin` (padrao 3h) ate o corte (se ainda nao feito).
    function lembraOuCobra(hhmm, corteMin, cadenciaMin = 180) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      if (agoraMin < min || agoraMin >= corteMin) return false
      return (agoraMin - min) % cadenciaMin < JANELA_MIN
    }""",
    'cron-check-lembraoucobra-cadencia-3h'
)

# 3) Rotina volta a usar corte simples ate as 22h (o corte "2h depois" foi superado pela cadencia de 3h)
replace_once(
    'api/cron-check.js',
    """    rotina.forEach((item, i) => {
      if (item.dias && !item.dias.includes(diaSemanaHoje)) return
      if (doneHoje.includes(i)) return
      const minItemRotina = paraMinutos(item.t)
      const corteItemRotina = minItemRotina !== null ? minItemRotina + 120 : 22 * 60
      if (lembraOuCobra(item.t, corteItemRotina)) avisos.push(`⏰ ${item.t} · ${item.n}`)
    })""",
    """    rotina.forEach((item, i) => {
      if (item.dias && !item.dias.includes(diaSemanaHoje)) return
      if (doneHoje.includes(i)) return
      if (lembraOuCobra(item.t, 22 * 60)) avisos.push(`⏰ ${item.t} · ${item.n}`)
    })""",
    'cron-check-rotina-corte-simples-22h'
)

print('TUDO OK:', feitos)
