from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
	"""Custom user model extending Django's AbstractUser.

	Fields added:
	- public_visibility: whether profile is public
	- birth_year: optional integer birth year
	- age: calculated from birth_year on save
	- address: optional free-text address
	"""
	public_visibility = models.BooleanField(default=True)
	birth_year = models.PositiveIntegerField(null=True, blank=True)
	age = models.PositiveIntegerField(null=True, blank=True)
	address = models.TextField(blank=True)

	def save(self, *args, **kwargs):
		# calculate age if birth_year is provided
		if self.birth_year:
			current_year = timezone.now().year
			try:
				self.age = max(0, current_year - int(self.birth_year))
			except Exception:
				# if invalid birth_year, leave age as-is
				pass
		super().save(*args, **kwargs)

# Create your models here.
