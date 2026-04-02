from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models
from app import oauth2
from loguru import logger
import sentry_sdk
router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    logger.info(f"User Voting attempt | user:{current_user.id}")

    try:
        post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

        if not post:
            logger.warning(f"Post not found | post_id:{vote.post_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {vote.post_id} does not exist"
            )

        vote_query = db.query(models.Votes).filter(
            models.Votes.post_id == vote.post_id,
            models.Votes.user_id == current_user.id
        )

        vote_found = vote_query.first()

        if vote.dir == 1:
            if vote_found:
                logger.warning(f"User already voted | user:{current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already voted on this post"
                )

            new_vote = models.Votes(
                post_id=vote.post_id,
                user_id=current_user.id
            )

            db.add(new_vote)
            db.commit()

            logger.success(f"Vote added | user:{current_user.id}")
            return {"message": "Successfully added vote"}

        else:
            if not vote_found:
                logger.warning(f"Vote not found | user:{current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vote does not exist"
                )

            vote_query.delete(synchronize_session=False)
            db.commit()
            logger.success(f"Vote removed | user:{current_user.id}")
            return {"message": "Successfully removed vote"}

    except Exception as e:
        logger.exception("Error in voting system")
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
        )