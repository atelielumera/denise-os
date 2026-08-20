from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# Bug serio: cada mensagem sua no WhatsApp era tratada pela Luna como se fosse a primeira
# conversa da vida dela - ela nao lembrava nem do que ela mesma tinha acabado de perguntar.
# Alem disso, quando voce pediu pra colocar "Culto de mulheres toda quinta" na agenda, ela
# disse "Anotado!" mas nao salvou nada de verdade - so falou.
#
# Esse script corrige os dois problemas:
#  1) askLuna passa a aceitar um historico de mensagens anteriores.
#  2) O webhook do WhatsApp agora le e grava o historico de conversa (mesmo dado que o chat
#     do app usa - dos_luna_chat), entao ela lembra do que foi falado antes, no WhatsApp E
#     no app, tanto faz.
#  3) Quando voce pede pra colocar um compromisso recorrente (tipo "toda quinta X das Y as
#     Z"), agora isso realmente vira um item na sua Rotina (categoria Compromisso, no dia
#     certo da semana) - nao fica so na conversa.

cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_ask = """export async function askLuna(systemPrompt, userContent) {
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY nao configurada.')
  const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 4096,
      output_config: { effort: 'low' },
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }]
    })
  })"""
new_ask = """export async function askLuna(systemPrompt, userContent, history) {
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('ANTHROPIC_API_KEY nao configurada.')
  const anthropicResp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 4096,
      output_config: { effort: 'low' },
      system: systemPrompt,
      messages: [...(Array.isArray(history) ? history : []), { role: 'user', content: userContent }]
    })
  })"""
c = replace_once(c, old_ask, new_ask, "cronlib-askluna-history")
cronlib_file.write_text(c)

webhook_file = Path("api/whatsapp-webhook.js")
if not webhook_file.exists():
    raise SystemExit("ABORTADO (webhook-nao-encontrado): rode este script na raiz do projeto denise-os.")
w = webhook_file.read_text()

old_1 = """async function processarComando(number, userText, hojeIso) {
  if (!userText) return false
  const supabase = getSupabaseAdmin()
  if (!supabase) return false
  try {
    const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
    const d = snap?.data || {}

    const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()"""
new_1 = """async function processarComando(number, userText, hojeIso, supabase, d) {
  if (!userText || !supabase) return false
  try {
    const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()"""
w = replace_once(w, old_1, new_1, "webhook-processarComando-assinatura")

old_2 = """    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && !/compr|adicion|mercado|lista/i.test(userText)) {
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
    }"""
new_2 = """    if (rotinaPendente.length === 0 && casaPendente.length === 0 && avalDomiPendente.length === 0 && avalDerickPendente.length === 0 && !/compr|adicion|mercado|lista|coloca|agenda|toda |todo /i.test(userText)) {
      return false
    }

    const classPrompt = 'Responda APENAS com um JSON, nada mais, sem comentario. Formato exato: {"feitos_rotina":[numeros],"feitos_casa":[numeros],"feitos_aval_domi":[numeros],"feitos_aval_derick":[numeros],"novos_casa":[{"nome":"...","categoria":"Mercado|Doméstico|Manutenção|Contas"}],"novos_compromissos":[{"nome":"...","dia_semana":numero de 0 a 6 (0=domingo,1=segunda,2=terca,3=quarta,4=quinta,5=sexta,6=sabado),"horario":"HH:MM"}]}. A Denise mandou esta mensagem pelo WhatsApp: "' + userText.replace(/"/g, "'") + '".\\n\\nRotina de hoje ainda pendente (id, horario, nome): ' + JSON.stringify(rotinaPendente.map((p) => ({ id: p.idx, horario: p.horario, nome: p.nome }))) + '\\nItens pendentes da Casa (id, nome, categoria): ' + JSON.stringify(casaPendente.map((p) => ({ id: p.idx, nome: p.nome, categoria: p.categoria }))) + '\\nAvaliações pendentes da Domi (id, data, tipo): ' + JSON.stringify(avalDomiPendente) + '\\nAvaliações pendentes do Derick (id, data, tipo): ' + JSON.stringify(avalDerickPendente) + '\\n\\nSe a mensagem confirmar que ela fez algo dessas listas (ex: "ja fiz X", "paguei a luz", "registrei a prova de matematica da domi"), coloque os ids certos no campo correspondente. Se a mensagem for uma lista de compras ou tarefas novas pra Casa (ex: "compra leite, pao e ovos", "adiciona pagar internet"), coloque cada item novo em novos_casa com nome e a categoria certa (Mercado para compras de supermercado, Contas para contas a pagar, Doméstico para tarefas de casa, Manutenção para consertos). Se a mensagem pedir pra colocar um compromisso recorrente (toda segunda/terca/etc) na agenda/rotina (ex: "coloca toda quinta Culto de mulheres das 13:30 as 16:00"), coloque em novos_compromissos com nome (inclua o horario de termino no nome se houver, ex: "Culto de mulheres (ate 16:00)"), dia_semana e horario de inicio. Se nada disso se aplicar, responda com todos os campos vazios.'
    const classResp = await askLuna(classPrompt, [{ type: 'text', text: userText }])
    const match = classResp.match(/\\{[\\s\\S]*\\}/)
    const parsed = match ? JSON.parse(match[0]) : {}

    const feitosRotina = Array.isArray(parsed.feitos_rotina) ? parsed.feitos_rotina.filter((n) => typeof n === 'number' && rotinaPendente.some((p) => p.idx === n)) : []
    const feitosCasa = Array.isArray(parsed.feitos_casa) ? parsed.feitos_casa.filter((n) => typeof n === 'number' && casaPendente.some((p) => p.idx === n)) : []
    const feitosAvalDomi = Array.isArray(parsed.feitos_aval_domi) ? parsed.feitos_aval_domi.filter((n) => typeof n === 'number' && avalDomiPendente.some((p) => p.idx === n)) : []
    const feitosAvalDerick = Array.isArray(parsed.feitos_aval_derick) ? parsed.feitos_aval_derick.filter((n) => typeof n === 'number' && avalDerickPendente.some((p) => p.idx === n)) : []
    const novosCasa = Array.isArray(parsed.novos_casa) ? parsed.novos_casa.filter((n) => n && n.nome) : []
    const novosCompromissos = Array.isArray(parsed.novos_compromissos) ? parsed.novos_compromissos.filter((n) => n && n.nome && typeof n.dia_semana === 'number' && n.dia_semana >= 0 && n.dia_semana <= 6 && /^\\d{1,2}:\\d{2}$/.test(n.horario || '')) : []

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0) {
      return false
    }"""
