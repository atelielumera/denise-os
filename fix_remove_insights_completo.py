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

# 1) Remove "Insights" da barra lateral (o conceito agora vive dentro da aba Insights da Luna)
old1 = "['/casa','Casa','🏡'],['/insights','Insights','💡'],['/relatorios','Relatórios','📊'],"
new1 = "['/casa','Casa','🏡'],['/relatorios','Relatórios','📊'],"
s = replace_once(s, old1, new1, "remove-navitem-insights")

# 2) Rota /insights passa a redirecionar para a Luna (nao quebra links salvos, sem tela separada)
old2 = '<Route path="insights" element={<Insights/>}/>'
new2 = '<Route path="insights" element={<Navigate to="/assistente" replace/>}/>'
s = replace_once(s, old2, new2, "route-insights-redirect")

# 3) Remove a funcao Insights() inteira (ficou orfa: nada mais a renderiza, o motor novo
#    ja mora dentro de Assistente()/gerarInsightsLuna). Localiza pelos marcadores em vez de
#    copiar o bloco na mao, pra nao arriscar erro de transcricao num bloco de ~70 linhas.
start_marker = "function Insights(){"
end_marker = "\nfunction Relatorios(){"
n_start = s.count(start_marker)
if n_start != 1:
    raise SystemExit(f"ABORTADO (remove-funcao-insights): esperava 1 ocorrencia de '{start_marker}', encontrei {n_start}.")
i = s.index(start_marker)
j = s.index(end_marker, i)
if j == -1:
    raise SystemExit("ABORTADO (remove-funcao-insights): nao encontrei o fim do bloco (function Relatorios(){ apos Insights).")
removido = s[i:j]
s = s[:i] + s[j+1:]  # +1 pula soh o \n inicial do end_marker, mantendo 'function Relatorios(){' intacto
applied.append(f"remove-funcao-insights ({len(removido)} chars)")

p.write_text(s)
print("TUDO OK:", applied)
