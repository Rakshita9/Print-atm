import win32print
import win32api
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import fitz
import os
import uuid
from django.conf import settings
from django.http import JsonResponse
from .models import PrintJob

@api_view(['POST'])
def upload_pdf(request):
    file = request.FILES.get('file')

    if not file:
        return Response(
            {"error": "PDF file is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if file.content_type != 'application/pdf':
        return Response(
            {"error": "Only PDF files are allowed"},
            status=status.HTTP_400_BAD_REQUEST
        )

    pdf = fitz.open(stream=file.read(), filetype="pdf")

    pages = len(pdf)

    copies = int(request.data.get('copies', 1))
    color = request.data.get('color', 'false').lower() == 'true'

    if copies < 1:
        return Response(
            {"error": "Copies must be at least 1"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if color:
        price_per_page = 5
    else:
        price_per_page = 1

    total_price = pages * copies * price_per_page
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"

    upload_dir = os.path.join(settings.BASE_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            
            
    PrintJob.objects.create(
    file_id=file_id,
    original_filename=file.name,
    pages=pages,
    copies=copies,
    color=color,
    price_per_page=price_per_page,
    total_price=total_price
)
    
    
    pdf.close()

    return Response({
        "message": "PDF received successfully",
        "filename": file.name,
        "file_id": file_id,
        "size": file.size,
        "pages": pages,
        "copies": copies,
        "color": color,
        "price_per_page": price_per_page,
        "total_price": total_price
    })
    
@api_view(['GET'])
def get_job(request, file_id):
    try:
        job = PrintJob.objects.get(file_id=file_id)
    except PrintJob.DoesNotExist:
        return Response(
            {"error": "Print job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        "file_id": job.file_id,
        "filename": job.original_filename,
        "pages": job.pages,
        "copies": job.copies,
        "color": job.color,
        "price_per_page": job.price_per_page,
        "total_price": job.total_price,
        "status": job.status,
        "created_at": job.created_at
    })
    
    
@api_view(['POST'])
def make_payment(request, file_id):
    try:
        job = PrintJob.objects.get(file_id=file_id)
    except PrintJob.DoesNotExist:
        return Response(
            {"error": "Print job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if job.status != 'PENDING':
        return Response(
            {"error": f"Payment not allowed. Current status is {job.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    job.status = 'PAID'
    job.save()

    return Response({
        "message": "Payment successful",
        "file_id": job.file_id,
        "amount": job.total_price,
        "status": job.status
    })
    
@api_view(['POST'])
def start_printing(request, file_id):
    try:
        job = PrintJob.objects.get(file_id=file_id)
    except PrintJob.DoesNotExist:
        return Response(
            {"error": "Print job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if job.status != 'PAID':
        return Response(
            {"error": f"Printing not allowed. Current status is {job.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    job.status = 'PRINTING'
    job.save()

    return Response({
        "message": "Printing started",
        "file_id": job.file_id,
        "status": job.status
    })
    
@api_view(['POST'])
def complete_printing(request, file_id):
    try:
        job = PrintJob.objects.get(file_id=file_id)
    except PrintJob.DoesNotExist:
        return Response(
            {"error": "Print job not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if job.status != 'PRINTING':
        return Response(
            {"error": f"Print completion not allowed. Current status is {job.status}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    job.status = 'COMPLETED'
    job.save()

    return Response({
        "message": "Printing completed successfully",
        "file_id": job.file_id,
        "status": job.status
    })
    
    
def get_printers(request):
    printers = win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL |
        win32print.PRINTER_ENUM_CONNECTIONS
    )

    printer_names = []

    for printer in printers:
        printer_names.append(printer[2])

    return JsonResponse({
        "printers": printer_names
    })
    
    
@api_view(['POST'])
def test_printer(request):
    printer_name = request.data.get('printer')

    if not printer_name:
        return Response(
            {"error": "Printer name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        printer = win32print.OpenPrinter(printer_name)

        return Response({
            "message": "Printer found successfully",
            "printer": printer_name
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
        
        
        
@api_view(['POST'])
def test_print_pdf(request):
    printer_name = request.data.get('printer')
    file_id = request.data.get('file_id')

    if not printer_name:
        return Response(
            {"error": "Printer name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not file_id:
        return Response(
            {"error": "file_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    file_path = os.path.join(
        settings.BASE_DIR,
        "uploads",
        f"{file_id}.pdf"
    )

    if not os.path.exists(file_path):
        return Response(
            {"error": "PDF file not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        printer = win32print.OpenPrinter(printer_name)

        win32api.ShellExecute(
            0,
            "print",
            file_path,
            f'"{printer_name}"',
            ".",
            0
        )

        win32print.ClosePrinter(printer)

        return Response({
            "message": "Print command sent successfully",
            "printer": printer_name,
            "file_id": file_id,
            "file_path": file_path
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )