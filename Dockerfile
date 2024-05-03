FROM python:3.11-slim as challenge

RUN apt-get update && \
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*

ENV FOUNDRY_DIR=/opt/foundry
ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}
RUN curl -L https://foundry.paradigm.xyz | bash && \
    foundryup

RUN cd /tmp && curl -L https://gethstore.blob.core.windows.net/builds/geth-linux-amd64-1.13.14-2bd6bd01.tar.gz | tar xz
RUN cp /tmp/geth-linux-amd64-1.13.14-2bd6bd01/geth /bin/

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /home/ctf

COPY . challenge
