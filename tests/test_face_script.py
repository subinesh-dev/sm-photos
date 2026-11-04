from pathlib import Path
from app.ai.face_engine import FaceEngine

# Initialize face detection model
engine = FaceEngine()

# Test image path
image_path = Path("storage/events/wedding_001/originals/test.jpg")

# Check whether image exists
if not image_path.exists():
    raise FileNotFoundError(f"Image not found: {image_path}")

# Output image path
output_path = Path("storage/events/wedding_001/processed/test_detected.jpg")

# Detect faces
result = engine.process_image(
    image_path,
    output_path
)

print("\n========== FACE DETECTION RESULT ==========")
print("Total faces detected:", result["total_faces"])

for face in result["faces"]:
    print(
        f'Face {face["face_number"]}: '
        f'Confidence = {face["confidence"]:.2f}'
    )

print("\nProcessed image saved:", output_path)
