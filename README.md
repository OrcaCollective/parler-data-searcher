# parler-data-searcher

## Development

### If you just want to run the app

```sh
docker compose up
```

### If you want to make changes

This project uses Poetry to manage environment and dependencies.

1. Use `pyenv` to install Python 3.9: `pyenv install 3.9.6`
1. Use the new Python: `pyenv local 3.9.6`
1. Use the new env: `poetry env use python`
1. Install dependencies: `poetry install`
1. Install the pre-commit hook: `poetry run pre-commit install`
1. Copy the `.env.example` to `.env` and fill it in.
1. Run the app `QUART_DEBUG=1 QUART_ENV=development poetry run hypercorn --reload --bind=0.0.0.0:5000 src/app:app`
1. Make changes and contribute 🙌

### Run tests

Follow steps 1 - 4 above and then run `poetry run pytest`.

## Rate limiting

The application is rate limited in order to prevent spamming the service. Each route and its limit is recorded below with rationale for the specific limit:

| Route | Limit | Reason |
| --- | --- | --- |
| `/home` | 1 request per half second | This is the main page, it loads quickly, and if it makes a redirect the redirected route can handle itself |
| `/about` | 1 request per half second | This is a fast page as well and makes no queries, 99.99% of the time the response will be cached by Quart anyway and will be close to free |
| `/posts` | 1 request per 3 seconds | This is an exceptionally slow route and spamming it could easily take down the service. Believe it or not 3 seconds is actually a pretty reasonable amount of time considering the average amount of time it takes for this route to do its thing |
| `/users` | 1 request per second | This is slightly faster than the `/posts` route. |
