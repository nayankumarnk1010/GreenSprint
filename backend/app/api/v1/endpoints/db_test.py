from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

router = APIRouter()


@router.get("/db-test")
def db_test(
    db: Session = Depends(get_db),
):
    return {
        "message": "Database connection successful"
    }