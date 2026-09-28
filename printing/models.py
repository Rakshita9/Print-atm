from django.db import models


class PrintJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PRINTING', 'Printing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    file_id = models.CharField(max_length=100, unique=True)
    original_filename = models.CharField(max_length=255)

    pages = models.IntegerField()
    copies = models.IntegerField(default=1)

    color = models.BooleanField(default=False)
    price_per_page = models.IntegerField()
    total_price = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename