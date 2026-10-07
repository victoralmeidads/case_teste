# Modelo operacional e gerencial

## Problema de negocio

Dados de plano, producao, indisponibilidade e cadastro podem estar dispersos entre sistemas e arquivos. Sem definicoes e owners claros, a coordenacao gasta tempo conciliando numeros e demora a localizar perdas que merecem investigacao. A demonstracao cria um fluxo repetivel entre fonte, regra, sinal e decisao; nao presume que esse problema ou esses numeros descrevam uma unidade real.

## Processo de negocio

1. Operacoes e Planejamento disponibilizam o extrato aprovado com periodo e granularidade definidos.
2. Engenharia de Dados conecta uma fonte, valida o contrato e registra qualidade e auditoria.
3. Owners de negocio aprovam plano, realizado, unidade, meta e limiares.
4. Analytics calcula desvios, tendencias e candidatos a anomalia; cada sinal preserva contexto e fonte.
5. Coordenacao conduz revisao com Operacoes, Engenharia e Planejamento, prioriza investigacao e registra responsavel, acao e prazo.
6. Owners acompanham o resultado e revisam regra, fonte ou processo quando o sinal e falso, tardio ou insuficiente.

## Fluxo dos dados

`Sistema operacional / arquivo / API -> adaptador -> validacao e normalizacao -> camada canonica -> regras -> indicadores e sinais -> dashboard/API -> registro da decisao`.

Linhas com periodo ou dimensao critica invalidos sao excluidas e contabilizadas; nulos numericos viram zero com alerta no demonstrador. Auditoria registra origem, horario, volumes, ocorrencias e status. No alvo corporativo, incluir identificadores de execucao, linhagem por coluna, retencao e controles formais.

## Fluxo das decisoes

`Sinal -> confirmacao do contexto operacional -> avaliacao de risco e valor -> priorizacao -> responsavel e prazo -> acao -> verificacao do resultado -> aprendizado`.

Nenhum insight dispara acao automatica. Decisao de seguranca, integridade, intervencao de poco e alocacao de recursos permanece com os responsaveis e processos existentes.

## Papeis e responsabilidades

| Papel | Responsabilidade |
|---|---|
| Product Owner / Coordenacao | Priorizar problema, usuario, KPI, criterio de aceite e adocao; arbitrar backlog e valor |
| Data Owner de Operacoes | Aprovar significado, qualidade aceitavel, acesso, periodicidade e uso do dado |
| Owner do indicador | Aprovar formula, limiar, versao e interpretacao executiva |
| Especialista de Engenharia de Producao | Validar coerencia tecnica, causas plausiveis e limites da analise |
| Engenharia de Dados | Integrar fontes, implementar contrato, qualidade, observabilidade e reprocessamento |
| Analytics / BI | Implementar camada semantica, visualizacoes e validacao de resultados |
| TI / Plataforma / Seguranca | Identidade, ambientes, disponibilidade, acesso, continuidade e controles tecnicos |
| Lideranca operacional | Confirmar prioridade, patrocinar capacidade e cobrar fechamento das acoes |

## Riscos e controles

| Risco | Controle proposto |
|---|---|
| Definicao de KPI divergente | Dicionario versionado, owner identificado e aceite antes de publicar |
| Dado incompleto ou atrasado | Validacao de esquema, completude, frescor, alerta e visibilidade da origem |
| Falso positivo de anomalia | Limiares explicaveis, contexto temporal e confirmacao humana |
| Uso indevido de dado sintetico | Identificacao explicita no dashboard, API e apresentacao |
| Vazamento de dado operacional | Acesso minimo, classificacao, criptografia e uso apenas de ambiente aprovado no alvo |
| Acao priorizada por volume e nao por risco | Seguranca/integridade como veto; considerar risco, valor, recorrencia e viabilidade |
| Dependencia de pessoa-chave | Runbook, ownership, revisao por pares e transferencia de conhecimento |
| Mudanca sem avaliar impacto | Versionamento de contrato/regra e testes de regressao para consumidores |

## Priorizacao

Aplicar primeiro criterios eliminatorios: seguranca, integridade, conformidade, confianca minima do dado e disponibilidade de owner. Entre itens elegiveis, comparar valor decisorio esperado, urgencia/recorrencia, alcance de usuarios, viabilidade, esforco e dependencias. Um score simples pode ordenar a conversa, mas nao substituir julgamento de negocio nem ocultar premissas. Entregar um MVP de uma decisao recorrente antes de ampliar escopo.

## Indicadores de sucesso e beneficios

- **Adocao:** usuarios-alvo ativos na cadencia operacional; decisoes que consultam a visao.
- **Velocidade:** tempo entre disponibilidade do dado e revisao de desempenho.
- **Confiabilidade:** cargas concluidas, frescor no SLA acordado, registros aceitos e incidentes de definicao.
- **Acionabilidade:** sinais confirmados, acoes com owner/prazo e taxa de fechamento.
- **Resultado:** perdas evitadas ou recuperacao validada pelo negocio, sem atribuir causalidade indevida ao dashboard.
- **Governanca:** KPIs publicados com definicao, owner, versao e aceite.

Beneficios esperados: menor conciliacao manual, foco mais rapido em desvios, linguagem comum entre Operacoes e tecnologia, rastreabilidade da definicao e um caminho incremental para BI corporativo.

## Adocao e evolucao

Comecar com uma rotina-piloto e usuarios representantes; apresentar a decisao que a tela apoia, treinar owners e registrar feedback. Medir uso e fechamento de acoes antes de escalar. Evolucao para Power BI/Databricks exige arquitetura corporativa de identidade, dados curados, catalogo, monitoramento, custos, ambientes e suporte.