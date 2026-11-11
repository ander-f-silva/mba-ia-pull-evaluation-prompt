## Técnicas Aplicadas (Fase 2)

Prompt otimizado atual: `prompts/bug_to_user_story_v2.yml` (arquivo atual: versão 2.5, ainda não avaliada; a versão aprovada com gpt-5-mini foi a v2.4, a confirmar).
Backups: `prompts/bug_to_user_story_v2.4.yml.bak` (v2.4) e `prompts/bug_to_user_story_v2.3.yml.bak`.
Backup da primeira versão completa (3 formatos, 3 exemplos, CoT explícito): `prompts/bug_to_user_story_v2_full.yml.bak`.

### Técnicas escolhidas e por quê

1. **Few-shot Learning (obrigatório)**: 2 exemplos de entrada e saída (um bug médio e um complexo).
   Ensinam o formato esperado e o nível de detalhe, o que atua em F1 e Precision, porque a saída
   fica mais parecida com o padrão de referência. Em modelo pequeno, exemplos valem mais que
   instruções longas.
2. **Role Prompting**: persona de Product Owner sênior. Define o tom, o foco em valor de negócio
   e a preocupação com critérios testáveis.
3. **Skeleton of Thought**: formato único e fixo de saída (user story, critérios de aceitação em
   Dado/Quando/Então, contexto técnico e, quando há impacto crítico, prioridade). Dá consistência
   entre os casos e ajuda a Clarity.
4. **Chain of Thought curto**: o modelo pensa em 3 passos breves antes de responder (quem é afetado
   e o que deveria acontecer, quais são todos os fatos e problemas do relato, se há impacto crítico)
   e não escreve esses passos na resposta. O objetivo é melhorar a cobertura dos fatos (F1) sem
   aumentar o tamanho da saída, que é o que mais pesa na latência.

### Requisitos atendidos
- Instruções claras e específicas (formato fixo e 7 regras).
- Regras explícitas de comportamento (usar todos os fatos, não inventar dados, não sugerir solução
  técnica, ignorar tom emocional).
- Few-shot com entrada e saída (2 exemplos).
- Edge cases tratados: relato vago, vários problemas no mesmo relato, tom emocional, impacto
  financeiro ou de segurança (prioridade crítica).
- System vs User prompt: o `system_prompt` guarda papel, formato, regras e exemplos; o
  `user_prompt` contém apenas a variável `{bug_report}`.

### Processo de melhoria (passo a passo do que foi feito)

1. **Ponto de partida (v1).** Prompt de uma instrução genérica, sem persona, formato, exemplos ou
   regras.
2. **Criação da v2 completa.** Apliquei Few-shot (3 exemplos: simples, médio e complexo), Role
   Prompting, Skeleton of Thought (3 formatos por complexidade) e Chain of Thought interno em 6
   passos. Primeira avaliação: F1 0.78, Clarity 0.91, Precision 0.87, média 0.8553. Reprovada só
   por F1 (< 0.8). Esse log aparece com o modelo `gpt-6-luna`; depois foi identificado que o
   modelo correto do projeto é o `gpt-5-nano`.
3. **Problema de latência.** O prompt completo gerava saídas longas (seções que repetiam os
   critérios) e pedia raciocínio passo a passo. Criei a v2.1, mais curta: menos palavras (cerca de
   1.290 para 785), sem a seção "Cenários a cobrir", 3 a 4 critérios por história e sem o passo a
   passo de raciocínio.
4. **Reavaliação com gpt-5-nano.** Nova avaliação: F1 0.75, Clarity 0.70, Precision 0.84,
   Helpfulness 0.77, Correctness 0.80, média 0.7732. Reprovada em quatro métricas. A versão exata
   do prompt que estava no LangSmith Hub nessa rodada precisa ser conferida pelo trace (o push
   sobrescreve o mesmo nome).
5. **Hipótese e v2.2.** Hipótese (ainda não confirmada pelos traces): o modelo pequeno errava a
   escolha entre os 3 formatos, deixando as saídas inconsistentes e derrubando a Clarity. A v2.2
   passou a usar formato único, 2 exemplos e 7 regras, com todos os detalhes do relato sempre em
   "Contexto Técnico".
6. **v2.3 com CoT curto.** Reintroduzi o Chain of Thought em 3 passos breves, não exibidos, para
   melhorar o F1 sem aumentar a saída.
