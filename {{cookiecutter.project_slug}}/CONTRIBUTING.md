# {{ cookiecutter.project_name }} Development Notes

## Environmental setup

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

## Creating a release

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
