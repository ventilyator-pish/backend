FROM --platform=linux/x86_64 python:3.10-slim AS app

ENV PATH=/root/.local/bin:${PATH}


WORKDIR /app/
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --user --no-cache-dir -r requirements.txt
COPY . /app/


FROM app AS web-server
CMD ["bash", "./docker-entrypoint.sh", "runserver"]
