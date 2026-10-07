# Regras de negocio e indicadores

As regras estao implementadas fora da interface, em `src/config.py`, `src/business/metrics.py` e `src/analytics/analysis.py`. Os valores abaixo sao parametros de demonstracao e requerem validacao dos owners antes de qualquer uso oficial.

## Regras

| Regra | Definicao | Parametro demonstrativo | Tratamento |
|---|---|---|---|
| Plano | Producao prevista por poco e semana | Campo de entrada `production_plan_bopd` | Unidade: bopd |
| Realizado | Producao medida para o mesmo poco e semana | Campo de entrada `production_actual_bopd` | Unidade: bopd |
| Desvio absoluto | Realizado menos plano | Sem limiar | Positivo indica acima do plano; negativo indica perda |
| Desvio percentual | Desvio absoluto / plano x 100 | Plano zero resulta em valor indefinido | Evita divisao por zero |
| Cumprimento | Realizado / plano x 100 | Meta de referencia: 95% | O agregado so e conclusivo quando plano e realizado cobrem todos os registros do periodo |
| Desvio material | Cumprimento relativo ao plano abaixo do limiar | Desvio <= -10% | Sinal para triagem, nao diagnostico |
| Queda relevante | Variacao do realizado contra semana anterior | Queda >= 15% | Sinaliza queda semanal; compara registros do mesmo ativo |
| Tendencia | Media das diferencas semanais do realizado | Quatro periodos mais recentes | Classifica recuperacao, queda ou estabilidade |

## Regras de interpretacao

- Agregar apenas registros com a mesma granularidade e unidade; validar a definicao de periodo operacional na fonte real.
- Perdas absolutas e percentuais respondem perguntas diferentes. O ranking apresenta volume e percentual para evitar priorizacao distorcida.
- Um insight automatico e uma hipotese de investigacao. O responsavel operacional confirma contexto, causa, acao e prazo.
- Zero explicito e preservado como valor observado; ausencia permanece nula e tem cobertura exibida. O prototipo nunca substitui ausencia por zero.
- `N/A`/`nao aplicavel` e valores ausentes permanecem nulos, mas geram codigos de qualidade distintos. Texto marcado como estimativa sem metadado numerico tambem permanece nulo e recebe alerta proprio; a fonte atual nao oferece um campo estruturado para estimativa.
- Texto numerico invalido permanece nulo e gera alerta por campo. Valores numericos ausentes nao entram como zero em somas; totais conhecidos podem ser parciais e sao acompanhados por cobertura.
- Cumprimento agregado e desvio total nao sao apresentados como conclusivos com cobertura incompleta. Tendencia exige observacoes completas na janela usada.
- Registros sem periodo ou dimensao critica sao rejeitados e contados na qualidade.
- Valores negativos sao aceitos com alerta para revisao, pois podem ter significado contabil/operacional especifico.

## Priorizacao operacional proposta

Ordenar oportunidades por perda absoluta, criticidade/risco de seguranca, impacto economico, persistencia do desvio, confianca do dado e viabilidade de intervencao. Seguranca e integridade operacional sao criterios de veto, nao uma variavel compensavel por ganho de producao. Este prototipo demonstra apenas perda e persistencia; criticidade e economics exigem dados aprovados.