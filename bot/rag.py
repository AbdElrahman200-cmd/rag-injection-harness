import chromadb

_client = chromadb.PersistentClient(path="chroma_db")


def _col():
    # Get the collection fresh each time, so it still works after re-running ingest.
    return _client.get_or_create_collection("docs")


def retrieve(query: str, k: int = 3) -> list[dict]:
    col = _col()
    total = col.count()
    if total == 0:
        return []
    res = col.query(query_texts=[query], n_results=min(k, total))
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


def add_document(doc_id: str, text: str, trusted: bool = False) -> None:
    """Used by /test/plant: adds one extra (planted) document to the knowledge base."""
    _col().upsert(
        ids=[f"planted-{doc_id}"],
        documents=[text],
        metadatas=[{"doc_id": doc_id, "trusted": trusted, "planted": True}],
    )


def reset() -> None:
    """Used by /test/reset: removes only the planted documents."""
    _col().delete(where={"planted": True})