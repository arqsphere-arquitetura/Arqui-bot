import os
import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove  # 👈 Import para remover teclado

API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

# Simulação da "base de alunos"
alunos = {
    "aluno1@email.com": "medio",
    "aluno2@email.com": "premium",
    "arqsphere.arquitetura@gmail.com": "premium"
}

# Estado temporário
esperando_email = {}
plano_ativo = {}   # <- guarda se o aluno é medio ou premium
modo_conversa = {} # <- guarda se o aluno está no "Arqui responde"

# ----------- START COM BOTÕES INLINE -----------

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
    # 🔹 Remove teclado antigo
    bot.send_message(message.chat.id, " ", reply_markup=ReplyKeyboardRemove())

# ----------- CALLBACK QUANDO CLICA NOS BOTÕES -----------

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

# ----------- VERIFICAR EMAIL -----------

@bot.message_handler(func=lambda msg: msg.chat.id in esperando_email)
def verify_email(message):
    email = message.text.strip().lower()
    plano = alunos.get(email)

    if plano:
        del esperando_email[message.chat.id]
        plano_ativo[message.chat.id] = plano  # guarda plano ativo
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
        types.InlineKeyboardButton("🌐 Segue a ArqSphere", callback_data="redes")
    )
    bot.send_message(message.chat.id, "✅ Acesso Médio desbloqueado!", reply_markup=markup)
    bot.send_message(message.chat.id, " ", reply_markup=ReplyKeyboardRemove())

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
    bot.send_message(message.chat.id, " ", reply_markup=ReplyKeyboardRemove())

# ----------- SUBMENU DE REDES SOCIAIS -----------

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
    bot.send_message(call.message.chat.id, " ", reply_markup=ReplyKeyboardRemove())

# ----------- "ARQUI RESPONDE" MODO CONVERSA -----------

@bot.callback_query_handler(func=lambda call: call.data == "arqui_responde")
def arqui_responde(call):
    modo_conversa[call.message.chat.id] = True

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="voltar_menu"))

    bot.send_message(
        call.message.chat.id,
        "🤖 Estou muito feliz em poder ajudar!\n\nEscreve a tua dúvida e vou responder com base nos materiais e ebooks 📚✨",
        reply_markup=markup
    )

# ----------- PROCESSAR MENSAGENS NO MODO CONVERSA -----------

@bot.message_handler(func=lambda msg: msg.chat.id in modo_conversa)
def responder_duvidas(message):
    pergunta = message.text.strip().lower()

    # Se o aluno digitar "menu", sai do modo conversa
    if pergunta in ["menu", "/menu"]:
        del modo_conversa[message.chat.id]
        if plano_ativo.get(message.chat.id) == "medio":
            botoes_medio(message)
        elif plano_ativo.get(message.chat.id) == "premium":
            botoes_premium(message)
        return

    # Placeholder de resposta automática
    resposta = f"📖 Boa questão!\nAinda não tenho ligação direta à base de ebooks, mas em breve vou poder responder automaticamente.\n\nRegistei a tua dúvida: *{message.text}*"
    bot.send_message(message.chat.id, resposta, parse_mode="Markdown")

# ------------------------------------------------------------

if __name__ == "__main__":
    print("Bot a correr 🚀")
    bot.infinity_polling()
