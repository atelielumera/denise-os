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
    "import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento, normalizarAval, detectarBoleto } from './_cronlib.js'",
    "import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento, updateGoogleCalendarEvento, deleteGoogleCalendarEvento, normalizarAval, detectarBoleto } from './_cronlib.js'",
    'webhook-import-google-update-delete'
)

# Corrige o evento criado por WhatsApp: hoje ele nascia sem id, sem origem e sem
# guardar o googleEventId retornado - ficava desconectado do evento real do Google
# e sem id ate a proxima vez que o app abrisse a agenda.
replace_once(
    'api/whatsapp-webhook.js',
    """    if (novosEventosGoogle.length > 0) {
      const agendaAtual = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
      const adicionadosAgenda = []
      for (const ev of novosEventosGoogle) {
        adicionadosAgenda.push({ data: ev.data, hora: ev.hora || '', nome: ev.nome, cor: '#38bdf8' })
        await insertGoogleCalendarEvento(supabase, { nome: ev.nome, data: ev.data, hora: ev.hora || '' }).catch(() => null)
      }
      d.dos_agenda = [...agendaAtual, ...adicionadosAgenda].sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora))
      partesConfirmacao.push('📅 Marquei na sua agenda (e no Google Agenda): ' + adicionadosAgenda.map((a) => `${a.nome} em ${a.data}${a.hora ? ' às ' + a.hora : ''}`).join(', '))
    }""",
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
    'webhook-corrige-forma-evento-whatsapp'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    const livroAtual = d.dos_livro_atual || null
    const pedidosOracao = Array.isArray(d.dos_pedidos_oracao) ? d.dos_pedidos_oracao : []
    const pedidosAtivos = pedidosOracao.map((p, idx) => ({ idx, pedido: p.pedido, pessoaTema: p.pessoaTema })).filter((_, idx) => pedidosOracao[idx].status !== 'respondida')

    const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \\d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria|peso|sono|dormi|humor|energia|intestino|ora[cç][aã]o|\\borar\\b|reza/i
    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && trabalhoAbertas.length === 0 && pedidosAtivos.length === 0 && !GATE_RE.test(userText)) {
      return false
    }""",
    """    const livroAtual = d.dos_livro_atual || null
    const pedidosOracao = Array.isArray(d.dos_pedidos_oracao) ? d.dos_pedidos_oracao : []
    const pedidosAtivos = pedidosOracao.map((p, idx) => ({ idx, pedido: p.pedido, pessoaTema: p.pessoaTema })).filter((_, idx) => pedidosOracao[idx].status !== 'respondida')
    const agendaAtualClassif = Array.isArray(d.dos_agenda) ? d.dos_agenda : []
    const eventosEditaveis = agendaAtualClassif.filter((e) => !e.ehMestre && !e.recorrenciaId && e.data >= hojeIso).slice(0, 30).map((e) => ({ id: e.id, nome: e.nome, data: e.data, hora: e.hora }))

    const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \\d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria|peso|sono|dormi|humor|energia|intestino|ora[cç][aã]o|\\borar\\b|reza|cancela|remarca|reagenda|desmarca|adia/i
    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && trabalhoAbertas.length === 0 && pedidosAtivos.length === 0 && !GATE_RE.test(userText)) {
      return false
    }""",
    'webhook-gate-e-eventos-editaveis'
)

replace_once(
    'api/whatsapp-webhook.js',
    """"saude_registro":{"pessoa":"denise"|"flavio","peso":numero em kg|null,"sono":numero de horas|null,"energia":numero de 1 a 10|null,"humor":numero de 1 a 10|null,"intestino":"Regular"|"Preso"|"Solto"|null}|null (preencha se ela mencionar peso, horas de sono, energia, humor ou intestino dela ou do Flavio; deixe os campos nao mencionados como null; nao preencha isso para as criancas).'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])""",
    """"saude_registro":{"pessoa":"denise"|"flavio","peso":numero em kg|null,"sono":numero de horas|null,"energia":numero de 1 a 10|null,"humor":numero de 1 a 10|null,"intestino":"Regular"|"Preso"|"Solto"|null}|null (preencha se ela mencionar peso, horas de sono, energia, humor ou intestino dela ou do Flavio; deixe os campos nao mencionados como null; nao preencha isso para as criancas).' + '\\n\\nEventos da agenda que podem ser alterados ou cancelados (id, nome, data, hora): ' + JSON.stringify(eventosEditaveis) + '\\n\\nMais um campo no JSON: "evento_alterar_ou_cancelar":{"id":"...","acao":"editar"|"cancelar","novo_data":"YYYY-MM-DD"|null,"novo_hora":"HH:MM"|null,"novo_nome":"..."|null}|null (preencha SOMENTE se a Denise pedir claramente pra mudar de dia/horario, renomear, ou cancelar/desmarcar um evento especifico que esteja na lista acima - use o id exato da lista; nunca invente um id que nao esteja la; se ela nao deixar claro qual evento entre varios, ou o evento nao estiver na lista (pode ser recorrente, que so pode ser editado pelo app), deixe null; NUNCA aplique a mudanca diretamente, so proponha - preencha os campos que ela pediu pra mudar e deixe null os que nao mudam).'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])""",
    'webhook-classprompt-evento-editar'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    const saudeRegistro = parsed.saude_registro && SAUDE_PESSOAS_VALIDAS.includes(parsed.saude_registro.pessoa) && (parsed.saude_registro.peso || parsed.saude_registro.sono || parsed.saude_registro.energia || parsed.saude_registro.humor || parsed.saude_registro.intestino) ? parsed.saude_registro : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada && !pedidoOracaoNovo && pedidoOracaoRespondidoId === null && !saudeRegistro) {
      return null
    }""",
    """    const saudeRegistro = parsed.saude_registro && SAUDE_PESSOAS_VALIDAS.includes(parsed.saude_registro.pessoa) && (parsed.saude_registro.peso || parsed.saude_registro.sono || parsed.saude_registro.energia || parsed.saude_registro.humor || parsed.saude_registro.intestino) ? parsed.saude_registro : null
    const eventoAlterarOuCancelar = parsed.evento_alterar_ou_cancelar && ['editar', 'cancelar'].includes(parsed.evento_alterar_ou_cancelar.acao) && eventosEditaveis.some((e) => e.id === parsed.evento_alterar_ou_cancelar.id) ? parsed.evento_alterar_ou_cancelar : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada && !pedidoOracaoNovo && pedidoOracaoRespondidoId === null && !saudeRegistro && !eventoAlterarOuCancelar) {
      return null
    }""",
    'webhook-extrai-evento-alterar'
)

replace_once(
    'api/whatsapp-webhook.js',
    """      partesConfirmacao.push(`❤️ Registrei ${itensSaude.join(', ')} ${saudeRegistro.pessoa === 'denise' ? 'pra você' : 'do Flávio'}.`)
    }

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    return partesConfirmacao.join('\\n')
  } catch {
    return null
  }
}""",
    """      partesConfirmacao.push(`❤️ Registrei ${itensSaude.join(', ')} ${saudeRegistro.pessoa === 'denise' ? 'pra você' : 'do Flávio'}.`)
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
    return partesConfirmacao.join('\\n')
  } catch {
    return null
  }
}""",
    'webhook-propoe-evento-alterar'
)

# Confirmacao ("sim"/"nao") do pendente - reaproveita o mesmo mecanismo do boleto (Fase 5)
replace_once(
    'api/whatsapp-webhook.js',
    """      if (pendente.tipo === 'conta_boleto' && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, 'Combinado, não criei a conta.')
        res.status(200).json({ ok: true })
        return
      }
    }""",
    """      if (pendente.tipo === 'conta_boleto' && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, 'Combinado, não criei a conta.')
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
    }""",
    'webhook-confirma-evento-alterar'
)

print('TUDO OK:', feitos)
