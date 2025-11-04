# Triage Robot MVP


Este projeto detecta rostos pela webcam, conversa com o paciente e realiza uma triagem básica.


## Como executar


1. Crie um ambiente virtual:
python -m venv .venv
source .venv/bin/activate (Linux/Mac) ou .venv\Scripts\activate (Windows)


2. Instale dependências:
pip install -r requirements.txt


3. Ajuste o endpoint do n8n no arquivo src/config.py


4. Execute:
python src/main.py


## Fluxo
- Detecta rosto
- Libera gravação
- Envia áudio para n8n
- Aguarda resposta em áudio
- Salva triagem em data/sessions/