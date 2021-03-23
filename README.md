# Seiso's python project template

This is Seiso's cookiecuter template for creating new python repositories

## Getting Started

```bash
# Install the prereqs
python3 -m pip install pipx
python3 -m pipx ensurepath
pipx install pipenv

# Initialize your project either with HTTP or SSH
# Uses HTTP
pipx run cookiecutter gh:seisollc/cookiecutter-python
# Uses SSH
pipx run cookiecutter git+ssh://git@github.com/seisollc/cookiecutter-python.git

# Enter the project directory
cd $(ls -td * | head -1)

# Check for any remaining TODOs and address them
grep -r TODO *

# Add your code and tests
pipenv install --dev
# ...

# Commit and test your work
git init --initial-branch=main
git add -A
git commit -m "Initial commit"
pipenv run invoke test

# Make your first release
git remote add origin git@github.com:SeisoLLC/$(basename $(pwd)).git
git push origin $(git branch --show-current)

###############################
# CalVer
pipenv run invoke release
###############################
# or
###############################
# SemVer
pipenv run invoke release minor
###############################

# Ship it!
git push --atomic origin $(git branch --show-current) $(git describe --tags)

# Finally, setup your repo settings (setup a branch policy, enable dependabot, add docker hub secrets, etc...)
```

## Updating the dependencies

```bash
pipenv update
```

## FAQs

Q: Why am I getting `invalid reference format: repository name must be
lowercase` when I try to build my docker container?  
A: You customized the `project_slug` when answering the `cookiecutter`
questions and included a capital letter. Don't do that!

Q: What does `SemVer-ish` mean?  
A: Docker isn't compatible with SemVer, as it doesn't allow `+` symbols in
their tags (which are used by Semver to indicate builds). As a workaround, we
use `-`s instead (only for local builds, not official releases), which is not
compliant with the official SemVer spec, but is easily human understandable. In
order to keep the docker image tags in line with git tags, both use this
SemVer-like notation.
