# Architecture

This document describes the top-level structure of the codebase, so that you can orient yourself in it. It starts with a couple of [C4 model](https://c4model.com/) diagrams and at the end there's a description of the source code folder structure.


## Container diagram

Starting from the very top we have the two primary parts: frontend and backend. Frontend is a React app which runs in the user's browser. It communicates with the backend server which is responsible for invoking the machine learning models.

The two two parts run as separate processes on (possibly) different machines, which corresponds to two containers in the C4 model:

<img src="img/container-diagram.svg" alt="C4 Container diagram of the demo application" />

The backend server only requires a set of 3 external filesystem folders to interact with. The model checkpoints and repositories folders are set up during backend installation and are read-only from the backend's perspective.

The `storage` folder acts as a lightweight "database" for the backend server combined with a lightweight object storage.

> **Note:** An object storage is a cloud filesystem (kinda like Google Drive or Dropbox) which is used by cloud applications to store larger binary files (images, videos).


## Domain model

> **Note:** Domain model is a set of "things" an application knows about, for example, a hospital information system would have a concept of a "patient", "employee", "treatment", and similar. See [Domain Modelling, Cosmic Python](https://www.cosmicpython.com/book/chapter_01_domain_model.html).

The domain model of the demo application is very simple. There is only one entity defined and that is the `Video`. This entity represents one uploaded video and the list of all uploaded videos is shown on the demo's home page. When you upload a new video, a new `Video` instance is created. Then the video is processed, which modifies the state stored in the `Video` instance. Finaly, when you delete a video, the `Video` instance is destroyed.

> **Note:** The REST HTTP API between the frontend and the backend mirrors this data model, using `GET /videos` to list existing videos, `POST /videos` to upload a new video and `GET /videos/{video-id}` to fetch a specific video. To see all the URLs of the API, visit the backend URL and open the Swagger page. Should be present at http://localhost:1817/docs.

The `Video` entity is defined in [`app.domain.Video`](../backend/app/domain/Video.py) and all known videos are stored in the `storage` folder in the `videos.pkl` file. Access to this file is abstracted away via the [`app.services.VideosRepository`](../backend/app/services/VideosRepository.py) class.

> **Note:** You can think of the `videos.pkl` file as a `videos` table in an SQL database, but to keep the demo lightweight, these implementation details are hidden behind the `VideosRepository` service and replaced by a simple python list pickle dump. A proper database implementation of the `VideosRepository` could be added in the future.

While the `Video` entity holds structured data about the video (the title, ID, length, timestamps), there is a lot of additional binary data to be stored (the video MP4 file, extracted visual features, cropped JPGs). This additional data is stored in a corresponding "video folder" in the `storage/videos_data/{video_id}` folder.

This folder is currently accessed via the standard python filesystem operations (think `with open("filename", "r") as file:`), but the structure of this folder is captured by the [`app.services.VideoFolderRepository`](../backend/app/services/VideoFolderRepository.py) class. It handles the construction of proper filesystem paths for you (e.g. `np.load(video_folder.DINO_FEATURES_FILE)`).

To see what are all the files stored there, check out the [Dataflow](dataflow.md) page.


## Backend components

The primary purpose of the backend container is to perform the processing of the uploaded videos. This is performed by the class [`app.services.VideoProcessor`](../backend/app/services/VideoProcessor.py) which you can see in the middle of the following diagram:

<img src="img/backend-component-diagram.svg" alt="C4 Component diagram of the backend server" />

You can see the external filesystem folders at the very bottom, the `storage` folder being abstracted away via the two repository classes `VideosRepository` and `VideoFolderRepository`. These are used by the `VideoProcessor` which is class with a single `run()` method, that performs all the actions necessary to process a given video file. Basically it computes the complete data-dependency graph as defined on the [Dataflow](dataflow.md) page.

The `VideoProcessor` has at its disposal a set or machine learning models and other processors, some external, some part of this repository, that perform individual steps of the video processing pipeline.

The `HTTP API` implemented in the [FastApi](https://fastapi.tiangolo.com/) framework provides the gateway into the system, responsible for calling the `VideoProcessor` and also managing all the boring details, such as the uploading of videos, deletion of videos, and fetching of their data.

> **Note:** In theory, you could modify the codebase to become a proper python package and then import the `VideoProcessor` class manually and use it directly from your python code, side stepping the HTTP API port. Or you could create a CLI port for the application in addition to the HTTP port. The separation of concerns into the 3-layer architecture is clear - the upper components connect the application to the outside world, the bottom components communicate with the data stores, and the middle components represent the business layer where the interesting application logic happens. See [Three-layered architecture, Cosmic Python](https://www.cosmicpython.com/book/introduction.html#_layering).

The models used during video processing are often quite straight-forward. They are simple mathematical functions that take an input and produce an output. They need to be loaded from their checkpoints before they can be used. They are usually represented by a single class that you construct, giving it paths to all the input files and output files and then calling a `run()` method on the instance.

The most interesting model is the LLM translation model, because of two differences:
- It is kept in-memory once loaded, because the loading takes too long (10-20 seconds).
- It contains more complicated logic (e.g. context tracking and embedding neighbor lookup) which makes the translator use additional utility classes.

The translator is encapsulated in the [`app.translation.SignLlavaTranslator`](../backend/app/translation/SignLlavaTranslator.py) class. You can see the context of this component in the following diagram:

<img src="img/signllavatranslator-component-context.svg" alt="C4 Component context diagram of the SignLlavaTranslator class" />

The translator depends on a `SignLlavaCache` instance, which is responsible for loading the LLM into memory and holding it there. It uses the `ContextTracker` during translation to keep track of translations of individual clips, while a single video is being translated. Finally, it uses the `EmbeddingNeighborLookup` class to perform the conversion of visual embeddings to the nearest textual tokens (used for visualizations later).

You can see that the translator class does not depend on the `VideosRepository` nor the `VideoFolderRepository`. That is deliberate. The translator just needs the visual features and the clips, which it gets as arguments. It produces translations which it outputs into the `clips_collection.json` file directly. It does not care about the domain (about the `Video` class), it only performs the low-level translation on the raw data, regardless of the context. This is important for further potential re-usability of the model. Other models are written in the same fashion: the `VideoNormalizer` only cares about the input and output MP4 files, not the `Video` entity.


## Code-infrastructure

Because the application consists of many smaler components, these components need to be instantiated and put together before use. This composition is managed by the [`app.Application`](../backend/app/Application.py) class and the [`app.bootstrap`](../backend/app/bootstrap.py) function.

The `Application` class acts as a container for all the top-level components. It gives you access to the `VideosRepository` and `SignLLavaCache`. It is **the** object used by the HTTP API when it translates HTTP requests to application actions.

The construction of the `Application` instance is handled by the `bootstrap` function. This is the place where most components are configured and where configuration should be changed if needed.

> **Note:** Also, the `bootstrap` function is where any configuration should be loaded in case configuration files / more environment variables are to be introduced.

> **Note:** Here, all the components need to instantiated manually. In larger applications, the `Application` class typically extends or uses an IoC container to perform the instantiation.

> **Note:** You can read more about [Application Bootstrapping, Cosmic Python](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html).


## Codebase folder structure

- `backend/` Contains all the backend code.
    - `.venv/` Virtual environment for the backend application. Created during backend installation. Use the `.venv/bin/python3` interpreter to run the backend app.
    - `app/` The root python module for the entire backend application.
        - `api/` Contains the HTTP API entrypoint to the backend application. Uses the FastAPI framework.
            - `models/` Contains definitions of JSON documents passed along with the HTTP requests and responses. May loosely correspond to the domain model.
            - `routers/videos.py` The place where are `HTTP /videos` requests are handled. This is the semantic entrypoint to the whole backend app.
            - `main.py` The FastAPI entrypoint from which the backend app is started.
        - `debug/` Contains scripts for testing ML models and possibly other debugging. Should be executed direclty via `.venv/bin/python3 -m app.debug.<your-script>`.
        - `domain/` Contains the domain model of the application (mainly just defines internal data types).
            - `Video.py` The most important data type - represents one uploaded video.
        - `preprocessing/` Contains models for video preprocessing (normalization, frame enumeration, MediaPipe).
        - `encoding/` Contains models for visual feature encoding (MAE, DINO, Sign2Vec).
        - `translation/` Contains the `SignLlavaTranslator` models and its dependencies.
        - `services/` Contains the application logic services, such as the `VideoProcessor` and the data abstraction repositories (e.g. `VideosRepository`).
        - `video/` Set of low-level utility classes to work with videos as streams of frames and to manipulate these streams.
    - `models/` Contains the cloned repositories of machine learning models.
    - `checkpoints/` Contains the downloaded weights files of machine learning models. The names of subfolders match the subfolders in the `models/` directory.
    - `storage/` The default placement of permanent storage of the application (all uploaded videos and their metadata).
- `frontend/` Contains all the frontend code.
    - `dist/` This folder contains the compiled frontend application after `npm run build` is executed.
    - `node_modules/` Contains NPM packages needed to compile the frontend and to run the Parcel development server. Analogous to the `.venv` folder in backend.
    - `src/` Contains all source code for the frontend.
        - `favicon/` Contains the small icon used by browsers for the website.
        - `img/` Contains images used by the frontend app.
        - `api/` Provides abstraction over the HTTP API of the backend server. It should be accessed via the `BackendApi.current()` static method.
            - `connection/` Represents the low-level HTTP connection to the backend.
            - `model/` Contains type definition for JSON objects sent to and returned by the backend API. Corresponds to the `backend/app/api/models` folder.
        - `ui/` Contains React components and pages for the frontend app.
            - `VideoPlayer/` defines the `<VideoPlayer />` component.
        - `Application.tsx` Root of the React frontend application.
        - `router.tsx` defines the frontend URLs to pages mapping.
- `docs/` All the documentation files are located here.
