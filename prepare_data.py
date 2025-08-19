
import os
import json
import pickle
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_embeddings(input_jsonl, output_pkl):
    data = []
    with open(input_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            texto = obj["text"]
            emb = openai.embeddings.create(
                model="text-embedding-3-small",
                input=texto
            )["data"][0]["embedding"]
            data.append({"text": texto, "embedding": emb})

    with open(output_pkl, "wb") as f:
        pickle.dump(data, f)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    gerar_embeddings("data/base_medio.jsonl", "data/base_medio.pkl")
    gerar_embeddings("data/base_premium.jsonl", "data/base_premium.pkl")
    print("✅ Embeddings gerados e guardados em data/*.pkl")
