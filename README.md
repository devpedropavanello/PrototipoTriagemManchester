Protótipo de Triagem — Protocolo de Manchester (Flask)

Protótipo web desenvolvido como projeto de TCC para simular uma triagem baseada no Protocolo de Manchester, coletando dados do paciente, sintomas e respostas a perguntas para retornar uma classificação de risco (vermelho, laranja, amarelo ou verde).

⚠️ Projeto educacional e experimental.
Não substitui avaliação médica e não deve ser utilizado para decisões clínicas reais.

✨ Funcionalidades

Identificação do paciente (nome, data de nascimento e sexo)

Seleção de um ou mais sintomas

Perguntas dinâmicas conforme o(s) sintoma(s)

Classificação por cor com mensagem explicativa

Relatório das triagens realizadas (armazenadas em memória)

🧰 Tecnologias

Python

Flask (Jinja2)

HTML + Bootstrap

📁 Estrutura do Projeto
.
├── run.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   └── services/
│       └── triagem_service.py
└── templates/
    ├── base.html
    ├── index.html
    ├── identificacao.html
    ├── sintoma.html
    ├── perguntas.html
    ├── resultado.html
    └── relatorio.html

Observação: por se tratar de um protótipo acadêmico, os dados são armazenados apenas em memória.

✅ Pré-requisitos

Python 3.10+

pip



👤 Autor

Pedro Pavanello
Engenharia de Software — Univassouras
