from pathlib import Path


class RAGService:
    KNOWLEDGE_DIR = Path("app/ai/knowledge")

    @staticmethod
    def load_documents() -> list[dict]:
        documents = []

        if not RAGService.KNOWLEDGE_DIR.exists():
            return documents

        for file_path in RAGService.KNOWLEDGE_DIR.glob("*.md"):
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            documents.append(
                {
                    "source": file_path.name,
                    "content": content,
                }
            )

        return documents

    @staticmethod
    def retrieve(
        query: str,
        limit: int = 3,
    ) -> list[dict]:
        documents = RAGService.load_documents()

        if not documents:
            return []

        query_words = {
            word.lower().strip(".,!?")
            for word in query.split()
            if len(word.strip()) > 2
        }

        scored_documents = []

        for document in documents:
            content_lower = document["content"].lower()
            score = 0

            for word in query_words:
                if word in content_lower:
                    score += 1

            scored_documents.append(
                {
                    "source": document["source"],
                    "content": document["content"],
                    "score": score,
                }
            )

        scored_documents.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        selected_documents = [
            item
            for item in scored_documents
            if item["score"] > 0
        ]

        if not selected_documents:
            selected_documents = scored_documents[:limit]

        return selected_documents[:limit]

    @staticmethod
    def build_context(
        query: str,
    ) -> tuple[str, list[str]]:
        documents = RAGService.retrieve(
            query=query,
        )

        context_parts = []
        sources = []

        for document in documents:
            sources.append(document["source"])
            context_parts.append(
                f"Source: {document['source']}\n{document['content']}"
            )

        return "\n\n---\n\n".join(context_parts), sources