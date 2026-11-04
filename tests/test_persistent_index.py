from pathlib import Path

from app.ai.face_engine import FaceEngine
from app.services.persistent_face_index import PersistentFaceIndex
from app.database.db import SessionLocal
from app.database.models import Face, Photo


if __name__ == "__main__":

    EVENT_ID = 1

    # Build and save the event index
    index_manager = PersistentFaceIndex()

    index_manager.build_event_index(EVENT_ID)

    # Reload index from disk
    index_manager.load_event_index(EVENT_ID)

    # Generate query embedding from test photograph
    engine = FaceEngine()

    result = engine.process_image(
        Path("storage/events/wedding_001/originals/test.jpg")
    )

    if result["total_faces"] == 0:
        raise RuntimeError("No face detected in test photograph.")

    query_embedding = result["faces"][0]["embedding"]

    # Search the saved index
    matches = index_manager.search(
        query_embedding,
        top_k=5
    )

    db = SessionLocal()

    try:
        print("\n========== PERSISTENT SEARCH RESULTS ==========")

        for match in matches:

            face = db.query(Face).filter(
                Face.id == match["face_id"]
            ).first()

            photo = db.query(Photo).filter(
                Photo.id == face.photo_id
            ).first()

            print("Face ID:", face.id)
            print("Photo:", photo.filename)
            print("Similarity:", round(match["similarity"], 4))
            print("Original path:", photo.file_path)
            print("--------------------------------")

    finally:
        db.close()