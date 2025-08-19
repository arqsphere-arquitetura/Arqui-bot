import os
import telebot
from telebot import types

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

# Simulação da "base de alunos" (podes puxar de CSV, JSON ou DB)
alunos = {
    "aluno1@email.com": "medio",
    "aluno2@email.com": "premium"
}

# Estado temporário (guarda quem está a inserir email)
esperando_email = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("📧 Insere o teu mail para desbloquear", "🆘 Preciso de ajuda")
    bot.send_message(message.chat.id, "Bem-vindo à ArqSphere 🚀\nEscolhe uma opção:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🆘 Preciso de ajuda")
def help_message(message):
    bot.send_message(message.chat.id, "📩 Suporte ao cliente: suporte@arqsphere.com")

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
    bot.send_message(message.chat.id, "📧 suporte@arqsphere.com")

@bot.message_handler(func=lambda msg: msg.text == "💎 Desbloqueia Premium")
def premium_link(message):
    bot.send_message(message.chat.id, "👉 Acede aqui: https://landing.arqsphere.com/premium")

@bot.message_handler(func=lambda msg: msg.text == "🌐 Segue a ArqSphere")
def redes(message):
    bot.send_message(message.chat.id, "🌍 Redes sociais:\nInstagram: https://instagram.com/arqsphere\nLinkedIn: https://linkedin.com/company/arqsphere")

@bot.message_handler(func=lambda msg: msg.text == "📂 Acessar Drive")
def drive(message):
    bot.send_message(message.chat.id, "📂 Drive Premium: https://drive.google.com/xxxx")

# Futuro: implementar "🤖 A Arqui responde" → chamada ao modelo
# usando os ficheiros JSONL que já tens

if __name__ == "__main__":
    print("Bot a correr 🚀")
    bot.infinity_polling()
