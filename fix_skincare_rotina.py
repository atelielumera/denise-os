from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

# Adiciona o skincare de verdade (produtos exatos que a Denise mandou) na Minha Rotina.
# Mesmo padrao seguro dos chas/Domi: so adiciona se ainda nao existir item com esse nome
# exato, entao nunca duplica rodando de novo.
#
# Manha e igual todo santo dia. A noite muda o "extra" dependendo do dia da semana -
# em vez de criar 3 itens que apareceriam todos os dias juntos (confuso, risco dela usar
# o produto de tratamento no dia errado), ficou 1 item so de noite que already deixa
# escrito qual dia usa qual extra.

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old_chas = """    const chas:RItem[]=[
      {t:'06:00',n:'Chá verde + gengibre + canela',cat:'Alimentação'},
      {t:'12:00',n:'Chá hortelã + erva-doce (digestivo)',cat:'Alimentação'},
      {t:'15:00',n:'Chá hibisco + cavalinha',cat:'Alimentação'},
      {t:'20:30',n:'Chá camomila + melissa',cat:'Alimentação'},
      {t:'11:25',n:'Buscar Domi (sair 15 min antes) — Seg/Qua 12:50 · Ter/Qui 11:40 · Sex 13:00',cat:'Família'},
    ]"""
new_chas = """    const chas:RItem[]=[
      {t:'06:00',n:'Chá verde + gengibre + canela',cat:'Alimentação'},
      {t:'12:00',n:'Chá hortelã + erva-doce (digestivo)',cat:'Alimentação'},
      {t:'15:00',n:'Chá hibisco + cavalinha',cat:'Alimentação'},
      {t:'20:30',n:'Chá camomila + melissa',cat:'Alimentação'},
      {t:'11:25',n:'Buscar Domi (sair 15 min antes) — Seg/Qua 12:50 · Ter/Qui 11:40 · Sex 13:00',cat:'Família'},
      {t:'08:00',n:'Skincare manhã: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Filtro Solar La Roche-Posay, Cicaplast',cat:'Saúde'},
      {t:'21:00',n:'Skincare noite: Água Micelar Effaclar, Gel Effaclar, Ácido Hialurônico, Cicaplast + extra do dia — Seg/Qua/Sex: Vitacid · Ter/Qui/Sáb: Effaclar Duo+M · Domingo: sem extra',cat:'Saúde'},
    ]"""
s = replace_once(s, old_chas, new_chas, "rotina-seed-skincare")
main_file.write_text(s)

print("OK - 2 itens novos adicionados na Minha Rotina (bloco Manhã as 08:00 e bloco Noite as 21:00):")
print(" - Skincare manha: Agua Micelar Effaclar, Gel Effaclar, Acido Hialuronico, Filtro Solar La Roche-Posay, Cicaplast")
print(" - Skincare noite: Agua Micelar Effaclar, Gel Effaclar, Acido Hialuronico, Cicaplast")
print("   + extra do dia escrito no proprio item: Seg/Qua/Sex usa Vitacid, Ter/Qui/Sab usa Effaclar Duo+M,")
print("   Domingo nao usa produto extra.")
print("Nao duplica se voce ja tiver item com esse nome exato.")
