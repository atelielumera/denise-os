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

# ---------- api/whatsapp-webhook.js: transforma processarComando numa funcao compartilhavel ----------

replace_once(
    'api/whatsapp-webhook.js',
    "async function processarComando(number, userText, hojeIso, supabase, d) {",
    "export async function processarComando(userText, hojeIso, supabase, d) {",
    'webhook-processarComando-assinatura'
)

replace_once(
    'api/whatsapp-webhook.js',
    "  if (!userText || !supabase) return false",
    "  if (!userText || !supabase) return null",
    'webhook-processarComando-guard-vazio'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada) {
      return false
    }""",
    """    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada) {
      return null
    }""",
    'webhook-processarComando-nada-aplicado'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    await sendWhatsappText(number, partesConfirmacao.join('\\n'))
    return true
  } catch {
    return false
  }
}""",
    """    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    return partesConfirmacao.join('\\n')
  } catch {
    return null
  }
}""",
    'webhook-processarComando-retorna-mensagem'
)

replace_once(
    'api/whatsapp-webhook.js',
    """    if (userText) {
      const processou = await processarComando(number, userText, context.data_hoje, supabase, d)
      if (processou) {
        res.status(200).json({ ok: true })
        return
      }
    }""",
    """    if (userText) {
      const mensagemAcao = await processarComando(userText, context.data_hoje, supabase, d)
      if (mensagemAcao) {
        await sendWhatsappText(number, mensagemAcao)
        res.status(200).json({ ok: true })
        return
      }
    }""",
    'webhook-chamada-processarComando'
)

# ---------- api/chat.js: usa o mesmo contexto real e as mesmas acoes do WhatsApp ----------

replace_once(
    'api/chat.js',
    "export default async function handler(req, res) {",
    """import { getSupabaseAdmin, buildLunaContext, transcribeAudio } from './_cronlib.js'
import { processarComando } from './whatsapp-webhook.js'

export default async function handler(req, res) {""",
    'chat-imports'
)

replace_once(
    'api/chat.js',
    "  const { message, history, context, images, audio } = req.body || {}",
    "  const { message, history, images, audio } = req.body || {}",
    'chat-remove-context-do-cliente'
)

replace_once(
    'api/chat.js',
    """    if (audio && audio.base64) {
      const geminiKey = process.env.GEMINI_API_KEY
      if (!geminiKey) {
        res.status(500).json({ error: 'GEMINI_API_KEY nao configurada no servidor (necessaria para audio).' })
        return
      }
      const geminiResp = await fetch(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + geminiKey,
        {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({
            contents: [{
              parts: [
                { text: 'Transcreva este audio em portugues do Brasil. Responda apenas com o texto transcrito, sem comentarios.' },
                { inline_data: { mime_type: audio.mediaType || 'audio/webm', data: audio.base64 } }
              ]
            }]
          })
        }
      )
      const geminiData = await geminiResp.json()
      if (!geminiResp.ok) {
        res.status(502).json({ error: geminiData?.error?.message || 'Erro ao transcrever audio.' })
        return
      }
      const transcript = (geminiData.candidates?.[0]?.content?.parts?.[0]?.text || '').trim()
      if (!transcript) {
        res.status(422).json({ error: 'Nao consegui entender o audio. Pode tentar de novo ou digitar?' })
        return
      }
      userText = userText ? (userText + '\\n\\n(audio transcrito): ' + transcript) : transcript
    }""",
    """    if (audio && audio.base64) {
      let transcript = ''
      try {
        transcript = await transcribeAudio(audio.base64, audio.mediaType || 'audio/webm')
      } catch (err) {
        res.status(500).json({ error: err?.message || 'Erro ao transcrever audio.' })
        return
      }
      if (!transcript) {
        res.status(422).json({ error: 'Nao consegui entender o audio. Pode tentar de novo ou digitar?' })
        return
      }
      userText = userText ? (userText + '\\n\\n(audio transcrito): ' + transcript) : transcript
    }""",
    'chat-transcricao-compartilhada'
)

replace_once(
    'api/chat.js',
    """    if (!userText && !(images && images.length > 0)) {
      res.status(400).json({ error: 'Nenhuma mensagem recebida.' })
      return
    }

    const systemPrompt = 'Voce e a Luna""",
    """    if (!userText && !(images && images.length > 0)) {
      res.status(400).json({ error: 'Nenhuma mensagem recebida.' })
      return
    }

    const supabase = getSupabaseAdmin()
    const context = await buildLunaContext()

    if (userText && supabase) {
      const { data: snap } = await supabase.from('app_snapshot').select('data').eq('id', 'denise').maybeSingle()
      const d = snap?.data || {}
      const mensagemAcao = await processarComando(userText, context.data_hoje, supabase, d)
      if (mensagemAcao) {
        res.status(200).json({ reply: mensagemAcao, transcript: audio ? userText : undefined })
        return
      }
    }

    const systemPrompt = 'Voce e a Luna""",
    'chat-contexto-real-e-acoes-rapidas'
)

print('TUDO OK:', feitos)
