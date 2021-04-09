# {{ cookiecutter.project_name }}

Welcome to {{ cookiecutter.project_name }}

## Getting Started

First, you need to ensure you have `docker`, `git`, `pipenv`, and `python3`
installed locally, and the `docker` daemon is running.

Then, you can setup your local environment via:

```bash
# Install the dependencies
pipenv install --dev

# Build the docker image
pipenv run invoke build

# Run the docker image
{%- if cookiecutter.versioning == "SemVer-ish" %}
docker run seiso/{{ cookiecutter.project_slug }}:0.0.0 --help
{%- elif cookiecutter.versioning == "CalVer" %}
docker run seiso/{{ cookiecutter.project_slug }}:{% now 'local', '%Y.%m.00' %} --help
{%- endif %}
```

## Development Notes

### Linting locally

```bash
pipenv run invoke lint
```

### Updating the dependencies

```bash
pipenv update
```

### Creating a release

```bash
# Create the release
{%- if cookiecutter.versioning == "SemVer-ish" %}
pipenv run invoke release minor # or major, or patch
{%- elif cookiecutter.versioning == "CalVer" %}
pipenv run invoke release
{%- endif %}

# Push it!  (Subject to branch policies)
git push --atomic origin $(git branch --show-current) $(git describe --tags)
```
