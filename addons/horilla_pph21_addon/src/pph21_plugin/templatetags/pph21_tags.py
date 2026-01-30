from django import template

from pph21_plugin.forms import EmployeeTaxProfileForm
from pph21_plugin.models import EmployeeTaxProfile
from pph21_plugin.services import desired_pph21_filing_status_name

register = template.Library()


@register.inclusion_tag("pph21_plugin/employee_tax_profile_card.html")
def pph21_tax_profile_card(employee):
    profile = EmployeeTaxProfile.objects.filter(employee_id=employee).first()
    if profile is None:
        profile = EmployeeTaxProfile(employee_id=employee, ptkp_status="TK0")

    form = EmployeeTaxProfileForm(instance=profile)
    desired_status = desired_pph21_filing_status_name(
        ptkp_status=profile.ptkp_status, has_npwp=profile.has_npwp
    )
    contract = (
        employee.contract_set.filter(contract_status="active").order_by("-id").first()
        if hasattr(employee, "contract_set")
        else None
    )
    return {
        "employee": employee,
        "profile": profile,
        "form": form,
        "desired_status": desired_status,
        "contract": contract,
    }

