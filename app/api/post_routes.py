
# # Server API
# # GETS
# # Users
# @app.get("/api/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
#     result = db.execute(select(models.User).where(models.User.id == user_id))
#     user = result.scalar_one_or_none()

#     if user:
#         return user
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"User with the id: {user_id} doesn't exist!",
#     )


# # User Posts
# @app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
# def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
#     result = db.execute(select(models.User).where(models.User.id == user_id))
#     user = result.scalar_one_or_none()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with the id: {user_id} doesn't exist!",
#         )

#     result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
#     posts = result.scalars().all()
#     return posts


# # POSTS
# # Users
# @app.post(
#     "/api/users",
#     status_code=status.HTTP_201_CREATED,
#     response_model=UserResponse,
# )
# def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
#     existing_user = db.execute(
#         select(models.User).where(
#             or_(
#                 models.User.username == user.username,
#                 models.User.email == user.email,
#             )
#         )
#     ).scalar_one_or_none()

#     if existing_user:
#         field = "Username" if existing_user.username == user.username else "Email"

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"{field} already exists",
#         )

#     new_user = models.User(**(user.model_dump()))

#     db.add(new_user)

#     try:
#         db.commit()
#         db.refresh(new_user)
#         return new_user

#     except IntegrityError as e:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"User already exists, {e._message}",
#         )


# # Posts
# @app.post(
#     "/api/posts",
#     status_code=status.HTTP_201_CREATED,
#     response_model=PostResponse,
# )
# def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):

#     user = db.execute(
#         select(models.User).where(models.User.id == post.user_id)
#     ).scalar_one_or_none()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=" User doesn't exists",
#         )

#     new_post = models.Post(**(post.model_dump()))

#     db.add(new_post)

#     db.commit()
#     db.refresh(new_post)
#     return new_post
