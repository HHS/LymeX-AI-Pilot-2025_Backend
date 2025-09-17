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
This project uses [mkdocs](https://www.mkdocs.org/) with [material](https://squidfunk.github.io/mkdocs-material/) to generate project documentation. To preview locally, use:
```bash
mkdocs serve
```

### Contributing

If you'd like to contribute directly to LymeX Regulatory Support Backend, please follow our contributing guidelines [here](CONTRIBUTING.md).

## Policies

### Open Source Policy

We adhere to the [HHS Open Source Policy](https://www.hhs.gov/sites/default/files/hhs-open-gov-plan-v4-2016.pdf). If you have any questions, just [send us an email](mailto:cdo@hhs.gov).

### Security and Responsible Disclosure Policy

_Submit a vulnerability:_ Vulnerability reports can be submitted through processes listed on the [HHS VDP Page](https://www.hhs.gov/vulnerability-disclosure-policy/index.html). 

For more information about our Security, Vulnerability, and Responsible Disclosure Policies, see [SECURITY.md](SECURITY.md).

### Software Bill of Materials (SBOM)

A Software Bill of Materials (SBOM) is a formal record containing the details and supply chain relationships of various components used in building software.

In the spirit of [Executive Order 14028 - Improving the Nation’s Cyber Security](https://www.gsa.gov/technology/it-contract-vehicles-and-purchasing-programs/information-technology-category/it-security/executive-order-14028), a SBOM for this repository is provided here: https://github.com/hhs/hhs-cdo/network/dependencies.

For more information and resources about SBOMs, visit: https://www.cisa.gov/sbom.

## Public domain

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.