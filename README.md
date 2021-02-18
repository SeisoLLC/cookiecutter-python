# Seiso's cookiecutter template
This is Seiso's cookiecuter template for creating new repositories

## Getting Started
```bash
# Install the prereqs
python3 -m pip install pipx
python3 -m pipx ensurepath
pipx install pipenv

# Initialize your project
pipx run cookiecutter gh:seisollc/cookiecutter-seiso

# Enter the project directory
cd $(ls -td * | head -1)

# Check for any remaining TODOs and address them
grep -r TODO *

# Add your code and tests
...

# Commit and push your work
git init --initial-branch=main
git add -A
git commit -m "Initial commit"

# Do some final testing
pipenv install --dev
pipenv run invoke test

# Ship it!
git remote add origin git@github.com:SeisoLLC/TODO.git
git push origin main
```

## FAQs
Q: Why am I getting `invalid reference format: repository name must be lowercase` when I try to build my docker container?  
A: You customized the `project_slug` when answering the `cookiecutter` questions and included a capital letter. Don't do that!  
