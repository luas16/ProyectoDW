from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from ModeloB.forms import ClientesForm
from ModeloB.mixins import ValidatePermissionRequiredMixin
from ModeloB.models import Client


#ver registro
class ClientesListView(ValidatePermissionRequiredMixin, ListView):
    model = Client
    template_name = 'clientes/list.html'
    permission_required = "view_client"

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Client.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Clientes'
        context['object_list'] = Client.objects.all()
        context['create_url'] = reverse_lazy('cliente_create')
        return context

#Crear un registro
class ClientesCreateView(ValidatePermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientesForm
    template_name = 'clientes/create.html'
    success_url = reverse_lazy('clientes')
    permission_required = "add_client"

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opcion'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ingreso Clientes'
        context['entity'] = 'Clientes'
        context['list_url'] = reverse_lazy('clientes')
        context['action'] = 'add'
        return context

#Editar un registro
class ClientesUpdateView(ValidatePermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientesForm
    template_name = 'clientes/create.html'
    success_url = reverse_lazy('clientes')
    permission_required = "change_client"

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opcion'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Cliente'
        context['entity'] = 'Clientes'
        context['list_url'] = reverse_lazy('clientes')
        context['action'] = 'edit'
        return context

#Eliminar un registro
class ClientesDeleteView(ValidatePermissionRequiredMixin, DeleteView):
    model = Client
    template_name = 'clientes/delete.html'
    success_url = reverse_lazy('clientes')
    permission_required = "delete_client"

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Cliente'
        context['entity'] = 'Clientes'
        context['list_url'] = reverse_lazy('productos')
        return context