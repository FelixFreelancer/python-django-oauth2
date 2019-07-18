from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.db import models
from coupon.models import ApiKey, Coupon, CouponType, CouponRequest
from couponadmin.models import CouponAdmin
from django.template import loader
from io import TextIOWrapper
from django.utils.text import mark_safe
import csv
import datetime


class CouponUploadAdmin(admin.ModelAdmin):
    list_display = ('upload_time', 'coupon_uploaded_count', 'coupon_skipped_count', 'upload_status')
    change_list_template = "admin/coupon_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('csvUpload', self.csv_upload)
        ]
        return custom_urls + urls

    def upload_time(self, obj):
        return obj.coupon_upload_date.strftime("%Y-%m-%d %H:%M:%S")

    def upload_status(self, obj):
        if obj.coupon_upload_status == 'true' and obj.coupon_skipped_count == '0':
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" style="width: 18px">')
        else:
            return mark_safe('<img src="/static/admin/img/icon-alert.svg" style="width: 18px">')
    def csv_upload(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES["couponCSV"].file, encoding=request.encoding)
            coupon_type = request.POST['couponType']
            reader = csv.reader(csv_file)
            coupon_total_count = 0
            coupon_count = 0
            coupon_skipped_count = 0

            for row in reader:
                existing_coupon_count = Coupon.objects.filter(coupon=''.join(row)).count()
                coupon_total_count = coupon_total_count + 1
                if existing_coupon_count == 0:
                    coupon = Coupon(coupon=''.join(row))
                    coupon.save()
                    coupon_count = coupon_count + 1
                else:
                    coupon_skipped_count = coupon_skipped_count + 1

            coupon_admin = CouponAdmin(coupon_upload_date=datetime.datetime.now(), coupon_uploaded_count=coupon_count,
                                       coupon_upload_status='true', coupon_skipped_count=coupon_skipped_count)
            coupon_admin.save()
            self.message_user(request, "Your csv file has been imported")
            return HttpResponseRedirect('./')


admin.site.register(CouponAdmin, CouponUploadAdmin)
