from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("employee", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeTaxProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                (
                    "ptkp_status",
                    models.CharField(
                        choices=[
                            ("TK0", "TK0"),
                            ("TK1", "TK1"),
                            ("TK2", "TK2"),
                            ("TK3", "TK3"),
                            ("K0", "K0"),
                            ("K1", "K1"),
                            ("K2", "K2"),
                            ("K3", "K3"),
                        ],
                        default="TK0",
                        max_length=3,
                    ),
                ),
                (
                    "npwp_number",
                    models.CharField(
                        blank=True,
                        max_length=32,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="NPWP hanya boleh berisi angka, titik, strip, atau spasi.",
                                regex="^[0-9.\\-\\\\s]*$",
                            )
                        ],
                    ),
                ),
                (
                    "employee_id",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pph21_tax_profile",
                        to="employee.employee",
                    ),
                ),
            ],
            options={},
        ),
    ]

