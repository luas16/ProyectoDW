import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from ModeloB.forms import VentasForm, ClientesForm
from ModeloB.mixins import ValidatePermissionRequiredMixin
from ModeloB.models import Sale, Product, DetSale, Client

# librerias para generar factura en pdf
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


class VentasListView(ValidatePermissionRequiredMixin, ListView):
    model = Sale
    template_name = 'ventas/list.html'
    permission_required = "view_sale"

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
                position = 1
                for i in Sale.objects.all():
                    item = i.toJSON()
                    item['position'] = position
                    data.append(item)
                    position += 1
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

# Crear un registro
class VentasCreateView(ValidatePermissionRequiredMixin, CreateView):
    # se identifica el modelo, el form, la direccion url y el retorno al finalizar.
    model = Sale
    form_class = VentasForm
    template_name = 'ventas/create.html'
    success_url = reverse_lazy('ventas')
    permission_required = "add_sale"

    # decoradores para la seguridad, token y login
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # metodo post para trasportar datos
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
                    # item['value'] = i.names #se envian valores par buscar por medio de jquery
                    item['text'] = i.name  # se envian valores par buscar por medio de select2
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
                    data = {'id': venta.id}
            # se se selecciona crear cliente dentro del formulario
            elif action == 'create_cliente':
                # se manda toda la informacion captada al fomulario
                with transaction.atomic():
                    frmCliente = ClientesForm(request.POST)
                    data = frmCliente.save()
            #buscar Clientes
            elif action == 'search_cliente':
                data = []
                clie = Client.objects.filter(names__icontains=request.POST['term'])[0:10]
                for i in clie:
                    item = i.toJSON()
                    # item['value'] = i.names #se envian valores par buscar por medio de jquery
                    item['text'] = i.names  # se envian valores par buscar por medio de select2
                    data.append(item)
            else:
                data['error'] = 'No ha ingresado a ninguna opcion'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # contex lleva los datos que se mostrara y utilizara en la pagina
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Facturar'
        context['entity'] = 'Ventas'
        context['list_url'] = reverse_lazy('ventas')
        context['action'] = 'add'
        context['det'] = []
        context['frmCliente'] = ClientesForm
        return context

# editar un registro
class VentasUpdateView(ValidatePermissionRequiredMixin, UpdateView):
    # se identifica el modelo, el form, la direccion url y el retorno al finalizar.
    model = Sale
    form_class = VentasForm
    template_name = 'ventas/create.html'
    success_url = reverse_lazy('ventas')
    permission_required = "change_sale"

    # decoradores para la seguridad, token y login
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # metodo post para trasportar datos
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
            # editamos productos a la factura y a nuestras tablas
            elif action == 'edit':
                # control de transaccion
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    # guardamos los datos de nuestra factura en nuestra base de datos
                    # tabla ventas (sale)
                    venta = self.get_object()
                    venta.date_joined = vents['date_joined']
                    venta.cli_id = vents['cli']
                    venta.subtotal = float(vents['subtotal'])
                    venta.iva = float(vents['iva'])
                    venta.total = float(vents['total'])
                    venta.save()
                    venta.detsale_set.all().delete()
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
                    data = {'id': venta.id}
            elif action == 'create_cliente':
                # se manda toda la informacion captada al fomulario
                with transaction.atomic():
                    frmCliente = ClientesForm(request.POST)
                    data = frmCliente.save()
            # buscar clientes
            elif action == 'search_cliente':
                data = []
                clie = Client.objects.filter(names__icontains=request.POST['term'])[0:10]
                for i in clie:
                    item = i.toJSON()
                    # item['value'] = i.names #se envian valores par buscar por medio de jquery
                    item['text'] = i.names  # se envian valores par buscar por medio de select2
                    data.append(item)
            else:
                data['error'] = 'No ha ingresado a ninguna opcion'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # metodo para ver detalle de factura al momento de editar
    def get_det_product(self):
        data = []
        try:
            for i in DetSale.objects.filter(sale_id=self.get_object().id):
                item = i.prod.toJSON()
                item['cant'] = i.cant
                data.append(item)
        except:
            pass
        return data

    # contex lleva los datos que se mostrara y utilizara en la pagina
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Factura'
        context['entity'] = 'Ventas'
        context['list_url'] = reverse_lazy('ventas')
        context['action'] = 'edit'
        # enviamos los valores de los detalles convetidos a formato json para poder utilizarlos en js
        context['det'] = json.dumps(self.get_det_product())
        return context

# Eliminar un registro
class VentasDeleteView(ValidatePermissionRequiredMixin, DeleteView):
    model = Sale
    template_name = 'ventas/delete.html'
    success_url = reverse_lazy('ventas')
    permission_required = "delete_sale"

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

# clase para generar factura en pdf
class facturaPDFView(View):
    # metodo para trabajar con archivos media
    def link_callback(self, uri, rel):
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path

    # # metodo get
    def get(self, request, *args, **kwargs):
        try:
            # indicamos la ruta del template
            template = get_template('ventas/facturaPDF.html')
            #le enviamos el contenido a nuestro pdf
            context = {
                # objeto sale para tomar los datos en el html de mi factura
                'sale': Sale.objects.get(pk=self.kwargs['pk']),
                # objeto para datos de la compañia
                'comp': {'name': 'Multiservicios LUAS', 'nit': '75146314', 'direccion': '2da calle 2-36 Z 4, Bo. Ressurreccion, San Juan Chamelco, A.V., GT'},
                # objeto para el logo
                'logo': '{}{}'.format(settings.STATIC_URL, 'img/logo.jpg')
            }
            # toma el contenido de la ruta
            html = template.render(context)
            # se crea un objeto en Django de tipo pdf
            response = HttpResponse(content_type='application/pdf')
            # el pdf se decargara con nombre factura
            # response['Content-Disposition'] = 'attachment; filename="factura.pdf"'  # para que solo lo muestre no hay necesidad de esta linea

            # se crea el pdf
            pisaStatus = pisa.CreatePDF(
                # se le envia la ruta que contiene el objeto, cual es el objeto que tiene la conversion y el metodo para trabajar con archivos media
                html, dest=response,
                link_callback=self.link_callback
            )
            return response
            # si hay error nos redirecciona a ventas
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('ventas'))

