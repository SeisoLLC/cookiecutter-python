# {{ cookiecutter.project_name }}
Welcome to {{ cookiecutter.project_name }}

## Getting Started
```bash
# Install the dependencies
pipenv install --dev

# Build the docker image
pipenv run invoke build

# Run the docker image
{%- if cookiecutter.versioning == "SemVer-ish" %}
docker run seiso/{{ cookiecutter.project_slug }}:0.0.0
{%- elif cookiecutter.versioning == "CalVer" %}
docker run seiso/{{ cookiecutter.project_slug }}:{% now 'local', '%Y.%m.0' %}
{%- endif %}
```
