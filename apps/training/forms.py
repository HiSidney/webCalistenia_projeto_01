from django import forms

from .models import Set


class SetForm(forms.ModelForm):

    class Meta:
        model = Set

        fields = [
            "repetitions",
            "weight",
            "duration",
            "completed",
            "notes",
        ]

        widgets = {
            "repetitions": forms.NumberInput(
                attrs={
                    "min": 0,
                }
            ),

            "weight": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": 0,
                }
            ),

            "duration": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            ),
        }
