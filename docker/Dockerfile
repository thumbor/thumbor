ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-bullseye AS builder-image

ARG DEBIAN_FRONTEND=noninteractive
ARG THUMBOR_VERSION

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y autoremove && \
    apt-get install --no-install-recommends -y \
        curl \
        libssl-dev \
        libcurl4-openssl-dev \
        libjpeg-dev \
        libwebp-dev \
        libjpeg-progs \
        zlib1g-dev \
        gifsicle \
        gcc \
        libcairo2-dev \
        build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/thumbor_dist
COPY dist/* /tmp/thumbor_dist

RUN python3 -m venv /home/thumbor/venv
ENV PATH="/home/thumbor/venv/bin:$PATH"

RUN pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir --find-links=/tmp/thumbor_dist thumbor[all]==${THUMBOR_VERSION}

FROM python:${PYTHON_VERSION}-slim-bullseye AS runner-image

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        gifsicle \
        libcairo2 \
        libjpeg-turbo-progs && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home thumbor
COPY --from=builder-image /home/thumbor/venv /home/thumbor/venv

USER thumbor

EXPOSE 8888

ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/home/thumbor/venv
ENV PATH="/home/thumbor/venv/bin:$PATH"

ENTRYPOINT ["thumbor"]
