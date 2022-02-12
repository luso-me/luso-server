from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.rest.auth.routes import router as auth_router
from app.adapters.rest.user.routes import router as user_router
from app.adapters.rest.skill.routes import router as skill_router
from app.config import settings


def get_application() -> FastAPI:
    application = FastAPI()

    # TODO: Add logging configuration

    application.add_middleware(
            middleware_class=CORSMiddleware,
            # allow_origins=settings.cors_allowed_origins,
            allow_origins=["http://localhost",
                           "http://localhost:7000",
                           "http://localhost:5000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
    )

    # TODO: Move to own module
    application.include_router(skill_router, prefix="/skills")
    application.include_router(user_router, prefix="/users")
    application.include_router(auth_router, prefix='/auth')

    return application


app = get_application()
