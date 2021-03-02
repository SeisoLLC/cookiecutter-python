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
{%- if cookiecutter.license != 'Not open source' %}
LABEL org.opencontainers.image.licenses="{{ cookiecutter.license }}"
{%- endif %}

# hadolint ignore=DL3008
RUN apt-get update \
 && apt-get install -y --no-install-recommends pipenv \
                                               python3 \
                                               python3-pip \
 && apt-get clean autoclean \
 && apt-get -y autoremove \
 && rm -rf /var/lib/apt/lists/*


FROM base AS builder

COPY Pipfile Pipfile.lock ./
RUN PIP_IGNORE_INSTALLED=1 \
    PIPENV_VENV_IN_PROJECT=true \
    pipenv install --deploy --ignore-pipfile


FROM base AS final

WORKDIR /usr/src/app

RUN useradd --create-home appuser
USER appuser

COPY --from=builder /.venv .venv
ENV PATH="/usr/src/app/.venv/bin:${PATH}"

COPY ./{{ cookiecutter.project_slug }} ./
ENTRYPOINT ["python3", "-c", "print('TODO: Setup the {{ cookiecutter.project_name }} entrypoint')"]
