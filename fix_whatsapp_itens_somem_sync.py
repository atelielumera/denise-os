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

# 1) Itens de mercado criados pela Luna via WhatsApp nao tinham "id" - a funcao
# que junta o que e novo do servidor com o que esta no navegador (mesclarArrayPorId,
# em src/main.tsx) so consegue reconhecer itens que tem id. Sem id, o item nunca
# era juntado e acabava apagado na proxima sincronizacao automatica (a cada 30s).
replace_once(
    'api/whatsapp-webhook.js',
    """    if (novosCasa.length > 0) {
      const adicionados = novosCasa.map((n) => ({ n: n.nome, cat: CASA_CATS_VALIDAS.includes(n.categoria) ? n.categoria : 'Mercado', done: false }))
      casaAtualizada = [...casaAtualizada, ...adicionados]
      partesConfirmacao.push('🛒 Adicionei na Casa: ' + adicionados.map((a) => a.n).join(', '))
    }""",
    """    if (novosCasa.length > 0) {
      const adicionados = novosCasa.map((n) => ({ id: `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`, n: n.nome, cat: CASA_CATS_VALIDAS.includes(n.categoria) ? n.categoria : 'Mercado', done: false }))
      casaAtualizada = [...casaAtualizada, ...adicionados]
      partesConfirmacao.push('🛒 Adicionei na Casa: ' + adicionados.map((a) => a.n).join(', '))
    }""",
    'webhook-novoscasa-com-id'
)

# 2) Mesma causa raiz para tarefas de trabalho criadas pela Luna via WhatsApp.
replace_once(
    'api/whatsapp-webhook.js',
    """    if (novosTrabalho.length > 0) {
      const trabalhoAtual = Array.isArray(d.dos_trabalho) ? d.dos_trabalho : trabalhoTarefas
      const adicionadosTrabalho = novosTrabalho.map((n) => ({ t: n.tarefa, p: TRABALHO_PROJETOS_VALIDOS.includes(n.projeto) ? n.projeto : 'Outros', s: 'pendente' }))
      d.dos_trabalho = [...trabalhoAtual, ...adicionadosTrabalho]
      partesConfirmacao.push('💼 Adicionei nas tarefas de trabalho: ' + adicionadosTrabalho.map((a) => a.t).join(', '))
    }""",
    """    if (novosTrabalho.length > 0) {
      const trabalhoAtual = Array.isArray(d.dos_trabalho) ? d.dos_trabalho : trabalhoTarefas
      const adicionadosTrabalho = novosTrabalho.map((n) => ({ id: `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`, t: n.tarefa, p: TRABALHO_PROJETOS_VALIDOS.includes(n.projeto) ? n.projeto : 'Outros', s: 'pendente' }))
      d.dos_trabalho = [...trabalhoAtual, ...adicionadosTrabalho]
      partesConfirmacao.push('💼 Adicionei nas tarefas de trabalho: ' + adicionadosTrabalho.map((a) => a.t).join(', '))
    }""",
    'webhook-novostrabalho-com-id'
)

# 3) dos_trabalho nunca entrava na lista de "juntar o que e novo do servidor" da
# sincronizacao automatica do app (sincronizarSnapshot, roda a cada 30s) - so
# dos_casa_items, dos_pedidos_oracao e dos_agenda entravam. Por isso qualquer
# tarefa de trabalho nova vinda de fora do navegador (WhatsApp) era sempre
# sobrescrita pela copia local antiga, mesmo depois do fix acima dar um id a ela.
replace_once(
    'src/main.tsx',
    """        mesclarArrayPorId('dos_casa_items')
        mesclarArrayPorId('dos_pedidos_oracao')
        mesclarArrayPorId('dos_agenda')""",
    """        mesclarArrayPorId('dos_casa_items')
        mesclarArrayPorId('dos_pedidos_oracao')
        mesclarArrayPorId('dos_agenda')
        mesclarArrayPorId('dos_trabalho')""",
    'sincronizarsnapshot-mescla-trabalho'
)

print('TUDO OK:', feitos)
