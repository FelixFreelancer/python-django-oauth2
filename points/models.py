from django.db import models

# Create your models here.
class Point(models.Model):
    id = models.AutoField(primary_key=True)
    third_party_sh_name = models.CharField(max_length=100, blank=True, default="", null=True)
    request_mode = models.CharField(max_length=50, blank=True, default="", null=True)
    third_userid = models.CharField(max_length=100, blank=True, default="", null=True)
    userid = models.CharField(max_length=50, blank=True, default="", null=True)
    account_name = models.CharField(max_length=50, blank=True, default="", null=True)
    balance = models.CharField(max_length=20, blank=True, default="", null=True)
    transaction_type = models.CharField(max_length=50, blank=True, default="", null=True)
    linked_trans_id = models.CharField(max_length=50, blank=True, default="", null=True)
    expiration_time = models.DateTimeField()
    points_accumulate_so_far = models.CharField(max_length=20, blank=True, default="", null=True)
    member_ship_no = models.CharField(max_length=50, blank=True, default="", null=True)
    token = models.TextField(max_length=256, blank=True, default="", null=True)
    reward_point = models.CharField(max_length=20, blank=True, default="", null=True)
    member_id = models.CharField(max_length=50, blank=True, default="", null=True)
    expiration_date = models.CharField(max_length=20, blank=True, default="", null=True)
    remaining_balance = models.CharField(max_length=20, blank=True, default="", null=True)
    points_to_be_expire_by_monthend = models.CharField(max_length=20, blank=True, default="", null=True)
    stays_balance = models.CharField(max_length=20, blank=True, default="", null=True)
    nights_balance = models.CharField(max_length=20, blank=True, default="", null=True)
    points_balance = models.CharField(max_length=20, blank=True, default="", null=True)
    point_accumulated = models.CharField(max_length=20, blank=True, default="", null=True)
    nights_accumulated = models.CharField(max_length=20, blank=True, default="", null=True)
    member_name = models.CharField(max_length=50, blank=True, default="", null=True)
    updated_at = models.CharField(max_length=50, blank=True, default="", null=True)


    def __str__(self):
        return self.third_party_sh_name

    class Meta:
        managed = False
        db_table = 'points'