from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


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


class UploadedFile(models.Model):
    """User-uploaded file with metadata for the Upload Books dashboard."""
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploaded_files")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=7, choices=VISIBILITY_CHOICES, default="public")
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    year_published = models.PositiveIntegerField(null=True, blank=True)
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.user})"
