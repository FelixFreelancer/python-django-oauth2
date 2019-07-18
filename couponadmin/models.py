from django.db import models


class CouponAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    coupon_uploaded_count = models.CharField(max_length=20, blank=True, default="", null=True)
    coupon_skipped_count = models.CharField(max_length=20, blank=True, default="", null=True)
    coupon_upload_status = models.CharField(max_length=20, blank=True, default="", null=True)
    coupon_upload_date = models.DateTimeField()

    def __str__(self):
        return self.coupon_upload_date

    class Meta:
        managed = False
        db_table = 'coupon_import_trans'
