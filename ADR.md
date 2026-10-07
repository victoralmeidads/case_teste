# ADR | Decisoes de arquitetura

## Contexto

O case precisa demonstrar coordenacao de uma capacidade analitica de E&P, da extracao a decisao, em um prototipo local. O valor de demonstracao e governanca, integracao negocio-tecnologia e priorizacao; nao e uma arquitetura de producao nem um modelo de engenharia de reservatorios.

## Decisoes

### ADR-001 | Monolito modular local

**Decisao tecnica:** organizar por responsabilidades em `src/ingestion`, `transformation`, `business`, `analytics`, `governance`, `api` e `frontend`. O contrato canonico evita acoplamento entre formato de origem e regra de negocio.

**Alternativas:** microsservicos e plataforma distribuida foram adiados por custo operacional e por nao contribuirem para a pergunta da banca.

**Consequencia:** simples de instalar e demonstrar; limites de escala, concorrencia e disponibilidade devem ser revisitados antes de producao.

### ADR-002 | Streamlit para experiencia; FastAPI para integracao

**Decisao tecnica:** Streamlit entrega os fluxos de demonstracao rapidamente; FastAPI publica endpoints de exemplo com os mesmos calculos de dominio.

**Decisao gerencial:** manter a interface substituivel protege o investimento em regras e contratos sem antecipar uma decisao de produto corporativo.

### ADR-003 | Adaptadores para CSV, Excel e API simulada

**Decisao tecnica:** cada fonte implementa o protocolo `DataSource`; todas passam pela mesma validacao e normalizacao.

**Decisao de governanca:** a fonte e preservada no registro de auditoria e exibida na interface. O dataset simulado e rotulado como sintetico.

### ADR-004 | Regras explicaveis e configuraveis

**Decisao tecnica:** limiares estao em `src/config.py`; formulas ficam em `src/business/metrics.py`; tendencias e sinais ficam em `src/analytics/analysis.py`.

**Trade-off:** limiares simples e faceis de questionar, revisar e explicar; nao substituem modelos de causa-raiz, reservatorio ou previsao validados.

### ADR-005 | SQLite apenas para auditoria local

**Decisao tecnica:** persistir metadados de cargas em SQLite; dados de negocio sao processados em memoria no prototipo.

**Decisao de governanca:** trilha identifica fonte, horario, volumes, ocorrencias e status. Nenhum dado pessoal e necessario no recorte.

**Evolucao:** armazenar dados curados e historico em plataforma gerenciada conforme requisitos de acesso, retencao e disponibilidade.

### ADR-006 | Assistente analitico deterministico e fundamentado

**Decisao tecnica:** oferecer perguntas guiadas de panorama, comparacao, rastreabilidade de indicador, associacao exploratoria, priorizacao e exportacao. As respostas consultam somente o DataFrame carregado e as definicoes do catalogo; nao ha LLM, consulta externa ou acesso implicito a documentos.

**Decisao de governanca:** cada resposta apresenta periodo/fonte, evidencia, owner ou criterio, cobertura e limitacoes. Associacao entre perda e indisponibilidade nao e apresentada como causalidade; ausencia de dados suficientes torna a resposta inconclusiva.

**Trade-off:** escopo de perguntas limitado, mas auditavel e testavel. Uma interface de linguagem natural so deve ser adicionada com consultas permitidas, citacoes verificaveis, protecao contra prompt injection e avaliacao de respostas.

## Nao objetivos

- Nao integrar sistemas corporativos ou publicar credenciais.
- Nao afirmar que o dado sintetico representa producao real.
- Nao automatizar intervencao operacional ou recomendacao de seguranca.
- Nao certificar indicador para uso oficial sem aprovacao dos owners.

## Criterios de revisao

Revisar as decisoes quando houver fonte real autorizada, multiplos consumidores, requisito formal de SLA, historico auditavel, identidade corporativa, segregacao de acesso ou aprovacao de KPIs oficiais.