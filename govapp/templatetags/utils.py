from django.conf import settings
from django.template import Library

register = Library()


@register.simple_tag()
def project_title():
    return settings.PROJECT_TITLE


@register.simple_tag()
def project_description():
    return settings.PROJECT_DESCRIPTION


@register.simple_tag()
def application_version():
    return settings.APPLICATION_VERSION


@register.simple_tag()
def department_name():
    return settings.DEPARTMENT_NAME


@register.simple_tag()
def support_phone():
    return settings.SUPPORT_PHONE


@register.simple_tag()
def support_email():
    return settings.SUPPORT_EMAIL
