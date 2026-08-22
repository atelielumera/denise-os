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
    """export function calcularAutonomiaTirzepatida(tzMap, saldoMg) {
  const mgDia = ['denise', 'flavio'].reduce((soma, pessoa) => {
    const sched = tzMap[pessoa]
    if (!sched || !sched.planned_dose_mg || !sched.interval_days) return soma
    return soma + sched.planned_dose_mg / sched.interval_days
  }, 0)
  return mgDia > 0 ? Math.floor(saldoMg / mgDia) : null
}""",
    """export function calcularAutonomiaTirzepatida(tzMap, saldoMg) {
  const mgDia = ['denise', 'flavio'].reduce((soma, pessoa) => {
    const sched = tzMap[pessoa]
    if (!sched || !sched.planned_dose_mg || !sched.interval_days) return soma
    return soma + sched.planned_dose_mg / sched.interval_days
  }, 0)
  return mgDia > 0 ? Math.floor(saldoMg / mgDia) : null
}

export async function detectarBoleto(base64, mediaType) {
  const prompt = 'Essa imagem e um boleto, conta ou fatura (agua, luz, internet, cartao, mensalidade, condominio, etc)? Responda APENAS com um JSON, nada mais, sem comentario. Se for boleto/conta: {"eh_boleto":true,"nome":"descricao curta, ex: Conta de luz","valor":numero em reais sem simbolo ou null se nao aparecer,"vencimento":"YYYY-MM-DD ou null se nao aparecer"}. Se nao for um boleto/conta: {"eh_boleto":false}.'
  let resposta = ''
  try {
    resposta = await askLuna(prompt, [{ type: 'image', source: { type: 'base64', media_type: mediaType, data: base64 } }, { type: 'text', text: 'Analise a imagem.' }])
  } catch {
    return { eh_boleto: false }
  }
  const match = resposta.match(/\\{[\\s\\S]*\\}/)
  if (!match) return { eh_boleto: false }
  try { return JSON.parse(match[0]) } catch { return { eh_boleto: false } }
}""",
    'cronlib-detecta-boleto'
)

# ---------- api/whatsapp-webhook.js ----------

replace_once(
    'api/whatsapp-webhook.js',
    "import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento, normalizarAval } from './_cronlib.js'",
    "import { sendWhatsappText, transcribeAudio, askLuna, buildLunaContext, lunaSystemPrompt, getSupabaseAdmin, insertGoogleCalendarEvento, normalizarAval, detectarBoleto } from './_cronlib.js'",
    'webhook-import-detectarBoleto'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    if (!userText && userContent.length === 0) {
      res.status(200).json({ ok: true })
      return
    }
    userContent.push({ type: 'text', text: userText || 'A Denise enviou uma imagem sem legenda pelo WhatsApp. Comente o que você vê e pergunte no que pode ajudar.' })""",
    """    if (msg.documentMessage && !userText && userContent.length === 0) {
      await sendWhatsappText(number, 'Recebi seu documento, mas ainda não sei processar PDF por aqui no WhatsApp. Manda pelo aplicativo, na tela Família, que eu leio o calendário escolar direitinho.')
      res.status(200).json({ ok: true })
      return
    }

    if (!userText && userContent.length === 0) {
      res.status(200).json({ ok: true })
      return
    }
    userContent.push({ type: 'text', text: userText || 'A Denise enviou uma imagem sem legenda pelo WhatsApp. Comente o que você vê e pergunte no que pode ajudar.' })""",
    'webhook-pdf-nao-fica-mudo'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    if (userText) {
      const mensagemAcao = await processarComando(userText, context.data_hoje, supabase, d)
      if (mensagemAcao) {
        await sendWhatsappText(number, mensagemAcao)
        res.status(200).json({ ok: true })
        return
      }
    }""",
    """    const PALAVRAS_SIM_PENDENTE = ['sim', 'confirma', 'confirmo', 'pode', 'isso', 'correto', 'positivo', 'exato', 'certo']
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
    }""",
    'webhook-boleto-e-confirmacao-pendente'
)

print('TUDO OK:', feitos)
