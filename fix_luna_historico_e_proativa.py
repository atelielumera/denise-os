from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# --- 1) api/chat.js: nao puxar lembretes/agenda por conta propria no chat do app ---
chat_file = Path("api/chat.js")
if not chat_file.exists():
    raise SystemExit("ABORTADO (chat-js-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = chat_file.read_text()

old_prompt = "const systemPrompt = 'Voce e a Luna, assistente pessoal da Denise dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em portugues do Brasil, com respostas curtas (2 a 5 frases). Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente numeros, datas ou fatos que nao estao ali. Se um dado nao estiver no contexto, diga com naturalidade que ele ainda nao foi registrado no app.\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context || {}, null, 2)"
new_prompt = "const systemPrompt = 'Voce e a Luna, assistente pessoal da Denise dentro do Denise OS. Seja direta, acolhedora e sem julgamento, em portugues do Brasil, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - nao puxe lembretes, contas, agenda ou avisos por conta propria. Se ela so cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informacoes do contexto. Use APENAS os dados reais fornecidos no contexto abaixo - nunca invente numeros, datas ou fatos que nao estao ali. Se um dado nao estiver no contexto, diga com naturalidade que ele ainda nao foi registrado no app.\\n\\nContexto atual (dados reais da Denise, agora):\\n' + JSON.stringify(context || {}, null, 2)"
c = replace_once(c, old_prompt, new_prompt, "chat-js-prompt-nao-proativo")
chat_file.write_text(c)

# --- 2) api/whatsapp-webhook.js: mesma regra para as respostas da Luna no WhatsApp ---
# (os resumos automaticos de cron-morning/evening/weekly/nextweek continuam proativos de proposito - nao mexemos neles)
webhook_file = Path("api/whatsapp-webhook.js")
if not webhook_file.exists():
    raise SystemExit("ABORTADO (webhook-nao-encontrado): rode este script na raiz do projeto denise-os.")
w = webhook_file.read_text()

old_extra = "lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases).')"
new_extra = "lunaSystemPrompt('Você está respondendo agora pelo WhatsApp, com respostas curtas (2 a 5 frases). Responda apenas o que a Denise perguntou ou comentou agora - não puxe lembretes, contas, agenda ou avisos por conta própria. Se ela só cumprimentar ou bater papo, cumprimente de volta e pergunte como pode ajudar, sem listar informações do contexto.')"
w = replace_once(w, old_extra, new_extra, "webhook-prompt-nao-proativo")
webhook_file.write_text(w)

# --- 3) src/main.tsx: Luna do app passa a lembrar da conversa (como um chat tipo GPT) ---
main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_msgs = "  const [msgs,setMsgs]=React.useState<{me:boolean,t:string}[]>([{me:false,t:`${g}, Denise! Sou a Luna 💜 Pode falar comigo por texto, áudio ou mandar uma foto. Como posso ajudar?`}])"
new_msgs = """  const LUNA_CHAT_KEY='dos_luna_chat'
  const saudacaoInicial=()=>[{me:false,t:`${g}, Denise! Sou a Luna 💜 Pode falar comigo por texto, áudio ou mandar uma foto. Como posso ajudar?`}]
  const [msgs,setMsgs]=React.useState<{me:boolean,t:string}[]>(()=>{
    try{
      const salvo=JSON.parse(localStorage.getItem(LUNA_CHAT_KEY)||'null')
      if(Array.isArray(salvo)&&salvo.length>0)return salvo
    }catch{}
    return saudacaoInicial()
  })
  React.useEffect(()=>{
    try{localStorage.setItem(LUNA_CHAT_KEY,JSON.stringify(msgs.slice(-40)))}catch{}
  },[msgs])
  function novaConversa(){setMsgs(saudacaoInicial())}"""
s = replace_once(s, old_msgs, new_msgs, "main-tsx-msgs-persistidos")

old_header = """  return(<div style={{padding:'24px 28px'}}>
    <h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Luna</h1>
    <p style={{color:'rgba(255,255,255,.4)',fontSize:13,marginBottom:20}}>Sua assistente pessoal — entende texto, áudio e imagem.</p>
    <div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const,height:'60vh'}}>"""
new_header = """  return(<div style={{padding:'24px 28px'}}>
    <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:12,marginBottom:20}}>
      <div><h1 style={{fontSize:24,fontWeight:800,marginBottom:4}}>Luna</h1><p style={{color:'rgba(255,255,255,.4)',fontSize:13}}>Sua assistente pessoal — entende texto, áudio e imagem.</p></div>
      <button onClick={novaConversa} style={{background:C.s2,border:`1px solid ${C.line}`,color:'rgba(255,255,255,.7)',borderRadius:9,padding:'8px 14px',fontSize:12,cursor:'pointer',flexShrink:0,whiteSpace:'nowrap' as const}}>+ Nova conversa</button>
    </div>
    <div style={{background:'linear-gradient(180deg,#16161f,#131320)',border:`1px solid ${C.line}`,borderRadius:16,padding:18,display:'flex',flexDirection:'column' as const,height:'60vh'}}>"""
s = replace_once(s, old_header, new_header, "main-tsx-botao-nova-conversa")

main_file.write_text(s)

print("OK - 3 arquivos corrigidos:")
print(" - api/chat.js: Luna do app nao puxa mais lembretes/agenda sem ser perguntada")
print(" - api/whatsapp-webhook.js: mesma regra para as respostas da Luna no WhatsApp (os resumos automaticos continuam iguais)")
print(" - src/main.tsx: a conversa com a Luna no app agora fica salva (ultimas 40 mensagens) e sincroniza entre dispositivos; botao '+ Nova conversa' para comecar do zero quando quiser")
