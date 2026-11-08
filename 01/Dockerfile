FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./entrypoint.sh ./entrypoint.sh
# Windows checkouts with core.autocrlf=true store CRLF. A trailing CR
# becomes part of the Python path inside Linux: app.py\r
RUN sed -i 's/\r$//' ./entrypoint.sh

CMD ["/bin/sh", "./entrypoint.sh"]