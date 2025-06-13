NOIS2 Backend Deployment Guide
==============================

This document describes how to deploy and operate the NOIS2 backend (FastAPI + Celery)

* * * * *

1. Prerequisites
-----------------

-   **Docker & Docker Compose:** Already installed (any recent version is OK)

-   **Code location:** `~/nois2/nois2_192_backend`

* * * * *

2. Directory Structure
-----------------------

-   All code should be located at:\
    `~/nois2/nois2_192_backend`

-   Your `.env.prod` file (provided separately) must be in the project root:\
    `~/nois2/nois2_192_backend/.env.prod`

* * * * *

3. Environment Variables
-------------------------

-   The `.env.prod` file contains all environment variables, secrets, and external service connections (MongoDB, Redis, RabbitMQ, S3, etc.).


* * * * *

4. Network and External Services
---------------------------------

-   The deployment uses the **Docker network** named `nois2_network`.\
    This is a shared network where containers for MongoDB, Redis, and RabbitMQ are already running and configured.

-   The backend will automatically connect to these services based on settings in `.env.prod`.

-   **No extra setup is needed for MongoDB, Redis, or RabbitMQ.**

* * * * *

5. How to Deploy
-----------------

1.  **Place the Environment File:**\
    Make sure the `.env.prod` file is present in the project root.

2.  **Start Services:**

    cd ~/nois2/nois2_192_backend
    docker-compose up -d --build

    -   The following two containers will run:

        -   **server:** Serves FastAPI on port 8000 (mapped to host port 19000)

        -   **background:** Runs Celery workers for background jobs

4.  **Accessing the Application:**

    -   FastAPI server is accessible at:\
        `http://<server-ip>:19000`

    -   Health check endpoint:\
        `http://<server-ip>:19000/`

    -   Docs (swagger) endpoint:\
        `http://<server-ip>:19000/docs`

* * * * *

7. Troubleshooting & Logs
--------------------------

-   To check logs for a container:

    docker logs nois2_192_server
    docker logs nois2_192_background

-   If a container keeps restarting, check your `.env.prod` file for missing or incorrect values.

* * * * *

8. Components Overview
-----------------------

-   **server:** Runs FastAPI, exposes API on port 19000. Triggers background jobs for long-running tasks like email or AI analysis.

-   **background:** Celery worker processing jobs from FastAPI.

* * * * *

9. Notes
---------

-   All persistent data (DB, cache, broker) is handled by external containers already joined to `nois2_network`.

-   No log collector is set up by default.

-   S3 storage is already configured in `.env.prod`.

-   The firewall is already open for port 19000, so you can test/debug remotely.
