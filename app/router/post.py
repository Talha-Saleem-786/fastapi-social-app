from fastapi import HTTPException, status, Response,APIRouter,Query,Path
import sentry_sdk
from .. import models, schemas
from typing import List,Optional,Annotated
from sqlalchemy import func, select
from loguru import logger
from ..dependencies import DB
from app.oauth2 import get_current_user
from fastapi import Depends
from sqlalchemy.orm import selectinload

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
async def get_posts(db:DB,current_user :Annotated[int, Depends(get_current_user)],limit:Annotated[int,Query(ge=0,le=100)]=10, skip:Annotated[int, Query(ge=0)]=0,search:Annotated[Optional[str],Query(max_length=50)]=""):
    logger.info(f"User {current_user.id} fetching posts | limit={limit} skip={skip} search={search}")
    try:
      result = await db.execute(select(models.Post,func.count(models.Votes.post_id).label("votes"))
          .options(selectinload(models.Post.owner))
          .join(models.Votes,models.Post.id == models.Votes.post_id,isouter=True)
          .group_by(models.Post.id)
          .filter(models.Post.title.contains(search)).limit(limit).offset(skip)
      )
      posts= result.all()
      logger.success(f"Posts fetched successfully | count={len(posts)}")
      return posts
    except Exception as e:
        logger.error(f"Posts fetch failed | user={current_user.id} | error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Posts fetch failed")

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
async def individual_post(id: Annotated[int, Path(gt=0)], db: DB, current_user:Annotated[int, Depends(get_current_user)]):
    logger.info(f"User {current_user.id} fetching post id:{id}")
    try:
      result = await db.execute(select(models.Post,func.count(models.Votes.post_id).label("votes"))
          .options(selectinload(models.Post.owner))
          .join(models.Votes, models.Post.id == models.Votes.post_id, isouter=True)
          .group_by(models.Post.id)
          .filter(models.Post.id == id)
      )
      post= result.first()
      if not post:
          logger.warning(f"Post id:{id} not found")
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail=f"Post with id:{id} not found"
          )
      logger.success(f"Post id:{id} fetched Successfully")
      return post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Post fetch failed | id={id} | error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Post fetch failed")

    # conn=  get_connection()
    # if not conn:
    #     return {"Error":"Cannot connect to databse"}
    # cursor=conn.cursor()
    # cursor.execute("select * from post where id =%s",(str(id)))
    # post=cursor.fetchone()
    # cursor.close()
    # conn.close()

   

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate,db: DB, current_user : Annotated[models.User, Depends(get_current_user)]):
    logger.info(f"User {current_user.id} created a post")
    try:
      new_post= models.Post(**post.model_dump(),user_id=current_user.id)
      db.add(new_post)
      await db.commit()
      await db.refresh(new_post)
      # ✅ owner explicitly load karo!
      result = await db.execute(
            select(models.Post)
            .options(selectinload(models.Post.owner))  
            .filter(models.Post.id == new_post.id)
        )
      new_post = result.scalar_one()
      logger.success(f"User {current_user.id} successfully created a post {new_post.id}")
      return new_post
    
    except Exception as e:
        logger.error(f"Post creation failed of user:{current_user.id} error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Post creation failed")


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
async def delete_post(id: Annotated[int, Path(gt=0)],db: DB,current_user : Annotated[models.User, Depends(get_current_user)]):
    logger.info(f"User {current_user.id} deleting post id={id}")
    try:
      result =await db.execute(select(models.Post).filter(models.Post.id == id))
      post = result.scalar_one_or_none()
  
      if post is None:
          logger.warning(f"Delete failed | post id={id} not found")
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id:{id} does not exist")
  
      if post.user_id != current_user.id:
          logger.warning(f"Unauthorized delete | user={current_user.id} post owner={post.user_id}")
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Cannot delete other user's post" )
      await db.delete(post)   
      await db.commit()
      logger.success(f"Post id={id} deleted by user={current_user.id}")
      return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
      raise
    
    except Exception as e:
        logger.error(f"Delete failed | post={id} error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Delete failed")
    
    # conn= get_connection()
    # if not conn:
    #     return {"Error":"Cannot Connect to Database"}
    # cursor =conn.cursor()
    # cursor.execute("delete from post where id=%s",(id,))
    # cursor.fetchone()
    # conn.commit()
    # deleted_rows = cursor.rowcount
    

@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(                      
    id: Annotated[int, Path(gt=0)],
    post_data: schemas.PostCreate,
    db: DB,
    current_user: Annotated[models.User, Depends(get_current_user)]  
):
    logger.info(f"User {current_user.id} updating post id={id}")
    try:
        result = await db.execute(select(models.Post).options(selectinload(models.Post.owner)).filter(models.Post.id == id))
        db_post = result.scalar_one_or_none()

        if db_post is None:
            logger.warning(f"Update failed | post id={id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exist")

        if db_post.user_id != current_user.id:
            logger.warning(f"Unauthorized update | user={current_user.id} post owner={db_post.user_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update other user's post")

        for key, value in post_data.model_dump().items():
            setattr(db_post, key, value)
        # ↑ async mein .update() directly nahi hota
        # setattr se har field update karo

        await db.commit()      
        await db.refresh(db_post) 
        result = await db.execute(
            select(models.Post)
            .options(selectinload(models.Post.owner))
            .filter(models.Post.id == id)
        )
        db_post = result.scalar_one()
        logger.success(f"Post id={id} updated by user={current_user.id}")
        return db_post

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Update failed | post={id} | error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update failed")
    # conn=get_connection()
    # if not conn:
    #     return {"Error":"Cannot connect to database"}
    # cursor=conn.cursor()
    # cursor.execute("Update post set title=%s, content=%s where id=%s",(post.title,post.content, id))
    # conn.commit()
    # cursor.close()
    # conn.close()
    # updated_rows = cursor.rowcount 