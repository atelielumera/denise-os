import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento, updateGoogleCalendarEvento, deleteGoogleCalendarEvento, normalizarAval, detectarBoleto } from './_cronlib.js'

const CASA_CATS_VALIDAS = ['Mercado', 'Doméstico', 'Manutenção', 'Contas']
const STATUS_TRABALHO_VALIDOS = ['pendente', 'andamento', 'aguardando', 'concluído']

export async function processarComando(userText, hojeIso, supabase, d) {
  if (!userText || !supabase) return null
  try {
    const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
    const rotina = Array.isArray(d.dos_rotina) ? d.dos_rotina : []
    const chaveRotinaHoje = `dos_rotina_done_${hojeIso}`
    const doneRotina = Array.isArray(d[chaveRotinaHoje]) ? d[chaveRotinaHoje] : []
    const rotinaPendente = rotina
      .map((it, idx) => ({ idx, horario: it.t, nome: it.n, dias: it.dias }))
      .filter((it) => (!it.dias || it.dias.includes(diaSemanaHoje)) && !doneRotina.includes(it.idx))

    const casaItens = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
    const casaPendente = casaItens.map((it, idx) => ({ idx, nome: it.n, categoria: it.cat, done: it.done })).filter((it) => !it.done)

    const avals = d.dos_avals || {}
    const avalDomi = (Array.isArray(avals.domi) ? avals.domi : []).map(normalizarAval)
    const avalDerick = (Array.isArray(avals.derick) ? avals.derick : []).map(normalizarAval)
    const avalDomiPendente = avalDomi.map((a, idx) => ({ idx, data: a.data, tipo: a.materia + (a.tipoAvaliacao ? ' ' + a.tipoAvaliacao : '') })).filter((_, idx) => avalDomi[idx].status !== 'realizado')
    const avalDerickPendente = avalDerick.map((a, idx) => ({ idx, data: a.data, tipo: a.materia + (a.tipoAvaliacao ? ' ' + a.tipoAvaliacao : '') })).filter((_, idx) => avalDerick[idx].status !== 'realizado')

    const trabalhoTarefas = Array.isArray(d.dos_trabalho) ? d.dos_trabalho : []
    const trabalhoAbertas = trabalhoTarefas.map((t, idx) => ({ idx, tarefa: t.t, projeto: t.p, status: t.s })).filter((t) => t.status !== 'concluído')

    const livroAtual = d.dos_livro_atual || null
    const pedidosOracao = Array.isArray(d.dos_pedidos_oracao) ? d.dos_pedidos_oracao : []
    const pedidosAtivos = pedidosOracao.map((p, idx) => ({ idx, pedido: p.pedido, pessoaTema: p.pessoaTema })).filter((_, idx) => pedidosOracao[idx].status !== 'respondida')
    const agendaAtualClassif = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
    const eventosEditaveis = agendaAtualClassif.filter((e) => !e.ehMestre && !e.recorrenciaId && e.data >= hojeIso).slice(0, 30).map((e) => ({ id: e.id, nome: e.nome, data: e.data, hora: e.hora }))

    const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|tarefa|pendenc|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria|peso|sono|dormi|humor|energia|intestino|ora[cç][aã]o|\borar\b|reza|cancela|remarca|reagenda|desmarca|adia/i
    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && trabalhoAbertas.length === 0 && pedidosAtivos.length === 0 && !GATE_RE.test(userText)) {
      return false
    }

    const DIAS_NOME = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']
    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos_rotina":[numeros],"feitos_casa":[numeros],"feitos_aval_domi":[numeros],"feitos_aval_derick":[numeros],"novos_casa":[{"nome":"...","categoria":"Mercado|Doméstico|Manutenção|Contas"}],"novos_compromissos":[{"nome":"...","dia_semana":numero de 0 a 6 (0=domingo,1=segunda,2=terca,3=quarta,4=quinta,5=sexta,6=sabado),"horario":"HH:MM"}],"novos_eventos_google":[{"nome":"...","data":"YYYY-MM-DD","hora":"HH:MM ou vazio se o dia todo","hora_fim":"HH:MM ou vazio","duracao_minutos":numero ou null,"local":"..." ou vazio}],"novos_trabalho":[{"tarefa":"...","projeto":"PixelSAV|SecaVita|Impressões da Domi|Lumera|Outros"}],"tirzepatida_aplicada":{"pessoa":"denise|flavio"}|null,"trabalho_status":[{"id":numero,"novo_status":"pendente|andamento|aguardando|concluído"}],"leitura_registrada":{"paginas":numero|null,"minutos":numero|null,"parou_na_pagina":numero|null}|null,"treino_registrado":{"feito":true|false}|null,"devocional_resposta":"texto"|null,"agua_ml":numero|null,"proteina_g_avulsa":numero|null,"refeicao":{"tipo":"Café da manhã|Lanche|Almoço|Lanche da tarde|Jantar|Ceia|Outro","descricao":"...","proteina_g":numero|null,"calorias":numero|null}|null}. Hoje e ' + hojeIso + ' (' + DIAS_NOME[diaSemanaHoje] + '). A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '".\n\nRotina de hoje ainda pendente (id, horario, nome): ' + JSON.stringify(rotinaPendente.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '\nItens pendentes da Casa (id, nome, categoria): ' + JSON.stringify(casaPendente.map((p) => ({ id: p.idx, nome: p.nome, categoria: p.categoria }))) + '\nAvaliações pendentes da Domi (id, data, tipo): ' + JSON.stringify(avalDomiPendente) + '\nAvaliações pendentes do Derick (id, data, tipo): ' + JSON.stringify(avalDerickPendente) + '\nTarefas de trabalho em aberto (id, tarefa, projeto, status atual): ' + JSON.stringify(trabalhoAbertas) + '\nLivro que ela esta lendo agora: ' + JSON.stringify(livroAtual) + '\n\nRegras: Se a mensagem confirmar que ela fez algo dessas listas (ex: "ja fiz X", "paguei a luz", "registrei a prova de matematica da domi"), coloque os ids certos no campo correspondente. Se for lista de compras/tarefas novas pra Casa, coloque em novos_casa. Se pedir compromisso recorrente (toda segunda/terca/etc) na rotina, coloque em novos_compromissos. Se pedir para marcar/inserir uma reuniao, evento ou compromisso em uma DATA especifica (nao recorrente, ex: "marca reuniao com fulano dia 25 as 14h", "coloca consulta do dentista sexta que vem"), resolva a data relativa usando hoje=' + hojeIso + ' e coloque em novos_eventos_google (nome, data no formato YYYY-MM-DD; hora e o HORARIO DE INICIO se ela mencionou algum horario - NUNCA deixe hora vazio so porque ela tambem mencionou uma duracao, ex: "consulta as 15h por 2 horas" significa hora="15:00" e duracao_minutos=120, no exemplo hora NUNCA fica vazio; se ela informar horario de inicio e de fim separados, preencha hora e hora_fim; se informar so duracao, preencha duracao_minutos; local se ela mencionar endereco ou lugar, senao deixe vazio; so deixe hora vazio de verdade se ela disser claramente que e um evento sem horario/dia inteiro). Se ela disser que aplicou a tirzepatida (dela ou do Flavio; se nao especificar a pessoa, assuma "denise"), preencha tirzepatida_aplicada. Se ela mencionar uma tarefa ou pendencia NOVA de trabalho que ainda nao esta na lista abaixo (ex: "tenho que fazer X", "cria uma tarefa pra Y", "duas tarefas pra hoje: A e B"), coloque em novos_trabalho (tarefa = o que precisa ser feito, projeto = PixelSAV, SecaVita, Impressões da Domi, Lumera ou Outros - escolha o mais provavel pelo contexto, ou Outros se nao ficar claro). Se ela mencionar mudanca de status de alguma tarefa de trabalho JA EXISTENTE (ex: "a tarefa X esta concluida", "comecei a tarefa Y", "Z esta aguardando resposta"), ache o id certo na lista de tarefas em aberto e coloque em trabalho_status. Se ela disser quantas paginas leu, quantos minutos leu, ou em que pagina parou, preencha leitura_registrada (campos que ela nao mencionou ficam null). Se ela disser que fez o treino de hoje ou que NAO fez o treino hoje, preencha treino_registrado. Se a mensagem for uma resposta as perguntas do devocional (reflexao sobre mandamento, promessa, pecado, aplicacao, algo novo sobre Deus, ou quem/o que/quando/onde/por que), coloque o texto completo da resposta dela em devocional_resposta. Se ela disser que bebeu ou tomou uma quantidade de agua, cha, suco ou agua com gas (ex: \'tomei 300ml de agua\', \'bebi um copo dagua\', \'tomei uma garrafa\'), converta para mililitros (copo comum ~200ml, garrafa comum ~500ml se ela nao especificar) e preencha agua_ml. Se ela mencionar uma quantidade de proteina avulsa sem descrever uma refeicao completa (ex: \'tomei um shake de 20g de proteina\', \'bati um whey\'), preencha proteina_g_avulsa. Se ela disser que comeu, almocou, jantou, lanchou ou tomou cafe da manha descrevendo o que comeu, preencha refeicao com o tipo mais proximo, a descricao do que ela comeu, e proteina_g/calorias somente se ela mencionar (senao null). Se nada de uma categoria se aplicar, deixe vazio/null nela.' + '\n\nPedidos de oração ainda não respondidos (id, pedido, pessoa/tema): ' + JSON.stringify(pedidosAtivos.map((p) => ({ id: p.idx, pedido: p.pedido, pessoaTema: p.pessoaTema }))) + '\n\nCampos adicionais que voce tambem deve preencher no mesmo JSON: "pedido_oracao_novo":{"pedido":"...","pessoa_tema":"..."}|null (preencha se a Denise pedir pra registrar um pedido de oracao ou pedir pra voce orar por algo especifico; pessoa_tema e o nome da pessoa ou tema, pode ser vazio); "pedido_oracao_respondido":numero do id da lista de pedidos acima|null (preencha se ela disser que um desses pedidos foi respondido/Deus respondeu); "saude_registro":{"pessoa":"denise"|"flavio","peso":numero em kg|null,"sono":numero de horas|null,"energia":numero de 1 a 10|null,"humor":numero de 1 a 10|null,"intestino":"Regular"|"Preso"|"Solto"|null}|null (preencha se ela mencionar peso, horas de sono, energia, humor ou intestino dela ou do Flavio; deixe os campos nao mencionados como null; nao preencha isso para as criancas).' + '\n\nEventos da agenda que podem ser alterados ou cancelados (id, nome, data, hora): ' + JSON.stringify(eventosEditaveis) + '\n\nMais um campo no JSON: "evento_alterar_ou_cancelar":{"id":"...","acao":"editar"|"cancelar","novo_data":"YYYY-MM-DD"|null,"novo_hora":"HH:MM"|null,"novo_nome":"..."|null}|null (preencha SOMENTE se a Denise pedir claramente pra mudar de dia/horario, renomear, ou cancelar/desmarcar um evento especifico que esteja na lista acima - use o id exato da lista; nunca invente um id que nao esteja la; se ela nao deixar claro qual evento entre varios, ou o evento nao estiver na lista (pode ser recorrente, que so pode ser editado pelo app), deixe null; NUNCA aplique a mudanca diretamente, so proponha - preencha os campos que ela pediu pra mudar e deixe null os que nao mudam).'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\{[\s\S]*\}/)
    const parsed = match ? JSON.parse(match[0]) : {}

    const feitosRotina = Array.isArray(parsed.feitos_rotina) ? parsed.feitos_rotina.filter((n) => typeof n === 'number' && rotinaPendente.some((p) => p.idx === n)) : []
    const feitosCasa = Array.isArray(parsed.feitos_casa) ? parsed.feitos_casa.filter((n) => typeof n === 'number' && casaPendente.some((p) => p.idx === n)) : []
    const feitosAvalDomi = Array.isArray(parsed.feitos_aval_domi) ? parsed.feitos_aval_domi.filter((n) => typeof n === 'number' && avalDomiPendente.some((p) => p.idx === n)) : []
    const feitosAvalDerick = Array.isArray(parsed.feitos_aval_derick) ? parsed.feitos_aval_derick.filter((n) => typeof n === 'number' && avalDerickPendente.some((p) => p.idx === n)) : []
    const novosCasa = Array.isArray(parsed.novos_casa) ? parsed.novos_casa.filter((n) => n && n.nome) : []
    const novosCompromissos = Array.isArray(parsed.novos_compromissos) ? parsed.novos_compromissos.filter((n) => n && n.nome && typeof n.dia_semana === 'number' && n.dia_semana >= 0 && n.dia_semana <= 6 && /^\d{1,2}:\d{2}$/.test(n.horario || '')) : []
    const novosEventosGoogle = Array.isArray(parsed.novos_eventos_google) ? parsed.novos_eventos_google.filter((n) => n && n.nome && /^\d{4}-\d{2}-\d{2}$/.test(n.data || '')) : []
    const TRABALHO_PROJETOS_VALIDOS = ['PixelSAV', 'SecaVita', 'Impressões da Domi', 'Lumera', 'Outros']
    const novosTrabalho = Array.isArray(parsed.novos_trabalho) ? parsed.novos_trabalho.filter((n) => n && n.tarefa) : []
    const tirzepatidaAplicada = parsed.tirzepatida_aplicada && ['denise', 'flavio'].includes(parsed.tirzepatida_aplicada.pessoa) ? parsed.tirzepatida_aplicada : null
    const trabalhoStatus = Array.isArray(parsed.trabalho_status) ? parsed.trabalho_status.filter((n) => n && typeof n.id === 'number' && trabalhoAbertas.some((p) => p.idx === n.id) && STATUS_TRABALHO_VALIDOS.includes(n.novo_status)) : []
    const leituraRegistrada = parsed.leitura_registrada && (parsed.leitura_registrada.paginas || parsed.leitura_registrada.minutos || parsed.leitura_registrada.parou_na_pagina) ? parsed.leitura_registrada : null
    const treinoRegistrado = parsed.treino_registrado && typeof parsed.treino_registrado.feito === 'boolean' ? parsed.treino_registrado : null
    const devocionalResposta = typeof parsed.devocional_resposta === 'string' && parsed.devocional_resposta.trim() ? parsed.devocional_resposta.trim() : null
    const aguaMlAdicionada = typeof parsed.agua_ml === 'number' && parsed.agua_ml > 0 && parsed.agua_ml <= 3000 ? Math.round(parsed.agua_ml) : null
    const proteinaAvulsaG = typeof parsed.proteina_g_avulsa === 'number' && parsed.proteina_g_avulsa > 0 && parsed.proteina_g_avulsa <= 300 ? Math.round(parsed.proteina_g_avulsa) : null
    const TIPOS_REFEICAO_VALIDOS = ['Café da manhã', 'Lanche', 'Almoço', 'Lanche da tarde', 'Jantar', 'Ceia', 'Outro']
    const refeicaoRegistrada = parsed.refeicao && typeof parsed.refeicao.descricao === 'string' && parsed.refeicao.descricao.trim() && TIPOS_REFEICAO_VALIDOS.includes(parsed.refeicao.tipo) ? parsed.refeicao : null
    const pedidoOracaoNovo = parsed.pedido_oracao_novo && typeof parsed.pedido_oracao_novo.pedido === 'string' && parsed.pedido_oracao_novo.pedido.trim() ? parsed.pedido_oracao_novo : null
    const pedidoOracaoRespondidoId = typeof parsed.pedido_oracao_respondido === 'number' && pedidosAtivos.some((p) => p.idx === parsed.pedido_oracao_respondido) ? parsed.pedido_oracao_respondido : null
    const SAUDE_PESSOAS_VALIDAS = ['denise', 'flavio']
    const saudeRegistro = parsed.saude_registro && SAUDE_PESSOAS_VALIDAS.includes(parsed.saude_registro.pessoa) && (parsed.saude_registro.peso || parsed.saude_registro.sono || parsed.saude_registro.energia || parsed.saude_registro.humor || parsed.saude_registro.intestino) ? parsed.saude_registro : null
    const eventoAlterarOuCancelar = parsed.evento_alterar_ou_cancelar && ['editar', 'cancelar'].includes(parsed.evento_alterar_ou_cancelar.acao) && eventosEditaveis.some((e) => e.id === parsed.evento_alterar_ou_cancelar.id) ? parsed.evento_alterar_ou_cancelar : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && novosTrabalho.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada && !pedidoOracaoNovo && pedidoOracaoRespondidoId === null && !saudeRegistro && !eventoAlterarOuCancelar) {
      return null
    }

    const partesConfirmacao = []

    if (feitosRotina.length > 0) {
      const uniao = Array.from(new Set([...doneRotina, ...feitosRotina]))
      d[chaveRotinaHoje] = uniao
      partesConfirmacao.push('✅ Marquei como feito: ' + rotinaPendente.filter((p) => feitosRotina.includes(p.idx)).map((p) => p.nome).join(', '))
    }

    let casaAtualizada = casaItens
    if (feitosCasa.length > 0) {
      casaAtualizada = casaAtualizada.map((c, idx) => (feitosCasa.includes(idx) ? { ...c, done: true } : c))
      partesConfirmacao.push('✅ Marquei como feito na Casa: ' + casaPendente.filter((p) => feitosCasa.includes(p.idx)).map((p) => p.nome).join(', '))
    }
    if (novosCasa.length > 0) {
      const adicionados = novosCasa.map((n) => ({ n: n.nome, cat: CASA_CATS_VALIDAS.includes(n.categoria) ? n.categoria : 'Mercado', done: false }))
      casaAtualizada = [...casaAtualizada, ...adicionados]
      partesConfirmacao.push('🛒 Adicionei na Casa: ' + adicionados.map((a) => a.n).join(', '))
    }
    if (feitosCasa.length > 0 || novosCasa.length > 0) d.dos_casa_items = casaAtualizada

    if (feitosAvalDomi.length > 0 || feitosAvalDerick.length > 0) {
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
    }

    if (novosCompromissos.length > 0) {
      const rotinaAtual = Array.isArray(d.dos_rotina) ? d.dos_rotina : rotina
      const adicionados = novosCompromissos.map((n) => ({ t: n.horario, n: n.nome, cat: 'Compromisso', dias: [n.dia_semana] }))
      d.dos_rotina = [...rotinaAtual, ...adicionados]
      partesConfirmacao.push('📅 Adicionei na sua rotina: ' + adicionados.map((a) => `${a.n} toda ${DIAS_NOME[a.dias[0]]} às ${a.t}`).join(', '))
    }

    if (novosEventosGoogle.length > 0) {
      const agendaAtual = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
      const adicionadosAgenda = []
      const calcularHoraFimEvento = (hora, horaFimInformada, duracaoMin) => {
        if (!hora) return ''
        if (horaFimInformada && /^\d{1,2}:\d{2}$/.test(horaFimInformada)) return horaFimInformada
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
    }

    if (novosTrabalho.length > 0) {
      const trabalhoAtual = Array.isArray(d.dos_trabalho) ? d.dos_trabalho : trabalhoTarefas
      const adicionadosTrabalho = novosTrabalho.map((n) => ({ t: n.tarefa, p: TRABALHO_PROJETOS_VALIDOS.includes(n.projeto) ? n.projeto : 'Outros', s: 'pendente' }))
      d.dos_trabalho = [...trabalhoAtual, ...adicionadosTrabalho]
      partesConfirmacao.push('💼 Adicionei nas tarefas de trabalho: ' + adicionadosTrabalho.map((a) => a.t).join(', '))
    }

    if (tirzepatidaAplicada) {
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
    }

    if (trabalhoStatus.length > 0) {
      const novasTarefas = trabalhoTarefas.map((t, idx) => {
        const alteracao = trabalhoStatus.find((s) => s.id === idx)
        return alteracao ? { ...t, s: alteracao.novo_status } : t
      })
      d.dos_trabalho = novasTarefas
      partesConfirmacao.push('💼 Atualizei o status: ' + trabalhoStatus.map((s) => `"${trabalhoAbertas.find((t) => t.idx === s.id)?.tarefa}" → ${s.novo_status}`).join(', '))
    }

    if (leituraRegistrada) {
      const leiturasAtuais = Array.isArray(d.dos_leituras) ? d.dos_leituras : []
      const paginasLidas = Number(leituraRegistrada.paginas || 0)
      const reg = { data: hojeIso, pag: paginasLidas, min: Number(leituraRegistrada.minutos || 0), apren: '' }
      d.dos_leituras = [reg, ...leiturasAtuais]
      if (livroAtual && livroAtual.totalPaginas > 0) {
        const novaPagina = leituraRegistrada.parou_na_pagina != null ? Math.min(livroAtual.totalPaginas, Number(leituraRegistrada.parou_na_pagina)) : Math.min(livroAtual.totalPaginas, Number(livroAtual.paginaAtual || 0) + paginasLidas)
        d.dos_livro_atual = { ...livroAtual, paginaAtual: novaPagina }
        partesConfirmacao.push(`📖 Leitura registrada! Você parou na página ${novaPagina} de ${livroAtual.totalPaginas}.`)
      } else {
        partesConfirmacao.push('📖 Leitura registrada!')
      }
    }

    if (treinoRegistrado) {
      if (treinoRegistrado.feito) {
        const treinosAtuais = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
        d.dos_treinos = [{ data: hojeIso, tipo: 'Registrado via WhatsApp', duracaoMin: 0 }, ...treinosAtuais]
        partesConfirmacao.push('✅ Treino de hoje registrado como feito!')
      } else {
        partesConfirmacao.push('Ok, registrei que hoje não deu pra treinar. Sem culpa, amanhã tem mais.')
      }
      d[`dos_treino_registrado_${hojeIso}`] = true
    }

    if (devocionalResposta) {
      const devocionaisAtuais = Array.isArray(d.dos_devocionais) ? d.dos_devocionais : []
      const outros = devocionaisAtuais.filter((e) => e.data !== hojeIso)
      const existenteHoje = devocionaisAtuais.find((e) => e.data === hojeIso) || {}
      const reg = { ...existenteHoje, data: hojeIso, reflex: devocionalResposta }
      d.dos_devocionais = [reg, ...outros].sort((a, b) => b.data.localeCompare(a.data))
      partesConfirmacao.push('🙏 Devocional de hoje registrado no seu histórico!')
    }

    if (aguaMlAdicionada) {
      const aguaLogAtual = d.dos_agua_log || {}
      const aguaHojeAtualMl = Number(aguaLogAtual[hojeIso] || 0)
      const novaAguaMl = Math.min(aguaHojeAtualMl + aguaMlAdicionada, 6000)
      d.dos_agua_log = { ...aguaLogAtual, [hojeIso]: novaAguaMl }
      partesConfirmacao.push(`💧 Registrei +${aguaMlAdicionada}ml de água. Total hoje: ${novaAguaMl}ml.`)
    }

    if (proteinaAvulsaG || refeicaoRegistrada) {
      const horaAgoraHHMM = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).format(new Date())
      const refsLogAtual = d.dos_refs_log || {}
      let refsHojeAtual = Array.isArray(refsLogAtual[hojeIso]) ? refsLogAtual[hojeIso] : []
      if (proteinaAvulsaG) {
        refsHojeAtual = [{ id: `${Date.now()}_wa1`, tipo: 'Rápido', nome: 'Proteína (registro rápido)', prot: proteinaAvulsaG, hora: horaAgoraHHMM, origem: 'whatsapp' }, ...refsHojeAtual]
        partesConfirmacao.push(`🥩 Registrei +${proteinaAvulsaG}g de proteína.`)
      }
      if (refeicaoRegistrada) {
        const novaRef = { id: `${Date.now()}_wa2`, tipo: refeicaoRegistrada.tipo, nome: refeicaoRegistrada.descricao, prot: typeof refeicaoRegistrada.proteina_g === 'number' ? refeicaoRegistrada.proteina_g : undefined, cal: typeof refeicaoRegistrada.calorias === 'number' ? refeicaoRegistrada.calorias : undefined, hora: horaAgoraHHMM, origem: 'whatsapp' }
        refsHojeAtual = [novaRef, ...refsHojeAtual]
        partesConfirmacao.push(`🍽️ Registrei: ${refeicaoRegistrada.descricao}${novaRef.prot ? ` (${novaRef.prot}g proteína)` : ''}.`)
      }
      d.dos_refs_log = { ...refsLogAtual, [hojeIso]: refsHojeAtual }
    }

    if (pedidoOracaoNovo) {
      const pedidosAtuais = Array.isArray(d.dos_pedidos_oracao) ? d.dos_pedidos_oracao : []
      const novoPedidoReg = { id: `oracao_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`, pedido: pedidoOracaoNovo.pedido.trim(), pessoaTema: pedidoOracaoNovo.pessoa_tema || '', data: hojeIso, observacoes: '', status: 'em_oracao', dataResposta: '', testemunho: '' }
      d.dos_pedidos_oracao = [novoPedidoReg, ...pedidosAtuais]
      partesConfirmacao.push(`🙏 Anotei seu pedido de oração: ${novoPedidoReg.pedido}`)
    }

    if (pedidoOracaoRespondidoId !== null) {
      const pedidosAtuais = Array.isArray(d.dos_pedidos_oracao) ? d.dos_pedidos_oracao : []
      d.dos_pedidos_oracao = pedidosAtuais.map((p, idx) => (idx === pedidoOracaoRespondidoId ? { ...p, status: 'respondida', dataResposta: hojeIso } : p))
      const pedidoRespondidoTexto = pedidosAtivos.find((p) => p.idx === pedidoOracaoRespondidoId)?.pedido || ''
      partesConfirmacao.push(`🙌 Que bênção! Marquei como respondido: ${pedidoRespondidoTexto}`)
    }

    if (saudeRegistro) {
      const chaveSaude = saudeRegistro.pessoa === 'denise' ? 'dos_saude_extra' : 'dos_saude_extra_flavio'
      const listaSaude = Array.isArray(d[chaveSaude]) ? d[chaveSaude] : []
      const dataCurta = hojeIso.slice(8, 10) + '/' + hojeIso.slice(5, 7)
      const idxHoje = listaSaude.findIndex((r) => r.data === dataCurta)
      const baseSaude = idxHoje >= 0 ? { ...listaSaude[idxHoje] } : { data: dataCurta, peso: 0, imc: 0, gordura: 0, humor: 0, energia: 0, intestino: '', sint: '', sono: 0 }
      if (saudeRegistro.peso) { baseSaude.peso = Number(saudeRegistro.peso); if (saudeRegistro.pessoa === 'denise') baseSaude.imc = Number((baseSaude.peso / (1.63 ** 2)).toFixed(1)) }
      if (saudeRegistro.sono) baseSaude.sono = Number(saudeRegistro.sono)
      if (saudeRegistro.energia) baseSaude.energia = Number(saudeRegistro.energia)
      if (saudeRegistro.humor) baseSaude.humor = Number(saudeRegistro.humor)
      if (saudeRegistro.intestino) baseSaude.intestino = saudeRegistro.intestino
      d[chaveSaude] = idxHoje >= 0 ? listaSaude.map((r, i) => (i === idxHoje ? baseSaude : r)) : [baseSaude, ...listaSaude]
      const itensSaude = []
      if (saudeRegistro.peso) itensSaude.push(`peso ${baseSaude.peso}kg`)
      if (saudeRegistro.sono) itensSaude.push(`sono ${baseSaude.sono}h`)
      if (saudeRegistro.energia) itensSaude.push(`energia ${baseSaude.energia}/10`)
      if (saudeRegistro.humor) itensSaude.push(`humor ${baseSaude.humor}/10`)
      if (saudeRegistro.intestino) itensSaude.push(`intestino ${baseSaude.intestino}`)
      partesConfirmacao.push(`❤️ Registrei ${itensSaude.join(', ')} ${saudeRegistro.pessoa === 'denise' ? 'pra você' : 'do Flávio'}.`)
    }

    if (eventoAlterarOuCancelar) {
      const eventoAlvo = eventosEditaveis.find((e) => e.id === eventoAlterarOuCancelar.id)
      d.dos_luna_pendente = { tipo: eventoAlterarOuCancelar.acao === 'cancelar' ? 'evento_cancelar' : 'evento_editar', dados: { id: eventoAlterarOuCancelar.id, novaData: eventoAlterarOuCancelar.novo_data || null, novaHora: eventoAlterarOuCancelar.novo_hora || null, novoNome: eventoAlterarOuCancelar.novo_nome || null }, criadoEm: Date.now() }
      if (eventoAlterarOuCancelar.acao === 'cancelar') {
        partesConfirmacao.push(`🗑️ Achei "${eventoAlvo.nome}" em ${eventoAlvo.data}${eventoAlvo.hora ? ' às ' + eventoAlvo.hora : ''}. Quer que eu cancele? Responde "sim" pra confirmar.`)
      } else {
        const mudancas = []
        if (eventoAlterarOuCancelar.novo_data) mudancas.push(`data pra ${eventoAlterarOuCancelar.novo_data}`)
        if (eventoAlterarOuCancelar.novo_hora) mudancas.push(`horário pra ${eventoAlterarOuCancelar.novo_hora}`)
        if (eventoAlterarOuCancelar.novo_nome) mudancas.push(`nome pra "${eventoAlterarOuCancelar.novo_nome}"`)
        partesConfirmacao.push(`🗓️ Achei "${eventoAlvo.nome}" em ${eventoAlvo.data}${eventoAlvo.hora ? ' às ' + eventoAlvo.hora : ''}. Quer que eu mude ${mudancas.join(' e ')}? Responde "sim" pra confirmar.`)
      }
    }

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    return partesConfirmacao.join('\n')
  } catch {
    return null
  }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(200).json({ ok: true })
    return
  }
  try {
    const body = req.body || {}
    const event = body.event || ''
    if (event && !/messages\.?upsert/i.test(event)) {
      res.status(200).json({ ok: true })
      return
    }

    const data = body.data || {}
    const key = data.key || {}
    if (key.fromMe) {
      res.status(200).json({ ok: true })
      return
    }
    const remoteJid = key.remoteJid || ''
    if (!remoteJid || remoteJid.endsWith('@g.us')) {
      res.status(200).json({ ok: true })
      return
    }
    const number = remoteJid.split('@')[0].split(':')[0]

    function normalizarNumeroBR(n) {
      const d = String(n || '').replace(/\D/g, '')
      return (d.length === 13 && d.startsWith('55') && d[4] === '9') ? d.slice(0, 4) + d.slice(5) : d
    }
    const allowed = (process.env.EVOLUTION_ALLOWED_NUMBERS || '').split(',').map((s) => s.trim()).filter(Boolean)
    if (allowed.length && !allowed.map(normalizarNumeroBR).includes(normalizarNumeroBR(number))) {
      res.status(200).json({ ok: true })
      return
    }

    const msg = data.message || {}
    let userText = (msg.conversation || msg.extendedTextMessage?.text || '').trim()

    if (msg.audioMessage && data.message.base64) {
      try {
        const transcript = await transcribeAudio(data.message.base64, msg.audioMessage.mimetype || 'audio/ogg')
        userText = userText ? (userText + '\n\n(audio transcrito): ' + transcript) : transcript
      } catch (errAudio) {
        console.error('Erro ao transcrever audio do WhatsApp:', errAudio?.message || errAudio)
        await sendWhatsappText(number, 'Recebi seu áudio mas não consegui entender agora. Pode tentar de novo ou escrever?')
        res.status(200).json({ ok: true })
        return
      }
    }

    const userContent = []
    if (msg.imageMessage && data.message.base64) {
      userContent.push({ type: 'image', source: { type: 'base64', media_type: msg.imageMessage.mimetype || 'image/jpeg', data: data.message.base64 } })
    }

    if (msg.documentMessage && !userText && userContent.length === 0) {
      await sendWhatsappText(number, 'Recebi seu documento, mas ainda não sei processar PDF por aqui no WhatsApp. Manda pelo aplicativo, na tela Família, que eu leio o calendário escolar direitinho.')
      res.status(200).json({ ok: true })
      return
    }

    if (!userText && userContent.length === 0) {
      res.status(200).json({ ok: true })
      return
    }
    userContent.push({ type: 'text', text: userText || 'A Denise enviou uma imagem sem legenda pelo WhatsApp. Comente o que você vê e pergunte no que pode ajudar.' })

    const context = await buildLunaContext()
    const supabase = getSupabaseAdmin()
    let d = {}
    if (supabase) {
      const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
      d = snap?.data || {}
    }

    const PALAVRAS_SIM_PENDENTE = ['sim', 'confirma', 'confirmo', 'pode', 'isso', 'correto', 'positivo', 'exato', 'certo']
    const PALAVRAS_NAO_PENDENTE = ['não', 'nao', 'cancela', 'cancelar', 'errado', 'negativo']
    if (supabase && userText && d.dos_luna_pendente && (Date.now() - (d.dos_luna_pendente.criadoEm || 0)) < 30 * 60 * 1000) {
      const textoNormalizado = userText.trim().toLowerCase()
      const pendente = d.dos_luna_pendente
      if (pendente.tipo === 'conta_boleto' && PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        const casaAtual = Array.isArray(d.dos_casa_items) ? d.dos_casa_items : []
        const novaConta = { id: `${Date.now()}_boleto`, n: pendente.dados.nome, cat: 'Contas', done: false, valor: pendente.dados.valor || undefined, venc: pendente.dados.vencimento || undefined, criadaEm: new Date().toISOString() }
        d.dos_casa_items = [novaConta, ...casaAtual]
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, `✅ Conta registrada: ${novaConta.n}${novaConta.valor ? ` (R$ ${Number(novaConta.valor).toFixed(2)})` : ''}${novaConta.venc ? `, vence ${novaConta.venc}` : ''}.`)
        res.status(200).json({ ok: true })
        return
      }
      if (pendente.tipo === 'conta_boleto' && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, 'Combinado, não criei a conta.')
        res.status(200).json({ ok: true })
        return
      }
      if (pendente.tipo === 'treino_pergunta' && PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        const treinosAtuais = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
        d.dos_treinos = [{ data: context.data_hoje, tipo: 'Registrado via WhatsApp', duracaoMin: 0 }, ...treinosAtuais]
        d[`dos_treino_registrado_${context.data_hoje}`] = true
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, '✅ Treino de hoje registrado como feito!')
        res.status(200).json({ ok: true })
        return
      }
      if (pendente.tipo === 'treino_pergunta' && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        d[`dos_treino_registrado_${context.data_hoje}`] = true
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, 'Ok, registrei que hoje não deu pra treinar. Sem culpa, amanhã tem mais.')
        res.status(200).json({ ok: true })
        return
      }
      if (pendente.tipo === 'evento_cancelar' && PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        const agendaAtualEv = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
        const eventoEv = agendaAtualEv.find((e) => e.id === pendente.dados.id)
        if (eventoEv?.googleEventId) await deleteGoogleCalendarEvento(supabase, eventoEv.googleEventId).catch(() => null)
        d.dos_agenda = agendaAtualEv.filter((e) => e.id !== pendente.dados.id)
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, `✅ Cancelado: ${eventoEv?.nome || 'o evento'}.`)
        res.status(200).json({ ok: true })
        return
      }
      if (pendente.tipo === 'evento_editar' && PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        const agendaAtualEv = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
        const eventoEv = agendaAtualEv.find((e) => e.id === pendente.dados.id)
        if (eventoEv) {
          const atualizado = { ...eventoEv }
          if (pendente.dados.novaData) atualizado.data = pendente.dados.novaData
          if (pendente.dados.novaHora) atualizado.hora = pendente.dados.novaHora
          if (pendente.dados.novoNome) atualizado.nome = pendente.dados.novoNome
          if (atualizado.googleEventId) {
            await updateGoogleCalendarEvento(supabase, atualizado.googleEventId, { nome: atualizado.nome, data: atualizado.data, hora: atualizado.hora, horaFim: atualizado.horaFim, local: atualizado.local, descricao: atualizado.descricao }).catch(() => null)
          }
          d.dos_agenda = agendaAtualEv.map((e) => (e.id === pendente.dados.id ? atualizado : e))
        }
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, `✅ Alterado: ${eventoEv?.nome || 'o evento'}${pendente.dados.novaData ? ' — nova data ' + pendente.dados.novaData : ''}${pendente.dados.novaHora ? ' às ' + pendente.dados.novaHora : ''}.`)
        res.status(200).json({ ok: true })
        return
      }
      if ((pendente.tipo === 'evento_cancelar' || pendente.tipo === 'evento_editar') && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, 'Combinado, não mudei nada no evento.')
        res.status(200).json({ ok: true })
        return
      }
    }
    if (d.dos_luna_pendente) delete d.dos_luna_pendente

    if (msg.imageMessage && data.message.base64 && supabase) {
      let deteccaoBoleto = { eh_boleto: false }
      try { deteccaoBoleto = await detectarBoleto(data.message.base64, msg.imageMessage.mimetype || 'image/jpeg') } catch { /* segue como imagem normal */ }
      if (deteccaoBoleto.eh_boleto && deteccaoBoleto.nome) {
        d.dos_luna_pendente = { tipo: 'conta_boleto', dados: { nome: deteccaoBoleto.nome, valor: deteccaoBoleto.valor || null, vencimento: deteccaoBoleto.vencimento || null }, criadoEm: Date.now() }
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        const partesBoleto = [`Parece um boleto: ${deteccaoBoleto.nome}`]
        if (deteccaoBoleto.valor) partesBoleto.push(`R$ ${Number(deteccaoBoleto.valor).toFixed(2)}`)
        if (deteccaoBoleto.vencimento) partesBoleto.push(`vencimento ${deteccaoBoleto.vencimento}`)
        await sendWhatsappText(number, `📄 ${partesBoleto.join(', ')}. Quer que eu registre essa conta? Responde "sim" pra confirmar.`)
        res.status(200).json({ ok: true })
        return
      }
    }

    if (userText) {
      const mensagemAcao = await processarComando(userText, context.data_hoje, supabase, d)
      if (mensagemAcao) {
        await sendWhatsappText(number, mensagemAcao)
        res.status(200).json({ ok: true })
        return
      }
    }

    const historico = Array.isArray(d.dos_luna_chat) ? d.dos_luna_chat.slice(-20) : []
    const historyMsgs = historico.map((m) => ({ role: m.me ? 'user' : 'assistant', content: String(m.t || '') }))
    while (historyMsgs.length > 0 && historyMsgs[0].role === 'assistant') historyMsgs.shift()

    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\n\nContexto atual (dados reais da Denise, agora):\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent, historyMsgs)
    await sendWhatsappText(number, reply)

    if (supabase) {
      const novoHistorico = [...historico, { me: true, t: userText || '(enviou uma imagem)' }, { me: false, t: reply }].slice(-40)
      await supabase.from('app_snapshot').upsert({ id: 'denise', data: { ...d, dos_luna_chat: novoHistorico }, updated_at: new Date().toISOString() })
    }

    res.status(200).json({ ok: true })
  } catch (err) {
    console.error('Erro no webhook do WhatsApp:', err)
    res.status(200).json({ ok: true })
  }
}
