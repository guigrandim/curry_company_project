# Curry Company Project: Visão Estratégica Dashboard

https://currycompanyproject-ggsolutions.streamlit.app

<p align="center">
<img src="./docs/images/image_8.png" alt="Dashboard Estratégico da Curry Company" width="800px">
</p>

## 📊 Visão Geral do Projeto

Esse projeto foi desenvolvido como parte dos estudos da Comunidade DS - FTC: Analisando Dados com Python, sendo um prototipo desenvolvido
em aula em conjunto com o professor Meigarom Lopes. O principal desenvolvimento foi uma solução de inteligência de dados centralizada: um Dashboard de Visão Estratégica interativo utilizando Python e Streamlit. Esta ferramenta transforma dados brutos em insights acionáveis, permitindo o acompanhamento de KPIs cruciais através de três perspectivas principais: Empresa, Entregadores e Restaurantes.

## 🛠️ Stack Técnica
As seguintes ferramentas e bibliotecas foram utilizadas no desenvolvimento deste projeto:
- Linguagem: Python 3.8+
- Framework Web: Streamlit
- Manipulação de Dados: Pandas, NumPy
- Visualização de Dados: Plotly, Matplotlib
- Gerenciamento de Ambiente: pip


## 📂 Arquitetura do Projeto
### A estrutura do repositório está organizada da seguinte forma:

```text
curry_company_project/
├── archive/
│   └── legacy_aula/    # Algoritimos originais desenvolvidos nas aulas (não usados pelo app, mantidos como histórico).
├── assets/             # Imagens usadas pelo próprio dashboard (logos da sidebar).
├── data/               # O arquivo CSV com os dados operacionais (brutos/limpos).
├── docs/
│   └── images/         # Imagens usadas apenas na documentação (README).
├── pages/              # Páginas secundárias do dashboard Streamlit (Visão Entregadores, Visão Restaurantes).
├── src/
│   └── utils.py        # Limpeza de dados, carregamento (com cache) e sidebar, compartilhados pelas páginas.
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git.
├── Home.py             # Arquivo principal que renderiza a página inicial do dashboard (Visão Empresa).
├── LICENSE             # Licença MIT do projeto.
├── README.md           # Documentação principal do projeto.
└── requirements.txt    # Lista de bibliotecas Python necessárias.
```

## 📈 Funcionalidades e Visualizações
#### O dashboard está dividido em três visões estratégicas, acessíveis pelo menu lateral e todos os gráficos são interativos podendo ser filtrados por intervalo de datas e pelo tipo de trafego no menu lateral:

1. Visão Empresa (Página Inicial)
- Focada em métricas gerenciais e comportamento.
- Métricas Chave (KPIs): Total de Pedidos, Total de Entregadores, Avaliação Média dos Entregadores, % de Pedidos dentro do SLA (meta de 30 min).
- Gráficos: Volume de pedidos por dia e por semana, distribuição de pedidos por tipo de tráfego e por tipo de cidade

2. Visão Entregadores
- Focada na eficiência operacional da frota.
- Métricas Chave: Idade mínima/máxima dos entregadores, qualidade da frota (faixas documentadas na própria página)
- Gráficos: Avaliação média por tráfego e por clima; tabelas de avaliação por entregador e de entregadores mais rápidos/lentos por cidade

3. Visão Restaurantes
- Focada na performance dos parceiros e logística de retirada.
- Métricas Chave: Total de entregadores únicos, distância média de entrega, tempo médio e desvio-padrão de entrega (filtráveis por Festival: Todos/Sim/Não)
- Gráficos: Distancia média por cidade, distribuição de tempo por cidade e tempo médio por entrega e media de entrega por cidade e trafego

## 🔍 Qualidade e Tratamento de Dados

O dataset de origem contém armadilhas que não aparecem em uma inspeção superficial e que foram identificadas e tratadas na limpeza (`clean_code()`):

- **Valores ausentes mascarados**: colunas numéricas/categóricas trazem a string literal `"NaN"` em vez de um nulo real, então `df.isna().sum()` reporta zero ausências em qualquer coluna. Contagem real de ausências: `Delivery_person_Age` (1.854), `Delivery_person_Ratings` (1.908), `Road_traffic_density` (601), `multiple_deliveries` (993), `Festival` (228), `City` (1.200).
- **Prefixo redundante**: a coluna `Weatherconditions` mantém o texto `"conditions "` colado em cada valor (ex.: `"conditions Sunny"`).
- **Erro de digitação na fonte**: a coluna `City` traz o valor `"Metropolitian"` (typo original do dataset, não uma inconsistência introduzida no tratamento).

## 👩‍💻 Autor
 Desenvolvido por Guilherme Grandim durante as aulas da Comunidade DS como estudo para programação em Python e Streamlit. Fica meu agradecimento ao professor Meigarom Lopes pelo conhececimento transmitido.</br>
 Sinta-se à vontade para entrar em contato ou contribuir com o projeto!