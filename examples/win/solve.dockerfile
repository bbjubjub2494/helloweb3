FROM python:3.11-slim as base

RUN apt-get update && \
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

ENV FOUNDRY_DIR=/opt/foundry
ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}
RUN curl -L https://foundry.paradigm.xyz | bash && \
    foundryup

WORKDIR /home/ctf/solve

RUN pip install pwntools

COPY . /home/ctf/solve

CMD python3 solve.py
