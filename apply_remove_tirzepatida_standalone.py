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

# 1. Remove "Tirzepatida" do menu lateral — a funcionalidade já vive dentro de Saúde.
old1 = "['/exercicios','Exercícios','💪'],['/tirzepatida','Tirzepatida','💉'],['/familia','Família','👨‍👩‍👧']"
new1 = "['/exercicios','Exercícios','💪'],['/familia','Família','👨‍👩‍👧']"
s = replace_once(s, old1, new1, "remove-navitem-tirzepatida")

# 2. A rota /tirzepatida agora só redireciona pra /saude (links antigos não quebram).
old2 = '<Route path="tirzepatida" element={<TirzepatidaPage/>}/>'
new2 = '<Route path="tirzepatida" element={<Navigate to="/saude" replace/>}/>'
s = replace_once(s, old2, new2, "route-tirzepatida-redirect")

# 3. Remove a função TirzepatidaPage inteira (página separada) — tudo que ela fazia
#    (registrar aplicação, estornar, adicionar/ajustar estoque, editar protocolo,
#    histórico) já existe no card fundido renderTirzepatidaCard(), usado dentro de
#    Saúde > Denise/Flávio. Nada foi perdido, só duplicado.
start_marker = "function TirzepatidaPage(){"
end_marker = "\nfunction Familia(){"
start = s.index(start_marker)
end = s.index(end_marker, start)
if start == -1 or end == -1:
    raise SystemExit("ABORTADO (remove-tirzepatidapage): marcadores não encontrados.")
removed_len = end - start
s = s[:start] + s[end + 1:]
applied.append(f"remove-tirzepatidapage ({removed_len} chars)")

# 4. Os links "Gerenciar"/"Registrar" que apontavam pra /tirzepatida (cards da Home)
#    agora apontam pra /saude, onde o card de Tirzepatida vive.
count_navlinks = s.count('to="/tirzepatida"')
if count_navlinks != 5:
    raise SystemExit(f"ABORTADO (navlinks-para-saude): esperava 5 ocorrencias de to=\"/tirzepatida\", encontrei {count_navlinks}.")
s = s.replace('to="/tirzepatida"', 'to="/saude"')
applied.append(f"navlinks-para-saude (x{count_navlinks})")

p.write_text(s)
print("TUDO OK:", applied)
