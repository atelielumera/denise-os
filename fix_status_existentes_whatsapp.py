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

# 1) Leitura registrada pela Luna via WhatsApp tambem nao tinha id (mesma causa
# raiz de tudo que ja foi corrigido hoje).
replace_once(
    'api/whatsapp-webhook.js',
    """      const reg = { data: hojeIso, pag: paginasLidas, min: Number(leituraRegistrada.minutos || 0), apren: '' }""",
    """      const reg = { id: `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`, data: hojeIso, pag: paginasLidas, min: Number(leituraRegistrada.minutos || 0), apren: '' }""",
    'webhook-leitura-com-id'
)

# 2) Mesclagem de itens novos por id (dos_leituras) + uma mesclagem nova para
# quando o item JA EXISTE nos dois lados mas mudou de estado (feito/status) -
# isso cobre marcar item da Casa como comprado/feito, mudar status de tarefa
# de trabalho existente, e marcar pedido de oracao como respondido.
replace_once(
    'src/main.tsx',
    "        mesclarArrayPorId('dos_pedidos_oracao')",
    """        mesclarArrayPorId('dos_pedidos_oracao')
        mesclarArrayPorId('dos_leituras')
        function mesclarCampoPorId(chave:string,campos:string[]){
          const remotos=Array.isArray(remoto[chave])?remoto[chave]:[]
          if(remotos.length===0)return
          const locais=Array.isArray(dados[chave])?dados[chave]:[]
          let mudou=false
          const atualizados=locais.map((it:any)=>{
            if(!it||!it.id)return it
            const r=remotos.find((x:any)=>x&&x.id===it.id)
            if(!r)return it
            const novo:any={...it}
            let itemMudou=false
            campos.forEach(c=>{if(r[c]!==undefined&&r[c]!==it[c]){novo[c]=r[c];itemMudou=true}})
            if(itemMudou)mudou=true
            return itemMudou?novo:it
          })
          if(mudou){
            dados[chave]=atualizados
            localStorage.setItem(chave,JSON.stringify(atualizados))
          }
        }
        mesclarCampoPorId('dos_casa_items',['done'])
        mesclarCampoPorId('dos_trabalho',['s'])
        mesclarCampoPorId('dos_pedidos_oracao',['status','dataResposta','testemunho'])""",
    'sincronizarsnapshot-mescla-status-existentes'
)

# 3) Devocional e registro de saude (peso/sono/humor/energia/intestino) sao
# guardados por data, sem id - se o servidor tiver o registro de hoje e o
# navegador ainda nao souber dele, agora ele e trazido em vez de sumir na
# proxima sincronizacao automatica.
replace_once(
    'src/main.tsx',
    "        const aguaRemotaHoje=(remoto.dos_agua_log||{})[isoHojeSync]",
    """        const devRemotoHoje=(Array.isArray(remoto.dos_devocionais)?remoto.dos_devocionais:[]).find((e:any)=>e&&e.data===isoHojeSync)
        if(devRemotoHoje){
          const devLocalLista=Array.isArray(dados.dos_devocionais)?dados.dos_devocionais:[]
          if(!devLocalLista.some((e:any)=>e&&e.data===isoHojeSync)){
            const novaListaDev=[devRemotoHoje,...devLocalLista]
            dados.dos_devocionais=novaListaDev
            localStorage.setItem('dos_devocionais',JSON.stringify(novaListaDev))
          }
        }
        const dataCurtaHojeSync=isoHojeSync.slice(8,10)+'/'+isoHojeSync.slice(5,7)
        ;['dos_saude_extra','dos_saude_extra_flavio'].forEach((chaveSaude)=>{
          const remotoListaSaude=Array.isArray(remoto[chaveSaude])?remoto[chaveSaude]:[]
          const remotoHojeSaude=remotoListaSaude.find((r:any)=>r&&r.data===dataCurtaHojeSync)
          if(!remotoHojeSaude)return
          const localListaSaude=Array.isArray(dados[chaveSaude])?dados[chaveSaude]:[]
          if(!localListaSaude.some((r:any)=>r&&r.data===dataCurtaHojeSync)){
            const novaListaSaude=[remotoHojeSaude,...localListaSaude]
            dados[chaveSaude]=novaListaSaude
            localStorage.setItem(chaveSaude,JSON.stringify(novaListaSaude))
          }
        })
        const aguaRemotaHoje=(remoto.dos_agua_log||{})[isoHojeSync]""",
    'sincronizarsnapshot-mescla-devocional-e-saude'
)

print('TUDO OK:', feitos)
