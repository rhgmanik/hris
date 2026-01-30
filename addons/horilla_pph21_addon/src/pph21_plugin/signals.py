from django.db.models.signals import post_save
from django.dispatch import receiver

from pph21_plugin.models import EmployeeTaxProfile
from pph21_plugin.services import sync_contract_filing_status_from_tax_profile


@receiver(post_save, sender=EmployeeTaxProfile)
def _sync_employee_contract_on_tax_profile_change(sender, instance, **kwargs):
    employee = instance.employee_id
    if employee:
        sync_contract_filing_status_from_tax_profile(employee=employee, profile=instance)

