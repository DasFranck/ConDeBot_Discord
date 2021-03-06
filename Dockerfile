FROM python:3.9-alpine

RUN mkdir -p /app/ConDeBot /data/ConDeBot
WORKDIR /app/ConDeBot

COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del gcc musl-dev

COPY . .
COPY ./docker/config ./config
RUN rm -r ./docker

ENTRYPOINT ["python", "./ConDeBot.py" ]
