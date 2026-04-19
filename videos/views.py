from .models import Post
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# 動画フィード
def feed(request):
    posts = Post.objects.select_related("user").order_by("-created_at")
    return render(request, "videos/feed.html", {"posts": posts})



# 動画アップロード
@login_required
def upload(request):
    if request.method == "POST":
        Post.objects.create(
            user=request.user,
            media_type=request.POST.get("media_type"),
            file=request.FILES.get("file"),
            caption=request.POST.get("caption")
        )
        return redirect("feed")

    return render(request, "videos/upload.html")