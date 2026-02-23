# Protótipo de Triagem — Protocolo de Manchester (Flask)

Protótipo web desenvolvido como projeto de TCC para **simular** uma triagem baseada no **Protocolo de Manchester**, coletando dados do paciente, sintomas e respostas a perguntas para retornar uma **classificação de risco** (ex.: vermelho/laranja/amarelo/verde) e gerar um relatório das triagens realizadas na sessão.

> ⚠️ **Aviso importante:** este projeto é **educacional/experimental**.  
> **Não é um dispositivo médico** e **não deve** ser utilizado para diagnóstico, prescrição ou tomada de decisão clínica real.

---

## ✨ Funcionalidades

- Cadastro/identificação do paciente (nome, data/idade, sexo)
- Seleção de um ou mais sintomas
- Perguntas dinâmicas por sintoma
- Classificação por cor (prioridade) com mensagem explicativa
- Relatório das triagens feitas durante a execução do app (em memória)

---

## 🧰 Tecnologias

- **Python**
- **Flask** (renderização com **Jinja2**)
- **HTML + Bootstrap** (interface)

---

## 📁 Estrutura do projeto (arquitetura organizada)
run.py
├── requirements.txt
├── app/
│ ├── init.py # create_app() e config do Flask
│ ├── routes.py # rotas (Blueprint)
│ ├── models.py # dados em memória (protótipo)
│ └── services/
│ └── triagem_service.py # regras e classificação (Manchester)
└── templates/
├── base.html
├── index.html
├── identificacao.html
├── sintoma.html
├── perguntas.html
├── resultado.html
└── relatorio.html


> Obs.: por ser um protótipo, os dados ficam **em memória** (variáveis Python).  
> Em produção, o ideal é usar um **banco de dados**.

---

## ✅ Pré-requisitos

- Python 3.10+ (recomendado)
- pip

---

## ▶️ Como rodar localmente

1) Clone o repositório:
```bash
git clone https://github.com/devpedropavanello/PrototipoTriagemManchester.git
cd PrototipoTriagemManchester

Crie e ative um ambiente virtual:

Windows (PowerShell):

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Linux/macOS:

python -m venv .venv
source .venv/bin/activate

Instale as dependências:

pip install -r requirements.txt

(Opcional) Defina a SECRET_KEY (recomendado):

Windows (PowerShell):

$env:SECRET_KEY="coloque-uma-chave-forte-aqui"

Linux/macOS:

export SECRET_KEY="coloque-uma-chave-forte-aqui"

Rode a aplicação:

python run.py

Abra no navegador:

http://127.0.0.1:5000

🔐 Sobre a SECRET_KEY

A SECRET_KEY é usada pelo Flask para assinar cookies/sessões e proteger mensagens flash.
Para desenvolvimento, qualquer valor funciona; para produção, use uma chave forte e mantenha em variável de ambiente.

Exemplo de chave forte:

32+ bytes aleatórios (hex/base64)

nunca commitar a chave no repositório

🧪 Cenários de teste (cores)

O sistema considera, por sintoma:

Vermelho: “sim” em perguntas críticas

Laranja: “sim” em perguntas urgentes

Amarelo: “sim” em qualquer outra pergunta

Verde: todas “não”

Sugestão rápida:

Para vermelho, responda “sim” em uma pergunta marcada como crítica (ex.: em Dor no peito, “suor/enjoo/falta de ar” ou “irradia para braço/mandíbula/costas”).

Para laranja, responda “sim” em uma pergunta marcada como urgente (ex.: em Dor no peito, “começou de repente?”).

Para amarelo, responda “sim” em qualquer pergunta não crítica/urgente.

Para verde, responda “não” em tudo.

Obs.: com múltiplos sintomas, o sistema seleciona a cor mais grave encontrada.

🚀 Próximos passos (ideias)

Persistência em banco (SQLite/MySQL/PostgreSQL)

API REST (separando front e back) e autenticação

Logs e testes automatizados (pytest)

Deploy (Gunicorn + Docker)

👤 Autor

Pedro Pavanello
Projeto de TCC — Engenharia de Software (Univassouras) (ajuste aqui se quiser)

📄 Licença

Defina a licença que você quiser (MIT é comum para projetos públicos).
Se não quiser liberar geral, pode manter “All rights reserved”.


---

Se você quiser, eu também posso:
- sugerir uma **licença** adequada (MIT vs “All rights reserved”) pro seu caso,
- te dizer **o que revisar antes de deixar público** (ex.: dados sensíveis, chaves, prints, nomes reais),
- e depois que você colocar o README, eu reviso e ajusto a linguagem pro TCC (mais acadêmica ou mais “portfólio”).
::contentReference[oaicite:4]{index=4}
