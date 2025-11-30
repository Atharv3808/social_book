from rest_framework import serializers
from .models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = [
            "id",
            "title",
            "description",
            "visibility",
            "cost",
            "year_published",
            "file_url",
            "created_at",
        ]

    def get_file_url(self, obj):
        try:
            return obj.file.url
        except Exception:
            return None