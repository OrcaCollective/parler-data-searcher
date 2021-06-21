#! /bin/sh
QUART_DEBUG=1 QUART_ENV=development hypercorn --reload --bind=0.0.0.0:5000 src/app:app
