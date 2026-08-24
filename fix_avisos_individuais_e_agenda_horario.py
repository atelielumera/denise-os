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

# 1) cron-check.js: rotina para de cobrar 2h depois do horario, nao ate as 22h
replace_once(
    'api/cron-check.js',
    """    rotina.forEach((item, i) => {
      if (item.dias && !item.dias.includes(diaSemanaHoje)) return
      if (doneHoje.includes(i)) return
      if (lembraOuCobra(item.t, 22 * 60)) avisos.push(`⏰ ${item.t} · ${item.n}`)
    })""",
    """    rotina.forEach((item, i) => {
      if (item.dias && !item.dias.includes(diaSemanaHoje)) return
      if (doneHoje.includes(i)) return
      const minItemRotina = paraMinutos(item.t)
      const corteItemRotina = minItemRotina !== null ? minItemRotina + 120 : 22 * 60
      if (lembraOuCobra(item.t, corteItemRotina)) avisos.push(`⏰ ${item.t} · ${item.n}`)
    })""",
    'cron-check-rotina-para-de-cobrar-2h-depois'
)

# 2) cron-check.js: manda cada aviso em mensagem separada, nao em bloco unico
replace_once(
    'api/cron-check.js',
    """    if (avisos.length === 0) {
      res.status(200).json({ ok: true, avisos_enviados: 0 })
      return
    }

    if (criarPendenteTreino && (!d.dos_luna_pendente || (Date.now() - (d.dos_luna_pendente.criadoEm || 0)) >= 30 * 60 * 1000)) {
      d.dos_luna_pendente = { tipo: 'treino_pergunta', dados: {}, criadoEm: Date.now() }
      await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    }

    const texto = '🔔 Está na hora de:\\n\\n' + avisos.join('\\n')
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true, avisos_enviados: avisos.length })""",
    """    if (avisos.length === 0) {
      res.status(200).json({ ok: true, avisos_enviados: 0 })
      return
    }

    if (criarPendenteTreino && (!d.dos_luna_pendente || (Date.now() - (d.dos_luna_pendente.criadoEm || 0)) >= 30 * 60 * 1000)) {
      d.dos_luna_pendente = { tipo: 'treino_pergunta', dados: {}, criadoEm: Date.now() }
      await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    }

    for (const aviso of avisos) {
      await sendWhatsappText(numero, aviso).catch(() => null)
    }
    res.status(200).json({ ok: true, avisos_enviados: avisos.length })""",
    'cron-check-envia-mensagens-separadas'
)

# 3) whatsapp-webhook.js: classPrompt aprende hora_fim, duracao e local (nunca vira dia inteiro por engano)
replace_once(
    'api/whatsapp-webhook.js',
    '"novos_eventos_google":[{"nome":"...","data":"YYYY-MM-DD","hora":"HH:MM ou vazio se o dia todo"}],',
    '"novos_eventos_google":[{"nome":"...","data":"YYYY-MM-DD","hora":"HH:MM ou vazio se o dia todo","hora_fim":"HH:MM ou vazio","duracao_minutos":numero ou null,"local":"..." ou vazio}],',
    'webhook-classprompt-schema-agenda-completo'
)

replace_once(
    'api/whatsapp-webhook.js',
    """Se pedir para marcar/inserir uma reuniao, evento ou compromisso em uma DATA especifica (nao recorrente, ex: "marca reuniao com fulano dia 25 as 14h", "coloca consulta do dentista sexta que vem"), resolva a data relativa usando hoje=' + hojeIso + ' e coloque em novos_eventos_google (nome, data no formato YYYY-MM-DD, hora se houver).""",
    """Se pedir para marcar/inserir uma reuniao, evento ou compromisso em uma DATA especifica (nao recorrente, ex: "marca reuniao com fulano dia 25 as 14h", "coloca consulta do dentista sexta que vem"), resolva a data relativa usando hoje=' + hojeIso + ' e coloque em novos_eventos_google (nome, data no formato YYYY-MM-DD; hora e o HORARIO DE INICIO se ela mencionou algum horario - NUNCA deixe hora vazio so porque ela tambem mencionou uma duracao, ex: "consulta as 15h por 2 horas" significa hora="15:00" e duracao_minutos=120, no exemplo hora NUNCA fica vazio; se ela informar horario de inicio e de fim separados, preencha hora e hora_fim; se informar so duracao, preencha duracao_minutos; local se ela mencionar endereco ou lugar, senao deixe vazio; so deixe hora vazio de verdade se ela disser claramente que e um evento sem horario/dia inteiro).""",
    'webhook-classprompt-instrucao-agenda-completa'
)

