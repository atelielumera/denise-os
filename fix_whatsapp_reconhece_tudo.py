from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# A Luna so reconhecia "ja fiz" pra itens da Minha Rotina. Agora ela reconhece pelo WhatsApp:
#  - confirmar feito na Minha Rotina (ja existia)
#  - confirmar feito em itens da Casa (compras, contas, tarefas domesticas, manutencao)
#  - confirmar feito em avaliacoes escolares da Domi e do Derick
#  - criar itens novos na Casa quando voce manda tipo uma lista de compras ou tarefa nova
#    (ex: "compra leite, pao e ovos", "adiciona pagar internet", "limpar o quintal")
# Tudo isso numa mensagem so de confirmacao, e sem precisar abrir o app.

webhook_file = Path("api/whatsapp-webhook.js")
if not webhook_file.exists():
    raise SystemExit("ABORTADO (webhook-nao-encontrado): rode este script na raiz do projeto denise-os.")
w = webhook_file.read_text()

old_func = """async function tentarMarcarFeito(number, userText, context) {
  const pendentes = (context.rotina_de_hoje || []).map((it, idx) => ({ idx, ...it })).filter((it) => !it.feito_hoje)
  if (pendentes.length === 0 || !userText) return false
  try {
    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos":[numeros]}. A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '". Aqui estao os itens da rotina de hoje que AINDA NAO foram marcados como feitos, cada um com seu id: ' + JSON.stringify(pendentes.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '. Se a mensagem confirmar que ela fez um ou mais desses itens agora (ex: "ja fiz o X", "feito", "acabei de Y", "consegui buscar a Domi"), coloque os ids correspondentes em "feitos". Se a mensagem nao for uma confirmacao de tarefa feita (for pergunta, comentario, ou nao bater com nenhum item da lista), responda {"feitos":[]}.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\\{[\\s\\S]*\\}/)
    const parsed = match ? JSON.parse(match[0]) : { feitos: [] }
    const feitos = Array.isArray(parsed.feitos) ? parsed.feitos.filter((n) => typeof n === 'number' && pendentes.some((p) => p.idx === n)) : []
    if (feitos.length === 0) return false
    const supabase = getSupabaseAdmin()
    if (!supabase) return false
    const chave = `dos_rotina_done_${context.data_hoje}`
    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}
    const atual = Array.isArray(d[chave]) ? d[chave] : []
    const uniao = Array.from(new Set([...atual, ...feitos]))
    await supabase.from('app_snapshot').upsert({ id: 'denise', data: { ...d, [chave]: uniao }, updated_at: new Date().toISOString() })
    const nomes = pendentes.filter((p) => feitos.includes(p.idx)).map((p) => p.nome)
    await sendWhatsappText(number, '✅ Marquei como feito: ' + nomes.join(', ') + '!')
    return true
  } catch {
    return false
  }
}"""
new_func = """const CASA_CATS_VALIDAS = ['Mercado', 'Doméstico', 'Manutenção', 'Contas']

async function processarComando(number, userText, hojeIso) {
  if (!userText) return false
  const supabase = getSupabaseAdmin()
  if (!supabase) return false
  try {
    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}

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
    const avalDomi = Array.isArray(avals.domi) ? avals.domi : []
    const avalDerick = Array.isArray(avals.derick) ? avals.derick : []
    const avalDomiPendente = avalDomi.map((a, idx) => ({ idx, data: a.data, tipo: a.tipo })).filter((_, idx) => !avalDomi[idx].feito)
    const avalDerickPendente = avalDerick.map((a, idx) => ({ idx, data: a.data, tipo: a.tipo })).filter((_, idx) => !avalDerick[idx].feito)

    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && !/compr|adicion|mercado|lista/i.test(userText)) {
      return false
    }

    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos_rotina":[numeros],"feitos_casa":[numeros],"feitos_aval_domi":[numeros],"feitos_aval_derick":[numeros],"novos_casa":[{"nome":"...","categoria":"Mercado|Doméstico|Manutenção|Contas"}]}. A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '".\\n\\nRotina de hoje ainda pendente (id, horario, nome): ' + JSON.stringify(rotinaPendente.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '\\nItens pendentes da Casa (id, nome, categoria): ' + JSON.stringify(casaPendente.map((p) => ({ id: p.idx, nome: p.nome, categoria: p.categoria }))) + '\\nAvaliações pendentes da Domi (id, data, tipo): ' + JSON.stringify(avalDomiPendente) + '\\nAvaliações pendentes do Derick (id, data, tipo): ' + JSON.stringify(avalDerickPendente) + '\\n\\nSe a mensagem confirmar que ela fez algo dessas listas (ex: "ja fiz X", "paguei a luz", "registrei a prova de matematica da domi"), coloque os ids certos no campo correspondente. Se a mensagem for uma lista de compras ou tarefas novas pra Casa (ex: "compra leite, pao e ovos", "adiciona pagar internet"), coloque cada item novo em novos_casa com nome e a categoria certa (Mercado para compras de supermercado, Contas para contas a pagar, Doméstico para tarefas de casa, Manutenção para consertos). Se nada disso se aplicar, responda com todos os campos vazios.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\\{[\\s\\S]*\\}/)
    const parsed = match ? JSON.parse(match[0]) : {}

    const feitosRotina = Array.isArray(parsed.feitos_rotina) ? parsed.feitos_rotina.filter((n) => typeof n === 'number' && rotinaPendente.some((p) => p.idx === n)) : []
    const feitosCasa = Array.isArray(parsed.feitos_casa) ? parsed.feitos_casa.filter((n) => typeof n === 'number' && casaPendente.some((p) => p.idx === n)) : []
    const feitosAvalDomi = Array.isArray(parsed.feitos_aval_domi) ? parsed.feitos_aval_domi.filter((n) => typeof n === 'number' && avalDomiPendente.some((p) => p.idx === n)) : []
    const feitosAvalDerick = Array.isArray(parsed.feitos_aval_derick) ? parsed.feitos_aval_derick.filter((n) => typeof n === 'number' && avalDerickPendente.some((p) => p.idx === n)) : []
    const novosCasa = Array.isArray(parsed.novos_casa) ? parsed.novos_casa.filter((n) => n && n.nome) : []

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0) {
      return false
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
        novosAvals.domi = avalDomi.map((a, idx) => (feitosAvalDomi.includes(idx) ? { ...a, feito: true } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação da Domi: ' + avalDomiPendente.filter((p) => feitosAvalDomi.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      if (feitosAvalDerick.length > 0) {
        novosAvals.derick = avalDerick.map((a, idx) => (feitosAvalDerick.includes(idx) ? { ...a, feito: true } : a))
        partesConfirmacao.push('✅ Marquei como feita a avaliação do Derick: ' + avalDerickPendente.filter((p) => feitosAvalDerick.includes(p.idx)).map((p) => p.tipo).join(', '))
      }
      d.dos_avals = novosAvals
    }

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    await sendWhatsappText(number, partesConfirmacao.join('\\n'))
    return true
  } catch {
    return false
  }
}"""
w = replace_once(w, old_func, new_func, "webhook-processarComando")

old_uso = """    if (userText) {
      const marcou = await tentarMarcarFeito(number, userText, context)
      if (marcou) {
        res.status(200).json({ ok: true })
        return
      }
    }"""
new_uso = """    if (userText) {
      const processou = await processarComando(number, userText, context.data_hoje)
      if (processou) {
        res.status(200).json({ ok: true })
        return
      }
    }"""
w = replace_once(w, old_uso, new_uso, "webhook-usa-processarComando")

webhook_file.write_text(w)
print("OK - A Luna agora reconhece pelo WhatsApp, sem precisar do app:")
print(" - confirmar feito na Minha Rotina (ja existia)")
print(" - confirmar feito em itens da Casa (compras, contas, domestico, manutencao)")
print(" - confirmar feito em avaliacoes escolares da Domi e do Derick")
print(" - criar itens novos na Casa quando voce manda uma lista (ex: 'compra leite, pao e ovos')")
