from pydantic import BaseModel


class ChallengeProgressUpdate(BaseModel):
    progress: int


class ChallengeProgressResponse(BaseModel):
    challenge_id: str
    progress: int
    completed: bool
    points_awarded: int