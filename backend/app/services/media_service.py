from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import MediaType
from app.models.submission_media import SubmissionMedia

try:
    from PIL import Image
except ImportError:
    Image = None


class MediaService:
    ALLOWED_MIME_TYPES = {
        "image/jpeg": MediaType.IMAGE,
        "image/png": MediaType.IMAGE,
        "image/webp": MediaType.IMAGE,
        "video/mp4": MediaType.VIDEO,
        "application/pdf": MediaType.DOCUMENT,
    }

    @staticmethod
    def _get_media_type(mime_type: str) -> MediaType:
        return MediaService.ALLOWED_MIME_TYPES.get(
            mime_type,
            MediaType.OTHER,
        )

    @staticmethod
    def _get_image_dimensions(file_path: Path) -> tuple[int | None, int | None]:
        if Image is None:
            return None, None

        try:
            with Image.open(file_path) as image:
                return image.size
        except Exception:
            return None, None

    @staticmethod
    async def save_submission_media(
        db: Session,
        submission_id: str,
        file: UploadFile,
    ) -> SubmissionMedia:
        mime_type = file.content_type or "application/octet-stream"

        if mime_type not in MediaService.ALLOWED_MIME_TYPES:
            raise ValueError(
                "Unsupported file type. Allowed: JPG, PNG, WEBP, MP4, PDF"
            )

        content = await file.read()
        file_size = len(content)

        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise ValueError(
                f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit"
            )

        file_hash = sha256(content).hexdigest()

        safe_suffix = Path(file.filename or "upload").suffix.lower()
        if not safe_suffix:
            safe_suffix = ".bin"

        storage_dir = (
            Path(settings.MEDIA_STORAGE_DIR)
            / "submissions"
            / submission_id
        )
        storage_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4()}{safe_suffix}"
        stored_path = storage_dir / stored_filename
        stored_path.write_bytes(content)

        file_type = MediaService._get_media_type(mime_type)

        image_width = None
        image_height = None

        if file_type == MediaType.IMAGE:
            image_width, image_height = MediaService._get_image_dimensions(
                stored_path
            )

        media = SubmissionMedia(
            submission_id=submission_id,
            file_path=str(stored_path),
            original_filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            mime_type=mime_type,
            file_sha256=file_hash,
            image_width=image_width,
            image_height=image_height,
            metadata_json={
                "ai_ready": True,
                "verification_status": "NOT_STARTED",
                "sha256": file_hash,
                "image_width": image_width,
                "image_height": image_height,
            },
        )

        db.add(media)
        db.commit()
        db.refresh(media)

        return media