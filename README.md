# 🎧 Tribuna FM Discord Bot

Um bot simples para Discord que entra no canal de voz e toca a rádio **Tribuna FM 88.5**, ao vivo, via streaming. Ideal para quem curte ouvir música boa com os amigos direto do Discord.

---

## 🚀 Funcionalidades

- ✅ Conecta ao seu canal de voz com `!join`
- ✅ Reproduz a rádio Tribuna FM 88.5 ao vivo
- ✅ Sai do canal com `!leave`
- ✅ Leitura segura de token e caminho do FFmpeg via `.env`
- ✅ Totalmente personalizável e fácil de rodar

---

## ⚙️ Pré-requisitos

- Python 3.9+
- FFmpeg instalado
- Ambiente virtual Python (recomendado)

---

## 📦 Instalação

### 1. Clone o repositório

git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO

### 2. Crie e ative o ambiente virtual

python -m venv bot_tribuna
bot_tribuna\Scripts\activate

### 3. Instale as dependências

pip install -r requirements.txt

### 4. Configure o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com este conteúdo:

DISCORD_TOKEN=seu_token_do_bot_aqui
FFMPEG_PATH=C:\caminho\completo\para\ffmpeg.exe

Exemplo:

DISCORD_TOKEN=abc123xyz456
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe

---

## ▶️ Uso

Com o ambiente virtual ativado:

python bot.py

No Discord, use os comandos:

- !join → o bot entra no seu canal de voz e começa a tocar a rádio.
- !leave → o bot sai do canal de voz.

---

## 📡 Fonte do Stream

A rádio é transmitida via:

https://servidor22-2.brlogic.com:7076/live?source=8542

---

## 📃 Licença

MIT — use, modifique e compartilhe como quiser.
