from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from employee.models import Employee
from horilla.decorators import login_required, permission_required
from pph21_plugin.forms import EmployeeTaxProfileForm
from pph21_plugin.models import EmployeeTaxProfile
from pph21_plugin.services import sync_contract_filing_status_from_tax_profile


@login_required
@permission_required("employee.change_employee")
@require_http_methods(["POST"])
def employee_tax_profile_update(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    profile = EmployeeTaxProfile.objects.filter(employee_id=employee).first()
    if profile is None:
        profile = EmployeeTaxProfile(employee_id=employee)

    form = EmployeeTaxProfileForm(request.POST, instance=profile)
    if form.is_valid():
        profile = form.save()
        contract = sync_contract_filing_status_from_tax_profile(employee=employee, profile=profile)
        if contract is None:
            messages.success(
                request,
                _("Tax profile updated. Tidak ada contract aktif/draft untuk di-sync."),
            )
        else:
            messages.success(request, _("Tax profile updated dan contract telah di-sync."))
    else:
        messages.error(request, _("Tax profile tidak valid."))

    return HttpResponseRedirect(
        request.META.get("HTTP_REFERER")
        or reverse("employee-view-individual", kwargs={"obj_id": employee.id})
    )

