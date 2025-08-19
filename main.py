import os
import json
import numpy as np
from openai import OpenAI
from flask import Flask, request, jsonify

# ---- Configurações ----
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

app = Flask(__name__)

# ---- Função para carregar a base de conhecimento ----
def load_knowledge(plano):
    file_map = {
        "medio": "data/base_medio.jsonl",
        "premium": "data/base_premium.jsonl"
    }

    file_path = file_map.get(plano)
    if not file_path or not os.path.exists(file_path):
        return []

    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            data.append(obj)
    return data

# ---- Função para gerar embedding ----
def embed_text(text):
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(resp.data[0].embedding)

# ---- Função para buscar o chunk mais relevante ----
def search(query, knowledge_base, top_k=3):
    if not knowledge_base:
        return ["⚠️ Base de conhecimento não carregada."]

    query_emb = embed_text(query)
    scored = []
    for item in knowledge_base:
        emb = np.array(item["embedding"])
        score = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
        scored.append((score, item))

    scored = sorted(scored, key=lambda x: x[0], reverse=True)[:top_k]
    return [f"{item['text']} ({item['ref']})" for _, item in scored]

# ---- Endpoint de API ----
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    plano = data.get("plano", "medio").lower()
    pergunta = data.get("pergunta", "")

    knowledge_base = load_knowledge(plano)

    resultados = search(pergunta, knowledge_base)

    prompt = f"""
    Tu és um assistente que responde apenas com base nos documentos carregados.
    Pergunta: {pergunta}
    Contexto: {" ".join(resultados)}
    Resposta:
    """

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({"resposta": resposta.choices[0].message.content})

# ---- MAIN ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