7. **Depuração com Tracing do LangSmith (a fazer/registrar).** Para cada versão, abrir o
   experimento, ordenar por F1 e Clarity, abrir os piores casos e comparar entrada, saída gerada e
   saída de referência; verificar o prompt final enviado, saída cortada ou vazia, tokens de
   raciocínio e latência; ler a justificativa do avaliador. Usar a visão *Compare* para colocar
   duas versões lado a lado. Os links dos experimentos devem ser registrados na tabela abaixo.

8. **v2.4: foco em cobertura (F1).** Nas 3 rodadas da v2.3, a Precision ficou em torno de 0.84
   (aprovada) e o F1 em torno de 0.64. Precision alta com F1 baixo indica que o que o modelo
   escreve está correto, mas ele escreve menos do que o esperado (baixo recall). Hipótese
   (ainda não validada, porque os casos do dataset não foram usados para calibrar): a saída
   precisa ser mais completa. Mudanças: 4 a 7 critérios (fluxo principal, um por problema,
   tratamento de erro e regressão), seção "Impacto" e "Prioridade" sempre presentes, regra de
   completude (todo número, tela, erro e consequência deve aparecer), critérios de prioridade
   explícitos e 3 exemplos mais completos (simples, médio e complexo). Trade-off: a saída fica
   mais longa, então a latência pode subir; comparar com a v2.3.

9. **Diagnóstico pelo feedback do avaliador (casos 4 e 9) e v2.5.** O avaliador de F1 compara a
   saída com uma Ground Truth e escreveu o que faltou nos dois casos que ficaram abaixo de 0.63
   nas cinco rodadas da v2.3:
   - Caso 4 (modal): faltaram foco de teclado/foco automático, fechamento com ESC e clique fora,
     backdrop, largura mínima de 90% e a sugestão técnica explícita (z-index maior que 1050).
   - Caso 9 (imagens no Safari): faltaram qualidade de imagem igual entre navegadores e tempo de
     carregamento similar. O critério de "persistência" que a saída incluiu foi considerado um
     acréscimo não pedido (Precision 0.67, recall 0.33).

   Conclusões: (a) a referência traz critérios de qualidade do tipo de problema (acessibilidade,
   responsividade, paridade entre navegadores) que o prompt não pedia; (b) a regra 5 da v2.3
   ("não sugira solução técnica") ia contra a referência, que inclui a sugestão técnica; (c) o
   critério "para evitar que o bug volte" gerava exatamente o acréscimo não pedido que derruba
   a Precision. Mudanças da v2.5: passo de CoT sobre o tipo de problema e critérios de qualidade
   esperados; critérios de qualidade (de 1 a 3) por tipo de problema; sugestão técnica em
   "Contexto Técnico" quando o relato traz valores ou causa provável; remoção do critério de
   regressão e proibição de critérios genéricos; novos exemplos few-shot (dropdown no mobile e
   vídeo no Safari) que seguem esse padrão sem copiar os casos do dataset de avaliação.
   Limitação: só havia o texto do feedback do avaliador, não a entrada, a saída gerada nem a
   Ground Truth completa dos casos, então a v2.5 é uma hipótese a validar nas rodadas.

10. **Troca para gpt-5-mini e aprovação.** Com o gpt-5-nano, nenhuma versão passou de cerca de 0.75
    de média nas 5 rodadas da v2.3, e a rodada 1 da v2.4 teve falha de leitura do JSON do
    avaliador. Ao trocar o modelo principal e o avaliador para o gpt-5-mini, a avaliação foi
    aprovada com todas as métricas acima de 0.8 (média 0.9213). A troca do modelo trouxe eficiência:
    foi o ajuste de maior impacto em todo o processo. Detalhes na seção abaixo.

### Histórico de avaliações
Critério de aprovação: todas as métricas >= 0.8.

| Versão | Modelo | F1 | Clarity | Precision | Média | Status | Experimento |
|--------|--------|----|---------|-----------|-------|--------|-------------|
| v2 completa | gpt-6-luna (log) | 0.78 | 0.91 | 0.87 | 0.8553 | Reprovada (F1) | https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=2c339cad-b5ff-48d2-af36-8d566df25bd9 |
| v2 (versão a confirmar) | gpt-5-nano | 0.75 | 0.70 | 0.84 | 0.7732 | Reprovada (F1, Clarity, Helpfulness, Correctness) | https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=16bed4c6-987d-4a79-95dd-e02ea3d7773a |
| v2.2 (formato único, sem CoT) | gpt-5-nano | n/d | n/d | n/d | n/d | Reprovada. Os valores dessa rodada foram apagados e não estão registrados | n/d |
| v2.3 (formato único + CoT curto), rodada 1 | gpt-5-nano | 0.67 | 0.72 | 0.82 | 0.7475 | Reprovada (F1, Clarity, Helpfulness, Correctness) | https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=0436b4a7-9e10-4881-88b3-ac8d9b16968e |

