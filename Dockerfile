FROM docker.io/library/python:3.11

# install apt dependencies from requirements.txt
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get update \
    && apt-get -y --no-install-recommends install \
    espeak-ng ffmpeg

# install python dependencies from requirements.txt
ADD requirements.txt /tmp/requirements.txt
RUN --mount=target=/root/.cache/pip,type=cache,sharing=locked \
    pip install -r /tmp/requirements.txt

ADD . /app
WORKDIR /app
