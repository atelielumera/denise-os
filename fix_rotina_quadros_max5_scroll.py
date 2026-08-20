from pathlib import Path

def replace_once_n(s, old, new, label, esperado):
    n = s.count(old)
    if n != esperado:
        raise SystemExit(f"ABORTADO ({label}): esperava {esperado} ocorrencia(s), encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# Os quadros da Minha Rotina (por tema, Tirzepatida, Domi, Derick) agora tem altura maxima
# de +- 5 itens visiveis, com rolagem pro resto - pra nao ficarem gigantes na tela.

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old = "            <div>\n"
new = "            <div style={{maxHeight:225,overflowY:'auto' as const}}>\n"
s = replace_once_n(s, old, new, "rotina-quadros-max5-scroll", 3)

main_file.write_text(s)
print("OK - Os quadros da Minha Rotina (tema, Tirzepatida, Domi, Derick) agora mostram no")
print("maximo uns 5 itens de uma vez, com barra de rolagem pro resto.")
