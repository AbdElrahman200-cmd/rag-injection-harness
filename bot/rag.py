import chromadb

_client = chromadb.PersistentClient(path="chroma_db")
_col = _client.get_or_create_collection("docs")

def retrieve(query: str, k: int = 3) -> list[dict]:
    res = _col.query(query_texts=[query], n_results=k)
    out = []
    for text, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        out.append({
            "doc_id": meta["doc_id"],
            "text": text,
            "score": dist,
            "trusted": meta["trusted"],
        })
    return out