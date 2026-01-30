from django import forms

from pph21_plugin.indonesia import DEFAULT_PPH21_CONFIG
from pph21_plugin.models import EmployeeTaxProfile


class EmployeeTaxProfileForm(forms.ModelForm):
    ptkp_status = forms.ChoiceField(
        choices=[(k, k) for k in DEFAULT_PPH21_CONFIG.ptkp_map.keys()],
        required=True,
    )

    class Meta:
        model = EmployeeTaxProfile
        fields = ["ptkp_status", "npwp_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ptkp_status"].widget.attrs.update({"class": "oh-input w-100"})
        self.fields["npwp_number"].widget.attrs.update(
            {"class": "oh-input w-100", "placeholder": "12.345.678.9-012.345"}
        )

    def clean_npwp_number(self):
        value = (self.cleaned_data.get("npwp_number") or "").strip()
        return value or None
