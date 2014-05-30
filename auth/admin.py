from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from auth.models import Account
from monitor.models import Team

class TeamInline(admin.TabularInline):
    model = Team

class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'account'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (AccountInline, )



admin.site.register(Account)
admin.site.register(Team)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)