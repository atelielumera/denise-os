from pathlib import Path

def replace_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
    return s.replace(old, new)

main_file = Path("src/main.tsx")
if not main_file.exists():
    raise SystemExit("ABORTADO (main-tsx-nao-encontrado): rode este script na raiz do projeto denise-os.")
s = main_file.read_text()

old = """    sincronizarSnapshot()
    const t=setInterval(sincronizarSnapshot,30*1000)
    let debounceSync:any=null
    const origSetItem=localStorage.setItem.bind(localStorage)
    localStorage.setItem=function(key:string,value:string){
      origSetItem(key,value)
      if(key.startsWith('dos_')){
        if(debounceSync)clearTimeout(debounceSync)
        debounceSync=setTimeout(sincronizarSnapshot,4000)
      }
    }
    function sincronizarSeEscondeu(){if(document.hidden)sincronizarSnapshot()}
    window.addEventListener('beforeunload',sincronizarSnapshot)
    document.addEventListener('visibilitychange',sincronizarSeEscondeu)
    return()=>{
      clearInterval(t)
      if(debounceSync)clearTimeout(debounceSync)
      localStorage.setItem=origSetItem
      window.removeEventListener('beforeunload',sincronizarSnapshot)
      document.removeEventListener('visibilitychange',sincronizarSeEscondeu)
    }
  },[])"""
new = """    sincronizarSnapshot()
    const t=setInterval(sincronizarSnapshot,30*1000)
    function sincronizarSeEscondeu(){if(document.hidden)sincronizarSnapshot()}
    window.addEventListener('beforeunload',sincronizarSnapshot)
    document.addEventListener('visibilitychange',sincronizarSeEscondeu)
    return()=>{
      clearInterval(t)
      window.removeEventListener('beforeunload',sincronizarSnapshot)
      document.removeEventListener('visibilitychange',sincronizarSeEscondeu)
    }
  },[])"""
s = replace_once(s, old, new, "reverter-monkeypatch-localstorage")

main_file.write_text(s)
print("OK - removida a parte arriscada (reescrever localStorage.setItem globalmente).")
print("Mantido: sincroniza a cada 30s + ao trocar de aba/fechar (bem mais rapido que os 5min de antes, sem o risco).")