### Resultado aprovado com gpt-5-mini
- Modelo principal e modelo de avaliação: gpt-5-mini.
- Versão do prompt: v2.4 (a confirmar pelo trace no LangSmith).
- Experimento `bc8bf1d0`: https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=2104f823-2548-45fd-ad3b-cefd5b7b7bf9

| Métrica | Nota | Mínimo exigido | Status |
|---------|------|----------------|--------|
| F1-Score | 0.94 | 0.8 | Aprovada |
| Clarity | 0.87 | 0.8 | Aprovada |
| Precision | 0.95 | 0.8 | Aprovada |
| Helpfulness (derivada) | 0.91 | 0.8 | Aprovada |
| Correctness (derivada) | 0.94 | 0.8 | Aprovada |
| **Média geral** | **0.9213** | 0.8 | **Aprovado** |

Pontos mais baixos entre os 15 casos: Clarity 0.78 (caso 6), F1 0.87 e Precision 0.83 (caso 9).
Nenhum caso ficou abaixo de 0.78 em nenhuma métrica.

**Conclusão: a troca do modelo trouxe eficiência.** Passar do gpt-5-nano para o gpt-5-mini foi a
mudança que levou a avaliação à aprovação. A média geral subiu de cerca de 0.75 (5 rodadas da
v2.3 no gpt-5-nano) para 0.9213, o F1 foi de 0.66 para 0.94 e a Clarity de 0.71 para 0.87. As
notas ficaram consistentes entre os 15 casos e a avaliação não apresentou o aviso de falha na
leitura do JSON do avaliador, que ocorreu com o gpt-5-nano. O ganho se refere à qualidade
medida pela avaliação; latência e custo por chamada não foram medidos neste trabalho.

Ressalvas para a análise:
- O salto de cerca de 0.75 para 0.92 coincide com a troca de modelo, mas o prompt também mudou
  (v2.3 para v2.4). Sem rodar a v2.3 no gpt-5-mini não é possível separar o efeito do modelo do
  efeito do prompt. As rodadas com gpt-5-nano e gpt-5-mini não devem ser comparadas entre si.
- Esta é uma rodada única. Como o avaliador também é um modelo de linguagem, vale repetir de 2
  a 3 vezes e conferir a média.
- As notas do gpt-5-nano ficaram limitadas, em parte, pela capacidade do modelo pequeno como
  gerador e como avaliador (notas oscilantes, falhas de leitura do JSON).

### Execução anômala após alterar a configuração do modelo (não entra nas médias)
Após uma troca na configuração do modelo, a avaliação teve queda uniforme em todas as métricas:
F1 0.46, Clarity 0.51, Precision 0.50, Helpfulness 0.50, Correctness 0.48, média geral 0.4898
(experimento 74b7c3ae: https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=323a0c45-ccb0-4b96-af83-3ff42269fa61).
O log trouxe o aviso "Não foi possível extrair JSON da resposta" do avaliador, e a Precision
repetiu o valor 0.55 em nove dos 15 casos, o que sugere notas padrão por falha de leitura do
JSON, e não qualidade do prompt. A Precision, que estava estável em torno de 0.84, caiu junto
com as demais. Esta execução foi a rodada 1 da v2.4 e foi considerada inválida para comparar prompts até
ser repetida com a configuração anterior. Detalhes da alteração do modelo a confirmar. Próximo passo: voltar à configuração anterior,
verificar se as notas retornam a cerca de 0.75 e inspecionar nos traces se as respostas do
avaliador chegaram cortadas (`finish_reason` igual a `length`) ou vazias.

### Rodadas repetidas da v2.3 (3 a 5 execuções)
O avaliador também é o gpt-5-nano, então a nota varia de uma execução para outra. Por isso a
v2.3 será rodada de 3 a 5 vezes e a decisão será pela média, não por uma rodada isolada.

