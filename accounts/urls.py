from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import SignUpView, UserDetailView
from . import views

app_name = "accounts"

urlpatterns = [
    # 認証
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signup/done/", views.signup_done, name="signup_done"),
# ★ これが最重要
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),

    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(template_name="accounts/logout.html"), name="logout"),

    # ユーザー一覧・詳細
    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),

    # ユーザー公開ページ（username指定）
    path("user/<str:username>/", UserDetailView.as_view(), name="user_detail_by_username"),

    # メール認証（★これが唯一の activate）
    path("activate/<uuid:token>/", views.activate, name="activate")
]