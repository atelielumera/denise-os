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
    """const GOOGLE_CLIENT_ID = '386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'

export const BUSCA_DOMI_POR_DIA = { 1: { busca: '12:50', sair: '12:35' }, 2: { busca: '11:40', sair: '11:25' }, 3: { busca: '12:50', sair: '12:35' }, 4: { busca: '11:40', sair: '11:25' }, 5: { busca: '13:00', sair: '12:45' } }
export const PLANO_TREINO_SEMANA = { 0: null, 1: 'Calistenia', 2: 'Caminhada', 3: 'Calistenia', 4: 'Caminhada', 5: 'Calistenia', 6: 'Mobilidade' }""",
    """const GOOGLE_CLIENT_ID = '386247436984-g828bjjges33iherifnlbk18cfe0u1mj.apps.googleusercontent.com'

const FAM_PADRAO = {
  domi: { dropOff: '07:00', pk: { 1: '12:50', 2: '11:40', 3: '12:50', 4: '11:40', 5: '13:00' }, entrada: '07:00', responsavel: 'denise' },
  derick: { dropOff: '07:00', pk: { 1: '17:00', 2: '17:00', 3: '17:00', 4: '17:00', 5: '17:00' }, entrada: '07:00', responsavel: 'flavio' }
}

export function buscaEfetivaFamiliaPorDia(d, kid, iso, diaSemana) {
  const fam = (d.dos_fam && d.dos_fam[kid]) || FAM_PADRAO[kid]
  const excecao = (d.dos_fam_excecoes && d.dos_fam_excecoes[iso] && d.dos_fam_excecoes[iso][kid]) || null
  return {
    horario: excecao?.horarioBusca || (fam.pk || {})[diaSemana] || null,
    responsavel: excecao?.responsavel || fam.responsavel || FAM_PADRAO[kid].responsavel,
    semAula: !!excecao?.semAula
  }
}

export function minutosAntesStr(hhmm, minutosAntes) {
  const partes = String(hhmm || '').split(':').map(Number)
  const total = ((partes[0] || 0) * 60 + (partes[1] || 0) - minutosAntes + 1440) % 1440
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

const PLANO_TREINO_PADRAO = [
  { tipo: 'Descanso', nome: 'Descanso', descanso: true },
  { tipo: 'Calistenia', nome: 'Calistenia', duracaoMin: 30, descanso: false },
  { tipo: 'Caminhada', nome: 'Caminhada', duracaoMin: 45, descanso: false },
  { tipo: 'Calistenia', nome: 'Calistenia', duracaoMin: 30, descanso: false },
  { tipo: 'Caminhada', nome: 'Caminhada', duracaoMin: 45, descanso: false },
  { tipo: 'Calistenia', nome: 'Calistenia', duracaoMin: 30, descanso: false },
  { tipo: 'Mobilidade', nome: 'Mobilidade', duracaoMin: 20, descanso: false }
]

export function planoTreinoDoDia(d, diaSemana) {
  const plano = Array.isArray(d.dos_plano_treino) && d.dos_plano_treino.length === 7 ? d.dos_plano_treino : PLANO_TREINO_PADRAO
  return plano[diaSemana] || null
}""",
    'cronlib-fam-e-treino-dinamicos'
)

replace_once(
    'api/_cronlib.js',
    """  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaDomiHoje = BUSCA_DOMI_POR_DIA[diaSemanaHoje] || null

  return {""",
    """  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaEscolaHoje = {
    domi: (() => { const e = buscaEfetivaFamiliaPorDia(d, 'domi', hojeIso, diaSemanaHoje); return (e.semAula || !e.horario) ? null : { busca: e.horario, sair: minutosAntesStr(e.horario, 15), responsavel: e.responsavel } })(),
    derick: (() => { const e = buscaEfetivaFamiliaPorDia(d, 'derick', hojeIso, diaSemanaHoje); return (e.semAula || !e.horario) ? null : { busca: e.horario, sair: minutosAntesStr(e.horario, 15), responsavel: e.responsavel } })()
  }

  return {""",
    'cronlib-context-busca-escola-hoje'
)

replace_once(
    'api/_cronlib.js',
    '    busca_domi_hoje: buscaDomiHoje,',
    '    busca_escola_hoje: buscaEscolaHoje,',
    'cronlib-context-renomeia-campo'
)

# ---------- api/cron-check.js ----------

