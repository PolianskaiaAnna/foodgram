from django.shortcuts import render
from django.views.generic import TemplateView

class AboutTemplateView(TemplateView):
    """Статическая страница О проекта"""
    template_name = 'frontend/src/pages/about/index.js'


class TechnologyTemplateView(TemplateView):
    """Статическая страница Технологии"""
    template_name = 'frontend/src/pages/technologies/index.js'