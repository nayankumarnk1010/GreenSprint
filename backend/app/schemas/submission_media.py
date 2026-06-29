from datetime import datetime

from pydantic import BaseModel

from app.core.enums import MediaType


class SubmissionMediaResponse(BaseModel):
    id: str
    submission_id: str
    file_path: str
    original_filename: str | None
    file_type: MediaType
    file_size: int
    mime_type: str
    file_sha256: str | None
    image_width: int | None
    image_height: int | None
    metadata_json: dict | None
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }