from django.urls import path

from employee import urls as employee_urls
from pph21_plugin import views


def patch_employee_urls():
    for p in employee_urls.urlpatterns:
        if getattr(p, "name", None) == "pph21-employee-tax-profile-update":
            return
    employee_urls.urlpatterns.append(
        path(
            "pph21-tax-profile/<int:employee_id>/",
            views.employee_tax_profile_update,
            name="pph21-employee-tax-profile-update",
        )
    )

