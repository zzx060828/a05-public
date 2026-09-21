import threading

from sentence_transformers import CrossEncoder, SentenceTransformer, util


class SemanticDeduplicator:
    def __init__(
        self,
        bi_model_name: str = "all-mpnet-base-v2",
        cross_model_name: str = "BAAI/bge-reranker-base",
    ):
        self.bi_model_name = bi_model_name
        self.cross_model_name = cross_model_name
        self.bi_model = None
        self.cross_model = None
        self._load_lock = threading.Lock()
        print(
            "\n[System] Semantic deduplication module initialized. "
            "Models will load on first use."
        )

    def _ensure_loaded(self):
        if self.bi_model is not None and self.cross_model is not None:
            return

        with self._load_lock:
            if self.bi_model is not None and self.cross_model is not None:
                return

            print(
                "\n[System] Loading semantic deduplication models. "
                "The first run may take a few minutes because the models need to download."
            )
            self.bi_model = SentenceTransformer(self.bi_model_name)
            self.cross_model = CrossEncoder(self.cross_model_name)
            print("[System] Semantic deduplication models loaded.")

    def is_semantically_duplicate(
        self,
        query_text: str,
        candidate_texts: list[str],
        bi_threshold: float = 0.85,
        cross_threshold: float = 0.95,
    ):
        if not candidate_texts:
            return False, 0.0, ""

        self._ensure_loaded()

        query_embedding = self.bi_model.encode(query_text, convert_to_tensor=True)
        candidate_embeddings = self.bi_model.encode(
            candidate_texts, convert_to_tensor=True
        )
        bi_scores = util.cos_sim(query_embedding, candidate_embeddings)[0]

        potential_duplicates = []
        for i, score in enumerate(bi_scores):
            if score >= bi_threshold:
                potential_duplicates.append(candidate_texts[i])

        if not potential_duplicates:
            return False, 0.0, ""

        cross_input_pairs = [[query_text, cand] for cand in potential_duplicates]
        cross_scores = self.cross_model.predict(cross_input_pairs)

        best_score_idx = cross_scores.argmax()
        best_score = float(cross_scores[best_score_idx])
        best_match_text = potential_duplicates[best_score_idx]

        if best_score >= cross_threshold:
            print(
                f"[AI Dedup] Duplicate detected: '{query_text}' <-> "
                f"'{best_match_text}' (score: {best_score:.2f})"
            )
            return True, best_score, best_match_text

        return False, 0.0, ""


deduplicator_instance = SemanticDeduplicator()
