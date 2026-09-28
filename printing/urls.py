from django.urls import path
from .views import upload_pdf, get_job,  make_payment, start_printing, complete_printing,get_printers, test_printer, test_print_pdf
urlpatterns = [
    path('upload/', upload_pdf),
    path('job/<str:file_id>/', get_job),
    path('pay/<str:file_id>/', make_payment),
    path('print/<str:file_id>/', start_printing),
    path('complete/<str:file_id>/', complete_printing),
    path('printers/', get_printers),
    path('test-printer/', test_printer),
    path('test-print-pdf/', test_print_pdf),
]