# {{ cookiecutter.project_name }}

Welcome to {{ cookiecutter.project_name }}

## Getting Started

First, you need to ensure you have `task`, `docker`, `git`, `pipenv`, and `python3` installed locally, and the `docker` daemon is running.

Then, you can setup your local environment via:

```bash
# Install the dependencies
task init

# Build the image
task build

# Run the image
{%- if cookiecutter.versioning == "SemVer-ish" %}
docker run seiso/{{ cookiecutter.project_slug }}:0.0.0 --help
{%- elif cookiecutter.versioning == "CalVer" %}
docker run seiso/{{ cookiecutter.project_slug }}:{% now 'local', '%Y.%m.00' %} --help
{%- endif %}
```

If you'd like to build all of the supported docker images, you can set the `PLATFORM` env var to `all` like this:

```bash
PLATFORM=all task build
```

You can also specify a single platform of either `linux/arm64` or `linux/amd64.

## Troubleshooting

If you're troubleshooting the results of any of the tasks, you can add `-v` to enable debug `task` logging, for instance:

```bash
task -v build
```

If you're troubleshooting a `goat` failure (you aren't the first one), you can pass one of the log levels as defined
[here](https://github.com/SeisoLLC/goat#debugging):

```bash
task lint -- debug
```
