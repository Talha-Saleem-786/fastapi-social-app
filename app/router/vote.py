from fastapi import HTTPException, status, APIRouter
from .. import schemas, models
from loguru import logger
import sentry_sdk
from ..dependencies import DB
from app.oauth2 import get_current_user
from fastapi import Depends
from typing import Annotated

router = APIRouter(prefix="/vote", tags=["Vote"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(vote: schemas.Vote, db: DB, current_user:Annotated[int, Depends(get_current_user)]):
    logger.info(f"Vote attempt | user={current_user.id} post={vote.post_id} dir={vote.dir}")

    try:
        post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
        if not post:
            logger.warning(f"Post not found | post_id={vote.post_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} does not exist")

        vote_query = db.query(models.Votes).filter(models.Votes.post_id == vote.post_id, models.Votes.user_id == current_user.id)
        vote_found = vote_query.first()

        if vote.dir == 1:
            if vote_found:
                logger.warning(f"Already voted | user={current_user.id} post={vote.post_id}")
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already voted on this post")
            db.add(models.Votes(post_id=vote.post_id, user_id=current_user.id))
            db.commit()
            logger.success(f"Vote added | user={current_user.id} post={vote.post_id}")
            return {"message": "Successfully added vote"}

        else:
            if not vote_found:
                logger.warning(f"Vote not found | user={current_user.id} post={vote.post_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
            vote_query.delete(synchronize_session=False)
            db.commit()
            logger.success(f"Vote removed | user={current_user.id} post={vote.post_id}")
            return {"message": "Successfully removed vote"}

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Voting error | user={current_user.id} | error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")