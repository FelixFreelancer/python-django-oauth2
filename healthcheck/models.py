from django.db import models
import datetime
# Create your models here.
class HealthCheck(models.Model):
    id = models.AutoField(primary_key=True)
    requested_api = models.CharField(max_length=50, blank=True, default="", null=True)
    requested_time = models.DateTimeField()
    ip_address = models.CharField(max_length=50, blank=True, default="", null=True)

    def __str__(self):
        return self.requested_api

    class Meta:
        managed = False
        db_table = 'healthcheck'

