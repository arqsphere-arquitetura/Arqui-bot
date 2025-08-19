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
def process_pdf(pdf_path, plano, append=False):
    pages = extract_pdf_text(pdf_path)
    data = []

    for page_num, page_text in pages:
        chunks = split_text(page_text)
        for i, chunk in enumerate(chunks, start=1):
            ref = f"Plano {plano} - {os.path.basename(pdf_path)} - Página {page_num}, Bloco {i}"
            embedding = embed_text(chunk)
            data.append({
                "text": chunk,
                "ref": ref,
                "embedding": embedding
            })

    output_path = f"data/base_{plano.lower()}.jsonl"
    mode = "a" if append else "w"

    with open(output_path, mode, encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ {plano} atualizado com {len(data)} blocos de {os.path.basename(pdf_path)}")


# ---- MAIN ----
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    # --- Plano Médio (1 PDF apenas) ---
    process_pdf("medio.pdf", plano="Médio")

    # --- Plano Premium (todos PDFs dentro da pasta premium_pdfs) ---
    premium_pdfs = "premium_pdfs"
    first = True
    for pdf_file in os.listdir(premium_pdfs):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(premium_pdfs, pdf_file)
            process_pdf(pdf_path, plano="Premium", append=not first)
            first = False

    print("🚀 Todos os planos processados com sucesso!")
