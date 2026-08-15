// ============================================================
// Calendário Avaliativo — Domi — 3º Bimestre 2026 — 5º ano
// Colégio Adventista Alto Boqueirão · Comunicado 033/2026
// ------------------------------------------------------------
// >>> AJUSTE 1 LINHA: a turma da Domi (51, 52, 53 ou 54).
// ============================================================

export const TURMA_DOMI: "51" | "52" | "53" | "54" = "51";
const _grupoAB = TURMA_DOMI === "51" || TURMA_DOMI === "52";

export type Avaliacao = {
  id: string; data: string; disciplina: string;
  tipo: "AV1" | "AV2" | "AV3" | "Recuperação";
  titulo: string; conteudo: string; turmaEspecifica?: boolean;
};

const d = (a: string, b: string) => (_grupoAB ? a : b);

export const CALENDARIO_DOMI_3BIM: Avaliacao[] = [
  { id: "av1-prodtext", data: "2026-08-11", disciplina: "Produção Textual", tipo: "AV1", titulo: "Produção textual (escrita)", conteudo: "Poema de Cordel — correção externa." },
  { id: "av1-ciencias", data: "2026-08-12", disciplina: "Ciências", tipo: "AV1", titulo: "Atividade avaliativa (trabalho)", conteudo: "Sistema urinário — mapa mental em cartolina, feito e apresentado em sala." },
  { id: "av1-matematica", data: "2026-08-14", disciplina: "Matemática", tipo: "AV1", titulo: "Avaliação", conteudo: "Números decimais — adição, subtração e introdução à multiplicação; situações-problema." },
  { id: "av1-portugues", data: "2026-08-17", disciplina: "Português", tipo: "AV1", titulo: "Avaliação", conteudo: "Capítulos 8 e 9: poema, linguagem regional, conjunções, notícia, discurso direto e indireto." },
  { id: "av1-edfisica", data: d("2026-08-17", "2026-08-20"), disciplina: "Ed. Física", tipo: "AV1", titulo: "Atividade avaliativa (trabalho)", conteudo: "A importância da atividade física — em sala.", turmaEspecifica: true },
  { id: "av1-musica", data: d("2026-08-17", "2026-08-20"), disciplina: "Música", tipo: "AV1", titulo: "Atividade (trabalho)", conteudo: "Parâmetros sonoros, ritmo, andamentos — Livro de Arte, pág. 57 e 60.", turmaEspecifica: true },
  { id: "av1-historia", data: "2026-08-19", disciplina: "História", tipo: "AV1", titulo: "Atividade avaliativa (trabalho)", conteudo: "Símbolos nacionais e a República (cap. 7) — Missão Criativa: agência de publicidade." },
  { id: "av1-ingles", data: d("2026-08-21", "2026-08-18"), disciplina: "Inglês", tipo: "AV1", titulo: "Atividade avaliativa (trabalho)", conteudo: "Routine (pág. 44-45) e Improving my routine (pág. 47-48) — em sala.", turmaEspecifica: true },
  { id: "av1-arte", data: d("2026-08-21", "2026-08-18"), disciplina: "Arte", tipo: "AV1", titulo: "Atividade avaliativa (trabalho)", conteudo: "Colagem — imagem com figuras geométricas do livro didático.", turmaEspecifica: true },
  { id: "av3-matematica", data: "2026-09-01", disciplina: "Matemática", tipo: "AV3", titulo: "Atividade avaliativa", conteudo: "Números decimais — lista de situações-problema em sala." },
  { id: "av3-portugues", data: "2026-09-02", disciplina: "Português", tipo: "AV3", titulo: "Atividade avaliativa (trabalho)", conteudo: "Notícia — pesquisar uma notícia do dia em que nasceu; jornal da turma." },
  { id: "av2-prodtext", data: "2026-09-11", disciplina: "Produção Textual", tipo: "AV2", titulo: "Produção textual (escrita)", conteudo: "Livro literário de Cordel — cada aluno produz seu poema; xilogravura em isopor." },
  { id: "av2-historia", data: "2026-09-14", disciplina: "História", tipo: "AV2", titulo: "Avaliação", conteudo: "Capítulos 8 e 9 — apostila pág. 78-83 e 86-92." },
  { id: "av2-matematica", data: "2026-09-15", disciplina: "Matemática", tipo: "AV2", titulo: "Avaliação", conteudo: "Decimais: comparação, adição/subtração, multiplicação e divisão por 10/100/1000." },
  { id: "av2-ingles", data: d("2026-09-18", "2026-09-15"), disciplina: "Inglês", tipo: "AV2", titulo: "Avaliação", conteudo: "My routine (44-46), Improving my routine (47-50), What is he doing? (51-54).", turmaEspecifica: true },
  { id: "av2-ciencias", data: "2026-09-16", disciplina: "Ciências", tipo: "AV2", titulo: "Avaliação", conteudo: "Sistema urinário (pág. 129-136) e sistema nervoso central/periférico (pág. 143-148)." },
  { id: "av2-portugues", data: "2026-09-17", disciplina: "Português", tipo: "AV2", titulo: "Avaliação", conteudo: "Cordel, rimas, parônimas, sons do /S/, substantivo/adjetivo, conjunções." },
  { id: "av2-geografia", data: "2026-09-18", disciplina: "Geografia", tipo: "AV2", titulo: "Avaliação", conteudo: "Indústria e trabalho nas cidades; Para entender a Terra — cap. 8 e 9." },
  { id: "rec-prodtext", data: "2026-09-24", disciplina: "Produção Textual", tipo: "Recuperação", titulo: "Recuperação bimestral", conteudo: "Reescrita da AV2." },
  { id: "rec-portugues", data: "2026-09-25", disciplina: "Português", tipo: "Recuperação", titulo: "Recuperação bimestral", conteudo: "Conteúdos da AV1 e AV2." },
  { id: "rec-matematica", data: "2026-09-28", disciplina: "Matemática", tipo: "Recuperação", titulo: "Recuperação bimestral", conteudo: "Conteúdos da AV1 e AV2." },
  { id: "rec-ciencias", data: "2026-09-29", disciplina: "Ciências", tipo: "Recuperação", titulo: "Recuperação bimestral", conteudo: "Conteúdos da AV1 e AV2." },
  { id: "rec-hist-geo", data: "2026-09-30", disciplina: "História/Geografia", tipo: "Recuperação", titulo: "Recuperação bimestral", conteudo: "Conteúdos da AV1 e AV2." },
];

export default CALENDARIO_DOMI_3BIM;
