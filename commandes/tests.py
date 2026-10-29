from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Commande


def donnees_commande(**kwargs):
    data = {
        "nom": "Jean Dupont",
        "email": "jean@email.com",
        "telephone": "+237 600 000 000",
        "service": "Transport de colis",
        "date": (timezone.localdate() + timedelta(days=3)).isoformat(),
        "adresse": "Bastos",
        "message": "",
    }
    data.update(kwargs)
    return data


class PagesPubliquesTests(TestCase):
    def test_pages_accessibles(self):
        for name in ["home", "services", "galerie", "admin_login"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)


class CommandeTests(TestCase):
    def test_commande_valide_redirige_vers_confirmation(self):
        resp = self.client.post(reverse("commander"), donnees_commande())
        commande = Commande.objects.get()
        self.assertRedirects(resp, reverse("commande_success", args=[commande.pk]))
        self.assertContains(self.client.get(resp.url), "Jean Dupont")

    def test_date_passee_refusee(self):
        hier = (timezone.localdate() - timedelta(days=1)).isoformat()
        resp = self.client.post(reverse("commander"), donnees_commande(date=hier))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Commande.objects.exists())

    def test_confirmation_inaccessible_a_un_autre_visiteur(self):
        self.client.post(reverse("commander"), donnees_commande())
        commande = Commande.objects.get()
        self.client.logout()
        resp = self.client.get(reverse("commande_success", args=[commande.pk]))
        self.assertRedirects(resp, reverse("services"))


@override_settings(MOVECO_ADMIN_PASSWORD="secret-test")
class AdminTests(TestCase):
    def setUp(self):
        self.commande = Commande.objects.create(
            nom="Awa", email="awa@email.com", telephone="600",
            service="Transport de colis", date=timezone.localdate(),
        )

    def connexion(self):
        self.client.post(reverse("admin_login"), {"password": "secret-test"})

    def test_dashboard_protege(self):
        self.assertRedirects(self.client.get(reverse("admin_dashboard")), reverse("admin_login"))

    def test_mauvais_mot_de_passe(self):
        resp = self.client.post(reverse("admin_login"), {"password": "faux"})
        self.assertContains(resp, "Mot de passe incorrect")

    def test_dashboard_apres_connexion(self):
        self.connexion()
        resp = self.client.get(reverse("admin_dashboard"))
        self.assertContains(resp, "Awa")
        self.assertContains(resp, 'id="chart-data"')

    def test_statut_invalide_ignore(self):
        self.connexion()
        url = reverse("admin_update_statut", args=[self.commande.pk])
        self.client.post(url, {"statut": "nimporte_quoi"})
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, "en_attente")
        self.client.post(url, {"statut": "confirme"})
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, "confirme")

    def test_suppression_exige_post(self):
        self.connexion()
        url = reverse("admin_delete", args=[self.commande.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        self.assertFalse(Commande.objects.exists())

    def test_nom_echappe_dans_confirm_js(self):
        Commande.objects.create(
            nom="x'); alert(1); ('", email="a@b.cm", telephone="1",
            service="Transport de colis", date=timezone.localdate(),
        )
        self.connexion()
        resp = self.client.get(reverse("admin_dashboard"))
        self.assertNotContains(resp, "confirm('Supprimer la commande de x&#x27;")
        self.assertContains(resp, "confirm('Supprimer la commande de x\\u0027")
