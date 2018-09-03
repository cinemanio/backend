# to solve error "gunicorn: error: unrecognized arguments: --access-logfile-" which appear after introducing honcho
# discussion here https://github.com/heroku/heroku-buildpack-python/issues/627
export GUNICORN_CMD_ARGS=""
