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

# 1) Treino "feito" registrado pela Luna via WhatsApp tambem nao tinha id
# (mesma causa raiz dos itens de mercado/trabalho ja corrigidos).
replace_once(
    'api/whatsapp-webhook.js',
    """      if (treinoRegistrado.feito) {
        const treinosAtuais = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
        d.dos_treinos = [{ data: hojeIso, tipo: 'Registrado via WhatsApp', duracaoMin: 0 }, ...treinosAtuais]
        partesConfirmacao.push('✅ Treino de hoje registrado como feito!')""",
    """      if (treinoRegistrado.feito) {
        const treinosAtuais = Array.isArray(d.dos_treinos) ? d.dos_treinos : []
        d.dos_treinos = [{ id: `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`, data: hojeIso, tipo: 'Registrado via WhatsApp', duracaoMin: 0 }, ...treinosAtuais]
        partesConfirmacao.push('✅ Treino de hoje registrado como feito!')""",
    'webhook-treino-feito-com-id'
)

# 2) Junta treinos novos do servidor (por id) na sincronizacao do app - ancora
# num unico ponto pra funcionar independente da ordem em que voce roda os scripts.
replace_once(
    'src/main.tsx',
    "        mesclarArrayPorId('dos_agenda')",
    "        mesclarArrayPorId('dos_agenda')\n        mesclarArrayPorId('dos_treinos')",
    'sincronizarsnapshot-mescla-treinos'
)

# 3) "Nao fiz o treino" so grava uma marcacao (dos_treino_registrado_<hoje>=true)
# pra Luna nao ficar cobrando de novo no mesmo dia - mas essa marcacao nao tinha
# nenhuma protecao contra ser apagada na sincronizacao automatica do app. Agora,
# se o servidor tiver essa marcacao de hoje e o navegador ainda nao souber dela,
# ela e preservada em vez de sumir.
replace_once(
    'src/main.tsx',
    """        const chaveHoje=`dos_rotina_done_${isoHojeSync}`
        if(Array.isArray(remoto[chaveHoje])){
          const uniao=Array.from(new Set([...(dados[chaveHoje]||[]),...remoto[chaveHoje]]))
          dados[chaveHoje]=uniao
          localStorage.setItem(chaveHoje,JSON.stringify(uniao))
        }""",
    """        const chaveHoje=`dos_rotina_done_${isoHojeSync}`
        if(Array.isArray(remoto[chaveHoje])){
          const uniao=Array.from(new Set([...(dados[chaveHoje]||[]),...remoto[chaveHoje]]))
          dados[chaveHoje]=uniao
          localStorage.setItem(chaveHoje,JSON.stringify(uniao))
        }
        const chaveTreinoHoje=`dos_treino_registrado_${isoHojeSync}`
        if(remoto[chaveTreinoHoje]===true&&!dados[chaveTreinoHoje]){
          dados[chaveTreinoHoje]=true
          localStorage.setItem(chaveTreinoHoje,'true')
        }""",
    'sincronizarsnapshot-preserva-flag-treino-registrado'
)

print('TUDO OK:', feitos)
