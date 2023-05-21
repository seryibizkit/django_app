from django.contrib.auth.views import LoginView
from django.urls import path, include

from .views import get_cookie_view, set_cookie_view, \
    set_session_view, get_session_view, MyLogoutView, AboutMeView, \
    RegisterView


app_name = "myauth"

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    # path("login/",
    #      LoginView.as_view(
    #          redirect_authenticated_user=True,
    #          template_name="myauth/login.html"),
    #      name="login"),
    # path("logout/", logout_view, name="logout"),
    # path("logout/", MyLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),
]
