from __future__ import annotations

from typing import Optional

from employee.models import Employee
from payroll.models.models import Contract, FilingStatus
from pph21_plugin.indonesia import policy_code_snippet_for
from pph21_plugin.models import EmployeeTaxProfile


def desired_pph21_filing_status_name(*, ptkp_status: str, has_npwp: bool) -> str:
    status = (ptkp_status or "TK0").strip().upper()
    base = f"PPh21 {status}"
    if not has_npwp:
        return f"{base} No NPWP"
    return base


def ensure_pph21_filing_status(
    *,
    employee: Employee,
    ptkp_status: str,
    has_npwp: bool,
) -> FilingStatus:
    company = employee.get_company() if hasattr(employee, "get_company") else None
    status_name = desired_pph21_filing_status_name(ptkp_status=ptkp_status, has_npwp=has_npwp)

    qs = FilingStatus.objects.filter(filing_status=status_name)
    if company:
        qs = qs.filter(company_id=company)
    else:
        qs = qs.filter(company_id__isnull=True)

    filing = qs.first()
    if filing:
        return filing

    filing = FilingStatus(
        company_id=company,
        filing_status=status_name,
        based_on="taxable_gross_pay",
        use_py=True,
        python_code=policy_code_snippet_for(ptkp_status=ptkp_status, has_npwp=has_npwp),
    )
    filing.save()
    return filing


def sync_contract_filing_status_from_tax_profile(
    *,
    employee: Employee,
    profile: EmployeeTaxProfile,
) -> Optional[Contract]:
    filing = ensure_pph21_filing_status(
        employee=employee,
        ptkp_status=profile.ptkp_status,
        has_npwp=profile.has_npwp,
    )

    contract = (
        Contract.objects.filter(employee_id=employee, contract_status="active")
        .order_by("-id")
        .first()
    )
    if contract is None:
        contract = (
            Contract.objects.filter(employee_id=employee, contract_status="draft")
            .order_by("-id")
            .first()
        )

    if contract is None:
        return None

    contract.filing_status = filing
    contract.save(update_fields=["filing_status"])
    return contract

