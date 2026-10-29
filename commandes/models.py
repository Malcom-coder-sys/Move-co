from django.db import models

class Commande(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("confirme",   "Confirmé"),
        ("annule",     "Annulé"),
    ]
    SERVICE_CHOICES = [
        ("Déménagement simple",        "Déménagement simple"),
        ("Déménagement & Aménagement", "Déménagement & Aménagement"),
        ("Transport de colis",         "Transport de colis"),
        ("Aménagement intérieur",      "Aménagement intérieur"),
    ]

    nom        = models.CharField(max_length=100, verbose_name="Nom complet")
    email      = models.EmailField(verbose_name="Email")
    telephone  = models.CharField(max_length=20, verbose_name="Téléphone")
    service    = models.CharField(max_length=60, choices=SERVICE_CHOICES)
    date       = models.DateField(verbose_name="Date souhaitée")
    adresse    = models.TextField(verbose_name="Adresse de départ", blank=True)
    message    = models.TextField(verbose_name="Message / détails", blank=True)
    statut     = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Commande"

    def __str__(self):
        return f"{self.nom} — {self.service}"

    def statut_label(self):
        return dict(self.STATUT_CHOICES).get(self.statut, self.statut)

    def statut_color(self):
        return {"en_attente": "#f59e0b", "confirme": "#10b981", "annule": "#ef4444"}.get(self.statut, "#ccc")