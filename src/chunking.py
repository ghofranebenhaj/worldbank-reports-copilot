import hashlib
from pypdf import PdfReader


def read_pdf(path):
    reader = PdfReader(path)
    return [(i, page.extract_text() or "") for i, page in enumerate(reader.pages, start=1)]


def make_chunks(pages, size=800, overlap=100):
    chunks = []
    step = max(size - overlap, 1)
    for page_number, text in pages:
        text = " ".join((text or "").split())
        for start in range(0, len(text), step):
            piece = text[start : start + size].strip()
            if len(piece) > 50:
                chunks.append({"page": page_number, "content": piece})
    return chunks


def content_hash(content, config):
    return hashlib.sha256(f"{config}|{content}".encode("utf-8")).hexdigest()
