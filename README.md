# Seiso's Python Paved Road

This is Seiso's paved road for creating new python repositories.

## Getting Started

```bash
# Install the prerequisites
python3 -m pip install --upgrade pipx gitpython pyyaml
python3 -m pipx ensurepath
pipx install pipenv

# Initialize your project with *either* HTTP or SSH
# HTTP
pipx run --system-site-packages cookiecutter gh:seisollc/cookiecutter-python
# SSH
pipx run --system-site-packages cookiecutter git+ssh://git@github.com/seisollc/cookiecutter-python.git

# Enter the project directory
cd $(ls -td * | head -1)
```

At this point you need to ensure that there is an empty remote Git repository that aligns with the naming of the generated project. If it doesn't yet exist, you
need to create it. Once it exists, you can continue.

```bash
# Push the initial commit (IMPORTANT!)
git remote add origin git@github.com:SeisoLLC/$(basename $(pwd)).git
git push origin $(git branch --show-current) --follow-tags
```

After you've pushed the initial commit, you should setup your repository settings - such as setting a branch policy, enabling dependabot, adding docker hub
secrets, etc.

This can be done via Infrastructure as Code (IaC) or manually, but ostensibly at this point your repository is aligned with your organizational practices. If
you perform this step manually, consider a tool like OpenSSF [allstar](https://github.com/ossf/allstar) to monitor and alert or mitigate on your behalf.

Continue on if you're ready to add business logic to your new repository.

```bash
# Initialize the repository
task init

# Checkout a new branch for your initial content
git checkout -b initial-content

# Check for `NotImplementedError`s and address them
grep -r NotImplementedError *

# Add your code and tests

# Commit and build/test your work
git add -A
git commit -m "Initial content"
task build test

# Push your branch
git push origin $(git branch --show-current)

# Open a Pull Request

# (Optional) If you chose SemVer-ish as your versioning, run a release after your PR is merged
if grep -q SemVer setup.cfg; then task release -- minor; git push --atomic origin $(git branch --show-current) $(git describe --tags); fi
```

## Version Control System support

Currently this project only supports projects hosted on GitHub.

## FAQs

Q: Why am I getting `invalid reference format: repository name must be lowercase` when I try to build my docker container?<br />
A: You customized the `project_slug` when answering the `cookiecutter` questions and included a capital letter. Don't do that!

Q: What does `SemVer-ish` mean?<br />
A: Docker isn't compatible with SemVer, as it doesn't allow `+` symbols in their tags (which are used by SemVer to indicate builds). As a
workaround,
we use `-`s instead (only for local builds, not official releases), which is not compliant with the official SemVer spec, but is easily human
understandable. In order to keep the image tags in line with Git tags, both use this SemVer-like notation.

Q: I use `pyenv`; how do I keep `pipx` aligned with my activated python version and package installations?<br />
A: Set the `PIPX_DEFAULT_PYTHON` env var like the following:

```bash
PIPX_DEFAULT_PYTHON="${HOME}/.pyenv/versions/$(pyenv version | cut -f1 -d\ )/bin/python3"
export PIPX_DEFAULT_PYTHON
```

You may also want to consider storing this in your .zshrc or similar if it fixes your issue.

Q: How do I contribute?<br />
A: See our [contributing docs](./CONTRIBUTING.md)
