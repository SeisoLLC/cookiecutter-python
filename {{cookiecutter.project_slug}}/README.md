# {{ cookiecutter.project_name }}

Welcome to {{ cookiecutter.project_name }}

## Getting Started

First, you need to ensure you have `docker`, `git`, `pipenv`, and `python3` installed locally, and the `docker` daemon is running.

Then, you can setup your local environment via:

```bash
# Install the dependencies
pipenv install --deploy --ignore-pipfile --dev

# Build the image
pipenv run invoke build

# Run the image
{%- if cookiecutter.versioning == "SemVer-ish" %}
docker run seiso/{{ cookiecutter.project_slug }}:0.0.0 --help
{%- elif cookiecutter.versioning == "CalVer" %}
docker run seiso/{{ cookiecutter.project_slug }}:{% now 'local', '%Y.%m.00' %} --help
{%- endif %}
```

## Troubleshooting

If you're troubleshooting the results of any of the invoke tasks, you can add `--debug` to enable debug logging, for instance:

```bash
pipenv run invoke build --debug
```
