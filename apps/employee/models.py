import threading

import decouple
import requests
from django.db import models
from requests.auth import HTTPDigestAuth

from apps.utils.base_models import CreateUpdateBaseModel

HIK_USER= decouple.config('HIK_USER')
HIK_PASS= decouple.config('HIK_PASS')
HIK_BASE1= decouple.config('HIK_BASE1')




# Create your models here.
class Employee(CreateUpdateBaseModel):
    full_name = models.CharField(max_length=255, db_index=True, null=True)
    department = models.CharField(max_length=255, db_index=True, null=True)
    lavozim = models.CharField(max_length=255, db_index=True, null=True)
    image = models.FileField(upload_to='employee_faces/', null=True)
    face_encoding = models.JSONField(null=True, blank=True)

    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)  # +998...
    tg_id = models.BigIntegerField(unique=True, db_index=True, null=True)

    hemis_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'employee'
        verbose_name = 'Employees'
        ordering = ['-created_at']


    def add_to_hikvision(self):
        """
        Hikvision ga user va face image (URL orqali) yuborish
        """

        def thread_func(employee):
            auth = HTTPDigestAuth(HIK_USER, HIK_PASS)
            try:
                # --- STEP 1: User yaratish ---
                body_user = {
                    "UserInfo": {
                        "employeeNo": str(employee.id),
                        "name": employee.full_name,
                        "userType": "normal",
                        "Valid": {
                            "enable": True,
                            "beginTime": "2025-01-01T00:00:00",
                            "endTime": "2035-12-31T23:59:59"
                        }
                    }
                }
                for base in [HIK_BASE1]:
                    try:
                        res = requests.post(
                            f"{base}/ISAPI/AccessControl/UserInfo/Record?format=json",
                            auth=auth,
                            json=body_user,
                            timeout=5
                        )
                        if res.status_code not in [200, 201]:
                            print(f"User create xatosi ({base}): {res.status_code} | {res.text}")
                    except Exception as e:
                        print(f"User create exception ({base}): {e}")

                # --- STEP 2: Face image URL yuborish (agar rasm bor bo'lsa) ---
                if employee.image:
                    try:
                        # Django MEDIA URL ni olish
                        image_url = f"https://api-kengash.tashmeduni.uz/media/{employee.image}"
                        print(image_url)

                        face_body = {
                            "faceURL": image_url,
                            "faceLibType": "blackFD",
                            "FPID": str(employee.id),
                            "FDID": '1',
                            "featurePointType": "face"
                        }

                        for base in [HIK_BASE1]:
                            try:
                                res = requests.post(
                                    f"{base}/ISAPI/Intelligent/FDLib/FaceDataRecord?format=json",
                                    auth=auth,
                                    json=face_body,
                                    timeout=10
                                )
                                if res.status_code not in [200, 201]:
                                    print(f"Face URL upload xatosi ({base}): {res.status_code} | {res.text}")
                            except Exception as e:
                                print(f"Face URL upload exception ({base}): {e}")
                    except Exception as e:
                        print(f"Face URL tayyorlash xatosi: {e}")

                print(f"Hikvision: {employee.full_name} qo‘shildi")
            except Exception as e:
                print("Hikvision umumiy xatosi:", e)

        threading.Thread(target=thread_func, args=(self,)).start()

    def delete_from_hikvision(self):
        """
        Hikvision dan user o'chirish
        """

        def thread_func(employee):
            auth = HTTPDigestAuth(HIK_USER, HIK_PASS)
            try:
                body_del = {
                    "UserInfoDelCond": {
                        "EmployeeNoList": [{"employeeNo": str(employee.id)}]
                    }
                }
                for base in [HIK_BASE1]:
                    try:
                        res = requests.put(
                            f"{base}/ISAPI/AccessControl/UserInfo/Delete?format=json",
                            auth=auth,
                            json=body_del,
                            timeout=5
                        )
                        if res.status_code not in [200, 201]:
                            print(f"Delete xatosi ({base}): {res.status_code} | {res.text}")
                    except Exception as e:
                        print(f"Delete exception ({base}): {e}")

                print(f"Hikvision: {employee.full_name} o‘chirildi")
            except Exception as e:
                print("Hikvision delete umumiy xatosi:", e)

        threading.Thread(target=thread_func, args=(self,)).start()

