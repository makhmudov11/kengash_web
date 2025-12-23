from django.contrib import admin
from apps.employee.models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "department",
        "lavozim",
        "phone_number",
        "tg_id",
        "created_at",
    )
    list_filter = ("department", "lavozim", "created_at")
    search_fields = ("full_name", "phone_number", "tg_id")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Asosiy maʼlumotlar", {
            "fields": ("full_name", "department", "lavozim")
        }),
        ("Kontakt", {
            "fields": ("phone_number", "tg_id", "hemis_id")
        }),
        ("Face maʼlumotlar", {
            "fields": ("image", "face_encoding")
        }),
        ("Vaqtlar", {
            "fields": ("created_at", "updated_at")
        }),
    )

    actions = ["add_to_hikvision_action", "delete_from_hikvision_action"]

    @admin.action(description="Hikvision ga yuborish")
    def add_to_hikvision_action(self, request, queryset):
        for employee in queryset:
            employee.add_to_hikvision()

    @admin.action(description="Hikvision dan o‘chirish")
    def delete_from_hikvision_action(self, request, queryset):
        for employee in queryset:
            employee.delete_from_hikvision()
