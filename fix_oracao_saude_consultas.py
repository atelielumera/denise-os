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

# ---------- api/whatsapp-webhook.js ----------

replace_once(
    'api/whatsapp-webhook.js',
    """    const livroAtual = d.dos_livro_atual || null

    const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \\d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria/i
    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && trabalhoAbertas.length === 0 && !GATE_RE.test(userText)) {
      return false
    }""",
    """    const livroAtual = d.dos_livro_atual || null
    const pedidosOracao = Array.isArray(d.dos_pedidos_oracao) ? d.dos_pedidos_oracao : []
    const pedidosAtivos = pedidosOracao.map((p, idx) => ({ idx, pedido: p.pedido, pessoaTema: p.pessoaTema })).filter((_, idx) => pedidosOracao[idx].status !== 'respondida')

    const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \\d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria|peso|sono|dormi|humor|energia|intestino|ora[cç][aã]o|\\borar\\b|reza/i
    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && trabalhoAbertas.length === 0 && pedidosAtivos.length === 0 && !GATE_RE.test(userText)) {
      return false
    }""",
    'webhook-gate-e-pedidos-ativos'
)

replace_once(
    'api/whatsapp-webhook.js',
    """Se nada de uma categoria se aplicar, deixe vazio/null nela.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])""",
    """Se nada de uma categoria se aplicar, deixe vazio/null nela.' + '\\n\\nPedidos de oração ainda não respondidos (id, pedido, pessoa/tema): ' + JSON.stringify(pedidosAtivos.map((p) => ({ id: p.idx, pedido: p.pedido, pessoaTema: p.pessoaTema }))) + '\\n\\nCampos adicionais que voce tambem deve preencher no mesmo JSON: "pedido_oracao_novo":{"pedido":"...","pessoa_tema":"..."}|null (preencha se a Denise pedir pra registrar um pedido de oracao ou pedir pra voce orar por algo especifico; pessoa_tema e o nome da pessoa ou tema, pode ser vazio); "pedido_oracao_respondido":numero do id da lista de pedidos acima|null (preencha se ela disser que um desses pedidos foi respondido/Deus respondeu); "saude_registro":{"pessoa":"denise"|"flavio","peso":numero em kg|null,"sono":numero de horas|null,"energia":numero de 1 a 10|null,"humor":numero de 1 a 10|null,"intestino":"Regular"|"Preso"|"Solto"|null}|null (preencha se ela mencionar peso, horas de sono, energia, humor ou intestino dela ou do Flavio; deixe os campos nao mencionados como null; nao preencha isso para as criancas).'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])""",
    'webhook-classprompt-oracao-saude'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    const refeicaoRegistrada = parsed.refeicao && typeof parsed.refeicao.descricao === 'string' && parsed.refeicao.descricao.trim() && TIPOS_REFEICAO_VALIDOS.includes(parsed.refeicao.tipo) ? parsed.refeicao : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada) {
      return null
    }""",
    """    const refeicaoRegistrada = parsed.refeicao && typeof parsed.refeicao.descricao === 'string' && parsed.refeicao.descricao.trim() && TIPOS_REFEICAO_VALIDOS.includes(parsed.refeicao.tipo) ? parsed.refeicao : null
    const pedidoOracaoNovo = parsed.pedido_oracao_novo && typeof parsed.pedido_oracao_novo.pedido === 'string' && parsed.pedido_oracao_novo.pedido.trim() ? parsed.pedido_oracao_novo : null
    const pedidoOracaoRespondidoId = typeof parsed.pedido_oracao_respondido === 'number' && pedidosAtivos.some((p) => p.idx === parsed.pedido_oracao_respondido) ? parsed.pedido_oracao_respondido : null
    const SAUDE_PESSOAS_VALIDAS = ['denise', 'flavio']
    const saudeRegistro = parsed.saude_registro && SAUDE_PESSOAS_VALIDAS.includes(parsed.saude_registro.pessoa) && (parsed.saude_registro.peso || parsed.saude_registro.sono || parsed.saude_registro.energia || parsed.saude_registro.humor || parsed.saude_registro.intestino) ? parsed.saude_registro : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada && !pedidoOracaoNovo && pedidoOracaoRespondidoId === null && !saudeRegistro) {
      return null
    }""",
    'webhook-extrai-oracao-saude'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    return partesConfirmacao.join('\\n')
  } catch {
    return null
  }
}""",
    """    if (pedidoOracaoNovo) {
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

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    return partesConfirmacao.join('\\n')
  } catch {
    return null
  }
}""",
    'webhook-aplica-oracao-saude'
)

# ---------- api/cron-check.js: consulta medica das criancas ganha alerta proprio ----------

replace_once(
    'api/cron-check.js',
    """    if (provasProximas.length > 0 && lembraOuCobra('08:00', 21 * 60)) {
      const nomeKidLabel = { domi: 'Domi', derick: 'Derick' }
      const detalheProvas = provasProximas.map((p) => `${p.materia}${p.tipo ? ` (${p.tipo})` : ''} — ${nomeKidLabel[p.crianca] || p.crianca}, ${p.dias === 0 ? 'hoje' : 'amanhã'}`).join('; ')
      avisos.push(`📝 Prova ${provasProximas.some((p) => p.dias === 0) ? 'hoje' : 'chegando'}: ${detalheProvas}`)
    }""",
    """    if (provasProximas.length > 0 && lembraOuCobra('08:00', 21 * 60)) {
      const nomeKidLabel = { domi: 'Domi', derick: 'Derick' }
      const detalheProvas = provasProximas.map((p) => `${p.materia}${p.tipo ? ` (${p.tipo})` : ''} — ${nomeKidLabel[p.crianca] || p.crianca}, ${p.dias === 0 ? 'hoje' : 'amanhã'}`).join('; ')
      avisos.push(`📝 Prova ${provasProximas.some((p) => p.dias === 0) ? 'hoje' : 'chegando'}: ${detalheProvas}`)
    }

    const amanhaIso = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date(Date.now() + 86400000))
    const consultasBrutas = d.dos_consuls || {}
    const consultasProximas = Object.keys(consultasBrutas).flatMap((kid) =>
      (Array.isArray(consultasBrutas[kid]) ? consultasBrutas[kid] : [])
        .filter((c) => c.data === hojeIso || c.data === amanhaIso)
        .map((c) => ({ crianca: kid, tipo: c.tipo, hoje: c.data === hojeIso }))
    )
    if (consultasProximas.length > 0 && lembraOuCobra('08:00', 21 * 60)) {
      const nomeKidLabelConsulta = { domi: 'Domi', derick: 'Derick' }
      const detalheConsultas = consultasProximas.map((c) => `${c.tipo} — ${nomeKidLabelConsulta[c.crianca] || c.crianca}, ${c.hoje ? 'hoje' : 'amanhã'}`).join('; ')
      avisos.push(`🏥 Consulta médica ${consultasProximas.some((c) => c.hoje) ? 'hoje' : 'chegando'}: ${detalheConsultas}`)
    }""",
    'cron-check-alerta-consultas-criancas'
)

print('TUDO OK:', feitos)
