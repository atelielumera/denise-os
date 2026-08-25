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

# Os tres botoes (Editar, Reagendar, Excluir) da Agenda so funcionavam quando
# ev.origem === 'app'. Mas consultas registradas pela tela Saude sao criadas
# com origem:'saude' (ver addConsulta em Saude()), entao pra elas os botoes
# aparecem mas nao fazem nada quando clicados - exatamente o bug reportado.
# O "if(!ev)" sozinho ja bloqueia corretamente eventos que vem so do Google
# (esses tem evento:null), entao o "|| ev.origem!=='app'" e redundante e
# excludente demais - basta remove-lo.

replace_once(
    'src/main.tsx',
    """  function abrirEdicao(e:any){
    const ev=e.evento
    if(!ev||ev.origem!=='app')return
    setEventoEditando(ev)""",
    """  function abrirEdicao(e:any){
    const ev=e.evento
    if(!ev)return
    setEventoEditando(ev)""",
    'agenda-abriredicao-remove-checagem-origem'
)

replace_once(
    'src/main.tsx',
    """  async function pedirExclusao(e:any){
    const ev=e.evento
    if(!ev||ev.origem!=='app')return
    if(ev.recorrenciaId){setEscopoPendente({acao:'excluir',id:ev.id});return}""",
    """  async function pedirExclusao(e:any){
    const ev=e.evento
    if(!ev)return
    if(ev.recorrenciaId){setEscopoPendente({acao:'excluir',id:ev.id});return}""",
    'agenda-pedirexclusao-remove-checagem-origem'
)

replace_once(
    'src/main.tsx',
    """  function abrirReagendar(e:any){
    const ev=e.evento
    if(!ev||ev.origem!=='app')return
    setReagendando({id:ev.id,data:ev.data,hora:ev.hora||'',recorrenciaId:ev.recorrenciaId})""",
    """  function abrirReagendar(e:any){
    const ev=e.evento
    if(!ev)return
    setReagendando({id:ev.id,data:ev.data,hora:ev.hora||'',recorrenciaId:ev.recorrenciaId})""",
    'agenda-abrirreagendar-remove-checagem-origem'
)

print('TUDO OK:', feitos)
