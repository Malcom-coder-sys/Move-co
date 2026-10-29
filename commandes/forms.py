from django import forms
from django.utils import timezone
from .models import Commande

class CommandeForm(forms.ModelForm):
    class Meta:
        model  = Commande
        fields = ["nom", "email", "telephone", "service", "date", "adresse", "message"]
        widgets = {
            "nom":       forms.TextInput(attrs={"placeholder": "Jean Dupont",         "class": "form-input"}),
            "email":     forms.EmailInput(attrs={"placeholder": "jean@email.com",      "class": "form-input"}),
            "telephone": forms.TextInput(attrs={"placeholder": "+237 6XX XXX XXX",     "class": "form-input"}),
            "service":   forms.Select(attrs={"class": "form-input"}),
            "date":      forms.DateInput(attrs={"type": "date",                        "class": "form-input"}),
            "adresse":   forms.Textarea(attrs={"placeholder": "Votre adresse actuelle","class": "form-input", "rows": 2}),
            "message":   forms.Textarea(attrs={"placeholder": "Informations complémentaires...", "class": "form-input", "rows": 3}),
        }
        labels = {
            "nom":       "Nom complet",
            "email":     "Adresse email",
            "telephone": "Téléphone",
            "service":   "Service souhaité",
            "date":      "Date souhaitée",
            "adresse":   "Adresse de départ",
            "message":   "Message (optionnel)",
        }

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date < timezone.localdate():
            raise forms.ValidationError("La date souhaitée ne peut pas être dans le passé.")
        return date
