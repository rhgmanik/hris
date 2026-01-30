from django.core.management.base import BaseCommand
from django.db import transaction

from base.models import Company
from payroll.models.models import FilingStatus
from pph21_plugin.indonesia import policy_code_snippet


class Command(BaseCommand):
    help = "Install/update PPh21 Python Code (plugin) pada FilingStatus."

    def add_arguments(self, parser):
        parser.add_argument("--company-id", type=int, default=None)
        parser.add_argument("--all-companies", action="store_true")
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        company_id = options.get("company_id")
        all_companies = bool(options.get("all_companies"))
        force = bool(options.get("force"))
        dry_run = bool(options.get("dry_run"))

        if company_id and all_companies:
            self.stdout.write("Pilih salah satu: --company-id atau --all-companies")
            return

        snippet = policy_code_snippet().strip() + "\n"

        if all_companies:
            targets = list(Company.objects.all())
        elif company_id:
            targets = [Company.objects.get(id=company_id)]
        else:
            targets = [None]

        updated = 0
        skipped = 0
        created = 0

        for company in targets:
            filing = (
                FilingStatus.objects.filter(company_id=company, filing_status="PPh21").first()
                if company
                else FilingStatus.objects.filter(company_id__isnull=True, filing_status="PPh21").first()
            )
            if filing is None:
                filing = FilingStatus(
                    company_id=company,
                    filing_status="PPh21",
                    based_on="taxable_gross_pay",
                )
                if not dry_run:
                    filing.save()
                created += 1

            current = (filing.python_code or "").strip()
            next_code = snippet.strip()

            if current and not force and current != next_code:
                skipped += 1
                self.stdout.write(
                    f"- SKIP filing id={getattr(filing,'id',None)} company_id={getattr(company,'id',None)}: sudah ada python_code. Pakai --force untuk overwrite."
                )
                continue

            filing.use_py = True
            filing.python_code = snippet

            if not dry_run:
                filing.save()

            updated += 1
            self.stdout.write(
                f"- OK filing id={getattr(filing,'id',None)} company_id={getattr(company,'id',None)} use_py=True"
            )

        self.stdout.write("")
        self.stdout.write(f"Created policy: {created}")
        self.stdout.write(f"Updated policy: {updated}")
        self.stdout.write(f"Skipped policy: {skipped}")
        if dry_run:
            self.stdout.write("Dry-run: tidak ada perubahan yang disimpan.")
