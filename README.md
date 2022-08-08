# Seiso's python project template

This is Seiso's cookiecutter template for creating new python repositories.

## Getting Started

```bash
# Install the prerequisites
python3 -m pip install --upgrade pipx gitpython pyyaml
python3 -m pipx ensurepath
pipx install pipenv

# Initialize your project either with HTTP or SSH
# Uses HTTP
pipx run --system-site-packages cookiecutter gh:seisollc/cookiecutter-python
# Uses SSH
pipx run --system-site-packages cookiecutter git+ssh://git@github.com/seisollc/cookiecutter-python.git

# Enter the project directory
cd $(ls -td * | head -1)

# Check for `NotImplementedError`s and address them
grep -r NotImplementedError *

# Add your code and tests
pipenv install --deploy --ignore-pipfile --dev
# ...

# Commit and test your work
git add -A
git commit -m "Initial content"
pipenv run invoke build test

# Make your first release
git remote add origin git@github.com:SeisoLLC/$(basename $(pwd)).git
git push origin $(git branch --show-current)
if grep -q CalVer setup.cfg; then pipenv run invoke release; else pipenv run invoke release minor; fi

# Ship it!
git push --atomic origin $(git branch --show-current) $(git describe --tags)

# Finally, setup your repo settings (setup a branch policy, enable dependabot, add docker hub secrets, etc...)
```

## Troubleshooting

If you're troubleshooting the results of any of the invoke tasks, you can add `--debug` to enable debug logging, for instance:

```bash
pipenv run invoke build --debug
```

### Using pyenv

If you use `pyenv` to manage your python environments, `pipx` won't using the same `python` that your `python -m pip install`s are installing
dependencies for.  Set the `PIPX_DEFAULT_PYTHON` env var like the following:

```bash
PIPX_DEFAULT_PYTHON="${HOME}/.pyenv/versions/$(pyenv version | cut -f1 -d\ )/bin/python3"
export PIPX_DEFAULT_PYTHON
```
You may also want to consider storing this in your .zshrc or similar if it fixes your issue.

## Updating the dependencies

```bash
pipenv run invoke update
```

## FAQs

Q: Why am I getting `invalid reference format: repository name must be lowercase` when I try to build my docker container?  
A: You customized the `project_slug` when answering the `cookiecutter` questions and included a capital letter. Don't do that!

Q: What does `SemVer-ish` mean?  
A: Docker isn't compatible with SemVer, as it doesn't allow `+` symbols in their tags (which are used by SemVer to indicate builds). As a workaround,
we use `-`s instead (only for local builds, not official releases), which is not compliant with the official SemVer spec, but is easily human
understandable. In order to keep the image tags in line with git tags, both use this SemVer-like notation.
