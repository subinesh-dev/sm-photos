from app.ai.face_engine import FaceEngine


engine = FaceEngine()

image_path = (
    "storage/events/wedding_001/originals/test.jpg"
)

result = engine.process_image(
    image_path,
    output_path="storage/events/wedding_001/processed/quality_test.jpg"
)

print("\n========== FACE QUALITY REPORT ==========")

print("Total faces:", result["total_faces"])

print("Good faces:", result["good_faces"])

print("Poor faces:", result["poor_faces"])

for face in result["faces"]:

    print("\nFace:", face["face_number"])

    print("Confidence:", face["confidence"])

    print("Quality:", face["quality"]["quality_status"])

    print("Width:", face["quality"]["face_width"])

    print("Height:", face["quality"]["face_height"])

    print("Blur:", face["quality"]["blur_score"])

    print("Brightness:", face["quality"]["brightness"])

    print("Issues:", face["quality"]["quality_issues"])