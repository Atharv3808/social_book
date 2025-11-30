from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import mimetypes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UploadedFile
from .serializers import UploadedFileSerializer


class MyUploadsList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = UploadedFile.objects.filter(user=request.user).order_by("-created_at")
        serializer = UploadedFileSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class MyUploadDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        obj = get_object_or_404(UploadedFile, pk=pk)
        # Only allow owner to access specific file
        if obj.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UploadedFileSerializer(obj, context={"request": request})
        return Response(serializer.data)


class MyUploadDownload(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        obj = get_object_or_404(UploadedFile, pk=pk)
        # Allow owner; optionally allow public visibility files
        if obj.user != request.user and obj.visibility != "public":
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not obj.file:
            return Response({"detail": "File not available."}, status=status.HTTP_404_NOT_FOUND)

        file_handle = obj.file.open("rb")
        content_type, _ = mimetypes.guess_type(obj.file.name)
        response = FileResponse(file_handle, content_type=content_type or "application/octet-stream")
        response["Content-Disposition"] = f"attachment; filename={obj.file.name.split('/')[-1]}"
        return response


class LoginAndMyFiles(APIView):
    """
    Combined endpoint: authenticate with username/password, issue JWT tokens,
    and return the authenticated user's uploaded files in one response.

    Request: POST {"username": "...", "password": "..."}
    Response: {"access": "...", "refresh": "...", "files": [ ... ]}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"detail": "username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is None or not getattr(user, "is_active", True):
            return Response({"detail": "No active account found with the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Return user's files
        qs = UploadedFile.objects.filter(user=user).order_by("-created_at")
        serializer = UploadedFileSerializer(qs, many=True, context={"request": request})

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "files": serializer.data,
        })
