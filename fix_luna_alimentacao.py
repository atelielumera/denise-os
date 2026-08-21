from pathlib import Path

applied = []

def replace_once(s, old, new, label):
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {c}. Nada foi alterado.")
    applied.append(label)
    return s.replace(old, new, 1)

# ============ api/_cronlib.js: buildLunaContext ganha dados de alimentacao ============
p1 = Path("api/_cronlib.js")
s1 = p1.read_text()

old1 = """  const aguaLog = d.dos_agua_log || {}
  const aguaHojeMl = Number(aguaLog[hojeIso] || 0)

  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaDomiHoje = BUSCA_DOMI_POR_DIA[diaSemanaHoje] || null

  return {
    data_hoje: hojeIso,
    agua_hoje_ml: aguaHojeMl,
    meta_agua_ml: Number(d.dos_meta_agua_ml || 2500),"""
new1 = """  const aguaLog = d.dos_agua_log || {}
  const aguaHojeMl = Number(aguaLog[hojeIso] || 0)

  const refsLog = d.dos_refs_log || {}
  const refeicoesHoje = Array.isArray(refsLog[hojeIso]) ? refsLog[hojeIso] : []
  const refeicoesOntemLuna = Array.isArray(refsLog[ontemIso]) ? refsLog[ontemIso] : []
  const proteinaHojeG = refeicoesHoje.reduce((a, r) => a + (r.prot || 0), 0)
  const mapRefeicaoContexto = (r) => ({ tipo: r.tipo, nome: r.nome, hora: r.hora, proteina_g: typeof r.prot === 'number' ? r.prot : null, calorias: typeof r.cal === 'number' ? r.cal : null })
  const resumoAlimentacao7dias = Array.from({ length: 7 }, (_, i) => {
    const iso = dataIsoBR(-i)
    const refsDia = Array.isArray(refsLog[iso]) ? refsLog[iso] : []
    return { data: iso, agua_ml: Number(aguaLog[iso] || 0), proteina_g: refsDia.reduce((a, r) => a + (r.prot || 0), 0), refeicoes: refsDia.length }
  })

  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaDomiHoje = BUSCA_DOMI_POR_DIA[diaSemanaHoje] || null

  return {
    data_hoje: hojeIso,
    agua_hoje_ml: aguaHojeMl,
    meta_agua_ml: Number(d.dos_meta_agua_ml || 2500),
    proteina_hoje_g: proteinaHojeG,
    meta_proteina_g: Number(d.dos_meta_prot_g || 120),
    refeicoes_hoje: refeicoesHoje.map(mapRefeicaoContexto),
    refeicoes_ontem: refeicoesOntemLuna.map(mapRefeicaoContexto),
    resumo_alimentacao_7dias: resumoAlimentacao7dias,"""
s1 = replace_once(s1, old1, new1, "cronlib-context-alimentacao")
p1.write_text(s1)

# ============ api/whatsapp-webhook.js: Luna registra agua/proteina/refeicao ============
p2 = Path("api/whatsapp-webhook.js")
s2 = p2.read_text()

old2 = r"const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando/i"
new2 = r"const GATE_RE = /compr|adicion|mercado|lista|coloca|agenda|toda |todo |tirze|apliq|li \d|p[aá]gina|treino|malhei|caminhad|calistenia|mobilidade|devocional|reflex|reuni[aã]o|evento|marcar|consulta|status|conclu[ií]|andamento|aguardando|agua|bebi|tomei|comi|almo|jant|lanche|caf[eé]|refei[cç]|prote[ií]na|kcal|caloria/i"
s2 = replace_once(s2, old2, new2, "gate-re-alimentacao")

old3 = '''"devocional_resposta":"texto"|null}. Hoje e ' + hojeIso'''
new3 = '''"devocional_resposta":"texto"|null,"agua_ml":numero|null,"proteina_g_avulsa":numero|null,"refeicao":{"tipo":"Café da manhã|Lanche|Almoço|Lanche da tarde|Jantar|Ceia|Outro","descricao":"...","proteina_g":numero|null,"calorias":numero|null}|null}. Hoje e ' + hojeIso'''
s2 = replace_once(s2, old3, new3, "classprompt-json-alimentacao")

