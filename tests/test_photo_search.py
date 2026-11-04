from pathlib import Path

from app.services.search_service import PhotoSearchService


if __name__ == "__main__":

    search_service = PhotoSearchService()

    # Load embeddings from SQLite records
    loaded = search_service.build_index(event_id=1)

    if loaded == 0:
        print("No face embeddings available.")
        raise SystemExit(1)

    # Initial test using the same photo already indexed
    selfie_path = Path(
        "storage/events/wedding_001/originals/test.jpg"
    )

    results = search_service.search_selfie(
        selfie_path,
        top_k=5
    )

    print("\n========== SEARCH RESULTS ==========")

    for result in results:
        print("Photo:", result["filename"])
        print("Similarity:", result["similarity"])
        print("Original path:", result["file_path"])
        print("--------------------------------")