w = replace_once(w, old_2, new_2, "webhook-classificador-compromissos")

old_3 = """      d.dos_avals = novosAvals
    }

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    await sendWhatsappText(number, partesConfirmacao.join('\\n'))
    return true
  } catch {
    return false
  }
}"""
new_3 = """      d.dos_avals = novosAvals
    }

    if (novosCompromissos.length > 0) {
      const rotinaAtual = Array.isArray(d.dos_rotina) ? d.dos_rotina : rotina
      const adicionados = novosCompromissos.map((n) => ({ t: n.horario, n: n.nome, cat: 'Compromisso', dias: [n.dia_semana] }))
      d.dos_rotina = [...rotinaAtual, ...adicionados]
      const DIAS_NOME = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']
      partesConfirmacao.push('📅 Adicionei na sua rotina: ' + adicionados.map((a) => `${a.n} toda ${DIAS_NOME[a.dias[0]]} às ${a.t}`).join(', '))
    }

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    await sendWhatsappText(number, partesConfirmacao.join('\\n'))
    return true
  } catch {
    return false
  }
}"""
w = replace_once(w, old_3, new_3, "webhook-aplica-compromissos")

old_4 = """    const context = await buildLunaContext()

    if (userText) {
      const processou = await processarComando(number, userText, context.data_hoje)
      if (processou) {
        res.status(200).json({ ok: true })
        return
      }
    }

    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent)
    await sendWhatsappText(number, reply)
    res.status(200).json({ ok: true })"""
new_4 = """    const context = await buildLunaContext()
    const supabase = getSupabaseAdmin()
    let d = {}
    if (supabase) {
      const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
      d = snap?.data || {}
    }

    if (userText) {
      const processou = await processarComando(number, userText, context.data_hoje, supabase, d)
      if (processou) {
        res.status(200).json({ ok: true })
        return
      }
    }

    const historico = Array.isArray(d.dos_luna_chat) ? d.dos_luna_chat.slice(-20) : []
    const historyMsgs = historico.map((m) => ({ role: m.me ? 'user' : 'assistant', content: String(m.t || '') }))
    while (historyMsgs.length > 0 && historyMsgs[0].role === 'assistant') historyMsgs.shift()

    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)

    const reply = await askLuna(systemPrompt, userContent, historyMsgs)
    await sendWhatsappText(number, reply)

    if (supabase) {
      const novoHistorico = [...historico, { me: true, t: userText || '(enviou uma imagem)' }, { me: false, t: reply }].slice(-40)
      await supabase.from('app_snapshot').upsert({ id: 'denise', data: { ...d, dos_luna_chat: novoHistorico }, updated_at: new Date().toISOString() })
    }

    res.status(200).json({ ok: true })"""
w = replace_once(w, old_4, new_4, "webhook-handler-memoria")

webhook_file.write_text(w)
print("OK:")
print(" 1) askLuna agora aceita historico de mensagens anteriores.")
print(" 2) A Luna no WhatsApp agora lembra da conversa (mesmo historico do chat do app,")
print("    dos_luna_chat) - nao esquece mais o que ela ou voce falou na mensagem anterior.")
print(" 3) Pedir um compromisso recorrente (ex: 'coloca toda quinta Culto de mulheres das")
print("    13:30 as 16:00') agora realmente cria o item na Minha Rotina - nao fica so na")
print("    conversa. Pode mandar de novo o pedido do Culto de mulheres que dessa vez salva.")