old4 = "coloque o texto completo da resposta dela em devocional_resposta. Se nada de uma categoria se aplicar, deixe vazio/null nela.'"
new4 = "coloque o texto completo da resposta dela em devocional_resposta. Se ela disser que bebeu ou tomou uma quantidade de agua, cha, suco ou agua com gas (ex: \\'tomei 300ml de agua\\', \\'bebi um copo dagua\\', \\'tomei uma garrafa\\'), converta para mililitros (copo comum ~200ml, garrafa comum ~500ml se ela nao especificar) e preencha agua_ml. Se ela mencionar uma quantidade de proteina avulsa sem descrever uma refeicao completa (ex: \\'tomei um shake de 20g de proteina\\', \\'bati um whey\\'), preencha proteina_g_avulsa. Se ela disser que comeu, almocou, jantou, lanchou ou tomou cafe da manha descrevendo o que comeu, preencha refeicao com o tipo mais proximo, a descricao do que ela comeu, e proteina_g/calorias somente se ela mencionar (senao null). Se nada de uma categoria se aplicar, deixe vazio/null nela.'"
s2 = replace_once(s2, old4, new4, "classprompt-regras-alimentacao")

old5 = """    const treinoRegistrado = parsed.treino_registrado && typeof parsed.treino_registrado.feito === 'boolean' ? parsed.treino_registrado : null
    const devocionalResposta = typeof parsed.devocional_resposta === 'string' && parsed.devocional_resposta.trim() ? parsed.devocional_resposta.trim() : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta) {
      return false
    }"""
new5 = """    const treinoRegistrado = parsed.treino_registrado && typeof parsed.treino_registrado.feito === 'boolean' ? parsed.treino_registrado : null
    const devocionalResposta = typeof parsed.devocional_resposta === 'string' && parsed.devocional_resposta.trim() ? parsed.devocional_resposta.trim() : null
    const aguaMlAdicionada = typeof parsed.agua_ml === 'number' && parsed.agua_ml > 0 && parsed.agua_ml <= 3000 ? Math.round(parsed.agua_ml) : null
    const proteinaAvulsaG = typeof parsed.proteina_g_avulsa === 'number' && parsed.proteina_g_avulsa > 0 && parsed.proteina_g_avulsa <= 300 ? Math.round(parsed.proteina_g_avulsa) : null
    const TIPOS_REFEICAO_VALIDOS = ['Café da manhã', 'Lanche', 'Almoço', 'Lanche da tarde', 'Jantar', 'Ceia', 'Outro']
    const refeicaoRegistrada = parsed.refeicao && typeof parsed.refeicao.descricao === 'string' && parsed.refeicao.descricao.trim() && TIPOS_REFEICAO_VALIDOS.includes(parsed.refeicao.tipo) ? parsed.refeicao : null

    if (feitosRotina.length === 0 && feitosCasa.length === 0 && feitosAvalDomi.length === 0 && feitosAvalDerick.length === 0 && novosCasa.length === 0 && novosCompromissos.length === 0 && novosEventosGoogle.length === 0 && !tirzepatidaAplicada && trabalhoStatus.length === 0 && !leituraRegistrada && !treinoRegistrado && !devocionalResposta && !aguaMlAdicionada && !proteinaAvulsaG && !refeicaoRegistrada) {
      return false
    }"""
s2 = replace_once(s2, old5, new5, "parsing-alimentacao")

old6 = """    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    await sendWhatsappText(number, partesConfirmacao.join('\\n'))
    return true"""
