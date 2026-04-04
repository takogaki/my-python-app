from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import SignUpView, UserDetailView, UserListView, like_user
from . import views
from .views import mypage


app_name = "accounts"

urlpatterns = [
    # 認証
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signup/done/", views.signup_done, name="signup_done"),

    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(template_name="accounts/logout.html"), name="logout"),

    # 利用規約
    path('terms/', views.terms, name='terms'),

    # ユーザー一覧・詳細
    path("users/", views.user_list, name="user_list"),
    path("users/<str:username>/", views.UserDetailView.as_view(), name="user_detail"),

    # ユーザー公開ページ（username指定）
    path("mypage/", views.mypage, name="mypage"),
    path("user/<str:username>/", UserDetailView.as_view(), name="user_detail_by_username"),

    # メール認証（★これが唯一の activate）
    path("activate/<uuid:token>/", views.activate, name="activate"),

    # プロフィール設定
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/image/delete/", views.profile_image_delete, name="profile_image_delete"),

    # アカウント削除（退会）
    path("withdraw/", views.withdraw_confirm, name="withdraw_confirm"),
    path("withdraw/execute/", views.withdraw_execute, name="withdraw_execute"),

    # 管理人へ連絡
    path("contact-eden/", views.contact_eden, name="contact_eden"),
    path("contact-eden/done/", views.contact_eden_done, name="contact_eden_done"),
    # 404エラー未ログイン時
    path("contact-eden-public/", views.contact_eden_public, name="contact_eden_public"),

    # footprint（足跡）
    path("footprints/", views.footprint_list, name="footprints"),

    #likeユーザー
    path("liked/", views.liked_me, name="liked_me"),
    path("like/<int:user_id>/", views.like_user, name="like_user"),
    path("matches/", views.match_list, name="match_list"),

    #本人確認（KYC）
    path("kyc/", views.kyc_submit, name="kyc_submit"),
    path("admin/kyc/", views.admin_kyc_list, name="admin_kyc_list"),
    path("admin/kyc/<int:kyc_id>/approve/", views.admin_kyc_approve, name="admin_kyc_approve"),
    path("admin/kyc/<int:kyc_id>/reject/", views.admin_kyc_reject, name="admin_kyc_reject"),
    path("kyc/complete/mobile/", views.kyc_complete_mobile, name="kyc_complete_mobile"),

    # 通知
    path("notification/<int:id>/", views.notification_read, name="notification_read"),
]