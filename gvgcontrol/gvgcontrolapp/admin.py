from django.contrib import admin
# Register your models here.
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
	list_display = ('nickname', 'discord_id', 'status', 'payment_method', 'paid_at', 'expired_in', 'created_at')
	search_fields = ('nickname', 'discord_id')
	list_filter = ('status', 'payment_method')
# Register your models here.
