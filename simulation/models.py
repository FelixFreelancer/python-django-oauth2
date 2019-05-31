from django.db import models
import datetime
# Create your models here.
class Simulation(models.Model):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=50, blank=True, default="", null=True)
    third_userid = models.CharField(max_length=100, blank=True, default="", null=True)
    third_password = models.CharField(max_length=100, blank=True, default="", null=True)
    third_registered_phone_number = models.CharField(max_length=100, blank=True, default="", null=True)
    third_party_sh_name = models.CharField(max_length=100, blank=True, default="", null=True)
    request_mode = models.CharField(max_length=50, blank=True, default="", null=True)
    expiration_time = models.DateTimeField()
    error_msg = models.CharField(max_length=250, blank=True, default="", null=True)
    token = models.TextField(max_length=256, blank=True, default="", null=True)
    success = models.CharField(max_length=50, blank=True, default="", null=True)

    def __str__(self):
        return self.userid

    class Meta:
        managed = False
        db_table = 'user_profile'

class Cnonce(models.Model):
    nonce = models.CharField(db_index=True, max_length=300)
    timestamp = models.DateTimeField()
    created_time = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.timestamp

    class Meta:
        managed = False
        db_table = 'nonce'
