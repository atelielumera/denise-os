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

replace_once(
    'api/cron-check.js',
    """    const planoTreinoHoje = planoTreinoDoDia(d, diaSemanaHoje)
    const treinos = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
    const treinoRegistradoHoje = treinos.some((t) => t.data === hojeIso) || d[`dos_treino_registrado_${hojeIso}`]
    if (planoTreinoHoje && !planoTreinoHoje.descanso && !treinoRegistradoHoje && lembraOuCobra('12:00', 21 * 60 + 30)) {
      avisos.push(`🏋️ Treino de hoje (${planoTreinoHoje.nome}) — já fez ou não? Me conta pra eu registrar.`)
    }""",
    """    const planoTreinoHoje = planoTreinoDoDia(d, diaSemanaHoje)
    const treinos = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
    const treinoRegistradoHoje = treinos.some((t) => t.data === hojeIso) || d[`dos_treino_registrado_${hojeIso}`]
    let criarPendenteTreino = false
    if (planoTreinoHoje && !planoTreinoHoje.descanso && !treinoRegistradoHoje && lembraOuCobra('12:00', 21 * 60 + 30)) {
      avisos.push(`🏋️ Treino de hoje (${planoTreinoHoje.nome}) — já fez ou não? Me conta pra eu registrar.`)
      criarPendenteTreino = true
    }""",
    'cron-check-marca-pendente-treino'
)

replace_once(
    'api/cron-check.js',
    """    if (avisos.length === 0) {
      res.status(200).json({ ok: true, avisos_enviados: 0 })
      return
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

    const texto = '🔔 Está na hora de:\\n\\n' + avisos.join('\\n')
    await sendWhatsappText(numero, texto)
    res.status(200).json({ ok: true, avisos_enviados: avisos.length })""",
    'cron-check-envia-e-registra-pendente'
)

replace_once(
    'api/whatsapp-webhook.js',
    """      if (pendente.tipo === 'conta_boleto' && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))) {
        delete d.dos_luna_pendente
        await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
        await sendWhatsappText(number, 'Combinado, não criei a conta.')
        res.status(200).json({ ok: true })
        return
      }
      if (pendente.tipo === 'evento_cancelar' && PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))) {""",
    """      if (pendente.tipo === 'conta_boleto' && PALAVRAS_NAO_PENDENTE.some((p) => textoNormalizado.includes(p))) {
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
      if (pendente.tipo === 'evento_cancelar' && PALAVRAS_SIM_PENDENTE.some((p) => textoNormalizado.includes(p))) {""",
    'webhook-trata-pendente-treino'
)

print('TUDO OK:', feitos)
