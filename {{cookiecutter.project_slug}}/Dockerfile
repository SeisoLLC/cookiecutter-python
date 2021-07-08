FROM {{ cookiecutter.docker_base }} AS base

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

ARG VERSION
ARG COMMIT_HASH

LABEL org.opencontainers.image.title="{{ cookiecutter.project_name }}"
LABEL org.opencontainers.image.description="{{ cookiecutter.project_short_description }}"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.vendor="Seiso"
LABEL org.opencontainers.image.url="https://seisollc.com"
LABEL org.opencontainers.image.source="https://github.com/SeisoLLC/{{ cookiecutter.project_slug }}"
LABEL org.opencontainers.image.revision="${COMMIT_HASH}"
LABEL org.opencontainers.image.licenses="{{ cookiecutter.license }}"

# hadolint ignore=DL3008
RUN apt-get update \
 && apt-get install -y --no-install-recommends pipenv \
                                               python{{ cookiecutter.python_versions[0] }} \
                                               python3-pip \
 && ln -sf /usr/bin/python{{ cookiecutter.python_versions[0] }} /usr/bin/python3 \
 && apt-get clean autoclean \
 && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*


FROM base AS builder

WORKDIR /tmp
COPY Pipfile Pipfile.lock ./
RUN PIP_IGNORE_INSTALLED=1 \
    PIPENV_VENV_IN_PROJECT=true \
    pipenv install --deploy --ignore-pipfile


FROM base AS final

WORKDIR /usr/src/app

# appuser creation
RUN groupadd --gid 53150 -r appuser \
 && useradd -r -g appuser -s "$(which bash)" --create-home --uid 53150 appuser
USER appuser

COPY --from=builder /tmp/.venv .venv
ENV PATH="/usr/src/app/.venv/bin:${PATH}"

COPY ./{{ cookiecutter.project_slug }} ./{{ cookiecutter.project_slug }}/
COPY ./main.py ./
ENTRYPOINT ["/usr/src/app/main.py"]
