from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer,LoginSerializer

# CSRF

from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.views import APIView
# Create your views here.
User = get_user_model()

class CSRFTokenView(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        token = get_token(request)
        return JsonResponse({'csrfToken':token})


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
    print("Cookies:", request.COOKIES)

    refresh_token = request.COOKIES.get("refresh")

    if not refresh_token:
        print("No refresh cookie received")
        return Response(
            {"detail": "Refresh token missing"},
            status=401,
        )

    try:
        refresh = RefreshToken(refresh_token)
        print("Refresh successful")
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

    except Exception as e:
        print(e)
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

