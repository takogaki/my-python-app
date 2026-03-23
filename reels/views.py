from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import VideoPost
from .forms import VideoPostForm

# フィード（誰でも閲覧OK）
def video_feed(request):
    posts = VideoPost.objects.order_by('-created_at')[:20]
    return render(request, 'reels/feed.html', {'posts': posts})


# 投稿（ログイン必須）
@login_required
def video_upload(request):
    if request.method == 'POST':
        form = VideoPostForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            return redirect('video_feed')
    else:
        form = VideoPostForm()

    return render(request, 'reels/upload.html', {'form': form})