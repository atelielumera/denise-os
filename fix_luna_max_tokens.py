from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# Causa raiz encontrada: o modelo (claude-sonnet-5) usa "pensamento" (thinking) ligado por
# padrao, mesmo sem pedir. O max_tokens estava em 800 - baixo demais - entao o pensamento
# sozinho consumia todo esse limite antes do modelo conseguir escrever a resposta final.
# A API respondia "200 OK" (sem erro), so que sem nenhum bloco de texto - por isso caia
# sempre no texto de reserva "Desculpa, nao consegui gerar isso agora."

cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (_cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_req = """    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 800,
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }]
    })
  })
  const data = await anthropicResp.json()
  if (!anthropicResp.ok) throw new Error(data?.error?.message || 'Erro ao consultar a IA.')
  return data.content?.find((b) => b.type === 'text')?.text || 'Desculpa, não consegui gerar isso agora.'
}"""
new_req = """    body: JSON.stringify({
      model: 'claude-sonnet-5',
      max_tokens: 4096,
      output_config: { effort: 'low' },
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }]
    })
  })
  const data = await anthropicResp.json()
  if (!anthropicResp.ok) throw new Error(data?.error?.message || 'Erro ao consultar a IA.')
  const texto = data.content?.find((b) => b.type === 'text')?.text
  if (!texto) throw new Error('Luna nao gerou texto (stop_reason: ' + (data.stop_reason || '?') + ')')
  return texto
}"""
c = replace_once(c, old_req, new_req, "askLuna-max-tokens-e-diagnostico")
cronlib_file.write_text(c)

print("OK - api/_cronlib.js corrigido:")
print(" - max_tokens de 800 para 4096 (o modelo pensa antes de responder por padrao, e 800")
print("   era pouco - o pensamento sozinho consumia tudo antes de escrever a resposta final).")
print(" - effort 'low' (tarefa simples de resumo, nao precisa pensar muito - fica mais rapido")
print("   e mais barato tambem).")
print(" - se mesmo assim faltar texto, agora da erro de verdade em vez de mandar a frase de")
print("   desculpa pro WhatsApp - assim da pra ver o motivo real se acontecer de novo.")

# Mesmo bug, mesmo motivo, no chat da Luna dentro do proprio app (nao so no WhatsApp).
chat_file = Path("api/chat.js")
if not chat_file.exists():
    raise SystemExit("ABORTADO (chat-js-nao-encontrado): rode este script na raiz do projeto denise-os.")
ch = chat_file.read_text()

old_chat = """      body: JSON.stringify({
        model: 'claude-sonnet-5',
        max_tokens: 600,
        system: systemPrompt,
        messages: [...historico, { role: 'user', content: userContent }]
      })
    })
    const data = await anthropicResp.json()
    if (!anthropicResp.ok) {
      res.status(502).json({ error: data?.error?.message || 'Erro ao consultar a IA.' })
      return
    }
    const reply = data.content?.find(b => b.type === 'text')?.text || 'Desculpa, nao consegui responder agora.'
    res.status(200).json({ reply, transcript: audio ? userText : undefined })"""
new_chat = """      body: JSON.stringify({
        model: 'claude-sonnet-5',
        max_tokens: 4096,
        output_config: { effort: 'low' },
        system: systemPrompt,
        messages: [...historico, { role: 'user', content: userContent }]
      })
    })
    const data = await anthropicResp.json()
    if (!anthropicResp.ok) {
      res.status(502).json({ error: data?.error?.message || 'Erro ao consultar a IA.' })
      return
    }
    const reply = data.content?.find(b => b.type === 'text')?.text
    if (!reply) {
      res.status(502).json({ error: 'Luna nao gerou texto (stop_reason: ' + (data.stop_reason || '?') + ')' })
      return
    }
    res.status(200).json({ reply, transcript: audio ? userText : undefined })"""
ch = replace_once(ch, old_chat, new_chat, "chat-js-max-tokens-e-diagnostico")
chat_file.write_text(ch)

print("")
print("OK - api/chat.js (chat da Luna dentro do app) corrigido com a mesma logica.")
