# parler-data-searcher

## Development

### If you just want to run the app

Build the image with `docker build -t <tag> .`. Run it with `docker run -p 5000:5000 <tag>`.

### If you want to make changes

1. Install a python virtual environment: `python3 -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements-dev.txt`
4. Install the pre-commit hook: `pre-commit install`
5. Run the app: `QUART_ENV=development QUART_DEBUG=1 MONGO_USER=<mongo username> MONGO_PASS=<mongo password> MONGO_ENDPOINT=<mongo endpoint> MONGO_PORT=<mongo port> python src/app.py`
6. Make changes and contribute 🙌
