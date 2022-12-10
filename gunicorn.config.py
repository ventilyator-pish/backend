import os

bind = f":{os.getenv('SERVER_BIND_PORT', 4022)}"
capture_output = True
log_level = "INFO"
errorlog = "-"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
workers = os.getenv("GUNICORN_WORKERS", 1)
threads = os.getenv("GUNICORN_THREADS", 1)
timeout = 30

