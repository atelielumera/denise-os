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

replace_once(
    'vercel.json',
    """{
  "rewrites": [{ "source": "/((?!api/).*)", "destination": "/" }],
  "crons": [
    { "path": "/api/cron-morning", "schedule": "30 8 * * *" },
    { "path": "/api/cron-morning", "schedule": "0 9 * * *" },
    { "path": "/api/cron-evening", "schedule": "0 23 * * *" },
    { "path": "/api/cron-weekly", "schedule": "5 23 * * 5" },
    { "path": "/api/cron-nextweek", "schedule": "10 23 * * 0" }
  ]
}""",
    """{
  "rewrites": [{ "source": "/((?!api/).*)", "destination": "/" }],
  "crons": [
    { "path": "/api/cron-morning", "schedule": "30 8 * * *" },
    { "path": "/api/cron-morning", "schedule": "0 9 * * *" },
    { "path": "/api/cron-check", "schedule": "*/15 * * * *" },
    { "path": "/api/cron-evening", "schedule": "0 23 * * *" },
    { "path": "/api/cron-weekly", "schedule": "5 23 * * 5" },
    { "path": "/api/cron-nextweek", "schedule": "10 23 * * 0" }
  ]
}""",
    'vercel-registra-cron-check'
)

print('TUDO OK:', feitos)
