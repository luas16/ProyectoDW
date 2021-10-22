from django.views.generic import TemplateView


class PrincipalView(TemplateView):
    template_name = 'principal.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['panel'] = 'Panel de administrador'
        return contex


class ComprasView(TemplateView):
    template_name = 'compras.html'