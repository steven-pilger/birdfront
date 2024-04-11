### Dev

- Run the frontend with `yarn dev` while in frontend directory.
- Run the api with `docker compose up --build --no-cache --force-recreate`
- Run the worker with `docker compose up --build --no-cache --force-recreate analyzer recorder`, __but be aware that you need an audio device on the docker host__ for this to work.

Create a .env file in the root dir, with these values set:
```
FRONTEND_PORT=3000
API_PORT=8000
FLICK_API_TOKEN=your_token_here

# If you want the api to run on a subpath of a domain, specify this path here.
# Otherwise leave blank.
# This can be useful, for when your frontend runs on, e.g.:
- birdfront.com
# And you want the api to be on, .e.g:
- birdfront.com/api

API_ROOT_PATH=/api
# Specify the full API URL here.
API_URL=https://birdfron.com/api
```

Adjust the CORS origins in `api/api.py`.
