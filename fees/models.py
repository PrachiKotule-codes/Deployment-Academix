from django.db import models
from django.conf import settings
class FeeRecord(models.Model):
 student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='fee_records'); title=models.CharField(max_length=120); academic_year=models.CharField(max_length=20); amount=models.DecimalField(max_digits=10,decimal_places=2); due_date=models.DateField(blank=True,null=True); created_at=models.DateTimeField(auto_now_add=True)
class PaymentRecord(models.Model):
 fee=models.ForeignKey(FeeRecord,on_delete=models.CASCADE,related_name='payments'); amount=models.DecimalField(max_digits=10,decimal_places=2); paid_on=models.DateField(); reference=models.CharField(max_length=120,blank=True); recorded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