new6 = """    if (aguaMlAdicionada) {
      const aguaLogAtual = d.dos_agua_log || {}
      const aguaHojeAtualMl = Number(aguaLogAtual[hojeIso] || 0)
      const novaAguaMl = Math.min(aguaHojeAtualMl + aguaMlAdicionada, 6000)
      d.dos_agua_log = { ...aguaLogAtual, [hojeIso]: novaAguaMl }
      partesConfirmacao.push(`💧 Registrei +${aguaMlAdicionada}ml de água. Total hoje: ${novaAguaMl}ml.`)
    }

    if (proteinaAvulsaG || refeicaoRegistrada) {
      const horaAgoraHHMM = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/Sao_Paulo' }).format(new Date())
      const refsLogAtual = d.dos_refs_log || {}
      let refsHojeAtual = Array.isArray(refsLogAtual[hojeIso]) ? refsLogAtual[hojeIso] : []
      if (proteinaAvulsaG) {
        refsHojeAtual = [{ id: `${Date.now()}_wa1`, tipo: 'Rápido', nome: 'Proteína (registro rápido)', prot: proteinaAvulsaG, hora: horaAgoraHHMM, origem: 'whatsapp' }, ...refsHojeAtual]
        partesConfirmacao.push(`🥩 Registrei +${proteinaAvulsaG}g de proteína.`)
      }
      if (refeicaoRegistrada) {
        const novaRef = { id: `${Date.now()}_wa2`, tipo: refeicaoRegistrada.tipo, nome: refeicaoRegistrada.descricao, prot: typeof refeicaoRegistrada.proteina_g === 'number' ? refeicaoRegistrada.proteina_g : undefined, cal: typeof refeicaoRegistrada.calorias === 'number' ? refeicaoRegistrada.calorias : undefined, hora: horaAgoraHHMM, origem: 'whatsapp' }
        refsHojeAtual = [novaRef, ...refsHojeAtual]
        partesConfirmacao.push(`🍽️ Registrei: ${refeicaoRegistrada.descricao}${novaRef.prot ? ` (${novaRef.prot}g proteína)` : ''}.`)
      }
      d.dos_refs_log = { ...refsLogAtual, [hojeIso]: refsHojeAtual }
    }

    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    await sendWhatsappText(number, partesConfirmacao.join('\\n'))
    return true"""
s2 = replace_once(s2, old6, new6, "mutacao-alimentacao")
p2.write_text(s2)

# ============ src/main.tsx: sincronizarSnapshot tambem puxa agua/refeicoes que a Luna registrou pelo WhatsApp ============
p3 = Path("src/main.tsx")
s3 = p3.read_text()

old7 = """      try{
        const {data:snap}=await supabase.from('app_snapshot').select('data').eq('id','denise').maybeSingle()
        const remoto=snap?.data||{}
        const chaveHoje=`dos_rotina_done_${isoBR(new Date())}`
        if(Array.isArray(remoto[chaveHoje])){
          const uniao=Array.from(new Set([...(dados[chaveHoje]||[]),...remoto[chaveHoje]]))
          dados[chaveHoje]=uniao
          localStorage.setItem(chaveHoje,JSON.stringify(uniao))
        }
      }catch{}"""
new7 = """      try{
        const {data:snap}=await supabase.from('app_snapshot').select('data').eq('id','denise').maybeSingle()
        const remoto=snap?.data||{}
        const isoHojeSync=isoBR(new Date())
        const chaveHoje=`dos_rotina_done_${isoHojeSync}`
        if(Array.isArray(remoto[chaveHoje])){
          const uniao=Array.from(new Set([...(dados[chaveHoje]||[]),...remoto[chaveHoje]]))
          dados[chaveHoje]=uniao
          localStorage.setItem(chaveHoje,JSON.stringify(uniao))
        }
        const aguaRemotaHoje=(remoto.dos_agua_log||{})[isoHojeSync]
        if(typeof aguaRemotaHoje==='number'){
          const aguaLogLocal=dados.dos_agua_log||{}
          const aguaLocalHoje=Number(aguaLogLocal[isoHojeSync]||0)
          if(aguaRemotaHoje>aguaLocalHoje){
            const novoLogAgua={...aguaLogLocal,[isoHojeSync]:aguaRemotaHoje}
            dados.dos_agua_log=novoLogAgua
            localStorage.setItem('dos_agua_log',JSON.stringify(novoLogAgua))
          }
        }
        const refsRemotosHoje=(remoto.dos_refs_log||{})[isoHojeSync]
        if(Array.isArray(refsRemotosHoje)&&refsRemotosHoje.length>0){
          const refsLogLocal=dados.dos_refs_log||{}
          const refsLocaisHoje:any[]=refsLogLocal[isoHojeSync]||[]
          const idsLocais=new Set(refsLocaisHoje.map((r:any)=>r.id))
          const novosDoRemoto=refsRemotosHoje.filter((r:any)=>r&&r.id&&!idsLocais.has(r.id))
          if(novosDoRemoto.length>0){
            const unidos=[...novosDoRemoto,...refsLocaisHoje]
            const novoLogRefs={...refsLogLocal,[isoHojeSync]:unidos}
            dados.dos_refs_log=novoLogRefs
            localStorage.setItem('dos_refs_log',JSON.stringify(novoLogRefs))
          }
        }
      }catch{}"""
s3 = replace_once(s3, old7, new7, "sync-merge-alimentacao")
p3.write_text(s3)

print("TUDO OK:", applied)
