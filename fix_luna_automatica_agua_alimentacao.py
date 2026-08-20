from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# 1) NAO depende mais de voce criar conta em site nenhum (cron-job.org fica de lado). Crio
#    um workflow do GitHub Actions no seu proprio repositorio que dispara os avisos da Luna
#    sozinho, nos horarios certos, sem voce precisar fazer nada depois de rodar este script
#    e dar o push de sempre.
# 2) Lembrete de agua a cada 30 min (7h-22h) considerando que chimarrao, suco e agua com gas
#    tambem contam - a mensagem deixa isso claro.
# 3) Rotina ganha os 2 itens que faltavam do seu checklist (proteina leve as 8:30 e o almoco
#    completo ao meio-dia com as vitaminas).

api_dir = Path("api")
if not api_dir.is_dir():
    raise SystemExit("ABORTADO (pasta-api-nao-encontrada): rode este script na raiz do projeto denise-os.")

check_file = api_dir / "cron-check.js"
if not check_file.exists():
    raise SystemExit("ABORTADO (cron-check-nao-encontrado): precisa ja ter rodado o script que criou essa rota antes.")
k = check_file.read_text()
old_k = """    agenda.forEach((ev) => {
      if (ev.data !== hojeIso) return
      if (estaNaJanela(ev.hora)) avisos.push(`📅 ${ev.hora} · ${ev.nome}`)
    })

    if (avisos.length === 0) {"""
new_k = """    agenda.forEach((ev) => {
      if (ev.data !== hojeIso) return
      if (estaNaJanela(ev.hora)) avisos.push(`📅 ${ev.hora} · ${ev.nome}`)
    })

    const META_AGUA_ML = 2500
    const aguaLog = d.dos_agua_log || {}
    const aguaHojeMl = Number(aguaLog[hojeIso] || 0)
    const horaAgora = Math.floor(agoraMin / 60)
    const minutoDentroHora = agoraMin % 60
    if (aguaHojeMl < META_AGUA_ML && horaAgora >= 7 && horaAgora <= 22 && minutoDentroHora < JANELA_MIN) {
      avisos.push(`💧 Hidratação — ${aguaHojeMl} ml de ${META_AGUA_ML} ml hoje (água, chimarrão, suco, água com gás contam)`)
    }

    if (avisos.length === 0) {"""
k = replace_once(k, old_k, new_k, "cron-check-agua")
check_file.write_text(k)

WORKFLOW = """name: Luna - avisos automaticos

on:
  schedule:
    - cron: '0 9 * * *'
    - cron: '0 23 * * *'
    - cron: '5 23 * * 5'
    - cron: '10 23 * * 0'
    - cron: '*/30 * * * *'
  workflow_dispatch:

jobs:
  chamar-rota:
    runs-on: ubuntu-latest
    steps:
      - name: Chama a rota certa da Luna
        run: |
          case "${{ github.event.schedule }}" in
            "0 9 * * *") ROTA="cron-morning" ;;
            "0 23 * * *") ROTA="cron-evening" ;;
            "5 23 * * 5") ROTA="cron-weekly" ;;
            "10 23 * * 0") ROTA="cron-nextweek" ;;
            *) ROTA="cron-check" ;;
          esac
          echo "Chamando /api/$ROTA"
          curl -sS -X POST "https://denise-os.vercel.app/api/$ROTA"
"""
workflows_dir = Path(".github/workflows")
workflows_dir.mkdir(parents=True, exist_ok=True)
(workflows_dir / "luna-cron.yml").write_text(WORKFLOW)

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()
old_s = """      {t:'21:00',n:'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Cicaplast',cat:'Saúde',dias:[0]},
    ]"""
new_s = """      {t:'21:00',n:'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Cicaplast',cat:'Saúde',dias:[0]},
      {t:'08:30',n:'Proteína leve: 2 ovos ou iogurte natural',cat:'Alimentação'},
      {t:'12:00',n:'Almoço: proteína (frango/carne/peixe) + legumes + fio de azeite + vitaminas A/D/E/K',cat:'Alimentação'},
    ]"""
s = replace_once(s, old_s, new_s, "rotina-checklist-novos-itens")
main_file.write_text(s)

print("OK:")
print(" 1) Criado .github/workflows/luna-cron.yml - a partir do proximo push, o GitHub")
print("    dispara sozinho os avisos da Luna (bom dia, boa noite, semanal, proxima semana,")
print("    e a cobranca a cada 30 min) - sem precisar de conta em nenhum site externo.")
print(" 2) Cobranca a cada 30 min agora lembra de se hidratar (7h-22h), considerando que")
print("    chimarrao, suco e agua com gas tambem contam pra meta.")
print(" 3) Minha Rotina ganhou 2 itens novos do seu checklist: proteina leve as 8:30 e o")
print("    almoco completo (proteina+legumes+azeite+vitaminas) ao meio-dia.")
print("")
print("Os cha's das 6h/12h/15h/20h30 do outro print ja estavam certinhos, nao mexi neles.")
print("Os itens de lanche/cha do checklist (10:30, 13:30, 15:00, 16:00, 17h-18h) tem")
print("horarios diferentes dos que ja estao cadastrados pros mesmos chas/lanches - nao")
print("duplicei pra nao confundir. Se os horarios do checklist forem os certos, e so tocar")
print("no lapis do item existente na Minha Rotina e trocar o horario.")
