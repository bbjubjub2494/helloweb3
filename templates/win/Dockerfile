FROM python:3.11-slim AS base

RUN apt-get update && \
    apt-get install -y curl git build-essential && \
    rm -rf /var/lib/apt/lists/*

ENV FOUNDRY_DIR=/opt/foundry
ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}
RUN curl -L https://foundry.paradigm.xyz | bash && \
    foundryup

FROM base AS challenge

ARG HELLOWEB3_URL=helloweb3

RUN pip install $HELLOWEB3_URL

COPY . /home/ctf/challenge

WORKDIR /home/ctf/challenge

RUN cd contracts/; forge soldeer update

FROM base AS solve

RUN pip install pwntools

COPY . /home/ctf/solve

WORKDIR /home/ctf/solve

RUN cd contracts/; forge soldeer update

CMD python3 solve.py
