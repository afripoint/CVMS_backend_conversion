## Run Dockerised Application Locally


#### Clone the repository (if needed)

``
git clone this repo or checkout to this repo
cd cvms-backend xxxx
``


#### Pull the Docker images

``
docker-compose pull docker images from dockerhub
nginx and web images
``

#### Start the application

``
docker-compose up
``


Verify that:

The Django app is accessible at http://localhost:8000.

The Nginx reverse proxy is serving the app at http://localhost.
