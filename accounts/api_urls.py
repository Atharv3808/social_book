from django.urls import path
from .api_views import MyUploadsList, MyUploadDetail, MyUploadDownload, LoginAndMyFiles

app_name = "api"

urlpatterns = [
    path("uploads/", MyUploadsList.as_view(), name="my_uploads"),
    path("uploads/<int:pk>/", MyUploadDetail.as_view(), name="my_upload_detail"),
    path("uploads/<int:pk>/download/", MyUploadDownload.as_view(), name="my_upload_download"),
    path("auth/login-and-files/", LoginAndMyFiles.as_view(), name="login_and_files"),
]
