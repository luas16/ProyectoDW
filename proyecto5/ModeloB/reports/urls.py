from django.urls import path

from ModeloB.reports.views import ReportSaleView

urlpatterns = [
    # urls de reporte
    path('sale/', ReportSaleView.as_view(), name='sale_report'),
]