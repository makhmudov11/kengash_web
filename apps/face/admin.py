from django.contrib import admin
from apps.face.models import Attendance, FaceLog


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "status",
        "arrival_time",
        "created_at",
    )
    list_filter = ("status", "arrival_time")
    search_fields = ("employee__full_name",)
    ordering = ("-arrival_time",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(FaceLog)
class FaceLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("employee__full_name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
