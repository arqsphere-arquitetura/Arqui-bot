import os
import json
from PyPDF2 import PdfReader
from openai import OpenAI

# ---- Configurações ----
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY não está definido nas variáveis de ambiente.")
client = OpenAI(api_key=OPENAI_KEY)

# Base do projeto (pasta onde este ficheiro está)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def p(*parts):  # cria caminhos absolutos seguros
    return os.path.join(BASE_DIR, *parts)

# ---- Função para criar embeddings ----
def embed_text(text):
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding

# ---- Extrair texto dos PDFs ----
def extract_pdf_text(pdf_path):
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Não encontrei o ficheiro: {pdf_path}")
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
            data.append({"text": chunk, "ref": ref, "embedding": embedding})

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ {plano} pronto: {len(data)} blocos salvos em {output_path}")

if __name__ == "__main__":
    os.makedirs(p("data"), exist_ok=True)

    # --------- M É D I O -----------
    medio_pdf = p("medio.pdf")  # ficheiro da RAIZ
    print(f"📘 A processar MÉDIO: {medio_pdf}")
    process_pdf(medio_pdf, p("data", "base_medio.jsonl"), plano="Médio")

    # -------- P R E M I U M --------
    premium_pdfs = [
        p("premium_pdfs", "portfolio.pdf"),  # renomeado
        p("premium_pdfs", "seo.pdf"),
    ]
    premium_output = p("data", "base_premium.jsonl")

    premium_data = []
    for pdf_path in premium_pdfs:
        print(f"💎 A processar PREMIUM: {pdf_path}")
        pages = extract_pdf_text(pdf_path)
        for page_num, page_text in pages:
            chunks = split_text(page_text)
            for i, chunk in enumerate(chunks, start=1):
                ref = f"Premium - {os.path.basename(pdf_path)}, Página {page_num}, Bloco {i}"
                embedding = embed_text(chunk)
                premium_data.append({"text": chunk, "ref": ref, "embedding": embedding})

    with open(premium_output, "w", encoding="utf-8") as f:
        for entry in premium_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✨ Premium pronto: {len(premium_data)} blocos salvos em {premium_output}")
