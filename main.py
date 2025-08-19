import os
import telebot
from telebot import types
import openai
import pickle
import numpy as np

API_KEY = os.getenv("API_KEY")  # token do Telegram
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # token OpenAI
bot = telebot.TeleBot(API_KEY)
openai.api_key = OPENAI_API_KEY

# Carregar embeddings preparados
with open("data/base_medio.pkl", "rb") as f:
    base_medio = pickle.load(f)
with open("data/base_premium.pkl", "rb") as f:
    base_premium = pickle.load(f)

# Base de alunos (demo)
alunos = {
    "aluno1@email.com": "medio",
    "aluno2@email.com": "premium",
    "arqsphere.arquitetura@gmail.com": "premium"
}

esperando_email = {}
plano_ativo = {}

# ----------- FUNÇÃO BUSCA SEMÂNTICA -----------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def buscar_contexto(pergunta, plano):
    # Escolhe base conforme plano
    base = base_medio if plano == "medio" else base_premium
    # Embedding da pergunta
    emb = openai.embeddings.create(
        model="text-embedding-3-small",
        input=pergunta
    )["data"][0]["embedding"]

    # Calcular similaridade
    scores = []
    for item in base:
        score = cosine_similarity(np.array(emb), np.array(item["embedding"]))
        scores.append((score, item))

    # Ordenar por relevância
    scores.sort(key=lambda x: x[0], reverse=True)
    melhores = [s[1]["text"] for s in scores[:3]]

    return "\n\n".join(melhores)

def responder_aluno(pergunta, plano):
    contexto = buscar_contexto(pergunta, plano)

    prompt = f"""
    És a Arqui Bot, especialista em arquitetura.
    Usa o contexto abaixo para responder de forma clara e natural.

    Contexto:
    {contexto}

    Pergunta do aluno:
    {pergunta}

    Responde de forma curta, amigável e se necessário indica o capítulo/ponto onde pode encontrar mais detalhes.
    """

    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return resp.choices[0].message.content.strip()

# ----------- START -----------

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📧 Desbloquear acesso", callback_data="inserir_email")
    btn2 = types.InlineKeyboardButton("🆘 Preciso de ajuda", callback_data="ajuda")
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "👋 Olá, bem-vindo(a) à *Arqui Bot*! 🚀\n\nEscolhe uma opção para começar:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ----------- CALLBACKS -----------

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "ajuda":
        bot.send_message(call.message.chat.id, "📩 Suporte ao cliente: arqsphere.arquitetura@gmail.com")

    elif call.data == "inserir_email":
        esperando_email[call.message.chat.id] = True
        bot.send_message(call.message.chat.id, "Por favor, insere o teu email para verificarmos o teu acesso:")

    elif call.data == "arqui_responde":
        bot.send_message(call.message.chat.id, "🤖 Estou feliz por te ajudar! Qual a tua dúvida?")

# ----------- VERIFICAR EMAIL -----------

@bot.message_handler(func=lambda msg: msg.chat.id in esperando_email)
def verify_email(message):
    email = message.text.strip().lower()
    plano = alunos.get(email)

    if plano:
        del esperando_email[message.chat.id]
        plano_ativo[message.chat.id] = plano
        if plano == "medio":
            botoes_medio(message)
        elif plano == "premium":
            botoes_premium(message)
    else:
        bot.send_message(message.chat.id, "❌ Email não encontrado. Tenta novamente ou contacta o suporte.")

# ----------- MENUS -----------

def botoes_medio(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🤖 A Arqui responde", callback_data="arqui_responde"),
        types.InlineKeyboardButton("📩 Falar com suporte", callback_data="ajuda")
    )
    markup.add(
        types.InlineKeyboardButton("💎 Desbloqueia Premium", url="https://landing.arqsphere.com/premium"),
        types.InlineKeyboardButton("🌐 Segue a ArqSphere", callback_data="redes")
    )
    bot.send_message(message.chat.id, "✅ Acesso Médio desbloqueado!", reply_markup=markup)

def botoes_premium(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🤖 A Arqui responde", callback_data="arqui_responde"),
        types.InlineKeyboardButton("📩 Falar com suporte", callback_data="ajuda")
    )
    markup.add(
        types.InlineKeyboardButton("📂 Acessar Drive", url="https://drive.google.com/xxxx"),
        types.InlineKeyboardButton("🌐 Segue a ArqSphere", callback_data="redes")
    )
    bot.send_message(message.chat.id, "✨ Acesso Premium desbloqueado!", reply_markup=markup)

# ----------- CHAT LIVRE -----------

@bot.message_handler(func=lambda msg: plano_ativo.get(msg.chat.id) in ["medio", "premium"])
def chat_livre(message):
    plano = plano_ativo.get(message.chat.id)
    resposta = responder_aluno(message.text, plano)
    bot.send_message(message.chat.id, resposta)

if __name__ == "__main__":
    print("Bot a correr 🚀")
    bot.infinity_polling()
