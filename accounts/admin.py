from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	model = CustomUser
	# display these fields in the admin list
	list_display = ("username", "email", "first_name", "last_name", "is_staff", "public_visibility")
	# allow quick filtering and inline editing of visibility in the list view
	list_filter = ("public_visibility", "is_staff")
	list_editable = ("public_visibility",)
	list_display_links = ("username",)
	fieldsets = UserAdmin.fieldsets + (
		("Profile", {"fields": ("public_visibility", "birth_year", "age", "address")} ),
	)
	add_fieldsets = UserAdmin.add_fieldsets + (
		("Profile", {"fields": ("public_visibility", "birth_year", "address")} ),
	)
