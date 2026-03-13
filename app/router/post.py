from unittest import result

from fastapi import HTTPException, status, Response, Depends, APIRouter
from app import oauth2
from .. import models, schemas
from sqlalchemy.orm import Session
from .. database import get_db
from typing import List,Optional
from sqlalchemy import func

router =APIRouter(
    prefix="/posts",
    tags=["posts"]
)
# Read All the posts
# @router.get("/", response_model=List[schemas.Postout])
# def get_posts(db: Session= Depends(get_db), user_id:int=Depends(oauth2.get_current_user),limit:int=10,skip:int=0, search:Optional[str]=""):
#     new_post= db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
#     results = db.query(models.Post, func.count(models.Votes.post_id)).join(models.Votes, models.Post.id== models.Votes.post_id, 
#             isouter=True).group_by(models.Post.id).all()
#     return results

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user),limit:int=10, skip:int=0,search:Optional[str]=""):
    
    # new_post= db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts = (db.query(models.Post,func.count(models.Votes.post_id).label("votes"))
        .join(models.Votes,models.Post.id == models.Votes.post_id,isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search)).limit(limit).offset(skip)
        .all()
    )


    return posts

    # conn = get_connection()
    # if not conn:
    #     return {"error": "Cannot connect to database"}

    # cursor = conn.cursor(dictionary=True)
    # cursor.execute("SELECT * FROM post;")
    # posts = cursor.fetchall()
    # cursor.close()
    # conn.close()
    # return {"data": posts}
    
@router.get("/{id}", response_model=schemas.PostOut)
def individual_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # post= db.query(models.Post).filter(models.Post.id == id).first()
    post = (
        db.query(
            models.Post,
            func.count(models.Votes.post_id).label("votes")
        )
        .join(models.Votes, models.Post.id == models.Votes.post_id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} not found"
        )

    return post

    # conn=  get_connection()
    # if not conn:
    #     return {"Error":"Cannot connect to databse"}
    # cursor=conn.cursor()
    # cursor.execute("select * from post where id =%s",(str(id)))
    # post=cursor.fetchone()
    # cursor.close()
    # conn.close()

   

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate,db: Session= Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    print(current_user)
    new_post= models.Post(**post.model_dump(),user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

    # conn =get_connection()
    # if not conn:
    #     return {"Error":"Cannot connect to database"}
    # cursor = conn.cursor()
    # cursor.execute("Insert into post (title, content, published, rating) values(%s,%s,%s,%s);",(post.title, post.content, post.published, post.rating))
    # conn.commit()
    # post.id=cursor.lastrowid
    # cursor.close()
    # conn.close()
    # return {"message": "Post created", "post": post}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} does not exist"
        )

    # ownership check
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other user's post"
        )

    db.delete(post)   
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    # conn= get_connection()
    # if not conn:
    #     return {"Error":"Cannot Connect to Database"}
    # cursor =conn.cursor()
    # cursor.execute("delete from post where id=%s",(id,))
    # cursor.fetchone()
    # conn.commit()
    # deleted_rows = cursor.rowcount
    

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(
    id: int,
    post_data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    db_post = post_query.first()

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id:{id} does not exist"
        )

    if db_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other user's post"
        )
    
    post_query.update(post_data.model_dump(), synchronize_session=False)

    db.commit()

    return db_post
    # conn=get_connection()
    # if not conn:
    #     return {"Error":"Cannot connect to database"}
    # cursor=conn.cursor()
    # cursor.execute("Update post set title=%s, content=%s where id=%s",(post.title,post.content, id))
    # conn.commit()
    # cursor.close()
    # conn.close()
    # updated_rows = cursor.rowcount 