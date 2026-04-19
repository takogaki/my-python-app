from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.cache import never_cache

from .forms_auth import LoginForm
from .auth_utils import safe_next, secure_session_reset


@never_cache
def login_view(request):

    form = LoginForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                # 🔥 ① セッション完全破壊
                secure_session_reset(request)

                # 🔥 ② ログイン
                login(request, user)

                # 🔥 ③ next安全化
                next_url = safe_next(request.POST.get("next"))

                return redirect(next_url or "accounts:mypage")

            messages.error(request, "ログイン失敗")

    return render(request, "accounts/login.html", {
        "form": form
    })