replace_once(
    'api/cron-check.js',
    "import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, BUSCA_DOMI_POR_DIA, PLANO_TREINO_SEMANA } from './_cronlib.js'",
    "import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin, fetchGoogleCalendarEventos, horaLocalBR, buscaEfetivaFamiliaPorDia, minutosAntesStr, planoTreinoDoDia } from './_cronlib.js'",
    'cron-check-import'
)

replace_once(
    'api/cron-check.js',
    """    const buscaDomiHoje = BUSCA_DOMI_POR_DIA[diaSemanaHoje]
    if (buscaDomiHoje && estaNaJanela(buscaDomiHoje.sair)) {
      avisos.push(`🚗 Sair agora para buscar a Domi (sai da escola às ${buscaDomiHoje.busca})`)
    }""",
    """    ;['domi', 'derick'].forEach((kid) => {
      const efet = buscaEfetivaFamiliaPorDia(d, kid, hojeIso, diaSemanaHoje)
      if (efet.semAula || !efet.horario || efet.responsavel !== 'denise') return
      const horaSair = minutosAntesStr(efet.horario, 15)
      if (estaNaJanela(horaSair)) {
        const nomeKid = kid === 'domi' ? 'Domi' : 'Derick'
        avisos.push(`🚗 Sair agora para buscar a ${nomeKid} (sai da escola às ${efet.horario})`)
      }
    })""",
    'cron-check-busca-ambas-criancas'
)

replace_once(
    'api/cron-check.js',
    """    const treinoTipoHoje = PLANO_TREINO_SEMANA[diaSemanaHoje]
    const treinos = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
    const treinoRegistradoHoje = treinos.some((t) => t.data === hojeIso) || d[`dos_treino_registrado_${hojeIso}`]
    if (treinoTipoHoje && !treinoRegistradoHoje && lembraOuCobra('12:00', 21 * 60 + 30)) {
      avisos.push(`🏋️ Treino de hoje (${treinoTipoHoje}) — já fez ou não? Me conta pra eu registrar.`)
    }""",
    """    const planoTreinoHoje = planoTreinoDoDia(d, diaSemanaHoje)
    const treinos = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
    const treinoRegistradoHoje = treinos.some((t) => t.data === hojeIso) || d[`dos_treino_registrado_${hojeIso}`]
    if (planoTreinoHoje && !planoTreinoHoje.descanso && !treinoRegistradoHoje && lembraOuCobra('12:00', 21 * 60 + 30)) {
      avisos.push(`🏋️ Treino de hoje (${planoTreinoHoje.nome}) — já fez ou não? Me conta pra eu registrar.`)
    }""",
    'cron-check-treino-real'
)

replace_once(
    'api/cron-check.js',
    """    if (diaSemanaHoje === 4) {
      const [{ data: aplicacoesHoje }, { data: schedRows }] = await Promise.all([
        supabase.from('tirzepatida_applications').select('person,applied_at').gte('applied_at', `${hojeIso}T00:00:00`).lte('applied_at', `${hojeIso}T23:59:59`),
        supabase.from('tirzepatida_schedule').select('person,planned_dose_mg')
      ])
      const jaAplicou = new Set((aplicacoesHoje || []).map((a) => a.person))
      const doses = {}
      ;(schedRows || []).forEach((r) => { doses[r.person] = r.planned_dose_mg })
      const pendentes = ['denise', 'flavio'].filter((p) => !jaAplicou.has(p) && doses[p])
      if (pendentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
        const nomes = pendentes.map((p) => `${p === 'denise' ? 'sua' : 'do Flávio'} (${doses[p]}mg)`).join(' e ')
        avisos.push(`💉 Hoje é dia de aplicar a tirzepatida — falta registrar a aplicação ${nomes}. Me avise quando aplicar.`)
      }
    }""",
    """    {
      const [{ data: aplicacoesHoje }, { data: schedRows }] = await Promise.all([
        supabase.from('tirzepatida_applications').select('person,applied_at').gte('applied_at', `${hojeIso}T00:00:00`).lte('applied_at', `${hojeIso}T23:59:59`),
        supabase.from('tirzepatida_schedule').select('person,planned_dose_mg,next_application_date')
      ])
      const jaAplicou = new Set((aplicacoesHoje || []).map((a) => a.person))
      const doses = {}
      const proximaData = {}
      ;(schedRows || []).forEach((r) => { doses[r.person] = r.planned_dose_mg; proximaData[r.person] = r.next_application_date })
      const pendentes = ['denise', 'flavio'].filter((p) => !jaAplicou.has(p) && doses[p] && proximaData[p] === hojeIso)
      if (pendentes.length > 0 && lembraOuCobra('09:00', 21 * 60)) {
        const nomes = pendentes.map((p) => `${p === 'denise' ? 'sua' : 'do Flávio'} (${doses[p]}mg)`).join(' e ')
        avisos.push(`💉 Hoje é dia de aplicar a tirzepatida — falta registrar a aplicação ${nomes}. Me avise quando aplicar.`)
      }
    }""",
    'cron-check-tirzepatida-data-real'
)

