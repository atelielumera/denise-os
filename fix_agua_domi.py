from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# ---------------------------------------------------------------------------
# Parte 1: agua + medicamento no contexto da Luna (esse fix tinha sido escrito
# antes mas nunca chegou a ser rodado com sucesso - o _cronlib.js ainda estava
# sem nenhum dado de agua). Aproveitando pra tambem colocar o horario de
# buscar a Domi, que muda por dia da semana.
# ---------------------------------------------------------------------------

cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (_cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_ctx = """  const contasVencendo = casaItens.filter((i) => i.cat === 'Contas' && i.venc && !i.done && i.venc >= hojeIso && i.venc <= em7diasIso)

  return {
    data_hoje: hojeIso,"""
new_ctx = """  const contasVencendo = casaItens.filter((i) => i.cat === 'Contas' && i.venc && !i.done && i.venc >= hojeIso && i.venc <= em7diasIso)

  const aguaLog = d.dos_agua_log || {}
  const aguaHojeMl = Number(aguaLog[hojeIso] || 0)

  const BUSCA_DOMI_POR_DIA = { 1: { busca: '12:50', sair: '12:35' }, 2: { busca: '11:40', sair: '11:25' }, 3: { busca: '12:50', sair: '12:35' }, 4: { busca: '11:40', sair: '11:25' }, 5: { busca: '13:00', sair: '12:45' } }
  const diaSemanaHoje = new Date(hojeIso + 'T12:00:00-03:00').getDay()
  const buscaDomiHoje = BUSCA_DOMI_POR_DIA[diaSemanaHoje] || null

  return {
    data_hoje: hojeIso,
    agua_hoje_ml: aguaHojeMl,
    meta_agua_ml: 2500,
    busca_domi_hoje: buscaDomiHoje,"""
c = replace_once(c, old_ctx, new_ctx, "cronlib-contexto-agua-domi")
cronlib_file.write_text(c)

# --- cron-morning.js: agua + busca da Domi (horario certo por dia da semana) + medicamento mais confiavel ---
morning_file = Path("api/cron-morning.js")
if not morning_file.exists():
    raise SystemExit("ABORTADO (cron-morning-nao-encontrado): rode este script na raiz do projeto denise-os.")
m = morning_file.read_text()

old_pedido = "const pedido = 'Escreva a mensagem de bom dia da Denise. Comece com \"Bom dia, Denise! ☀️\" e liste, de forma organizada e curta, tudo que ela tem para fazer hoje: itens da rotina de hoje ainda não feitos, compromissos da agenda de hoje, tirzepatida se for hoje o dia de aplicar, medicamentos em curso hoje (considere em curso qualquer medicamento com \\'horarios\\' preenchido cujo \\'dias_desde_registro\\' seja 10 ou menos, mesmo que a data de registro nao seja hoje), e tarefas de trabalho pendentes se houver. Se uma dessas categorias estiver vazia ou sem dado, não mencione ela (não diga \"nada registrado\"). Termine com uma frase curta de incentivo. Formato de WhatsApp, use emojis com moderação, sem markdown de negrito.'"
new_pedido = "const pedido = 'Escreva a mensagem de bom dia da Denise. Comece com \"Bom dia, Denise! ☀️\" e liste, de forma organizada e curta, tudo que ela tem para fazer hoje: um lembrete de beber água ao longo do dia citando a meta_agua_ml em litros; se busca_domi_hoje existir no contexto (em dias de semana), lembre que ela precisa sair de casa no horário \\'sair\\' de busca_domi_hoje para buscar a Domi, que sai da escola às \\'busca\\' (15 minutos depois do horário de sair); itens da rotina de hoje ainda não feitos; compromissos da agenda de hoje; tirzepatida se for hoje o dia de aplicar; medicamentos em curso hoje (considere em curso QUALQUER medicamento que tenha \\'horarios\\' preenchido, independente de \\'dias_desde_registro\\' - a Denise ja remove o medicamento da lista quando o tratamento termina, entao se ele ainda esta na lista com horarios preenchido, esta em curso); e tarefas de trabalho pendentes se houver. Se uma dessas categorias estiver vazia ou sem dado (por exemplo busca_domi_hoje nulo no fim de semana), não mencione ela (não diga \"nada registrado\"). Termine com uma frase curta de incentivo. Formato de WhatsApp, use emojis com moderação, sem markdown de negrito.'"
m = replace_once(m, old_pedido, new_pedido, "cron-morning-pedido-agua-domi-medicamentos")
morning_file.write_text(m)

# --- cron-evening.js: status de agua do dia ---
evening_file = Path("api/cron-evening.js")
if not evening_file.exists():
    raise SystemExit("ABORTADO (cron-evening-nao-encontrado): rode este script na raiz do projeto denise-os.")
e = evening_file.read_text()

old_pedido_e = "const pedido = 'Escreva a mensagem de encerramento do dia da Denise. Comece com \"Boa noite, Denise 🌙\" e mostre: o que foi feito hoje (itens da rotina marcados como feito hoje, treino/leitura/devocional se houver registro de hoje), e o que fica pendente para amanhã (itens da agenda de amanhã, itens da rotina de hoje que não foram feitos). Se uma categoria estiver vazia, não mencione ela. Termine com uma frase curta e acolhedora. Formato de WhatsApp, emojis com moderação, sem markdown de negrito.'"
new_pedido_e = "const pedido = 'Escreva a mensagem de encerramento do dia da Denise. Comece com \"Boa noite, Denise 🌙\" e mostre: quanto de água ela bebeu hoje (agua_hoje_ml) comparado à meta (meta_agua_ml) - elogie se bateu a meta, lembre com carinho se ainda não bateu -, o que foi feito hoje (itens da rotina marcados como feito hoje, treino/leitura/devocional se houver registro de hoje), e o que fica pendente para amanhã (itens da agenda de amanhã, itens da rotina de hoje que não foram feitos). Se uma categoria estiver vazia, não mencione ela. Termine com uma frase curta e acolhedora. Formato de WhatsApp, emojis com moderação, sem markdown de negrito.'"
e = replace_once(e, old_pedido_e, new_pedido_e, "cron-evening-pedido-agua")
evening_file.write_text(e)

# ---------------------------------------------------------------------------
# Parte 2: Minha Rotina - adicionar um item explicando os 3 horarios de buscar
# a Domi (some pro bloco da manha, ja que o horario mais cedo e 11:25). So
# adiciona se ainda nao existir um item com esse nome exato (nunca duplica).
# ---------------------------------------------------------------------------

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_chas = """    const chas:RItem[]=[
      {t:'06:00',n:'Chá verde + gengibre + canela',cat:'Alimentação'},
      {t:'12:00',n:'Chá hortelã + erva-doce (digestivo)',cat:'Alimentação'},
      {t:'15:00',n:'Chá hibisco + cavalinha',cat:'Alimentação'},
      {t:'20:30',n:'Chá camomila + melissa',cat:'Alimentação'},
    ]"""
new_chas = """    const chas:RItem[]=[
      {t:'06:00',n:'Chá verde + gengibre + canela',cat:'Alimentação'},
      {t:'12:00',n:'Chá hortelã + erva-doce (digestivo)',cat:'Alimentação'},
      {t:'15:00',n:'Chá hibisco + cavalinha',cat:'Alimentação'},
      {t:'20:30',n:'Chá camomila + melissa',cat:'Alimentação'},
      {t:'11:25',n:'Buscar Domi (sair 15 min antes) — Seg/Qua 12:50 · Ter/Qui 11:40 · Sex 13:00',cat:'Família'},
    ]"""
s = replace_once(s, old_chas, new_chas, "rotina-seed-busca-domi")
main_file.write_text(s)

print("OK - alteracoes aplicadas:")
print(" - api/_cronlib.js: contexto da Luna agora inclui agua_hoje_ml, meta_agua_ml e busca_domi_hoje")
print("   (com o horario certo de sair/buscar a Domi calculado automaticamente pelo dia da semana).")
print(" - api/cron-morning.js: mensagem das 6h agora sempre lembra de beber agua, e nos dias certos")
print("   lembra do horario de sair pra buscar a Domi (15 min antes do horario dela sair da escola).")
print(" - api/cron-evening.js: mensagem das 20h agora conta quanto de agua foi bebido no dia vs a meta.")
print(" - Minha Rotina: adicionado 1 item novo (as 11:25, bloco da manha) com os 3 horarios certos de")
print("   buscar a Domi (Seg/Qua 12:50, Ter/Qui 11:40, Sex 13:00), sem duplicar se ja existir.")
print("")
print("IMPORTANTE: depois do deploy, abre 'Minha Rotina' e apaga (no X) o item antigo 'Buscar Domi'")
print("com um so horario (12:50) - ele fica desatualizado agora que tem o item novo com os 3 dias certos.")
print("")
print("ATENCAO - limite tecnico: a Luna manda mensagem no WhatsApp so 2x por dia (6h e 20h), por causa")
print("do plano do Vercel. Isso significa que ela vai te AVISAR de manha (6h) o horario certo de buscar")
print("a Domi naquele dia, mas NAO consegue mandar um alerta exatamente 15 min antes do horario real")
print("(ex: as 11:25 numa terca) - pra isso funcionar em tempo real seria preciso o plano pago do Vercel.")