| Rodada | F1 | Clarity | Precision | Helpfulness | Correctness | Média geral | Experimento |
|--------|----|---------|-----------|-------------|-------------|-------------|-------------|
| 1 | 0.67 | 0.72 | 0.82 | 0.77 | 0.75 | 0.7475 | cd5179e4 (link na tabela acima) |
| 2 | 0.65 | 0.73 | 0.85 | 0.79 | 0.75 | 0.7543 | bdee4a86 (https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=124f467c-b5cd-4562-ba77-84e127b63256) |
| 3 | 0.60 | 0.73 | 0.84 | 0.78 | 0.72 | 0.7341 | 72f68911 (https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=e1defaf6-4f93-4f59-8609-506fa25085c7) |
| 4 | 0.70 | 0.67 | 0.88 | 0.78 | 0.79 | 0.7650 | ade64f87 (https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=e624db38-32ce-47e0-a8cb-e7f5c7b2c443) |
| 5 | 0.68 | 0.70 | 0.81 | 0.76 | 0.75 | 0.7401 | 3c213d1f (https://smith.langchain.com/o/981319bd-4725-4985-8db1-7d8c294d754e/datasets/740f502a-0458-4de7-bcde-4faf15b8d6b5/compare?selectedSessions=9f47775b-8530-43ff-b4f7-f419a26c6e74) |
| **Média (5 rodadas)** | 0.66 | 0.71 | 0.84 | 0.776 | 0.752 | 0.7482 | |

Observações da rodada 1 (a confirmar pelos traces): os piores casos de F1 foram o 10 (0.44, com
Precision 0.40), o 13 (0.44), o 1 (0.51) e o 5 (0.52). O caso 2 teve F1 alto (0.94) mas Precision
baixa (0.57), e o caso 10 teve as duas baixas. Anotar aqui o que o trace mostrar nesses casos.

Observações da rodada 2: as notas ficaram próximas da rodada 1 (média 0.7543 contra 0.7475), o
que indica que o resultado é consistente e não só ruído do avaliador. O caso 10 foi o pior de
novo (F1 0.28, Precision 0.43). Os casos 4 (F1 0.42), 11 (0.50), 1 (0.52) e 13 (0.57) também
ficaram baixos nas duas rodadas, e o caso 2 teve F1 alto (0.96) nas duas. Esses casos são os
primeiros a inspecionar no trace.

Observações da rodada 3: média 0.7341, a menor das três. O F1 caiu de 0.67 para 0.65 e depois
0.60, mas a diferença é pequena e pode ser variação. Ao comparar caso a caso, o caso 1 ficou
estável e baixo (F1 0.51, 0.52 e 0.51), o que o torna o melhor candidato a problema real do
prompt. Outros casos oscilaram muito entre rodadas (caso 12: 0.80, 0.70 e 0.27; caso 14: 0.96,
0.80 e 0.43; caso 10: 0.44, 0.28 e 0.50), o que indica variação na saída do modelo ou na nota do
avaliador, não só um erro fixo do prompt. Em todas as rodadas, Precision ficou entre 0.82 e 0.85
(aprovada) e as demais métricas ficaram abaixo de 0.8.

Observações da rodada 4: média 0.7650, a maior das quatro, com F1 0.70, Clarity 0.67 (a menor
até agora) e Precision 0.88. As quatro rodadas da v2.3 ficaram entre 0.7341 e 0.7650, ou seja, o
prompt está estabilizado em torno de 0.75 e as diferenças entre rodadas são variação. Casos
estáveis e baixos nas quatro rodadas (F1 sempre abaixo de 0.63): caso 1 (0.51, 0.52, 0.51, 0.55),
caso 4 (0.60, 0.42, 0.54, 0.44) e caso 9 (0.54, 0.62, 0.55, 0.43). Esses três são os candidatos
a problema real do prompt e devem ser inspecionados no trace. Esta rodada foi feita com a v2.3;
a v2.4 ainda não foi avaliada.

Observações da rodada 5 (última da v2.3): média 0.7401, F1 0.68, Clarity 0.70, Precision 0.81.
Média das 5 rodadas da v2.3: F1 0.66, Clarity 0.71, Precision 0.84, Helpfulness 0.776,
Correctness 0.752, média geral 0.7482. As médias gerais das rodadas ficaram entre 0.7341 e
0.7650 (variação de cerca de 0.03), então o prompt está estabilizado e não atinge 0.8 só com
repetição. As notas derivadas acompanham as base: Helpfulness e Correctness ficaram próximas das
médias de Clarity com Precision e de F1 com Precision, respectivamente (hipótese a confirmar
pelo código das métricas). Correção da análise anterior: o caso 1 subiu para F1 0.77 nesta
rodada, então deixou de ser estável e baixo. Os casos com F1 abaixo de 0.63 em todas as cinco
rodadas são o 4 (0.60, 0.42, 0.54, 0.44, 0.29) e o 9 (0.54, 0.62, 0.55, 0.43, 0.50). O caso 4
também teve Clarity baixa (0.58 nesta rodada). Na Precision, os piores desta rodada foram os
casos 9 (0.43), 2 (0.47) e 10 (0.57). Próximo passo: avaliar a v2.4 e inspecionar no trace os
casos 4 e 9.
