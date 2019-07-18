from django.db import models
import datetime
# Create your models here.
class Coupon(models.Model):
    id = models.AutoField(primary_key=True)
    coupon = models.CharField(db_index=True, max_length=50, blank=True, default="", null=True)
    coupon_type_id = models.CharField(max_length=100, blank=True, default="", null=True)
    redeemed = models.CharField(max_length=10, blank=True, default="", null=True)
    validated = models.CharField(max_length=10, blank=True, default="", null=True)
    activated = models.CharField(max_length=10, blank=True, default="", null=True)
    min_pax = models.CharField(max_length=10, blank=True, default="", null=True)
    start_date = models.DateField(default=datetime.date.today)
    expiry_date = models.DateField(default=datetime.date.today)
    booking_expiry_date = models.DateField(default=datetime.date.today)
    def __str__(self):
        return self.coupon

    class Meta:
        managed = False
        db_table = 'coupon'
        indexes = [
            models.Index(fields=['coupon'])
        ]


class CouponType(models.Model):
    id = models.AutoField(primary_key=True)
    coupon_id = models.CharField(max_length=100, blank=True, default="", null=True)
    prefix = models.CharField(max_length=50, blank=True, default="", null=True)
    prefix_description = models.TextField(max_length=100, blank=True, default="", null=True)
    suffix = models.CharField(max_length=50, blank=True, default="", null=True)
    suffix_description = models.TextField(max_length=50, blank=True, default="", null=True)
    coupon_cost = models.CharField(max_length=20, blank=True, default="", null=True)
    coupon_value = models.CharField(max_length=50, blank=True, default="", null=True)
    coupon_validity_days = models.IntegerField(default=0, null=True)
    coupon_reseller_list_price = models.CharField(max_length=50, blank=True, default="", null=True)
    coupon_currency = models.CharField(max_length=50, blank=True, default="", null=True)
    def __str__(self):
        return self.coupon_id

    class Meta:
        managed = False
        db_table = 'coupon_type'

class CouponRequest(models.Model):
    id = models.AutoField(primary_key=True)
    coupon_type_id = models.CharField(max_length=100, blank=True, default="", null=True)
    coupon_count = models.CharField(max_length=20, blank=True, default="", null=True)
    coupon_code = models.TextField(blank=True, default="", null=True)
    coupon_purpose = models.TextField(blank=True, default="", null=True)
    coupon_description = models.TextField(blank=True, default="", null=True)
    coupon_issuance_date = models.DateTimeField()
    coupon_expiration_date = models.DateTimeField()
    def __str__(self):
        return self.coupon_type_id

    class Meta:
        managed = False
        db_table = 'coupon_request'

class ApiKey(models.Model):
    id = models.AutoField(primary_key=True)
    api_key = models.CharField(max_length=100, blank=True, default="", null=True)
    requestor_org_id = models.CharField(max_length=100, blank=True, default="", null=True)
    requestor_id = models.CharField(max_length=100, blank=True, default="", null=True)

    def __str__(self):
        return self.api_key

    class Meta:
        managed = False
        db_table = 'api_key'