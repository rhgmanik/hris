from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from base.horilla_company_manager import HorillaCompanyManager
from employee.models import Employee
from pph21_plugin.indonesia import DEFAULT_PPH21_CONFIG


class EmployeeTaxProfile(models.Model):
    NPWP_DIGITS_RE = r"^\d{15}$"

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    employee_id = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="pph21_tax_profile",
    )
    ptkp_status = models.CharField(
        max_length=3,
        choices=[(k, k) for k in DEFAULT_PPH21_CONFIG.ptkp_map.keys()],
        default="TK0",
    )
    npwp_number = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9.\-\\s]*$",
                message="NPWP hanya boleh berisi angka, titik, strip, atau spasi.",
            )
        ],
    )

    objects = HorillaCompanyManager(
        related_company_field="employee_id__employee_work_info__company_id"
    )

    @property
    def npwp_digits(self) -> str:
        return "".join(ch for ch in (self.npwp_number or "") if ch.isdigit())

    @property
    def has_npwp(self) -> bool:
        return bool(self.npwp_digits)

    def clean(self):
        super().clean()
        digits = self.npwp_digits
        if digits and len(digits) != 15:
            raise ValidationError(
                {"npwp_number": "NPWP harus 15 digit (boleh pakai pemisah . atau -)."}
            )

    def __str__(self) -> str:
        return f"PPh21 Tax Profile: {self.employee_id}"

    class Meta:
        verbose_name = "Employee Tax Profile (PPh21)"
        verbose_name_plural = "Employee Tax Profiles (PPh21)"
