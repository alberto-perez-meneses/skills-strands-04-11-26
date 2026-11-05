FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./entrypoint.sh ./entrypoint.sh

CMD ["/bin/sh", "./entrypoint.sh"]