#!/bin/bash
if [ -n "$1" ]; then
  manage_cmd=$1
  python3 manage.py migrate

  if [ "runserver" == "$manage_cmd" ]; then
    python3 manage.py collectstatic --noinput
    gunicorn --config file:gunicorn.config.py core.wsgi:application
  fi
else
  echo "You have to specify a command for manage.py"
fi
