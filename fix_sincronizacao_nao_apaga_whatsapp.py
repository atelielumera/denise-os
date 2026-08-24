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
    'src/main.tsx',
    """        const refsRemotosHoje=(remoto.dos_refs_log||{})[isoHojeSync]
        if(Array.isArray(refsRemotosHoje)&&refsRemotosHoje.length>0){
          const refsLogLocal=dados.dos_refs_log||{}
          const refsLocaisHoje:any[]=refsLogLocal[isoHojeSync]||[]
          const idsLocais=new Set(refsLocaisHoje.map((r:any)=>r.id))
          const novosDoRemoto=refsRemotosHoje.filter((r:any)=>r&&r.id&&!idsLocais.has(r.id))
          if(novosDoRemoto.length>0){
            const unidos=[...novosDoRemoto,...refsLocaisHoje]
            const novoLogRefs={...refsLogLocal,[isoHojeSync]:unidos}
            dados.dos_refs_log=novoLogRefs
            localStorage.setItem('dos_refs_log',JSON.stringify(novoLogRefs))
          }
        }
      }catch{}""",
    """        const refsRemotosHoje=(remoto.dos_refs_log||{})[isoHojeSync]
        if(Array.isArray(refsRemotosHoje)&&refsRemotosHoje.length>0){
          const refsLogLocal=dados.dos_refs_log||{}
          const refsLocaisHoje:any[]=refsLogLocal[isoHojeSync]||[]
          const idsLocais=new Set(refsLocaisHoje.map((r:any)=>r.id))
          const novosDoRemoto=refsRemotosHoje.filter((r:any)=>r&&r.id&&!idsLocais.has(r.id))
          if(novosDoRemoto.length>0){
            const unidos=[...novosDoRemoto,...refsLocaisHoje]
            const novoLogRefs={...refsLogLocal,[isoHojeSync]:unidos}
            dados.dos_refs_log=novoLogRefs
            localStorage.setItem('dos_refs_log',JSON.stringify(novoLogRefs))
          }
        }
        function mesclarArrayPorId(chave:string){
          const remotos=Array.isArray(remoto[chave])?remoto[chave]:[]
          if(remotos.length===0)return
          const locais=Array.isArray(dados[chave])?dados[chave]:[]
          const idsLocais=new Set(locais.map((it:any)=>it?.id))
          const novosDoRemoto=remotos.filter((it:any)=>it&&it.id&&!idsLocais.has(it.id))
          if(novosDoRemoto.length===0)return
          const unidos=[...locais,...novosDoRemoto]
          dados[chave]=unidos
          localStorage.setItem(chave,JSON.stringify(unidos))
        }
        mesclarArrayPorId('dos_casa_items')
        mesclarArrayPorId('dos_pedidos_oracao')
        mesclarArrayPorId('dos_agenda')
        if(remoto.dos_luna_pendente===undefined&&dados.dos_luna_pendente){
          delete dados.dos_luna_pendente
          localStorage.removeItem('dos_luna_pendente')
        }else if(remoto.dos_luna_pendente&&(!dados.dos_luna_pendente||(remoto.dos_luna_pendente.criadoEm||0)>(dados.dos_luna_pendente.criadoEm||0))){
          dados.dos_luna_pendente=remoto.dos_luna_pendente
          localStorage.setItem('dos_luna_pendente',JSON.stringify(remoto.dos_luna_pendente))
        }
      }catch{}""",
    'main-sincronizacao-preserva-whatsapp'
)

print('TUDO OK:', feitos)
