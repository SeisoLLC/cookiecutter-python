# {{ cookiecutter.project_name }} Development Notes

## Environmental setup

Ensure you have `docker`, `git`, `pipenv`, and `python3` installed locally, and the `docker` daemon is running. Then run the following command to
install the dependencies onto your local system.

```bash
pipenv install --deploy --ignore-pipfile --dev
```

## Linting locally

```bash
pipenv run invoke lint
```

## Updating the dependencies

```bash
pipenv run invoke update
```
{%- if cookiecutter.versioning == "SemVer-ish" %}

## Creating a release

```bash
# Create the release
pipenv run invoke release minor # or major, or patch

# Push it!  (Subject to branch policies)
git push --atomic origin $(git branch --show-current) $(git describe --tags)
```
{%- endif %}
