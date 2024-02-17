FROM ghcr.io/foundry-rs/foundry:latest AS foundry

COPY project /project

RUN cd /project && \
    forge build --out /artifacts/out --cache-path /artifacts/cache

FROM python:3.11-slim as challenge

RUN apt-get update && \
    apt-get install -y curl git socat && \
    rm -rf /var/lib/apt/lists/*

ENV FOUNDRY_DIR=/opt/foundry

ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}

RUN curl -L https://foundry.paradigm.xyz | bash && \
    foundryup

#COPY requirements.txt /tmp/requirements.txt
#RUN pip install -r /tmp/requirements.txt

WORKDIR /home/ctf

COPY . challenge
COPY --from=foundry /artifacts /artifacts
