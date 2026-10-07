# Roteiro para a banca

## Elevator pitch | 90 segundos

Eu trouxe uma demonstracao de como coordenar uma capacidade analitica de E&P, nao apenas construir um dashboard. O fluxo comeca em uma extracao operacional, passa por um contrato de dados e controles de qualidade, aplica regras de negocio aprovaveis pelos owners e transforma o resultado em sinais que apoiam uma decisao. A aplicacao recebe CSV, Excel ou uma API simulada; as tres fontes convergem para o mesmo esquema, entao trocar a origem nao exige reescrever as regras.

Na tela, a lideranca compara plano e realizado, identifica ativos e instalacoes que concentram perdas, acompanha tendencia e recebe insights automaticos explicaveis. Cada visao informa o problema, a decisao apoiada, a fonte, o responsavel e a atualizacao. Na aba de governanca, mostro dicionario, definicoes, versao, owners, qualidade, auditoria e modelo semantico.

Os dados sao sinteticos e os limiares sao parametros de demonstracao, claramente identificados. Nenhum insight dispara uma intervencao. O proximo passo seria validar granularidade e indicadores com Operacoes, Engenharia e Planejamento, selecionar uma decisao recorrente para piloto e medir qualidade, adocao e fechamento das acoes. A arquitetura modular preserva esse aprendizado e permite evoluir para Power BI e Databricks quando houver aprovacao, requisitos e plataforma definidos.

## Explicacao | 3 minutos

**1. Problema e valor.** A coordenacao precisa aproximar negocio e tecnologia para reduzir conciliacao manual e direcionar atencao a perdas relevantes. Uma visualizacao so gera valor se usar definicoes aceitas, chegar no momento da rotina e resultar em acao com owner e prazo.

**2. Processo e arquitetura.** Demonstro tres origens: API simulada, CSV e Excel. Adaptadores isolam o formato; uma validacao comum normaliza periodo, dimensoes e numeros, rejeita registros sem chave critica e registra alertas. Regras fora da interface calculam desvio absoluto e percentual, cumprimento de meta e tendencia. Analytics procura desvios materiais, quedas semanais e concentracao de perdas; a linguagem dos insights deixa explicito que sao sinais para triagem.

**3. Decisao.** Na visao geral, comparo producao semanal planejada e realizada. Na visao de ativos, vejo onde esta a maior perda absoluta e percentual. Na analitica, verifico persistencia e candidatos a anomalia. Isso orienta uma reuniao operacional: confirmar contexto, avaliar risco e viabilidade, nomear responsavel, acordar prazo e depois verificar o resultado.

**4. Governanca e coordenacao.** O catalogo identifica definicao, tipo, fonte, Data Owner e versao. Indicadores possuem owners; cargas deixam trilha SQLite; o modelo semantico explicita Ativo, Instalacao, Poco, Periodo, Meta, Producao e Indicador. Como coordenador, eu organizaria PO, owners, engenharia de dados, BI/Analytics, especialistas operacionais e plataforma em entregas incrementais, com criterio de aceite e gates de qualidade.

**5. Limites e proximo passo.** Os dados sao sinteticos, a tendencia e uma regra simples e o prototipo nao representa disponibilidade, seguranca ou escala corporativa. O primeiro piloto real deve validar definicoes, acesso, periodicidade e criterio de sucesso com os owners antes de integrar. A prioridade e uma decisao recorrente de alto valor e viabilidade, nao adicionar mais graficos.

## Explicacao executiva | 10 minutos

