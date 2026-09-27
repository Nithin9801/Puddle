from fastapi import FastAPI


from src.auth.routes import auth_router
from src.middlewares.corsmiddleware import cors_middleware

version = "v1"
version_prefix = f"/api/{version}"


app = FastAPI(title="Puddle",
              description="A global online video-sharing and social media platform ",
              version=version,
              docs_url=f"{version_prefix}/docs",
              redoc_url=None)

cors_middleware(app)

app.include_router(auth_router,prefix=f"{version_prefix}/auth",tags=['auth'])