
import json
from pathlib import Path
from datetime import datetime, timezone

from app.ai.face_engine import FaceEngine


SUPPORTED_FORMATS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


class PhotoProcessor:

    def __init__(self):
        self.engine = FaceEngine()

    def process_folder(self, input_folder, output_folder):

        input_folder = Path(input_folder)
        output_folder = Path(output_folder)

        output_folder.mkdir(parents=True, exist_ok=True)

        if not input_folder.exists():
            raise FileNotFoundError(
                f"Input folder not found: {input_folder}"
            )

        image_files = sorted(
            file for file in input_folder.rglob("*")
            if file.is_file()
            and file.suffix.lower() in SUPPORTED_FORMATS
        )

        print(f"\nFound {len(image_files)} photographs.")

        results = []
        total_faces = 0

        for number, image_path in enumerate(image_files, 1):

            print(
                f"\nProcessing {number}/{len(image_files)}: "
                f"{image_path.name}"
            )

            output_path = (
                output_folder / f"{image_path.stem}_detected.jpg"
            )

            try:
                detection = self.engine.process_image(
                    image_path,
                    output_path
                )

                photo_result = {
                    "filename": image_path.name,
                    "source_path": str(image_path),
                    "processed_path": str(output_path),
                    "total_faces": detection["total_faces"],
                    "faces": detection["faces"],
                    "status": "success"
                }

                total_faces += detection["total_faces"]

                print(
                    f"Detected {detection['total_faces']} faces."
                )

            except Exception as error:

                photo_result = {
                    "filename": image_path.name,
                    "status": "failed",
                    "error": str(error)
                }

                print(f"Error: {error}")

            results.append(photo_result)

        report = {
            "event": input_folder.parent.name,
            "processed_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "total_photos": len(image_files),
            "successful_photos": sum(
                r["status"] == "success" for r in results
            ),
            "failed_photos": sum(
                r["status"] == "failed" for r in results
            ),
            "total_faces": total_faces,
            "photos": results
        }

        report_path = output_folder / "batch_results.json"

        with report_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print("\n========== PROCESSING COMPLETE ==========")
        print("Total photos:", len(image_files))
        print("Successful:", report["successful_photos"])
        print("Failed:", report["failed_photos"])
        print("Total faces:", total_faces)
        print("Report:", report_path)

        return report
