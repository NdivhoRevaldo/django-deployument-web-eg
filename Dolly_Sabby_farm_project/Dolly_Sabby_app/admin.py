from django.contrib import admin
from Dolly_Sabby_app.models import *#AccessRecord,Topic,Webpage,UserProfileInfo
# Register your models here.
admin.site.register(AccessRecord)
admin.site.register(Topic)
admin.site.register(Webpage)
admin.site.register(UserProfileInfo)
admin.site.register([Admin,Customer, Category, Product, Cart, CartProduct, Order])
