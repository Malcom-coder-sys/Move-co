from django.contrib import admin
from .models import Commande

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display  = ["nom", "service", "date", "statut", "created_at"]
    list_filter   = ["statut", "service"]
    search_fields = ["nom", "email"]