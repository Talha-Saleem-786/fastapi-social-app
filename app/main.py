import os
from fastapi import FastAPI
# import mysql.connector
# from mysql.connector import Error
from .router import post,user,auth,vote
from  fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_dsn=os.getenv("SENTRY_DSN")
sentry_sdk.init(
    dsn=sentry_dsn,
    send_default_pii=True,
    integrations=[
        FastApiIntegration(),
        StarletteIntegration(),
    ],
    traces_sample_rate=1.0,
    environment="production",
    release="1.0.0",
)
app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
# models.Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def get():
    return {"message": "Hello world"}
# from passlib.context import CryptContext

# pwd_context = CryptContext(
#     schemes=["Argon2"],
#     deprecated="True",
#  
# )


# def get_connection():
#     try:
#         conn = mysql.connector.connect(
#             host="127.0.0.1",
#             user="root",
#             password="talhasql.69",
#             database="fastapi_db"
#         )
#         if conn.is_connected():
#             return conn
#     except Error as e:
#         print("Error connecting to MySQL", e)
#         return None


# @app.get("/posts")
# def get_posts(db: Session= Depends(get_db)):
#     new_post= db.query(models.Post).all()
#     return new_post

    # conn = get_connection()
    # if not conn:
    #     return {"error": "Cannot connect to database"}

    # cursor = conn.cursor(dictionary=True)
    # cursor.execute("SELECT * FROM post;")
    # posts = cursor.fetchall()
    # cursor.close()
    # conn.close()
    # return {"data": posts}
    
# @app.get("/posts/{id}")
# def individual_post(id: int, db: Session= Depends(get_db)): 
#     post= db.query(models.Post).filter(models.Post.id == id).first()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} not found ")
#     return post

    # conn=  get_connection()
    # if not conn:
    #     return {"Error":"Cannot connect to databse"}
    # cursor=conn.cursor()
    # cursor.execute("select * from post where id =%s",(str(id)))
    # post=cursor.fetchone()
    # cursor.close()
    # conn.close()

   

# @app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
# def create_post(post: schemas.PostCreate,db: Session= Depends(get_db)):

#     new_post= models.Post(**post.model_dump())
#     db.add(new_post)
#     db.commit()
#     db.refresh(new_post)
#     return new_post

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

# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int ,db: Session= Depends(get_db)):
#     post =db.query(models.Post).filter(models.Post.id == id)
#     if post.first() is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} not exist ")
#     post.delete(synchronize_session=False)
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    # conn= get_connection()
    # if not conn:
    #     return {"Error":"Cannot Connect to Database"}
    # cursor =conn.cursor()
    # cursor.execute("delete from post where id=%s",(id,))
    # cursor.fetchone()
    # conn.commit()
    # deleted_rows = cursor.rowcount
    

# @app.put("/posts/{id}")
# def update_post(id :int, post: schemas.PostCreate, db: Session= Depends(get_db) ):
    
#     post_query= db.query(models.Post).filter(models.Post.id == id)
#     new_post= post_query.first()
#     if new_post==0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} not exist ")
#     post_query.update(post.model_dump(), synchronize_session=False)
#     db.commit()
#     return post_query.first()
    # conn=get_connection()
    # if not conn:
    #     return {"Error":"Cannot connect to database"}
    # cursor=conn.cursor()
    # cursor.execute("Update post set title=%s, content=%s where id=%s",(post.title,post.content, id))
    # conn.commit()
    # cursor.close()
    # conn.close()
    # updated_rows = cursor.rowcount 
    
#Working with User Login

# @app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.userout)
# def create_user(user: schemas.UserCreated, db: Session = Depends(get_db)):
    # truncate password to 72 bytes to prevent bcrypt errors

    # password_to_hash = user.password[:72]
    # hashed_password = pwd_context.hash(password_to_hash)
    # user.password = hashed_password

#     new_user = models.User(**user.model_dump())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return new_user

# @app.get("/users/{id}", response_model=schemas.userout)
# def get_user(id :int , db: Session =Depends(get_db)):
#     user= db.query(models.User).filter(models.User.id==id).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User withif :{id} not Found...")
    
#     return user