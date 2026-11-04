import faiss
import numpy as np
from pathlib import Path


class FaceSearch:

    def __init__(self, dimension=512):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(dimension)

        self.face_ids = []

    def add_embedding(self, embedding, face_id):

        vector = np.asarray(
            embedding,
            dtype=np.float32
        ).reshape(1, -1)

        faiss.normalize_L2(vector)

        self.index.add(vector)

        self.face_ids.append(face_id)

    def search(self, query_embedding, top_k=5):

        if self.index.ntotal == 0:
            return []

        query = np.asarray(
            query_embedding,
            dtype=np.float32
        ).reshape(1, -1)

        faiss.normalize_L2(query)

        scores, indices = self.index.search(
            query,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, index_position in zip(
            scores[0],
            indices[0]
        ):

            if index_position < 0:
                continue

            results.append({
                "face_id": self.face_ids[index_position],
                "similarity": float(score)
            })

        return results  