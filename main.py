import os
import json
import telebot
from telebot import types
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ---- Configurações ----
API_KEY = os.getenv("API_KEY")  # Token do BotFather
bot = telebot.TeleBot(API_KEY)

# ---- Carregar bases já com embeddings ----
def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

base_medio = load_jsonl("data/base_medio.jsonl")
base_premium = load_jsonl("data/base_premium.jsonl")

# ---- Simulação da "base de alunos" ----
alunos = {
    "aluno1@email.com": "medio",
    "aluno2@email.com": "premium",
    "arqsphere.arquitetura@gmail.com": "premium"
}

esperando_email = {}
plano_ativo = {}  # Guarda o plano do aluno (medio/premium)

# ---- START ----
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

# ---- CALLBACKS ----
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "ajuda":
        bot.send_message(call.message.chat.id, "📩 Suporte ao cliente: arqsphere.arquitetura@gmail.com")

    elif call.data == "inserir_email":
        esperando_email[call.message.chat.id] = True
        bot.send_message(call.message.chat.id, "Por favor, insere o teu email para verificarmos o teu acesso:")

    elif call.data == "redes":
        mostrar_redes(call)

    elif call.data == "voltar_menu":
        if plano_ativo.get(call.message.chat.id) == "medio":
            botoes_medio(call.message)
        elif plano_ativo.get(call.message.chat.id) == "premium":
            botoes_premium(call.message)

# ---- Verificar Email ----
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

# ---- Menus ----
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

# ---- Submenu Redes ----
def mostrar_redes(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/arqsphere/"),
        types.InlineKeyboardButton("📘 Facebook", url="https://www.facebook.com/share/17BeqxVWTv/")
    )
    markup.add(
        types.InlineKeyboardButton("📌 Pinterest", url="https://pt.pinterest.com/ArqSphere/"),
        types.InlineKeyboardButton("📰 Blog", url="https://arqsphere.wixsite.com/arqsphere")
    )
    markup.add(types.InlineKeyboardButton("🔙 Voltar", callback_data="voltar_menu"))

    bot.send_message(call.message.chat.id, "🌐 Segue a ArqSphere nas nossas redes:", reply_markup=markup)

# ---- A Arqui responde ----
@bot.callback_query_handler(func=lambda call: call.data == "arqui_responde")
def arqui_responde(call):
    bot.send_message(call.message.chat.id, "🤖 Estou feliz por te ajudar! Qual a tua dúvida?")

@bot.message_handler(func=lambda msg: plano_ativo.get(msg.chat.id) in ["medio", "premium"])
def resposta_aluno(message):
    pergunta = message.text
    plano = plano_ativo.get(message.chat.id)

    # Escolhe a base correta
    base = base_medio if plano == "medio" else base_premium

    if not base:
        bot.send_message(message.chat.id, "⚠️ Não encontrei dados na base de conhecimento.")
        return

    # Embedding já vem do JSONL
    pergunta_vec = np.array(message.text.encode("utf-8")).astype(float)  # placeholder só p/ cálculo simples
    # Mas a comparação real é feita com embeddings já guardados
    embeds = [entry["embedding"] for entry in base]
    textos = [entry["text"] for entry in base]

    # Similaridade
    sims = cosine_similarity([embeds[0]], embeds)[0]  # BUG: aqui temos que usar embedding da pergunta

    # 🚨 Ajuste: como já tens os embeddings salvos, precisamos de gerar também o embedding da pergunta com OpenAI
    # mas não armazenar — só calcular em runtime.

    bot.send_message(message.chat.id, "⚠️ A versão atual ainda precisa de calcular embedding da pergunta em runtime.")
    bot.send_message(message.chat.id, "👉 Vamos corrigir isso já no próximo passo.")
    
# ---- RUN ----
if __name__ == "__main__":
    print("Bot a correr 🚀")
    bot.infinity_polling()