# 4) whatsapp-webhook.js: usa hora_fim/duracao/local reais ao criar o evento, nao deixa cair em dia inteiro
replace_once(
    'api/whatsapp-webhook.js',
    """    if (novosEventosGoogle.length > 0) {
      const agendaAtual = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
      const adicionadosAgenda = []
      for (const ev of novosEventosGoogle) {
        const googleEventoCriado = await insertGoogleCalendarEvento(supabase, { nome: ev.nome, data: ev.data, hora: ev.hora || '' }).catch(() => null)
        adicionadosAgenda.push({ id: `ev_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`, nome: ev.nome, data: ev.data, hora: ev.hora || '', horaFim: '', local: '', descricao: '', categoria: 'pessoal', origem: 'whatsapp', pessoa: '', cor: '#38bdf8', googleEventId: googleEventoCriado?.id || null, recorrencia: null, recorrenciaId: null, ehMestre: false, excecoes: [], lembretes: [] })
      }
      d.dos_agenda = [...agendaAtual, ...adicionadosAgenda].sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))
      partesConfirmacao.push('📅 Marquei na sua agenda (e no Google Agenda): ' + adicionadosAgenda.map((a) => `${a.nome} em ${a.data}${a.hora ? ' às ' + a.hora : ''}`).join(', '))
    }""",
    """    if (novosEventosGoogle.length > 0) {
      const agendaAtual = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
      const adicionadosAgenda = []
      const calcularHoraFimEvento = (hora, horaFimInformada, duracaoMin) => {
        if (!hora) return ''
        if (horaFimInformada && /^\\d{1,2}:\\d{2}$/.test(horaFimInformada)) return horaFimInformada
        const partes = hora.split(':').map(Number)
        const totalMin = (partes[0] || 0) * 60 + (partes[1] || 0) + (typeof duracaoMin === 'number' && duracaoMin > 0 ? duracaoMin : 60)
        const totalMinCiclado = totalMin % 1440
        return `${String(Math.floor(totalMinCiclado / 60)).padStart(2, '0')}:${String(totalMinCiclado % 60).padStart(2, '0')}`
      }
      for (const ev of novosEventosGoogle) {
        const horaFimCalculada = calcularHoraFimEvento(ev.hora, ev.hora_fim, ev.duracao_minutos)
        const googleEventoCriado = await insertGoogleCalendarEvento(supabase, { nome: ev.nome, data: ev.data, hora: ev.hora || '', horaFim: horaFimCalculada, local: ev.local || '' }).catch(() => null)
        adicionadosAgenda.push({ id: `ev_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`, nome: ev.nome, data: ev.data, hora: ev.hora || '', horaFim: horaFimCalculada, local: ev.local || '', descricao: '', categoria: 'pessoal', origem: 'whatsapp', pessoa: '', cor: '#38bdf8', googleEventId: googleEventoCriado?.id || null, recorrencia: null, recorrenciaId: null, ehMestre: false, excecoes: [], lembretes: [] })
      }
      d.dos_agenda = [...agendaAtual, ...adicionadosAgenda].sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))
      partesConfirmacao.push('📅 Marquei na sua agenda (e no Google Agenda): ' + adicionadosAgenda.map((a) => `${a.nome} em ${a.data}${a.hora ? ` das ${a.hora}${a.horaFim ? ' às ' + a.horaFim : ''}` : ' (dia todo)'}${a.local ? ' — ' + a.local : ''}`).join(', '))
    }""",
    'webhook-cria-evento-com-horario-real'
)

print('TUDO OK:', feitos)
