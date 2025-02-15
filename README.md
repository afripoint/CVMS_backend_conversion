## Run Dockerised Application Locally


##### Install Docker and Docker Compose (if not already installed):

- Install Docker

- Install Docker Compose

##### Create a Project Directory:


```
mkdir cvms-test
cd cvms-test
```

- Create docker-compose.yml file (use this below).

```
version: '3.8'

services:
  web:
    image: afripoint/cvms_backend_conversion-web:latest  # Pre-built image from Docker Hub
    container_name: web
    env_file:
      - .env  # Load environment variables from .env
    volumes:
      - staticfiles:/app/staticfiles  # Shared volume for static files
      - media:/app/media  # Shared volume for media files
      - db_data:/app/db.sqlite3  # Persist SQLite database
    command: gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 180 api.wsgi:application

  nginx:
    image: afripoint/cvms_backend_conversion-nginx:latest  # Pre-built image from Docker Hub
    container_name: nginx
    ports:
      - "80:80"  # Expose Nginx on port 80
    volumes:
      - staticfiles:/usr/share/nginx/html/static  # Shared static files
      - media:/usr/share/nginx/html/media  # Shared media files
    depends_on:
      - web

volumes:
  staticfiles:  # Shared volume for static files
  media:  # Shared volume for media files
  db_data:  # Persistent volume for SQLite database
```

- Create .env File (use your provided .env).

the (.env) file will be sent privately in your team chat.


- Run the Application:

```
docker-compose up
```

- Access the Application:

Open a browser and go to "http://localhost" .


- Stopping the Application

```
docker-compose down
```
























