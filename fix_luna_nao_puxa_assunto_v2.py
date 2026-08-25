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

# A instrucao de "nao puxar assunto" ja existia no comeco do prompt, mas a IA
# continuou ignorando em alguns casos. Modelos de linguagem seguem melhor uma
# instrucao repetida logo antes de responder (no fim do prompt) do que uma
# regra geral la no comeco, longe de onde a resposta e gerada. Repete a regra
# reforcada no final, junto com a mensagem literal da Denise.
replace_once(
    'api/whatsapp-webhook.js',
    """    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda APENAS o assunto exato que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda, treino, rotina ou qualquer outro aviso por conta própria, mesmo que esteja no contexto abaixo. NUNCA emende um segundo assunto que ela não mencionou nessa mensagem, mesmo que pareça relacionado ou pendente. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)""",
    """    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda APENAS o assunto exato que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda, treino, rotina ou qualquer outro aviso por conta própria, mesmo que esteja no contexto abaixo. NUNCA emende um segundo assunto que ela não mencionou nessa mensagem, mesmo que pareça relacionado ou pendente. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2) + '\\n\\nREGRA FINAL, A MAIS IMPORTANTE: a mensagem que a Denise mandou agora foi exatamente: "' + userText.replace(/"/g, "'") + '". Sua resposta deve falar SOMENTE sobre isso. Proibido mencionar treino, rotina, agenda, contas ou qualquer outro assunto do contexto acima que ela nao tenha citado nesta mensagem especifica, mesmo que pareca util ou relacionado.'""",
    'webhook-luna-nao-puxa-assunto-v2-reforco-final'
)

print('TUDO OK:', feitos)
