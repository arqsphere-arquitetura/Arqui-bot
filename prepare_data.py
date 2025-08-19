import os
import json
from PyPDF2 import PdfReader
from openai import OpenAI

# ---- Configurações ----
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# ---- Função para criar embeddings ----
def embed_text(text):
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding

# ---- Extrair texto dos PDFs ----
def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            pages.append((i, text))
    return pages

# ---- Dividir texto em blocos ----
def split_text(text, max_length=500):
    sentences = text.split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) < max_length:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())
    return chunks

# ---- Processar PDF em JSONL ----
def process_pdf(pdf_path, output_path, plano):
    pages = extract_pdf_text(pdf_path)
    data = []

    for page_num, page_text in pages:
        chunks = split_text(page_text)
        for i, chunk in enumerate(chunks, start=1):
            ref = f"Plano {plano} - Página {page_num}, Bloco {i}"
            embedding = embed_text(chunk)
            data.append({
                "text": chunk,
                "ref": ref,
                "embedding": embedding
            })

    with open(output_path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ {plano} pronto: {len(data)} blocos salvos em {output_path}")

# ---- MAIN ----
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    # Médio (ficheiro único)
    process_pdf("medio.pdf", "data/base_medio.jsonl", plano="Médio")

    # Premium (vários PDFs dentro da pasta)
    premium_folder = "premium_pdfs"
    premium_output = "data/base_premium.jsonl"

    premium_data = []
    for pdf_file in os.listdir(premium_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(premium_folder, pdf_file)
            print(f"📄 Processando {pdf_file}...")
            pages = extract_pdf_text(pdf_path)
            for page_num, page_text in pages:
                chunks = split_text(page_text)
                for i, chunk in enumerate(chunks, start=1):
                    ref = f"Premium - {pdf_file}, Página {page_num}, Bloco {i}"
                    embedding = embed_text(chunk)
                    premium_data.append({
                        "text": chunk,
                        "ref": ref,
                        "embedding": embedding
                    })

    with open(premium_output, "w", encoding="utf-8") as f:
        for entry in premium_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✨ Premium pronto: {len(premium_data)} blocos salvos em {premium_output}")
