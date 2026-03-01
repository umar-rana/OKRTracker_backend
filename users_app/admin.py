from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, Membership, Team, Invitation

@admin.register(User)
class TrackrUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active')
    list_filter = ('organization', 'role', 'is_active')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'lead')
    list_filter = ('organization',)

admin.site.register(Invitation)
