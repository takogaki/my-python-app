from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def random_call(request):

    return render(
        request,
        "random_call/index.html",
    )


@login_required
def random_call_test(request):

    return render(
        request,
        "random_call/test.html",
    )