from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

User = get_user_model()

def validate_video_size(file):
    limit = 50 * 1024 * 1024  # 50MB
    if file.size > limit:
        raise ValidationError("動画は50MB以下にしてください")

class VideoPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    video = models.FileField(
        upload_to='videos/',
        validators=[
            validate_video_size,
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'webm'])
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.id}"