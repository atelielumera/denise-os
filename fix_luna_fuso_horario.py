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

# Bug: a Luna calculava a hora dos eventos do Google Calendar em UTC (toISOString),
# enquanto a pagina Agenda usa a hora local do navegador (getHours/getMinutes).
# Resultado: Luna informava horarios 3h a frente do real (ex: 17h virava 20h).
old = "...agendaGoogle.map((ev:any)=>({data:(ev.start?.dateTime||ev.start?.date||'').slice(0,10),hora:ev.start?.dateTime?new Date(ev.start.dateTime).toISOString().slice(11,16):'',titulo:ev.summary||'(sem titulo)',origem:'google_calendar'})),"
new = "...agendaGoogle.map((ev:any)=>{const dtEv=ev.start?.dateTime?new Date(ev.start.dateTime):null;return{data:(ev.start?.dateTime||ev.start?.date||'').slice(0,10),hora:dtEv?`${String(dtEv.getHours()).padStart(2,'0')}:${String(dtEv.getMinutes()).padStart(2,'0')}`:'',titulo:ev.summary||'(sem titulo)',origem:'google_calendar'}}),"
s = replace_once(s, old, new, "luna-fuso-horario-google-events")

main_file.write_text(s)
print("OK - Luna agora calcula o horario dos eventos do Google Calendar em horario local (igual a pagina Agenda),")
print("em vez de UTC. Antes ela informava horarios 3h a frente do real (ex: 17h virava 20h).")
