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

# A Luna estava respondendo certo sobre o assunto perguntado, mas colando por
# conta propria um paragrafo extra sobre outro assunto pendente no contexto
# (ex: perguntou sobre o whey da tarde e ela emendou "vamos marcar os dias de
# treino"). A instrucao ja pedia pra nao fazer isso, mas de forma fraca demais.
# Reforca a regra de responder SO o assunto da mensagem atual.
replace_once(
    'api/whatsapp-webhook.js',
    """    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)""",
    """    const systemPrompt = lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda APENAS o assunto exato que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda, treino, rotina ou qualquer outro aviso por conta própria, mesmo que esteja no contexto abaixo. NUNCA emende um segundo assunto que ela não mencionou nessa mensagem, mesmo que pareça relacionado ou pendente. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto. Você tem o histórico recente da conversa (WhatsApp e app são a mesma conversa) - use ele pra lembrar do que foi falado antes.') + '\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context, null, 2)""",
    'webhook-luna-nao-puxa-assunto'
)

print('TUDO OK:', feitos)
