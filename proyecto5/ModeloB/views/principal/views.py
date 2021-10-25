from datetime import datetime
from random import randint

from django.db.models import Sum, IntegerField
from django.db.models.functions import Coalesce, Cast
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from ModeloB.models import Sale, Product, DetSale


class PrincipalView(TemplateView):
    template_name = 'principal.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['panel'] = 'Panel de administrador'
        return contex


class ComprasView(TemplateView):
    template_name = 'compras.html'


# clase para las graficas
class EstadisticaView(TemplateView):
    template_name = 'estadistica.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            # cuando la accion sea igual a la toma de datos en ajax
            if action == 'get_graph_sales_year_month':
                # se toma los datos de las ventas y se guarda en el diccionario para poder mandarlo a la peticion de ajax
                data = {
                    'name': 'Porcentaje de venta',
                    'showInLegend': False,
                    'colorByPoint': True,
                    'data': self.get_graph_sales_year_month()
                }
            elif action == 'get_graph_sales_products_year_month':
                data = {
                    'name': 'Porcentaje',
                    'colorByPoint': True,
                    'data': self.get_graph_sales_products_year_month(),
                }
            elif action == 'get_graph_online':
                data = {'y': randint(1, 100)}
                print(data)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # metodo para tomar los valores de la ventas
    def get_graph_sales_year_month(self):
        data = []
        try:
            year = datetime.now().year
            for m in range(1, 13):
                total = Sale.objects.filter(date_joined__year=year, date_joined__month=m).aggregate(
                    r=Coalesce(Cast((Sum('total')), output_field=IntegerField()), 0)).get('r')
                data.append(float(total))
        except:
            pass
        return data

    # metodo para tomar valores de ventas por porductos
    def get_graph_sales_products_year_month(self):
        data = []
        year = datetime.now().year
        month = datetime.now().month
        try:
            for p in Product.objects.all():
                total = DetSale.objects.filter(sale__date_joined__year=year, sale__date_joined__month=month,
                                               prod_id=p.id).aggregate(
                    r=Coalesce(Cast((Sum('subtotal')), output_field=IntegerField()), 0)).get('r')
                if total > 0:
                    data.append({
                        'name': p.name,
                        'y': float(total)
                    })
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['panel'] = 'Panel de administrador'
        context['graph_sales_year_month'] = self.get_graph_sales_year_month()
        return context
