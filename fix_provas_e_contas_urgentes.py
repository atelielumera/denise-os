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
    """export function planoTreinoDoDia(d, diaSemana) {
  const plano = Array.isArray(d.dos_plano_treino) && d.dos_plano_treino.length === 7 ? d.dos_plano_treino : PLANO_TREINO_PADRAO
  return plano[diaSemana] || null
}""",
    """export function planoTreinoDoDia(d, diaSemana) {
  const plano = Array.isArray(d.dos_plano_treino) && d.dos_plano_treino.length === 7 ? d.dos_plano_treino : PLANO_TREINO_PADRAO
  return plano[diaSemana] || null
}

export function normalizarAval(a) {
  if (a && a.status) return a
  const origTipo = a?.tipo || ''
  const tipoDetectado = /recupera/i.test(origTipo) ? 'Recuperação' : /AV1/.test(origTipo) ? 'AV1' : /AV2/.test(origTipo) ? 'AV2' : /AV3/.test(origTipo) ? 'AV3' : 'Outros'
  return { data: a?.data || '', materia: origTipo, tipoAvaliacao: tipoDetectado, conteudo: a?.obs || '', status: a?.feito ? 'realizado' : 'nao_iniciado' }
}

export function diasRestantesAval(dataDDMM) {
  const partes = (dataDDMM || '').split('/')
  if (partes.length < 2) return null
  const ano = new Date().getFullYear()
  const d = new Date(`${ano}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}T12:00:00-03:00`)
  if (isNaN(d.getTime())) return null
  return Math.ceil((d.getTime() - Date.now()) / 86400000)
}""",
    'cronlib-normaliza-avaliacoes'
)

replace_once(
    'api/_cronlib.js',
    """  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaEscolaHoje = {
    domi: (() => { const e = buscaEfetivaFamiliaPorDia(d, 'domi', hojeIso, diaSemanaHoje); return (e.semAula || !e.horario) ? null : { busca: e.horario, sair: minutosAntesStr(e.horario, 15), responsavel: e.responsavel } })(),
    derick: (() => { const e = buscaEfetivaFamiliaPorDia(d, 'derick', hojeIso, diaSemanaHoje); return (e.semAula || !e.horario) ? null : { busca: e.horario, sair: minutosAntesStr(e.horario, 15), responsavel: e.responsavel } })()
  }

  return {""",
    """  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaEscolaHoje = {
    domi: (() => { const e = buscaEfetivaFamiliaPorDia(d, 'domi', hojeIso, diaSemanaHoje); return (e.semAula || !e.horario) ? null : { busca: e.horario, sair: minutosAntesStr(e.horario, 15), responsavel: e.responsavel } })(),
    derick: (() => { const e = buscaEfetivaFamiliaPorDia(d, 'derick', hojeIso, diaSemanaHoje); return (e.semAula || !e.horario) ? null : { busca: e.horario, sair: minutosAntesStr(e.horario, 15), responsavel: e.responsavel } })()
  }

  const avalsBrutas = d.dos_avals || {}
  const provasEscolaresProximas = Object.keys(avalsBrutas).flatMap((kid) =>
    (Array.isArray(avalsBrutas[kid]) ? avalsBrutas[kid] : [])
      .map(normalizarAval)
      .filter((a) => a.status !== 'realizado')
      .map((a) => ({ crianca: kid, materia: a.materia, tipo: a.tipoAvaliacao, dias_restantes: diasRestantesAval(a.data) }))
  ).filter((a) => a.dias_restantes !== null && a.dias_restantes >= 0).sort((a, b) => a.dias_restantes - b.dias_restantes)

  return {""",
    'cronlib-contexto-provas-proximas'
)

replace_once(
    'api/_cronlib.js',
    """    trabalho_tarefas: d.dos_trabalho || [],
    treinos_recentes: treinos.slice(0, 10),
    leituras_recentes: leituras.slice(0, 10)
  }
}""",
    """    trabalho_tarefas: d.dos_trabalho || [],
    provas_escolares_proximas: provasEscolaresProximas,
    treinos_recentes: treinos.slice(0, 10),
    leituras_recentes: leituras.slice(0, 10)
  }
}""",
    'cronlib-contexto-campo-provas'
)

# ---------- api/whatsapp-webhook.js: usa o mesmo formato real das avaliacoes (status, nao feito) ----------

