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

# 1) GATE_RE: garante que "cria uma tarefa" / "pendencia de trabalho" tambem entra no classificador
replace_once(
    'api/whatsapp-webhook.js',
    'const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \\d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria|peso|sono|dormi|humor|energia|intestino|ora[cç][aã]o|\\borar\\b|reza|cancela|remarca|reagenda|desmarca|adia/i',
    'const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \\d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|tarefa|pendenc|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria|peso|sono|dormi|humor|energia|intestino|ora[cç][aã]o|\\borar\\b|reza|cancela|remarca|reagenda|desmarca|adia/i',
    'webhook-gate-re-tarefa-pendencia'
)

# 2) classPrompt: adiciona campo novos_trabalho no schema JSON
replace_once(
    'api/whatsapp-webhook.js',
    '"novos_eventos_google":[{"nome":"...","data":"YYYY-MM-DD","hora":"HH:MM ou vazio se o dia todo","hora_fim":"HH:MM ou vazio","duracao_minutos":numero ou null,"local":"..." ou vazio}],"tirzepatida_aplicada":{"pessoa":"denise|flavio"}|null,"trabalho_status":[{"id":numero,"novo_status":"pendente|andamento|aguardando|concluído"}],',
    '"novos_eventos_google":[{"nome":"...","data":"YYYY-MM-DD","hora":"HH:MM ou vazio se o dia todo","hora_fim":"HH:MM ou vazio","duracao_minutos":numero ou null,"local":"..." ou vazio}],"novos_trabalho":[{"tarefa":"...","projeto":"PixelSAV|SecaVita|Impressões da Domi|Lumera|Outros"}],"tirzepatida_aplicada":{"pessoa":"denise|flavio"}|null,"trabalho_status":[{"id":numero,"novo_status":"pendente|andamento|aguardando|concluído"}],',
    'webhook-classprompt-schema-novos-trabalho'
)

# 3) classPrompt: instrucao de quando preencher novos_trabalho
replace_once(
    'api/whatsapp-webhook.js',
    'Se ela mencionar mudanca de status de alguma tarefa de trabalho (ex: "a tarefa X esta concluida", "comecei a tarefa Y", "Z esta aguardando resposta"), ache o id certo na lista de tarefas em aberto e coloque em trabalho_status.',
    'Se ela mencionar uma tarefa ou pendencia NOVA de trabalho que ainda nao esta na lista abaixo (ex: "tenho que fazer X", "cria uma tarefa pra Y", "duas tarefas pra hoje: A e B"), coloque em novos_trabalho (tarefa = o que precisa ser feito, projeto = PixelSAV, SecaVita, Impressões da Domi, Lumera ou Outros - escolha o mais provavel pelo contexto, ou Outros se nao ficar claro). Se ela mencionar mudanca de status de alguma tarefa de trabalho JA EXISTENTE (ex: "a tarefa X esta concluida", "comecei a tarefa Y", "Z esta aguardando resposta"), ache o id certo na lista de tarefas em aberto e coloque em trabalho_status.',
    'webhook-classprompt-instrucao-novos-trabalho'
)

# 4) Parsing/validacao de novos_trabalho
replace_once(
    'api/whatsapp-webhook.js',
    """    const novosEventosGoogle = Array.isArray(parsed.novos_eventos_google) ? parsed.novos_eventos_google.filter((n) => n && n.nome && /^\\d{4}-\\d{2}-\\d{2}$/.test(n.data || '')) : []
    const tirzepatidaAplicada = parsed.tirzepatida_aplicada && ['denise', 'flavio'].includes(parsed.tirzepatida_aplicada.pessoa) ? parsed.tirzepatida_aplicada : null""",
    """    const novosEventosGoogle = Array.isArray(parsed.novos_eventos_google) ? parsed.novos_eventos_google.filter((n) => n && n.nome && /^\\d{4}-\\d{2}-\\d{2}$/.test(n.data || '')) : []
    const TRABALHO_PROJETOS_VALIDOS = ['PixelSAV', 'SecaVita', 'Impressões da Domi', 'Lumera', 'Outros']
    const novosTrabalho = Array.isArray(parsed.novos_trabalho) ? parsed.novos_trabalho.filter((n) => n && n.tarefa) : []
    const tirzepatidaAplicada = parsed.tirzepatida_aplicada && ['denise', 'flavio'].includes(parsed.tirzepatida_aplicada.pessoa) ? parsed.tirzepatida_aplicada : null""",
    'webhook-parsing-novos-trabalho'
)

# 5) Gate de "nada a fazer": inclui novosTrabalho
replace_once(
    'api/whatsapp-webhook.js',
    'if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada && !pedidoOracaoNovo && pedidoOracaoRespondidoId === null && !saudeRegistro && !eventoAlterarOuCancelar) {',
    'if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && novosTrabalho.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada && !pedidoOracaoNovo && pedidoOracaoRespondidoId === null && !saudeRegistro && !eventoAlterarOuCancelar) {',
    'webhook-gate-nada-a-fazer-novos-trabalho'
)

# 6) Mutacao: cria de fato as tarefas novas em d.dos_trabalho
replace_once(
    'api/whatsapp-webhook.js',
    """      d.dos_agenda = [...agendaAtual, ...adicionadosAgenda].sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))
      partesConfirmacao.push('📅 Marquei na sua agenda (e no Google Agenda): ' + adicionadosAgenda.map((a) => `${a.nome} em ${a.data}${a.hora ? ` das ${a.hora}${a.horaFim ? ' às ' + a.horaFim : ''}` : ' (dia todo)'}${a.local ? ' — ' + a.local : ''}`).join(', '))
    }

    if (tirzepatidaAplicada) {""",
    """      d.dos_agenda = [...agendaAtual, ...adicionadosAgenda].sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))
      partesConfirmacao.push('📅 Marquei na sua agenda (e no Google Agenda): ' + adicionadosAgenda.map((a) => `${a.nome} em ${a.data}${a.hora ? ` das ${a.hora}${a.horaFim ? ' às ' + a.horaFim : ''}` : ' (dia todo)'}${a.local ? ' — ' + a.local : ''}`).join(', '))
    }

    if (novosTrabalho.length > 0) {
      const trabalhoAtual = Array.isArray(d.dos_trabalho) ? d.dos_trabalho : trabalhoTarefas
      const adicionadosTrabalho = novosTrabalho.map((n) => ({ t: n.tarefa, p: TRABALHO_PROJETOS_VALIDOS.includes(n.projeto) ? n.projeto : 'Outros', s: 'pendente' }))
      d.dos_trabalho = [...trabalhoAtual, ...adicionadosTrabalho]
      partesConfirmacao.push('💼 Adicionei nas tarefas de trabalho: ' + adicionadosTrabalho.map((a) => a.t).join(', '))
    }

    if (tirzepatidaAplicada) {""",
    'webhook-cria-tarefas-trabalho'
)

print('TUDO OK:', feitos)
