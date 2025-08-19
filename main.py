import os
import telebot
from telebot import types

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

# Simulação da "base de alunos"
alunos = {
    "aluno1@email.com": "medio",
    "aluno2@email.com": "premium"
}

# Estado temporário
esperando_email = {}

# ----------- NOVO START COM BOTÃO "COMEÇA AGORA" -----------

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📧 Insere o teu email para desbloquear")
    btn2 = types.KeyboardButton("🆘 Preciso de ajuda")
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "👋 Olá, bem-vindo(a) à *Arqui Bot*! 🚀\n\nEscolhe uma opção para começar:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ----------- O RESTO DO TEU FLUXO CONTINUA IGUAL -----------

@bot.message_handler(func=lambda msg: msg.text == "🆘 Preciso de ajuda")
def help_message(message):
    bot.send_message(message.chat.id, "📩 Suporte ao cliente: arqsphere.arquitetura@gmail.com")

@bot.message_handler(func=lambda msg: msg.text == "📧 Insere o teu mail para desbloquear")
def ask_email(message):
    esperando_email[message.chat.id] = True
    bot.send_message(message.chat.id, "Por favor, insere o teu email para verificarmos o teu acesso:")

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

def botoes_medio(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤖 A Arqui responde", "📩 Falar com suporte")
    markup.add("💎 Desbloqueia Premium", "🌐 Segue a ArqSphere")
    bot.send_message(message.chat.id, "✅ Acesso Médio desbloqueado!", reply_markup=markup)

def botoes_premium(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤖 A Arqui responde", "📩 Falar com suporte")
    markup.add("📂 Acessar Drive", "🌐 Segue a ArqSphere")
    bot.send_message(message.chat.id, "✨ Acesso Premium desbloqueado!", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📩 Falar com suporte")
def suporte(message):
    bot.send_message(message.chat.id, "📧 arqsphere.arquitetura@gmail.com")

@bot.message_handler(func=lambda msg: msg.text == "💎 Desbloqueia Premium")
def premium_link(message):
    bot.send_message(message.chat.id, "👉 Acede aqui: https://landing.arqsphere.com/premium")

@bot.message_handler(func=lambda msg: msg.text == "🌐 Segue a ArqSphere")
def redes(message):
    bot.send_message(message.chat.id, "🌍 Redes sociais:\nInstagram: https://www.instagram.com/arqsphere/\nPinterest: https://pt.pinterest.com/ArqSphere/\nFacebook:https://www.facebook.com/share/17BeqxVWTv/")

@bot.message_handler(func=lambda msg: msg.text == "📂 Acessar Drive")
def drive(message):
    bot.send_message(message.chat.id, "📂 Drive Premium: https://drive.google.com/xxxx")

if __name__ == "__main__":
    print("Bot a correr 🚀")
    bot.infinity_polling()
