# MOVE&CO

Site web de **MOVE&CO**, une entreprise de déménagement, transport de colis et aménagement intérieur basée à Yaoundé (Cameroun).

Les visiteurs consultent les services et la galerie, puis envoient une demande de service. Un espace administrateur permet de suivre ces demandes (statistiques, graphiques, changement de statut, suppression).

## Fonctionnalités

| Page | URL | Description |
|---|---|---|
| Accueil | `/` | Présentation, services, arguments, appel à l'action |
| Services | `/services/` | Formulaire de commande (service pré-sélectionnable via `?service=...`) |
| Galerie | `/galerie/` | Réalisations filtrables par catégorie, avec visionneuse (lightbox) |
| Confirmation | `/confirmation/<id>/` | Récapitulatif, visible uniquement par le navigateur qui a passé la commande |
| Espace admin | `/admin-moveco/` | Connexion par mot de passe unique |
| Tableau de bord | `/admin-moveco/dashboard/` | Statistiques, courbe des 30 derniers jours, répartition par service, gestion des commandes |
| Admin Django | `/django-admin/` | Interface d'administration Django standard (compte superutilisateur) |

## Technologies

- Python 3.12, Django 6
- MySQL (pilote `mysqlclient`)
- HTML/CSS/JS sans framework front, [Chart.js](https://www.chartjs.org/) 4 pour les graphiques

## Structure

```
moveco_django/
├── manage.py
├── requirements.txt
├── .env.example          # variables d'environnement à copier en .env
├── moveco/               # configuration du projet (settings, urls, wsgi/asgi)
├── commandes/            # application principale
│   ├── models.py         # modèle Commande
│   ├── forms.py          # formulaire de commande
│   ├── views.py          # pages publiques + espace admin
│   ├── urls.py
│   ├── admin.py          # enregistrement dans l'admin Django
│   └── tests.py
├── templates/            # gabarits HTML (base.html + une page par vue)
├── static/               # CSS et JS sources
└── staticfiles/          # généré par collectstatic (ne pas modifier)
```

## Installation

### 1. Prérequis

- Python 3.12+
- Un serveur MySQL ou MariaDB
- Les en-têtes de développement MySQL pour compiler `mysqlclient` (Debian/Ubuntu : `sudo apt install python3-dev default-libmysqlclient-dev build-essential pkg-config`)

### 2. Base de données

```sql
CREATE DATABASE moveco_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'motdepasse123';
GRANT ALL PRIVILEGES ON moveco_db.* TO 'admin'@'localhost';
-- nécessaire pour lancer les tests (création de la base test_moveco_db)
GRANT ALL PRIVILEGES ON test_moveco_db.* TO 'admin'@'localhost';
```

Le projet utilise `USE_TZ = True` : MySQL doit connaître les fuseaux horaires, sinon la courbe du tableau de bord reste vide.

```bash
mysql_tzinfo_to_sql /usr/share/zoneinfo | sudo mysql mysql
```

### 3. Projet

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # puis adapter les valeurs
set -a; source .env; set +a   # charge les variables dans le shell

python manage.py migrate
python manage.py createsuperuser   # facultatif, pour /django-admin/
python manage.py runserver
```

Le site est alors disponible sur http://127.0.0.1:8000.

## Configuration

Toute la configuration sensible passe par des variables d'environnement (voir [.env.example](.env.example)) :

| Variable | Défaut (dev) | Rôle |
|---|---|---|
| `DJANGO_DEBUG` | `1` | `0` en production |
| `DJANGO_SECRET_KEY` | clé de dev | **Obligatoire** si `DJANGO_DEBUG=0` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Noms de domaine autorisés, séparés par des virgules |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | `moveco_db`, `admin`, … | Connexion MySQL |
| `MOVECO_ADMIN_PASSWORD` | `MOVECO123` | Mot de passe de l'espace admin. **Obligatoire** si `DJANGO_DEBUG=0` |

Générer une clé secrète :

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Tests

```bash
python manage.py test commandes
```

Les tests couvrent les pages publiques, la création de commande (dont le refus d'une date passée), la protection de la page de confirmation et de l'espace admin, ainsi que la mise à jour et la suppression des commandes.

## Mise en production

1. Définir `DJANGO_DEBUG=0`, une vraie `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` et `MOVECO_ADMIN_PASSWORD`.
2. Servir le site en HTTPS (les cookies de session et CSRF sont alors marqués `Secure`).
3. Collecter les fichiers statiques et lancer un serveur WSGI :

   ```bash
   python manage.py collectstatic --noinput
   pip install gunicorn
   gunicorn moveco.wsgi
   ```

4. Faire servir `staticfiles/` par le serveur web (Nginx, etc.).
5. Lancer `python manage.py check --deploy` pour vérifier la configuration.

## Modèle de données

`Commande` : `nom`, `email`, `telephone`, `service` (déménagement simple, déménagement & aménagement, transport de colis, aménagement intérieur), `date`, `adresse`, `message`, `statut` (`en_attente`, `confirme`, `annule`) et `created_at`.
