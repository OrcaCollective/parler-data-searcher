# parler-data-searcher

## Development

### If you just want to run the app

Build the image with `docker build -t <tag> .`. Run it with `docker run -p 5000:5000 <tag>`.

### If you want to make changes

1. Install a python virtual environment: `python3 -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements-dev.txt`
4. Install the pre-commit hook: `pre-commit install`
5. Create a `.env` file with the following: `MONGO_USER`, `MONGO_PASS`, `MONGO_ENDPOINT`, and `MONGO_PORT`
6. Run the app: `./bin/run_dev.sh`
7. Make changes and contribute 🙌
