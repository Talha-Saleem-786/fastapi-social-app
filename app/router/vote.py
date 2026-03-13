from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models
from app import oauth2

router=APIRouter(
    prefix="/vote",
    tags=["Vote"]
)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(vote: schemas.Vote,db: Session = Depends(database.get_db),current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {vote.post_id} does not exist")

    vote_query = db.query(models.Votes).filter(models.Votes.post_id == vote.post_id, models.Votes.user_id == current_user.id )
    vote_found = vote_query.first()

    if vote.dir == 1:
        if vote_found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already voted on this post")

        new_vote = models.Votes( post_id=vote.post_id,user_id=current_user.id)

        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}

    else:
        if not vote_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Vote does not exist")

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully removed vote"}