# {{ cookiecutter.project_name }} Development Notes

## Environmental setup

Ensure you have `docker`, `git`, `pipenv`, and `python3` installed locally, and the `docker` daemon is running. Then run the following command to
install the dependencies onto your local system.

```bash
pipenv install --deploy --ignore-pipfile --dev
```

## Linting locally

```bash
task lint
```

## Updating the dependencies

```bash
task update
```
{%- if cookiecutter.versioning == "SemVer-ish" %}

## Creating a release

```bash
# Create the release
task release minor # or major, or patch

# Push it!  (Subject to branch policies)
git push --atomic origin $(git branch --show-current) --follow-tags
```
{%- endif %}
