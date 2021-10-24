import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from ModeloB.forms import VentasForm
from ModeloB.models import Sale, Product, DetSale


class VentasListView(ListView):
    model = Sale
    template_name = 'ventas/list.html'

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Sale.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_details_prod':
                data = []
                for i in DetSale.objects.filter(sale_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ventas'
        context['object_list'] = Sale.objects.all()
        context['create_url'] = reverse_lazy('ventas_create')
        context['list_url'] = reverse_lazy('ventas')
        context['entity'] = 'Ventas'
        return context


class VentasCreateView(CreateView):
    model = Sale
    form_class = VentasForm
    template_name = 'ventas/create.html'
    success_url = reverse_lazy('ventas')

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            # buscar produuctos
            if action == 'search_products':
                data = []
                prods = Product.objects.filter(name__icontains=request.POST['term'])[0:10]
                for i in prods:
                    item = i.toJSON()
                    item['value'] = i.name
                    data.append(item)
            # agregamos productos a la factura y a nuestras tablas
            elif action == 'add':
                # control de transaccion
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    # guardamos los datos de nuestra factura en nuestra base de datos
                    # tabla ventas (sale)
                    venta = Sale()
                    venta.date_joined = vents['date_joined']
                    venta.cli_id = vents['cli']
                    venta.subtotal = float(vents['subtotal'])
                    venta.iva = float(vents['iva'])
                    venta.total = float(vents['total'])
                    venta.save()
                    # guardamos los datos de nuestra factura en nuestra base de datos
                    # tabla detalle de ventas (detsale)
                    for i in vents['products']:
                        det = DetSale()
                        det.sale_id = venta.id
                        det.prod_id = i['id']
                        det.cant = int(i['cant'])
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opcion'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Facturar'
        context['entity'] = 'Ventas'
        context['list_url'] = reverse_lazy('ventas')
        context['action'] = 'add'
        return context

# Eliminar un registro
class VentasDeleteView(DeleteView):
    model = Sale
    template_name = 'ventas/delete.html'
    success_url = reverse_lazy('ventas')

    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = reverse_lazy('ventas')
        return context
