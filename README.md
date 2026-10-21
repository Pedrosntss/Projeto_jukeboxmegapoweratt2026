# Jukebox

## Configurar em um computador novo

O ambiente virtual (`.venv`) é local de cada computador e não deve ser enviado ao GitHub. Depois de clonar o projeto, crie um ambiente e instale as dependências.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para executar um programa:

```powershell
.\.venv\Scripts\python.exe .\Test_menu.py
```

No VS Code, use **Python: Select Interpreter** e selecione `.venv` dentro da pasta do projeto.

### Linux ou macOS

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python Test_menu.py
```

## Porta serial do Arduino

O nome da porta depende do computador e do sistema operacional. Antes de executar, ajuste `PORTA` no programa para a porta à qual o Arduino está conectado (por exemplo, `COM3` no Windows ou `/dev/ttyACM0` no Linux). A dependência `pyserial` é instalada pelo `requirements.txt`.
