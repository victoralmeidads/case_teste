# Catalogo e dicionario de dados

## Dataset

| Atributo | Definicao |
|---|---|
| Nome | Producao semanal de E&P |
| Owner do dado | Gerencia de Operacoes de E&P |
| Owner dos indicadores | Coordenacao de Desempenho Operacional |
| Versao do contrato | 1.0.0 |
| Atualizacao | Sob demanda na demonstracao; proposta semanal para o processo |
| Fonte | CSV/Excel fornecido pelo usuario ou API simulada |
| Classificacao | Sintetico e demonstrativo; nao representa dado operacional corporativo |

## Dicionario

| Campo | Tipo | Definicao | Regra de qualidade |
|---|---|---|---|
| `period` | Data | Inicio da semana operacional | Obrigatorio e conversivel para data; registro invalido e rejeitado |
| `asset_id` | Texto | Identificador do ativo | Obrigatorio; retirar espacos laterais |
| `asset_name` | Texto | Nome de exibicao do ativo | Obrigatorio; retirar espacos laterais |
| `facility` | Texto | Instalacao associada | Obrigatorio; retirar espacos laterais |
| `well_id` | Texto | Identificador do poco | Obrigatorio; retirar espacos laterais |
| `production_plan_bopd` | Decimal anulavel | Producao planejada em barris por dia | Preservar zero; ausente, N/A, estimado sem metadado e invalido permanecem nulos e geram alertas distintos |
| `production_actual_bopd` | Decimal anulavel | Producao realizada em barris por dia | Preservar zero; ausente, N/A, estimado sem metadado e invalido permanecem nulos e geram alertas distintos |
| `downtime_hours` | Decimal anulavel | Horas de indisponibilidade do periodo | Preservar zero; ausente, N/A, estimado sem metadado e invalido permanecem nulos e geram alertas distintos |

## Indicadores publicados

| Indicador | Formula resumida | Owner | Versao |
|---|---|---|---|
| Producao realizada | Soma do realizado para o periodo | Coordenacao de Desempenho Operacional | 1.0.0 |
| Desvio (bopd) | Realizado menos planejado | Engenharia de Producao | 1.0.0 |
| Desvio (%) | (Realizado - planejado) / planejado | Engenharia de Producao | 1.0.0 |
| Cumprimento | Realizado / planejado; meta de referencia em 95% | Gerencia de Operacoes de E&P | 1.0.0 |
| Tendencia | Media das variacoes semanais nas quatro semanas recentes | Analytics de Operacoes | 1.0.0 |

## Entidades semanticas

`Ativo` possui muitos `Pocos`; `Instalacao` possui muitos `Pocos`; `Poco` tem fatos de `Producao` e `Meta` por `Periodo`; os fatos alimentam `Indicadores`. O diagrama Mermaid e gerado a partir de `src/analytics/semantic_model.py` ao iniciar o Streamlit e fica disponivel para download na aba Governanca.

## Contrato e mudanca

Mudanca de nome, tipo, granularidade, unidade, regra ou owner exige nova versao, avaliacao de impacto em consumidores e aceite dos owners. Em integracao real, manter catalogo corporativo, linhagem tecnica, classificacao, retencao e controles de acesso conforme politica vigente.

Na interface, cobertura numerica e alertas sao apresentados por campo. Os codigos de qualidade `NUMERIC_MISSING`, `NUMERIC_NOT_APPLICABLE`, `NUMERIC_ESTIMATE_UNSUPPORTED` e `NUMERIC_INVALID` nao representam valores numericos; um zero explicito continua sendo uma observacao. A fonte atual nao fornece status estruturado de estimativa, portanto texto marcado como estimado nao e convertido nem usado em calculo.