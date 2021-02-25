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
docker run seiso/{{ cookiecutter.project_slug }}:{% now 'local', '%Y.%m.00' %}
{%- endif %}
```

## Creating a release
```bash
git checkout -b release-branch
{%- if cookiecutter.versioning == "SemVer-ish" %}
pipenv run invoke release minor # or major, or patch
{%- elif cookiecutter.versioning == "CalVer" %}
pipenv run invoke release
{%- endif %}

# Push it!
git push --atomic origin $(git branch --show-current) $(git describe --tags)
```
