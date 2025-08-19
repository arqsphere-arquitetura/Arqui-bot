import os
import telebot
from telebot import types

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

# Simulação da "base de alunos"
alunos = {
    "aluno1@email.com": "medio",
    "aluno2@email.com": "premium",
    "arqsphere.arquitetura@gmail.com":"premium"
}

# Estado temporário
esperando_email = {}

# ----------- START COM BOTÕES INLINE -----------

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📧 Insere o teu email para desbloquear", callback_data="inserir_email")
    btn2 = types.InlineKeyboardButton("🆘 Preciso de ajuda", callback_data="ajuda")
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "👋 Olá, bem-vindo(a) à *Arqui Bot*! 🚀\n\nEscolhe uma opção para começar:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ----------- CALLBACK QUANDO CLICA NOS BOTÕES -----------

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "ajuda":
        bot.send_message(call.message.chat.id, "📩 Suporte ao cliente: arqsphere.arquitetura@gmail.com")

    elif call.data == "inserir_email":
        esperando_email[call.message.chat.id] = True
        bot.send_message(call.message.chat.id, "Por favor, insere o teu email para verificarmos o teu acesso:")

# ----------- VERIFICAR EMAIL -----------

@bot.message_handler(func=lambda msg: msg.chat.id in esperando_email)
def verify_email(message):
    email = message.text.strip().lower()
    plano = alunos.get(email)

    if plano:
        del esperando_email[message.chat.id]
        if plano == "medio":
            botoes_medio(message)
        elif plano == "premium":
            botoes_premium(message)
    else:
        bot.send_message(message.chat.id, "❌ Email não encontrado. Tenta novamente ou contacta o suporte.")

# ----------- MENUS INLINE MEDIO / PREMIUM -----------

def botoes_medio(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🤖 A Arqui responde", callback_data="arqui_responde"),
        types.InlineKeyboardButton("📩 Falar com suporte", callback_data="ajuda")
    )
    markup.add(
        types.InlineKeyboardButton("💎 Desbloqueia Premium", url="https://landing.arqsphere.com/premium"),
        types.InlineKeyboardButton("🌐 Segue a ArqSphere", url="https://www.instagram.com/arqsphere/")
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
        types.InlineKeyboardButton("🌐 Segue a ArqSphere", url="https://www.instagram.com/arqsphere/")
    )
    bot.send_message(message.chat.id, "✨ Acesso Premium desbloqueado!", reply_markup=markup)

# ----------- PLACEHOLDERS PARA CALLBACKS FUTUROS -----------

@bot.callback_query_handler(func=lambda call: call.data == "arqui_responde")
def arqui_responde(call):
    bot.send_message(call.message.chat.id, "🤖 Escreve a tua dúvida e a Arqui vai responder com base nos ebooks!")

if __name__ == "__main__":
    print("Bot a correr 🚀")
    bot.infinity_polling()
