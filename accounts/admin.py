from django.contrib import admin
from .models import CustomUser
from django.db.models.deletion import Collector
from django.db import router

@admin.action(description="選択したユーザーと関連データを完全削除")
def delete_users_and_all_related_data(modeladmin, request, queryset):
    for user in queryset:
        # DjangoのCollectorを使って関連オブジェクトを削除
        using = router.db_for_write(user._meta.model)  # データベースのルーティングを確認
        collector = Collector(using=using)  # Collectorを初期化
        collector.collect([user])  # 対象のユーザーと関連データを収集
        collector.delete()  # 収集したデータをすべて削除

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
    search_fields = ['username', 'email']