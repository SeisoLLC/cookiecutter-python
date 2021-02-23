"""
{{ cookiecutter.project_name }} init
"""
__maintainer__ = "Seiso"
{% if cookiecutter.license == 'Not open source' -%}
__copyright__ = "(c) {% now 'local', '%Y' %} Seiso, LLC"
{% elif cookiecutter.license == 'MIT' -%}
__license__ = "MIT"
{% elif cookiecutter.license == 'BSD-3' -%}
__license__ = "BSD-3-Clause"
{% endif -%}
__project_name__ = "{{ cookiecutter.project_slug }}"
{% if cookiecutter.versioning == 'SemVer-ish' -%}
__version__ = "0.0.0"
{% elif cookiecutter.versioning == 'CalVer' -%}
__version__ = "{% now 'local', '%Y.%m_00' %}"
{% endif -%}
