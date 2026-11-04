import numpy as np

from app.ai.face_engine import FaceEngine
from app.database.db import SessionLocal
from app.database.models import Face, Photo
from app.services.face_search import FaceSearch


class PhotoSearchService:

    def __init__(self):
        self.face_engine = FaceEngine()
        self.search_engine = FaceSearch(dimension=512)

        self.photo_lookup = {}

    def build_index(self, event_id=None):

        db = SessionLocal()

        try:
            query = db.query(Face, Photo).join(
                Photo,
                Face.photo_id == Photo.id
            )

            if event_id is not None:
                query = query.filter(Photo.event_id == event_id)

            records = query.all()

            self.search_engine = FaceSearch(dimension=512)
            self.photo_lookup = {}

            loaded = 0
            skipped = 0

            for face, photo in records:

                embedding_path = face.embedding_path

                try:
                    embedding = np.load(
                        embedding_path,
                        allow_pickle=False
                    )

                    if embedding.shape != (512,):
                        skipped += 1
                        continue

                    self.search_engine.add_embedding(
                        embedding,
                        face.id
                    )

                    self.photo_lookup[face.id] = {
                        "photo_id": photo.id,
                        "filename": photo.filename,
                        "file_path": photo.file_path
                    }

                    loaded += 1

                except (OSError, ValueError) as error:
                    print(
                        f"Skipping face {face.id}: {error}"
                    )
                    skipped += 1

            print("\n========== FAISS INDEX ==========")
            print("Embeddings loaded:", loaded)
            print("Embeddings skipped:", skipped)

            return loaded

        finally:
            db.close()

    def search_selfie(self, image_path, top_k=10):

        result = self.face_engine.process_image(image_path)

        if result["total_faces"] == 0:
            raise ValueError("No face detected in selfie.")

        if result["total_faces"] > 1:
            raise ValueError(
                "Please upload a selfie containing only one face."
            )

        query_embedding = result["faces"][0]["embedding"]

        matches = self.search_engine.search(
            query_embedding,
            top_k
        )

        final_results = []

        for match in matches:

            face_id = match["face_id"]

            photo_info = self.photo_lookup.get(face_id)

            if photo_info is None:
                continue

            final_results.append({
                "face_id": face_id,
                "photo_id": photo_info["photo_id"],
                "filename": photo_info["filename"],
                "file_path": photo_info["file_path"],
                "similarity": round(
                    match["similarity"], 4
                )
            })

        return final_results