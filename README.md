# 🍛 Curry Company — Dashboard de Visão Estratégica

Dashboard interativo em Streamlit para acompanhar a operação de entregas da Curry Company sob três óticas — Empresa, Entregadores e Restaurantes — com um notebook complementar de EDA e um modelo preditivo simples do tempo de entrega.

<p align="center">
<img src="./docs/images/image_8.png" alt="Dashboard Estratégico da Curry Company" width="800px">
</p>

**App em produção:** https://currycompanyproject-ggsolutions.streamlit.app

---

## 🚨 Problema de Negócio

A Curry Company é um marketplace de entregas que opera em múltiplas cidades da Índia, conectando restaurantes, entregadores e clientes. A gestão precisava acompanhar a operação sob três óticas ao mesmo tempo — crescimento do negócio, eficiência da frota de entregadores e performance logística dos restaurantes parceiros — sem depender de relatórios manuais e desatualizados espalhados em planilhas.

Além disso, o dataset operacional trazia armadilhas de qualidade que não aparecem numa inspeção superficial (valores ausentes mascarados como texto, em vez de nulos reais), o que tornava qualquer métrica calculada ingenuamente pouco confiável.

**Pergunta central:** Como está a operação de entregas da empresa, hoje, sob as óticas de negócio, frota e restaurantes — e o que isso indica sobre o tempo de entrega?

---

## 🗺️ Planejamento da Solução

A solução foi estruturada em 8 etapas:

1. **Descrição dos dados** — análise dimensional, tipagem e investigação da qualidade dos dados: descoberta de que colunas numéricas/categóricas usam a string literal `"NaN"` como sentinela de ausência, mascarando a real quantidade de dados faltantes de `df.isna()`.

2. **Limpeza e Feature Engineering** (`clean_code()` em [`src/utils.py`](./src/utils.py)) — correção de tipos, remoção das linhas com sentinela `"NaN"`, e criação da coluna `distancia_km` (fórmula de Haversine a partir das coordenadas de restaurante e entrega).

3. **Definição de KPIs de negócio** — Total de Pedidos, Total de Entregadores, Avaliação Média, e um SLA de entrega (% de pedidos concluídos em até 30 minutos) como meta fixa de negócio.

4. **Construção do dashboard** — 3 páginas Streamlit (Empresa, Entregadores, Restaurantes) compartilhando carregamento de dados (com cache), limpeza e sidebar de filtros via um módulo comum ([`src/utils.py`](./src/utils.py)).

5. **Análise exploratória** — no dashboard (gráficos interativos por tráfego, clima, cidade e festival) e num notebook dedicado, incluindo um mapa geográfico das entregas.

6. **Modelagem exploratória (bônus)** — [`notebooks/eda_e_modelo.ipynb`](./notebooks/eda_e_modelo.ipynb) treina e compara Regressão Linear e Random Forest para prever `Time_taken(min)`, como prova de conceito de que as variáveis disponíveis carregam sinal preditivo (não é um modelo de produção).

7. **Testes automatizados** — pytest cobrindo a função de limpeza de dados e o carregamento, para blindar o pipeline contra regressões.

8. **Deploy** — Streamlit Community Cloud, com versões de dependência fixadas em `requirements.txt`.

**Ferramentas:** Python (pandas, numpy, plotly, streamlit, scikit-learn), Streamlit Community Cloud, pytest.

---

## 🛠️ Desenvolvimento

### Dataset

| Atributo | Detalhe |
|---|---|
| Fonte | Dataset público de pedidos de um marketplace de food delivery na Índia |
| Linhas (bruto → após limpeza) | 45.593 → 41.419 |
| Entregadores únicos | 1.320 |
| Cidades | `Urban`, `Metropolitian` (typo original da fonte), `Semi-Urban` |
| Período coberto | 11/02/2022 a 06/04/2022 |
| Variável de interesse | `Time_taken(min)` — tempo de entrega em minutos |
| Granularidade | 1 linha = 1 pedido |

### Modelos Avaliados (notebook — previsão de `Time_taken(min)`)

| Modelo | MAE (min) | RMSE (min) | R² |
|---|---|---|---|
| Linear Regression | 5.58 | 6.98 | 0.428 |
| **Random Forest** | **4.27** | **5.45** | **0.652** |

A Random Forest supera a regressão linear por capturar interações não-lineares entre variáveis — por exemplo, o efeito combinado de tráfego pesado com dia de festival não é uma simples soma dos efeitos isolados. Esse modelo não foi implantado no dashboard: seu único propósito é validar, com números, que as variáveis operacionais disponíveis (tráfego, clima, distância, nº de entregas simultâneas) têm poder preditivo real sobre o tempo de entrega.

### Estrutura do Projeto

