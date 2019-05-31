from django.db import models

# Create your models here.
class BuyNotify(models.Model):
    id = models.AutoField(primary_key=True)
    projectName = models.CharField(max_length=150, blank=True, default="", null=True)
    shopName = models.CharField(max_length=150, blank=True, default="", null=True)
    goodsName = models.CharField(max_length=150, blank=True, default="", null=True)
    couponCode = models.CharField(max_length=150, blank=True, default="", null=True)
    buyAmount = models.CharField(max_length=50, blank=True, default="", null=True)
    buyTime = models.DateTimeField()
    belongArea = models.CharField(max_length=150, blank=True, default="", null=True)
    result = models.TextField(max_length=250, blank=True, default="", null=True)
    def __str__(self):
        return self.projectName

    class Meta:
        managed = False
        db_table = 'buynotify'


class UseNotify(models.Model):
    id = models.AutoField(primary_key=True)
    projectName = models.CharField(max_length=150, blank=True, default="", null=True)
    shopName = models.CharField(max_length=150, blank=True, default="", null=True)
    goodsName = models.CharField(max_length=150, blank=True, default="", null=True)
    couponCode = models.CharField(max_length=150, blank=True, default="", null=True)
    buyAmount = models.CharField(max_length=50, blank=True, default="", null=True)
    buyTime = models.DateTimeField()
    useStore = models.CharField(max_length=150, blank=True, default="", null=True)
    useAmount = models.CharField(max_length=50, blank=True, default="", null=True)
    useTime = models.DateTimeField()
    belongArea = models.CharField(max_length=150, blank=True, default="", null=True)
    result = models.TextField(max_length=250, blank=True, default="", null=True)
    def __str__(self):
        return self.projectName

    class Meta:
        managed = False
        db_table = 'usenotify'