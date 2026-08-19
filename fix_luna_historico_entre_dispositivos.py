from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

# O historico da Luna ja fica salvo no navegador (localStorage), mas so nesse mesmo navegador/aparelho.
# Se a Denise abrir em outro celular/computador, ou trocar de navegador, aparece vazio - nao porque
# quebrou, mas porque nunca existiu sincronizacao de volta do servidor pra esse aparelho novo.
# Este fix adiciona: ao abrir a Luna, se nao houver conversa real salva localmente, busca a ultima
# conversa sincronizada no Supabase (o mesmo snapshot que o app ja envia pra nuvem a cada 30s) e
# carrega ela. Assim a conversa acompanha a Denise entre aparelhos, de verdade.
old = """  React.useEffect(()=>{
    try{localStorage.setItem(LUNA_CHAT_KEY,JSON.stringify(msgs.slice(-40)))}catch{}
  },[msgs])
  function novaConversa(){setMsgs(saudacaoInicial())}"""
new = """  React.useEffect(()=>{
    try{localStorage.setItem(LUNA_CHAT_KEY,JSON.stringify(msgs.slice(-40)))}catch{}
  },[msgs])
  React.useEffect(()=>{
    (async()=>{
      try{
        const local=JSON.parse(localStorage.getItem(LUNA_CHAT_KEY)||'null')
        if(Array.isArray(local)&&local.length>1)return
        const {data:snap}=await supabase.from('app_snapshot').select('data').eq('id','denise').maybeSingle()
        const remoto=snap?.data?.[LUNA_CHAT_KEY]
        if(Array.isArray(remoto)&&remoto.length>1){
          setMsgs(remoto)
          localStorage.setItem(LUNA_CHAT_KEY,JSON.stringify(remoto))
        }
      }catch{}
    })()
  },[])
  function novaConversa(){setMsgs(saudacaoInicial())}"""
s = replace_once(s, old, new, "assistente-hidratar-historico-remoto")

main_file.write_text(s)
print("OK - Luna agora tambem busca a conversa salva no servidor quando abre num aparelho/navegador")
print("onde ainda nao tem nada salvo localmente. Continua funcionando offline (localStorage) e agora")
print("tambem acompanha entre dispositivos (via o mesmo snapshot que o app ja sincroniza a cada 30s).")
print()
print("IMPORTANTE: mensagens trocadas ANTES deste fix nunca foram salvas em lugar nenhum - nao tem")
print("como recuperar essas. So as mensagens de agora em diante ficam guardadas.")
