# parler-data-searcher

## Development

### If you just want to run the app

```sh
docker compose up
```

### If you want to make changes

1. Install a python virtual environment: `python3 -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements-dev.txt`
4. Install the pre-commit hook: `pre-commit install`
5. Create a `.env` file with the following: `MONGO_USER`, `MONGO_PASS`, `MONGO_ENDPOINT`, and `MONGO_PORT`
6. Run the app: `./bin/run_dev.sh`
7. Make changes and contribute 🙌

### Run tests

Follow steps 1 - 3 above and then run `pytest`.


## Rate limiting

The application is rate limited in order to prevent spamming the service. Each route and its limit is recorded below with rationale for the specific limit:

| Route | Limit | Reason |
| --- | --- | --- |
| `/home` | 1 request per half second | This is the main page, it loads quickly, and if it makes a redirect the redirected route can handle itself |
| `/about` | 1 request per half second | This is a fast page as well and makes no queries, 99.99% of the time the response will be cached by Quart anyway and will be close to free |
| `/posts` | 1 request per 3 seconds | This is an exceptionally slow route and spamming it could easily take down the service. Believe it or not 3 seconds is actually a pretty reasonable amount of time considering the average amount of time it takes for this route to do its thing |
| `/users` | 1 request per second | This is slightly faster than the `/posts` route. |
