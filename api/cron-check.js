import { verificarCron, getDeniseNumber, sendWhatsappText, getSupabaseAdmin } from './_cronlib.js'

function dataIsoBR() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date())
}

function horaAgoraBR() {
  const partes = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).formatToParts(new Date())
  const h = Number(partes.find((p) => p.type === 'hour')?.value || '0')
  const m = Number(partes.find((p) => p.type === 'minute')?.value || '0')
  return h * 60 + m
}

function paraMinutos(hhmm) {
  const m = /^(\d{1,2}):(\d{2})$/.exec((hhmm || '').trim())
  if (!m) return null
  return Number(m[1]) * 60 + Number(m[2])
}

const JANELA_MIN = 30

export default async function handler(req, res) {
  if (!verificarCron(req)) {
    res.status(401).json({ error: 'Nao autorizado.' })
    return
  }
  const numero = getDeniseNumber()
  if (!numero) {
    res.status(500).json({ error: 'DENISE_WHATSAPP_NUMBER nao configurada.' })
    return
  }
  const supabase = getSupabaseAdmin()
  if (!supabase) {
    res.status(500).json({ error: 'Supabase nao configurado.' })
    return
  }
  try {
    const hojeIso = dataIsoBR()
    const agoraMin = horaAgoraBR()
    const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()

    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}
    const rotina = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
    const doneHoje = Array.isArray(d[`dos_rotina_done_${hojeIso}`]) ? d[`dos_rotina_done_${hojeIso}`] : []
    const medicamentos = d.dos_medicamentos || {}

    function estaNaJanela(hhmm) {
      const min = paraMinutos(hhmm)
      if (min === null) return false
      return min <= agoraMin && min > agoraMin - JANELA_MIN
    }

    const avisos = []

    rotina.forEach((item, i) => {
      if (item.dias && !item.dias.includes(diaSemanaHoje)) return
      if (doneHoje.includes(i)) return
      if (estaNaJanela(item.t)) avisos.push(`⏰ ${item.t} · ${item.n}`)
    })

    Object.keys(medicamentos).forEach((pessoaId) => {
      const lista = Array.isArray(medicamentos[pessoaId]) ? medicamentos[pessoaId] : []
      lista.forEach((m) => {
        if (m.ate && m.ate < hojeIso) return
        const horarios = (m.horarios || '').split(',').map((h) => h.trim()).filter(Boolean)
        horarios.forEach((h) => {
          if (!estaNaJanela(h)) return
          const quem = pessoaId === 'denise' ? '' : ` (${pessoaId === 'flavio' ? 'Flávio' : pessoaId})`
          avisos.push(`💊 ${h} · ${m.nome}${m.dosagem ? ` ${m.dosagem}` : ''}${quem}`)
        })
      })
    })

    if (avisos.length === 0) {
      res.status(200).json({ ok: true, avisos_enviados: 0 })
      return
    }

    const texto = '🔔 Está na hora de:\n\n' + avisos.join('\n')
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true, avisos_enviados: avisos.length })
  } catch (err) {
    res.status(500).json({ error: err?.message || 'erro desconhecido' })
  }
}
