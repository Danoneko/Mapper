FROM python:3.11-slim AS builder
COPY ./requirements.txt .

RUN python -m venv venv
RUN pip install -r requirements.txt
ENV PATH="./venv/bin/activate:$PATH"

FROM builder AS bot
RUN mkdir /bot
WORKDIR /bot

COPY ./cmd ./cmd
COPY ./controllers ./controllers
COPY ./dal ./dal
COPY ./main.py .
COPY ./services ./services
COPY ./config.yaml .
COPY ./icon.jpg .

CMD [ "python", "-u", "./main.py" ]