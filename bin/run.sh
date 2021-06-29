#! /bin/sh
hypercorn --bind=0.0.0.0:5000 src/app:app
