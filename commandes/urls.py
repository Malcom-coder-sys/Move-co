from django.urls import path
from . import views

urlpatterns = [
    path("",                              views.home,                name="home"),
    path("services/",                     views.services,            name="services"),
    path("galerie/",                      views.galerie,             name="galerie"),
    path("commander/",                    views.commander,           name="commander"),
    path("confirmation/<int:pk>/",        views.commande_success,    name="commande_success"),
    path("admin-moveco/",                 views.admin_login,         name="admin_login"),
    path("admin-moveco/logout/",          views.admin_logout,        name="admin_logout"),
    path("admin-moveco/dashboard/",       views.admin_dashboard,     name="admin_dashboard"),
    path("admin-moveco/update/<int:pk>/", views.admin_update_statut, name="admin_update_statut"),
    path("admin-moveco/delete/<int:pk>/", views.admin_delete,        name="admin_delete"),
]