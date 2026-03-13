from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, CustomTokenObtainPairSerializer


@extend_schema(tags=['Authentication'])
class RegisterView(generics.CreateAPIView):
    """Register a new user account."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT token pair (access + refresh) using email and password."""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=['Authentication'])
class MeView(APIView):
    """Get and update current user profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