# ---------- api/whatsapp-webhook.js ----------

replace_once(
    'api/whatsapp-webhook.js',
    """    if (tirzepatidaAplicada) {
      try {
        const { data: schedRow } = await supabase.from('tirzepatida_schedule').select('planned_dose_mg').eq('person', tirzepatidaAplicada.pessoa).maybeSingle()
        const doseMg = Number(schedRow?.planned_dose_mg || 0)
        if (doseMg > 0) {
          const appliedAt = new Date().toISOString()
          const { error } = await supabase.rpc('tirze_apply_dose', { p_person: tirzepatidaAplicada.pessoa, p_applied_at: appliedAt, p_dose_mg: doseMg })
          if (!error) {
            const { data: bal } = await supabase.from('tirzepatida_stock_balance').select('*').maybeSingle()
            const quem = tirzepatidaAplicada.pessoa === 'denise' ? 'sua' : 'do Flávio'
            partesConfirmacao.push(`💉 Registrei a aplicação ${quem} (${doseMg}mg). Estoque atualizado: ${Number(bal?.current_balance_mg ?? 0)}mg restantes.`)
          }
        }
      } catch { /* nao bloqueia o resto */ }
    }""",
    """    if (tirzepatidaAplicada) {
      try {
        const { data: jaHoje } = await supabase.from('tirzepatida_applications').select('id').eq('person', tirzepatidaAplicada.pessoa).gte('applied_at', `${hojeIso}T00:00:00`).lte('applied_at', `${hojeIso}T23:59:59`).maybeSingle()
        if (jaHoje) {
          const quemJa = tirzepatidaAplicada.pessoa === 'denise' ? 'Sua aplicação' : 'A aplicação do Flávio'
          partesConfirmacao.push(`💉 ${quemJa} de hoje já estava registrada — não registrei de novo pra não duplicar no estoque.`)
        } else {
          const { data: schedRow } = await supabase.from('tirzepatida_schedule').select('planned_dose_mg').eq('person', tirzepatidaAplicada.pessoa).maybeSingle()
          const doseMg = Number(schedRow?.planned_dose_mg || 0)
          if (doseMg > 0) {
            const appliedAt = new Date().toISOString()
            const { error } = await supabase.rpc('tirze_apply_dose', { p_person: tirzepatidaAplicada.pessoa, p_applied_at: appliedAt, p_dose_mg: doseMg })
            if (!error) {
              const { data: bal } = await supabase.from('tirzepatida_stock_balance').select('*').maybeSingle()
              const quem = tirzepatidaAplicada.pessoa === 'denise' ? 'sua' : 'do Flávio'
              partesConfirmacao.push(`💉 Registrei a aplicação ${quem} (${doseMg}mg). Estoque atualizado: ${Number(bal?.current_balance_mg ?? 0)}mg restantes.`)
            }
          }
        }
      } catch { /* nao bloqueia o resto */ }
    }""",
    'whatsapp-tirzepatida-guard-duplicidade'
)

# ---------- api/cron-morning.js ----------

replace_once(
    'api/cron-morning.js',
    "se busca_domi_hoje existir no contexto (em dias de semana), lembre que ela precisa sair de casa no horário \\'sair\\' de busca_domi_hoje para buscar a Domi, que sai da escola às \\'busca\\' (15 minutos depois do horário de sair); ",
    "se busca_escola_hoje.domi e/ou busca_escola_hoje.derick existirem no contexto (em dias de semana, e so quando o campo responsavel dentro deles for \\'denise\\'), lembre para cada crianca presente que ela precisa sair de casa no horário \\'sair\\' para buscar a Domi e/ou o Derick, que saem da escola no horário \\'busca\\'; ",
    'cron-morning-busca-ambas-criancas'
)

print('TUDO OK:', feitos)
