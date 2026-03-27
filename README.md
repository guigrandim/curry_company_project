# Curry Company Project: Visão Estratégica Dashboard

https://currycompanyproject-ggsolutions.streamlit.app

<p align="center">
<img src="./assets/image_8.png" alt="Dashboard Estratégico da Curry Company" width="800px">
</p>

📊 Visão Geral do Projeto
Esse projeto foi desenvolvido como parte dos estudos da Comunidade DS - FTC: Analisando Dados com Python. Esse é um prototipo desenvolvido
em aula em conjunto com o professor Meigarom Lopes. O principal desenvolvimento foi uma solução de inteligência de dados centralizada: um Dashboard de Visão Estratégica interativo utilizando Python e Streamlit. Esta ferramenta transforma dados brutos em insights acionáveis, permitindo o acompanhamento de KPIs cruciais através de três perspectivas principais: Empresa, Entregadores e Restaurantes.

______________________________________________________________________________________________________________________________________________

🛠️ Stack Técnica
As seguintes ferramentas e bibliotecas foram utilizadas no desenvolvimento deste projeto:
- Linguagem: Python 3.8+
- Framework Web: Streamlit
- Manipulação de Dados: Pandas, NumPy
- Visualização de Dados: Plotly, Matplotlib
- Gerenciamento de Ambiente: pip
____________________________________________________________________________________________________________________________________________

📂 Arquitetura do Projeto
A estrutura do repositório está organizada da seguinte forma:

curry_company_project/
├── assets/             # Imagens e recursos visuais utilizados no README e no dashboard.
├── codigos_v1          # Algoritimos originais desenvolvidos nas aulas
├── dataset/            # O arquivo CSV com os dados operacionais (brutos/limpos).
├── pages/              # Páginas secundárias do dashboard Streamlit (Visão Entregadores, Visão Restaurantes).
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git.
├── Home.py             # Arquivo principal que renderiza a página inicial do dashboard (Visão Empresa).
├── LICENSE             # Licença MIT do projeto.
├── README.md           # Documentação principal do projeto.
└── requirements.txt    # Lista de bibliotecas Python necessárias.

______________________________________________________________________________________________________________________________________________

📈 Funcionalidades e Visualizações
O dashboard está dividido em três visões estratégicas, acessíveis pelo menu lateral e todos os gráficos são interativos podendo ser filtrados por intervalo de datas e pelo tipo de trafego no menu lateral:

1. Visão Empresa (Página Inicial)
- Focada em métricas gerenciais e comportamento.
- Métricas Chave (KPIs): Total de Pedidos, Total de Entregadores, Receita (simulada), Satisfação Média (NPS).
- Gráficos: Volume de pedidos por dia e por semana, distribuição de pedidos por tipo de tráfego e por tipo de cidade

2. Visão Entregadores
- Focada na eficiência operacional da frota.
- Métricas Chave: Média de idade dos entregadores, avaliação média, tempo médio de entrega e qualidade da frota
- Gráficos: Tabelas de avaliações dos entregadores, avaliação média por trafego e por clima, entregadores mais rápidos e mais lentos

3. Visão Restaurantes
- Focada na performance dos parceiros e logística de retirada.
- Métricas Chave: Total de restaurantes parceiros, distância média de entrega, previsibilidade da operação com e sem festival
- Gráficos: Distancia média por cidade, distribuição de tempo por cidade e tempo médio por entrega e media de entrega por cidade e trafego

_______________________________________________________________________________________________________________________________________________

👩‍💻 Autor
Desenvolvido por Guilherme Grandim conjunto da Comunidade DS. Fica meu agradecimento ao professor Meigarom Lopes pel conhececimento transmitido
Sinta-se à vontade para entrar em contato ou contribuir com o projeto!