from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# A Luna ja calculava os itens pendentes de casa (contas) mas nunca falava sobre eles nas
# mensagens de manha/noite, e a cobranca a cada 30 min (cron-check) nao incluia os
# compromissos da Agenda. Este script fecha essas pontas:
#  - contexto passa a ter TODOS os itens pendentes da Casa (nao so contas), em casa_pendente
#  - bom dia e boa noite passam a falar de contas vencendo e itens pendentes de casa
#  - a cobranca a cada 30 min tambem avisa compromissos da Agenda de hoje na hora certa

cronlib_file = Path("api/_cronlib.js")
if not cronlib_file.exists():
    raise SystemExit("ABORTADO (cronlib-nao-encontrado): rode este script na raiz do projeto denise-os.")
c = cronlib_file.read_text()

old_c1 = """  const contasVencendo = casaItens.filter((i) => i.cat === 'Contas' && i.venc && !i.done && i.venc >= hojeIso && i.venc <= em7diasIso)"""
new_c1 = """  const contasVencendo = casaItens.filter((i) => i.cat === 'Contas' && i.venc && !i.done && i.venc >= hojeIso && i.venc <= em7diasIso)
  const casaPendenteGeral = casaItens.filter((i) => i.cat !== 'Contas' && !i.done)"""
c = replace_once(c, old_c1, new_c1, "cronlib-casa-pendente-calculo")

old_c2 = """    contas_vencendo_7dias: contasVencendo.map((c) => ({ nome: c.n, vencimento: c.venc })),"""
new_c2 = """    contas_vencendo_7dias: contasVencendo.map((c) => ({ nome: c.n, vencimento: c.venc })),
    casa_pendente: casaPendenteGeral.map((c) => ({ nome: c.n, categoria: c.cat })),"""
c = replace_once(c, old_c2, new_c2, "cronlib-casa-pendente-no-contexto")
cronlib_file.write_text(c)

morning_file = Path("api/cron-morning.js")
if not morning_file.exists():
    raise SystemExit("ABORTADO (cron-morning-nao-encontrado): rode este script na raiz do projeto denise-os.")
m = morning_file.read_text()
old_m = """tirzepatida se for hoje o dia de aplicar; medicamentos em curso hoje (considere em curso QUALQUER medicamento que tenha \\'horarios\\' preenchido, independente de \\'dias_desde_registro\\' - a Denise ja remove o medicamento da lista quando o tratamento termina, entao se ele ainda esta na lista com horarios preenchido, esta em curso); e tarefas de trabalho pendentes se houver."""
new_m = """tirzepatida se for hoje o dia de aplicar; medicamentos em curso hoje (considere em curso QUALQUER medicamento que tenha \\'horarios\\' preenchido, independente de \\'dias_desde_registro\\' - a Denise ja remove o medicamento da lista quando o tratamento termina, entao se ele ainda esta na lista com horarios preenchido, esta em curso); tarefas de trabalho pendentes se houver; contas perto do vencimento (contas_vencendo_7dias); e itens pendentes de casa (casa_pendente - compras, tarefas domesticas, manutencao), agrupados por categoria se houver mais de um."""
m = replace_once(m, old_m, new_m, "cron-morning-casa-contas")
morning_file.write_text(m)

evening_file = Path("api/cron-evening.js")
if not evening_file.exists():
    raise SystemExit("ABORTADO (cron-evening-nao-encontrado): rode este script na raiz do projeto denise-os.")
e = evening_file.read_text()
old_e = """e o que fica pendente para amanhã (itens da agenda de amanhã, itens da rotina de hoje que não foram feitos)."""
new_e = """e o que fica pendente para amanhã (compromissos da agenda de amanhã em agenda_proximos_7dias, itens da rotina de hoje que não foram feitos, contas perto do vencimento em contas_vencendo_7dias, e itens pendentes de casa em casa_pendente)."""
e = replace_once(e, old_e, new_e, "cron-evening-casa-contas")
evening_file.write_text(e)

check_file = Path("api/cron-check.js")
if not check_file.exists():
    raise SystemExit("ABORTADO (cron-check-nao-encontrado): rode este script na raiz do projeto denise-os. (precisa rodar antes o script que criou essa rota)")
k = check_file.read_text()
old_k1 = """    const medicamentos = d.dos_medicamentos || {}"""
new_k1 = """    const medicamentos = d.dos_medicamentos || {}
    const agenda = Array.isArray(d.dos_agenda) ? d.dos_agenda : []"""
k = replace_once(k, old_k1, new_k1, "cron-check-agenda-le")

old_k2 = """    if (avisos.length === 0) {"""
new_k2 = """    agenda.forEach((ev) => {
      if (ev.data !== hojeIso) return
      if (estaNaJanela(ev.hora)) avisos.push(`📅 ${ev.hora} · ${ev.nome}`)
    })

    if (avisos.length === 0) {"""
k = replace_once(k, old_k2, new_k2, "cron-check-agenda-avisa")
check_file.write_text(k)

print("OK:")
print(" - Bom dia e boa noite agora falam de contas perto do vencimento e itens pendentes")
print("   da Casa (compras, tarefas domesticas, manutencao).")
print(" - A cobranca a cada 30 min tambem avisa os compromissos da Agenda de hoje na hora certa.")
