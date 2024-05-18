FROM python:3.11-slim AS builder
COPY ./requirements.txt .

RUN python -m venv venv
RUN pip install -r requirements.txt
ENV PATH="./venv/bin/activate:$PATH"

FROM builder AS bot
RUN mkdir /bot
WORKDIR /bot

COPY ./cmd /bot/cmd
COPY ./controllers /bot/controllers
COPY ./dal /bot/dal
COPY ./main.py /bot
COPY ./services /bot/services
COPY ./config.yaml /bot
COPY ./main.py /bot

CMD [ "python", "-u", "./main.py" ]