```text
curry_company_project/
├── archive/
│   └── legacy_aula/       # Algoritimos originais desenvolvidos nas aulas (não usados pelo app, mantidos como histórico).
├── assets/                # Imagens usadas pelo próprio dashboard (logos da sidebar, já otimizadas).
├── data/                  # O arquivo CSV com os dados operacionais (brutos/limpos).
├── docs/
│   └── images/            # Imagens usadas apenas na documentação (README).
├── notebooks/
│   └── eda_e_modelo.ipynb # Investigação de qualidade de dados, EDA e um modelo preditivo simples do tempo de entrega.
├── pages/                 # Páginas do dashboard Streamlit (Visão Empresa, Visão Entregadores, Visão Restaurantes).
├── src/
│   └── utils.py           # Limpeza de dados, carregamento (com cache) e sidebar, compartilhados pelas páginas.
├── tests/
│   └── test_utils.py      # Testes automatizados (pytest) para a limpeza e o carregamento dos dados.
├── .gitignore             # Arquivos e pastas a serem ignorados pelo Git.
├── Home.py                # Landing page do dashboard, com o menu de navegação entre as 3 visões.
├── LICENSE                # Licença MIT do projeto.
├── README.md              # Documentação principal do projeto.
├── requirements.txt       # Bibliotecas necessárias para rodar o dashboard (versões fixas).
└── requirements-dev.txt   # Bibliotecas extras para rodar o notebook e os testes (scikit-learn, pytest, etc.).
```

---

## 💡 Top Insights

### 1. 📏 Distância percorrida quase não explica o tempo de entrega

A intuição diria que o principal driver do tempo de entrega é a distância até o cliente. Os dados mostram o oposto: a correlação linear entre `distancia_km` e `Time_taken(min)` é praticamente nula (**r ≈ -0,002**). O tempo de entrega é ditado por fatores operacionais, não pela rota em si.

---

### 2. 🛵 O maior preditor do tempo de entrega é o número de entregas simultâneas do entregador

No modelo Random Forest, `multiple_deliveries` é a feature mais importante (**20,5%** da importância total) — à frente de qualquer variável isolada de trânsito ou clima. Entregadores fazendo múltiplas entregas na mesma rota atrasam o pedido individual, um efeito operacional maior do que qualquer condição externa.

---

### 3. 🚦 Trânsito leve é o sinal mais forte de entrega rápida

`Road_traffic_density = Low` é a segunda feature mais importante do modelo (**18,4%**). Na Visão Entregadores do dashboard, a avaliação e o tempo médio em tráfego `Jam` pioram de forma visível frente a tráfego `Low`, confirmando o padrão também na percepção do cliente.

---

### 4. 🎉 Dias de festival tornam a operação mais lenta *e* mais instável

Na Visão Restaurantes, filtrar por Festival mostra não só um tempo médio de entrega maior, como um coeficiente de variação mais alto — a operação some previsibilidade, não apenas velocidade, exatamente nos dias de maior demanda.

---

### 5. 🕵️ Qualidade de dados: quase 5 mil linhas de ausências estavam invisíveis

O dataset bruto usa a string `"NaN"` como sentinela de ausência em vez de um nulo real, então `df.isna().sum()` reporta zero em todas as colunas. Contagem real de ausências: `Delivery_person_Age` (1.854), `Delivery_person_Ratings` (1.908), `Road_traffic_density` (601), `multiple_deliveries` (993), `Festival` (228), `City` (1.200) — tratadas explicitamente em `clean_code()`.

---

## 📊 Resultados

### KPIs Atuais da Operação (Visão Empresa)

| KPI | Valor |
|---|---|
| Total de Pedidos (após limpeza) | 41.419 |
| Total de Entregadores | 1.320 |
| Avaliação Média dos Entregadores | 4,63 / 5 |
| % de Pedidos dentro do SLA (≤ 30 min) | 69,4% |
| Tempo Médio de Entrega | 26,55 min |

### Dashboard em Produção

As três visões (Empresa, Entregadores, Restaurantes) são interativas e filtráveis por data e tipo de tráfego pela barra lateral — acesse em [currycompanyproject-ggsolutions.streamlit.app](https://currycompanyproject-ggsolutions.streamlit.app).

### Performance do Modelo Exploratório (Random Forest)

| Métrica | Valor |
|---|---|
| MAE | 4,27 min |
| RMSE | 5,45 min |
| R² | 0,652 |

---

## ✅ Conclusões

O dashboard entrega, em tempo real e sem depender de relatórios manuais, uma visão consolidada da operação sob três óticas de negócio. O SLA de 69,4% (meta de 30 min) e a avaliação média de 4,63 dão à gestão uma linha de base clara para metas futuras. O notebook exploratório mostra que o tempo de entrega tem sinal preditivo real a partir de variáveis operacionais — com destaque para o achado contraintuitivo de que a distância percorrida importa muito menos do que o número de entregas simultâneas por entregador.

**Próximos passos:**
- Investigar por que `distancia_km` tem correlação quase nula com o tempo — possível efeito de coordenadas de origem/destino com ruído de coleta (algumas fora da faixa geográfica válida da Índia, já filtradas no mapa da Visão Empresa).
- Expandir o modelo exploratório com validação cruzada e tuning de hiperparâmetros, caso a ideia evolua para um modelo de produção.
- Adicionar alertas automáticos no dashboard para cidades ou janelas de tempo com SLA abaixo da meta.

**Limitações:** O dataset cobre um período de menos de 2 meses (fev–abr/2022) em cidades específicas da Índia; sazonalidades de médio/longo prazo e expansão para novas cidades não estão refletidas nas análises.

---
