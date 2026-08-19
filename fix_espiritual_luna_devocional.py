from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# 1) src/main.tsx - tira o bloco "Pergunte" (Quem/O que/Quando/Onde/Por que) do formulario
# do Espiritual. Essas perguntas agora a Luna manda pelo WhatsApp no devocional da manha,
# em vez da Denise ter que digitar resposta pra cada uma no app.
main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_pergunte = """        <div style={{fontSize:12,fontWeight:700,color:'rgba(255,255,255,.6)',margin:'12px 0 8px'}}>Pergunte</div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
          {([
            ['quem','Quem?'],['oque','O quê?'],['quando','Quando?'],['onde','Onde?'],['porque','Por quê?'],
          ] as [string,string][]).map(([campo,label])=>(
            <div key={campo}>
              <label style={{fontSize:11.5,color:'rgba(255,255,255,.4)',display:'block',marginBottom:4}}>{label}</label>
              <input value={(perguntas as any)[campo]} onChange={e=>setPergunta(campo,e.target.value)} style={{width:'100%',background:C.bg,border:'1px solid rgba(255,255,255,.15)',borderRadius:10,padding:'9px 12px',color:'#fff',fontSize:13.5}}/>
            </div>
          ))}
        </div>
        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Gratidão</label>"""
new_pergunte = """        <label style={{fontSize:12,color:'rgba(255,255,255,.4)',display:'block',marginBottom:5}}>Gratidão</label>"""
s = replace_once(s, old_pergunte, new_pergunte, "espiritual-tira-pergunte")
main_file.write_text(s)

# 2) api/_cronlib.js - adiciona no contexto se o devocional de hoje ja foi feito, pra Luna
# saber se deve cobrar/perguntar ou nao.
cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_ctx = """    sequencia_devocional_dias: sequencia(diasUnicos(devocionais)),"""
new_ctx = """    sequencia_devocional_dias: sequencia(diasUnicos(devocionais)),
    devocional_feito_hoje: devocionais.some((e) => e.data === hojeIso),"""
c = replace_once(c, old_ctx, new_ctx, "cronlib-devocional-feito-hoje")
cronlib_file.write_text(c)

# 3) api/cron-morning.js - a mensagem de bom dia passa a incluir as perguntas do devocional
# quando ainda nao foi feito hoje, pra Denise refletir direto pelo WhatsApp.
morning_file = Path("api/cron-morning.js")
if not morning_file.exists():
    raise SystemExit("ABORTADO (cron-morning-nao-encontrado): rode este script na raiz do projeto denise-os.")
m = morning_file.read_text()

old_pedido = """e tarefas de trabalho pendentes se houver. Se uma dessas categorias estiver vazia ou sem dado (por exemplo busca_domi_hoje nulo no fim de semana), não mencione ela (não diga "nada registrado"). Termine com uma frase curta de incentivo. Formato de WhatsApp, use emojis com moderação, sem markdown de negrito.'"""
new_pedido = """e tarefas de trabalho pendentes se houver. Se devocional_feito_hoje for false, inclua tambem uma seção "🙏 Devocional de hoje" com exatamente estas perguntas de reflexão, nesta ordem (não mude o texto delas): "Existe um mandamento a obedecer? Uma promessa a reivindicar? Um pecado a evitar? Uma aplicação a fazer? Algo novo sobre Deus?" e depois "Pergunte também: Quem? O quê? Quando? Onde? Por quê?" - é só um convite pra ela refletir mentalmente ao longo do dia, não peça pra responder por escrito. Se devocional_feito_hoje for true, não inclua essa seção. Se uma dessas categorias estiver vazia ou sem dado (por exemplo busca_domi_hoje nulo no fim de semana), não mencione ela (não diga "nada registrado"). Termine com uma frase curta de incentivo. Formato de WhatsApp, use emojis com moderação, sem markdown de negrito.'"""
m = replace_once(m, old_pedido, new_pedido, "cron-morning-devocional-perguntas")
morning_file.write_text(m)

print("OK:")
print(" - Espiritual: tirado o bloco 'Pergunte' (Quem/O que/Quando/Onde/Por que) do formulario.")
print(" - Luna agora manda essas perguntas pelo WhatsApp na mensagem de bom dia, so quando o")
print("   devocional do dia ainda nao foi feito - e um convite pra refletir, nao um formulario.")
