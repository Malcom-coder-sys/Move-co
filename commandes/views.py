from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.views.decorators.http import require_POST
from datetime import timedelta
from .models import Commande
from .forms import CommandeForm


# ── Accueil ──────────────────────────────────────────────────────────
def home(request):
    return render(request, "home.html")


# ── Galerie ──────────────────────────────────────────────────────────
def galerie(request):
    return render(request, "galerie.html")


# ── Services + formulaire de commande ────────────────────────────────
def services(request):
    service_preselect = request.GET.get("service", "")
    form = CommandeForm(initial={"service": service_preselect} if service_preselect else {})
    return render(request, "services.html", {"form": form, "service_preselect": service_preselect})


def commander(request):
    if request.method == "POST":
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save()
            # Seul le navigateur qui a passé la commande peut voir sa confirmation
            request.session["derniere_commande"] = commande.pk
            return redirect("commande_success", pk=commande.pk)
        return render(request, "services.html", {
            "form": form,
            "service_preselect": request.POST.get("service", ""),
        })
    return redirect("services")


def commande_success(request, pk):
    if request.session.get("derniere_commande") != pk and not request.session.get("admin_auth"):
        return redirect("services")
    commande = get_object_or_404(Commande, pk=pk)
    return render(request, "commande_success.html", {"commande": commande})


# ── Admin ─────────────────────────────────────────────────────────────
def admin_login(request):
    if request.session.get("admin_auth"):
        return redirect("admin_dashboard")
    error = ""
    if request.method == "POST":
        password = request.POST.get("password", "")
        if constant_time_compare(password, settings.MOVECO_ADMIN_PASSWORD):
            request.session.cycle_key()
            request.session["admin_auth"] = True
            return redirect("admin_dashboard")
        error = "Mot de passe incorrect."
    return render(request, "admin_login.html", {"error": error})


def admin_logout(request):
    request.session.flush()
    return redirect("admin_login")


def admin_dashboard(request):
    if not request.session.get("admin_auth"):
        return redirect("admin_login")

    statut_filter = request.GET.get("statut", "")
    commandes = Commande.objects.all()
    if statut_filter in dict(Commande.STATUT_CHOICES):
        commandes = commandes.filter(statut=statut_filter)

    stats = {
        "total":      Commande.objects.count(),
        "en_attente": Commande.objects.filter(statut="en_attente").count(),
        "confirme":   Commande.objects.filter(statut="confirme").count(),
        "annule":     Commande.objects.filter(statut="annule").count(),
    }

    # ── Données graphe : 30 derniers jours ──────────────────────────
    today      = timezone.localdate()
    date_debut = today - timedelta(days=29)

    qs = (
        Commande.objects
        .filter(created_at__date__gte=date_debut)
        .annotate(jour=TruncDate("created_at"))
        .values("jour")
        .annotate(total=Count("id"))
        .order_by("jour")
    )

    data_dict = {entry["jour"]: entry["total"] for entry in qs}
    labels, values = [], []
    for i in range(30):
        d = date_debut + timedelta(days=i)
        labels.append(d.strftime("%d/%m"))
        values.append(data_dict.get(d, 0))

    # Répartition par service
    services_qs = (
        Commande.objects
        .values("service")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    services_labels = [s["service"] for s in services_qs]
    services_values = [s["total"]   for s in services_qs]

    return render(request, "admin_dashboard.html", {
        "commandes":       commandes,
        "stats":           stats,
        "statut_filter":   statut_filter,
        "chart_data": {
            "labels":          labels,
            "values":          values,
            "services_labels": services_labels,
            "services_values": services_values,
        },
    })


@require_POST
def admin_update_statut(request, pk):
    if not request.session.get("admin_auth"):
        return redirect("admin_login")
    commande = get_object_or_404(Commande, pk=pk)
    statut = request.POST.get("statut")
    if statut in dict(Commande.STATUT_CHOICES):
        commande.statut = statut
        commande.save(update_fields=["statut"])
    return redirect("admin_dashboard")


@require_POST
def admin_delete(request, pk):
    if not request.session.get("admin_auth"):
        return redirect("admin_login")
    get_object_or_404(Commande, pk=pk).delete()
    return redirect("admin_dashboard")