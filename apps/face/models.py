from datetime import date

from django.contrib.auth.models import User
from django.db import models

from apps.employee.models import Employee
from apps.utils.base_models import CreateUpdateBaseModel


class AttendanceChoice(models.TextChoices):
    KELDI = 'keldi', 'Keldi'
    KETDI = 'ketdi', 'Ketdi'


class Attendance(CreateUpdateBaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=10, choices=AttendanceChoice.choices, null=True)
    arrival_time = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering = ["-arrival_time"]

    def __str__(self):
        return f"{self.employee.full_name} - {self.status} - {self.arrival_time.strftime('%Y-%m-%d %H:%M')}"

class FaceLogChoice(models.TextChoices):
    RECOGNIZED = "recognized", "Tanishdi"
    NOT_FOUND = "not_found", "Topilmadi"

class FaceLog(CreateUpdateBaseModel):

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='facelogs')
    status = models.CharField(max_length=20, choices=FaceLogChoice.choices, default="recognized")

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['employee', 'created_at']),
        ]

    def __str__(self):
        name = self.employee.full_name if self.employee else "Noma'lum"
        return f"{name} — {self.status} ({self.created_at:%Y-%m-%d %H:%M})"

    @staticmethod
    def has_attended_today(employee):
        """Bugun FaceLog da yozuv bormi?"""
        today = date.today()
        return FaceLog.objects.filter(
            employee=employee,
            created_at__date=today,
            status=FaceLogChoice.RECOGNIZED
        )
