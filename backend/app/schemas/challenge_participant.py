from pydantic import BaseModel


class ChallengeJoinResponse(BaseModel):
    id: str
    challenge_id: str
    user_id: str
    progress: int
    completed: bool

    model_config = {
        "from_attributes": True
    }

class UserChallengeResponse(BaseModel):
    id: str
    challenge_id: str
    progress: int
    completed: bool
    points_awarded: int

    model_config = {
        "from_attributes": True
    }