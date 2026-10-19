from django.urls import path

from .views import SignupView, LoginView, LogoutView, refresh_token, auth_status

urlpatterns = [
    path("signup/", SignupView),
    path('login/', LoginView.as_view()),
    path('token/refresh/', refresh_token),
    path('logout/', LogoutView),
    path('status/', auth_status),
]
