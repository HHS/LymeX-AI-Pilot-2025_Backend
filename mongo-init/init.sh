#!/bin/bash
mongoimport --db nois2_192 --collection email_templates --file /docker-entrypoint-initdb.d/nois2_192.email_templates.json --jsonArray
