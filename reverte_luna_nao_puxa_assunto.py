import pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent
p = BASE / 'api/whatsapp-webhook.js'
s = p.read_text(encoding='utf-8')

original = """    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)"""

versao_v1 = """    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda APENAS o assunto exato que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda, treino, rotina ou qualquer outro aviso por conta própria, mesmo que esteja no contexto abaixo. NUNCA emende um segundo assunto que ela não mencionou nessa mensagem, mesmo que pareça relacionado ou pendente. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)"""

versao_v2 = """    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda APENAS o assunto exato que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda, treino, rotina ou qualquer outro aviso por conta própria, mesmo que esteja no contexto abaixo. NUNCA emende um segundo assunto que ela não mencionou nessa mensagem, mesmo que pareça relacionado ou pendente. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2) + '\\n\\nREGRA FINAL, A MAIS IMPORTANTE: a mensagem que a Denise mandou agora foi exatamente: "' + userText.replace(/"/g, "'") + '". Sua resposta deve falar SOMENTE sobre isso. Proibido mencionar treino, rotina, agenda, contas ou qualquer outro assunto do contexto acima que ela nao tenha citado nesta mensagem especifica, mesmo que pareca util ou relacionado.'"""

if original in s:
    print('TUDO OK: ja esta na versao original, nada a fazer.')
    sys.exit(0)

if versao_v2 in s:
    s = s.replace(versao_v2, original, 1)
    p.write_text(s, encoding='utf-8')
    print('TUDO OK: revertido da v2 para a versao original.')
    sys.exit(0)

if versao_v1 in s:
    s = s.replace(versao_v1, original, 1)
    p.write_text(s, encoding='utf-8')
    print('TUDO OK: revertido da v1 para a versao original.')
    sys.exit(0)

print('ABORTADO: nao encontrei nenhuma das versoes conhecidas do systemPrompt no arquivo. Nada foi alterado.')
sys.exit(1)
