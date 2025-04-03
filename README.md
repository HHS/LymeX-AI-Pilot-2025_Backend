# NASA-NOIS2-192 Backend
This repository contains the backend for NOIS2-192 project.

## Getting Started
You will need:
- the python version configured for this project
- a virtual environment package of your choosing
- docker

Reach out to the team if you need assistance.


### Deployment
This project uses a multi-stage container build.

`docker-compose up --build -d` 

## Docs
This project uses [mkdocs](https://www.mkdocs.org/) with [material](https://squidfunk.github.io/mkdocs-material/) to
generate project documentation. To preview locally, use:
```bash
mkdocs serve
```