| Tempo | Conteudo | Evidencia na demonstracao |
|---|---|---|
| 0:00-1:00 | Problema de coordenacao: transformar dado operacional em decisao confiavel | Abrir pelo resultado de negocio, nao pela tecnologia |
| 1:00-2:30 | Processo: fonte, validacao, regras, indicadores, analise e decisao | Narrar a cadeia ponta a ponta |
| 2:30-4:00 | Visao geral: plano, realizado, cumprimento e tendencia | Dashboard e contexto de atualizacao/fonte |
| 4:00-5:30 | Ativos: concentracao de perdas, impacto absoluto versus percentual | Ranking e tabela de desempenho |
| 5:30-6:30 | Analytics: desvios, queda, tendencia e frases automaticas | Sublinhar explicabilidade e validacao humana |
| 6:30-7:30 | Governanca: qualidade, owners, catalogo, versao e auditoria | Dicionario, indicadores e cargas |
| 7:30-8:30 | Coordenacao: papeis, priorizacao, risco e adocao | Descrever ritual de revisao e fechamento |
| 8:30-9:30 | Arquitetura e evolucao para Power BI/Databricks | Adaptadores, contrato canonico e API |
| 9:30-10:00 | Limites, pedido de decisao e proximo passo | Propor piloto com owners e metricas de sucesso |

## Perguntas dificeis e respostas recomendadas

**1. Esses numeros representam operacoes reais?**

Nao. Sao sinteticos, criados para demonstrar o fluxo e testar sinais. Antes de qualquer conclusao operacional, eu conectaria uma fonte autorizada e pediria validacao aos Data Owners.

**2. Por que nao usou um modelo de machine learning?**

O objetivo e demonstrar decisao explicavel e coordenacao. Regras simples deixam limiares, comparacoes e responsaveis auditaveis. Eu so proporia maior complexidade se um caso de uso, dados rotulados, beneficio e criterio de avaliacao justificassem.

**3. Como evita que uma meta ou regra errada gere uma decisao ruim?**

Owner de negocio aprova definicao e limiar, a versao fica publicada, mudancas passam por impacto e teste, e o insight nao dispara acao automatica. A rotina confirma o contexto com a operacao.

**4. Como priorizaria ativos para uma intervencao?**

Nao usaria apenas o ranking de producao. Aplicaria primeiro veto de seguranca, integridade, conformidade e qualidade do dado; depois avaliaria perda, persistencia, valor, viabilidade, janela operacional e recursos disponiveis junto aos especialistas.

**5. Como provaria que a solucao gerou valor?**

Definiria linha de base, usuarios e rotina; mediria tempo de analise, qualidade/frescor, sinais confirmados, acoes fechadas e resultado operacional validado. Evitaria atribuir causalidade ao dashboard sem desenho de avaliacao.

**6. O que falta para producao?**

Fonte autorizada, identidade e acesso, historico curado, controles de seguranca, SLA, monitoramento, retencao, testes de integracao, suporte, processo de mudanca e aceite formal de indicadores.

**7. Por que Streamlit, SQLite e nao Power BI logo?**

Streamlit acelera a validacao do fluxo e da conversa com usuarios. SQLite atende a auditoria local da demonstracao. A escolha de Power BI e armazenamento corporativo deve seguir a plataforma, identidade, governanca e padroes existentes; as regras estao separadas para permitir essa evolucao.

**8. Como coordenaria especialistas sem microgerenciar?**

Alinharia objetivo, owners, interfaces, criterio de aceite, riscos e cadencia. Engenharia de dados responde por contrato e qualidade; BI por semantica e experiencia; Operacoes/Engenharia por definicao e validacao; plataforma por identidade e operacao. A coordenacao remove dependencias e acompanha valor e risco.

**9. O que faria se a qualidade estivesse ruim?**

Tornaria a limitacao visivel, impediria publicar o KPI abaixo do criterio acordado, colocaria a carga em quarentena quando necessario e trabalharia com o owner na causa-raiz. Nao preencheria dados silenciosamente para preservar um grafico.

**10. Qual seria o primeiro incremento do piloto?**

Escolher uma decisao semanal concreta, uma instalacao/recorte com owner e dados disponiveis, validar formula e baseline, executar a rotina com usuarios e medir adocao e fechamento de acoes. So depois ampliaria fontes e audiencia.