FROM python:3.11-slim as challenge

RUN apt-get update && \
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

ENV FOUNDRY_DIR=/opt/foundry
ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}
RUN curl -L https://foundry.paradigm.xyz | bash && \
    foundryup

RUN pip install git+https://github.com/bbjubjub2494/helloweb3

COPY . /home/ctf/challenge

WORKDIR /home/ctf/challenge
