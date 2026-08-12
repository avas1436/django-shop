# core/apps/website/views.py

from django.views.generic import TemplateView

from .models import *


class IndexView(TemplateView):
    template_name = "website/index.html"


class ContactView(TemplateView):
    template_name = "website/contact.html"


class AboutView(TemplateView):
    template_name = "website/about.html"
