from pathlib import Path
import chromadb

DOCS = Path(__file__).parent / "data" / "docs"

def chunk(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    out, start = [], 0
    while start < len(text):
        out.append(text[start:start + size])
        start += size - overlap
    return out

def main():
    client = chromadb.PersistentClient(path="chroma_db")
    try:
        client.delete_collection("docs")
    except Exception:
        pass
    col = client.get_or_create_collection("docs")
    for f in sorted(DOCS.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        for i, c in enumerate(chunk(text)):
            col.add(
                ids=[f"{f.stem}-{i}"],
                documents=[c],
                metadatas=[{"doc_id": f.stem, "trusted": True}],
            )
    print("Ingest done. Chunks:", col.count())

if __name__ == "__main__":
    main()