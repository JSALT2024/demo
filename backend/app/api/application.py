from fastapi import Depends
from typing_extensions import Annotated
from ..Application import Application
from ..bootstrap import bootstrap


# This file binds the demo backend application with the FastAPI HTTP web server
# allowing for dependency injection into any part of the FastAPI app

application_singleton = None

def application_factory():
    global application_singleton
    if application_singleton is None:
        application_singleton = bootstrap()
    return application_singleton


ApplicationDependency = Annotated[Application, Depends(application_factory)]

# This is how you mock the application for tests:
# (app here is the FastApi app, whereas application is the OmniOMR application)
# app.dependency_overrides[application_factory] = lambda: mocked_application


########################
# Service dependencies #
########################

from ..services.VideosRepository import VideosRepository
VideosRepositoryDependency = Annotated[
    VideosRepository,
    Depends(lambda: application_factory().videos_repository)
]

from ..services.VideoFilesRepository import VideoFilesRepository
VideoFilesRepositoryDependency = Annotated[
    VideoFilesRepository,
    Depends(lambda: application_factory().video_files_repository_factory)
]
