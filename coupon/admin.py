from django.contrib import admin
from coupon.models import ApiKey, Coupon, CouponType, CouponRequest
from django.urls import path
from django.http import HttpResponseRedirect
import csv
from io import TextIOWrapper
# Register your models here.

admin.site.site_header = 'AsiaTop Restful API Administrator'


class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'redeemed', 'validated', 'activated')
    change_list_template = 'admin/coupon/coupon_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('csvUpload', self.csvUpload)
        ]
        return custom_urls + urls


    def csvUpload(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES["couponCSV"].file, encoding=request.encoding)
            reader = csv.reader(csv_file)
            for row in reader:
                coupon = Coupon(coupon=''.join(row))
                coupon.save()
            self.message_user(request, "Your csv file has been imported")
            return HttpResponseRedirect('../')


admin.site.register(ApiKey)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(CouponType)
admin.site.register(CouponRequest)


# Register your models here.
