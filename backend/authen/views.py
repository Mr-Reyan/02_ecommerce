from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def SignupView(request):

    serializer = RegisterSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    serializer.save()

    return Response(
        {"info": "User created successfully!"},
        status=201
    )



class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data["access"]
            refresh = response.data["refresh"]
            
            response.set_cookie(
                key="access",
                value=access,
                httponly=True,
                secure=False,      
                samesite="Lax",
                max_age=60*15,
            )

            response.set_cookie(
                key="refresh",
                value=refresh,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=60 * 60 * 24 * 7,
            )

            del response.data["access"]
            del response.data["refresh"]

        return response



@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token = request.COOKIES.get("refresh")

    if not refresh_token:
        return Response(
            {"detail": "Refresh token missing"},
            status=401,
        )

    try:
        refresh = RefreshToken(refresh_token)
        access = str(refresh.access_token)

        response = Response({"success": True})

        response.set_cookie(
            "access",
            access,
            httponly=True,
            secure=False,      # True in production with HTTPS
            samesite="Lax",
            max_age=60 * 15
        )

        return response

    except Exception:
        return Response(
            {"detail": "Invalid refresh token"},
            status=401
        )

@api_view(['POST'])
def LogoutView(request):
    response = Response({
        'info':'Logged Out successfully.'
    },status=200)

    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_status(request):
    """Check if user has valid access token in cookies"""
    access_token = request.COOKIES.get('access')
    
    if not access_token:
        return Response({'authenticated': False}, status=200)
    
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        AccessToken(access_token)
        return Response({'authenticated': True}, status=200)
    except Exception:
        return Response({'authenticated': False}, status=200)

