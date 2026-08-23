// Dados pessoais e padroes desta instancia do sistema.
// Pra replicar pra uma cliente nova: edite so este arquivo com os dados dela
// (rotina, horarios de busca das criancas, localizacao). Nomes das chaves
// "domi"/"derick" continuam fixos no resto do codigo - trocar quem sao as
// pessoas (e nao so os horarios delas) ainda exige editar os componentes
// que usam esses nomes, isso aqui nao resolve sozinho.

export const NOME_RESPONSAVEL_PADRAO: Record<string, string> = { denise: 'Denise', flavio: 'Flávio' }

export const FAMILIA_PADRAO: Record<string, { dropOff: string, pk: Record<number, string>, entrada?: string, responsavel?: string }> = {
  domi: { dropOff: '07:00', pk: { 1: '12:50', 2: '11:40', 3: '12:50', 4: '11:40', 5: '13:00' }, entrada: '07:00', responsavel: 'denise' },
  derick: { dropOff: '07:00', pk: { 1: '17:00', 2: '17:00', 3: '17:00', 4: '17:00', 5: '17:00' }, entrada: '07:00', responsavel: 'flavio' },
}

export const ROTINA_PADRAO = [
  { t: '05:30', n: 'Devocional', cat: 'Espiritual' },
  { t: '06:00', n: 'Acordar · água · humor', cat: 'Saúde' },
  { t: '06:30', n: 'Café · whey · creatina', cat: 'Alimentação' },
  { t: '07:00', n: 'Levar crianças à escola', cat: 'Família' },
  { t: '07:30', n: 'Calistenia', cat: 'Exercícios' },
  { t: '08:20', n: 'Banho · skincare', cat: 'Casa' },
  { t: '08:45', n: 'Planejar o dia · prioridades', cat: 'Trabalho' },
  { t: '09:30', n: 'Lanche da manhã', cat: 'Alimentação' },
  { t: '12:50', n: 'Buscar Domi', cat: 'Família' },
  { t: '15:30', n: 'Whey da tarde', cat: 'Alimentação' },
  { t: '17:00', n: 'Buscar Derick', cat: 'Família' },
  { t: '19:00', n: 'Jantar', cat: 'Alimentação' },
  { t: '20:00', n: 'Célula (Qua) / Aula (Sex)', cat: 'Compromisso' },
  { t: '21:30', n: 'Probióticos', cat: 'Saúde' },
  { t: '22:00', n: 'Leitura · 20 min', cat: 'Desenvolvimento' },
]

// Usada so pro card de clima da Home. Coordenadas da cidade da cliente.
export const LOCALIZACAO_PADRAO = { latitude: -23.55, longitude: -46.63 }