replace_once(
    'api/whatsapp-webhook.js',
    "import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento } from './_cronlib.js'",
    "import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento, normalizarAval } from './_cronlib.js'",
    'webhook-import-normalizarAval'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    const avals = d.dos_avals || {}
    const avalDomi = Array.isArray(avals.domi) ? avals.domi : []
    const avalDerick = Array.isArray(avals.derick) ? avals.derick : []
    const avalDomiPendente = avalDomi.map((a, idx) => ({ idx, data: a.data, tipo: a.tipo })).filter((_, idx) => !avalDomi[idx].feito)
    const avalDerickPendente = avalDerick.map((a, idx) => ({ idx, data: a.data, tipo: a.tipo })).filter((_, idx) => !avalDerick[idx].feito)""",
    """    const avals = d.dos_avals || {}
    const avalDomi = (Array.isArray(avals.domi) ? avals.domi : []).map(normalizarAval)
    const avalDerick = (Array.isArray(avals.derick) ? avals.derick : []).map(normalizarAval)
    const avalDomiPendente = avalDomi.map((a, idx) => ({ idx, data: a.data, tipo: a.materia + (a.tipoAvaliacao ? ' ' + a.tipoAvaliacao : '') })).filter((_, idx) => avalDomi[idx].status !== 'realizado')
    const avalDerickPendente = avalDerick.map((a, idx) => ({ idx, data: a.data, tipo: a.materia + (a.tipoAvaliacao ? ' ' + a.tipoAvaliacao : '') })).filter((_, idx) => avalDerick[idx].status !== 'realizado')""",
    'webhook-avals-normalizadas'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    if (feitosAvalDomi.length > 0 || feitosAvalDerick.length > 0) {
      const novosAvals = { ...avals }
      if (feitosAvalDomi.length > 0) {
        novosAvals.domi = avalDomi.map((a, idx) => (feitosAvalDomi.includes(idx) ? { ...a, feito: true } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação da Domi: ' + avalDomiPendente.filter((p) => feitosAvalDomi.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      if (feitosAvalDerick.length > 0) {
        novosAvals.derick = avalDerick.map((a, idx) => (feitosAvalDerick.includes(idx) ? { ...a, feito: true } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação do Derick: ' + avalDerickPendente.filter((p) => feitosAvalDerick.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      d.dos_avals = novosAvals
    }""",
    """    if (feitosAvalDomi.length > 0 || feitosAvalDerick.length > 0) {
      const novosAvals = { ...avals }
      if (feitosAvalDomi.length > 0) {
        novosAvals.domi = avalDomi.map((a, idx) => (feitosAvalDomi.includes(idx) ? { ...a, status: 'realizado' } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação da Domi: ' + avalDomiPendente.filter((p) => feitosAvalDomi.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      if (feitosAvalDerick.length > 0) {
        novosAvals.derick = avalDerick.map((a, idx) => (feitosAvalDerick.includes(idx) ? { ...a, status: 'realizado' } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação do Derick: ' + avalDerickPendente.filter((p) => feitosAvalDerick.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      d.dos_avals = novosAvals
    }""",
    'webhook-marca-aval-status-real'
)

# ---------- api/cron-check.js: contas urgentes separadas + alerta de prova proxima ----------

replace_once(
    'api/cron-check.js',
    "import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, buscaEfetivaFamiliaPorDia, minutosAntesStr, planoTreinoDoDia } from './_cronlib.js'",
    "import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, buscaEfetivaFamiliaPorDia, minutosAntesStr, planoTreinoDoDia, normalizarAval, diasRestantesAval } from './_cronlib.js'",
    'cron-check-import'
)

replace_once(
    'api/cron-check.js',
    """    const casaItens = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
    const casaPendenteHoje = casaItens.filter((i) => !i.done)
    if (casaPendenteHoje.length > 0 && lembraOuCobra('12:00', 21 * 60)) {
      avisos.push(`🏠 Pendente na Casa: ${casaPendenteHoje.map((i) => i.n).join(', ')}. Já fez alguma coisa? Me conta pra eu registrar.`)
    }""",
    """    const casaItens = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
    const contasUrgentes = casaItens.filter((i) => i.cat === 'Contas' && !i.done && i.venc && i.venc <= hojeIso)
    if (contasUrgentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
      const detalheContas = contasUrgentes.map((c) => `${c.n}${typeof c.valor === 'number' ? ` (R$ ${c.valor.toFixed(2)})` : ''}${c.venc < hojeIso ? ' — atrasada' : ' — vence hoje'}`).join(', ')
      avisos.push(`💸 Conta(s) precisando de atenção: ${detalheContas}. Me avise quando pagar.`)
    }
    const idsContasUrgentes = new Set(contasUrgentes.map((i) => i.id))
    const casaPendenteHoje = casaItens.filter((i) => !i.done && !idsContasUrgentes.has(i.id))
    if (casaPendenteHoje.length > 0 && lembraOuCobra('12:00', 21 * 60)) {
      avisos.push(`🏠 Pendente na Casa: ${casaPendenteHoje.map((i) => i.n).join(', ')}. Já fez alguma coisa? Me conta pra eu registrar.`)
    }

    const avalsBrutas = d.dos_avals || {}
    const provasProximas = Object.keys(avalsBrutas).flatMap((kid) =>
      (Array.isArray(avalsBrutas[kid]) ? avalsBrutas[kid] : [])
        .map(normalizarAval)
        .filter((a) => a.status !== 'realizado')
        .map((a) => ({ crianca: kid, materia: a.materia, tipo: a.tipoAvaliacao, dias: diasRestantesAval(a.data) }))
    ).filter((a) => a.dias === 0 || a.dias === 1)
    if (provasProximas.length > 0 && lembraOuCobra('08:00', 21 * 60)) {
      const nomeKidLabel = { domi: 'Domi', derick: 'Derick' }
      const detalheProvas = provasProximas.map((p) => `${p.materia}${p.tipo ? ` (${p.tipo})` : ''} — ${nomeKidLabel[p.crianca] || p.crianca}, ${p.dias === 0 ? 'hoje' : 'amanhã'}`).join('; ')
      avisos.push(`📝 Prova ${provasProximas.some((p) => p.dias === 0) ? 'hoje' : 'chegando'}: ${detalheProvas}`)
    }""",
    'cron-check-contas-urgentes-e-provas'
)

print('TUDO OK:', feitos)
