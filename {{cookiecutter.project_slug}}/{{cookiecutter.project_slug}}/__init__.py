"""
{{ cookiecutter.project_name }} init
"""
__maintainer__ = "Seiso"
{% if cookiecutter.licensing == 'Not open source' -%}
__copyright__ = "(c) {% now 'local', '%Y' %} Seiso, LLC"
{% elif cookiecutter.licensing == 'MIT' -%}
__license__ = "MIT"
{% elif cookiecutter.licensing == 'BSD-3' -%}
__license__ = "BSD-3-Clause"
{% endif -%}
__project_name__ = "{{ cookiecutter.project_slug }}"
{% if cookiecutter.versioning == 'SemVer' -%}
__version__ = "0.1.0"
{% elif cookiecutter.versioning == 'CalVer' -%}
__version__ = "{% now 'local', '%Y.%m-01' %}"
{% endif -%}
