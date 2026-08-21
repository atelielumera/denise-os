from pathlib import Path

p = Path("src/main.tsx")
s = p.read_text()
applied = []

def replace_once(s, old, new, label):
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {c}. Nada foi alterado.")
    applied.append(label)
    return s.replace(old, new, 1)

# Luna passa a ficar logo depois de Casa, antes de Relatorios
old = "['/casa','Casa','🏡'],['/relatorios','Relatórios','📊'],['/assistente','Luna','🌙'],"
new = "['/casa','Casa','🏡'],['/assistente','Luna','🌙'],['/relatorios','Relatórios','📊'],"
s = replace_once(s, old, new, "luna-antes-de-relatorios")

p.write_text(s)
print("TUDO OK:", applied)
