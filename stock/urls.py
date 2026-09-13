from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.home, name='home'),
    path('mouvements/', views.mouvement_list, name='mouvement_list'),
    path('mouvements/nouveau/', views.mouvement_create, name='mouvement_create'),
    path('bons-de-livraison/', views.bon_livraison_list, name='bon_livraison_list'),
    path('bons-de-livraison/nouveau/', views.bon_livraison_create, name='bon_livraison_create'),
    path('trajets/', views.trajet_list, name='trajet_list'),
    path('trajets/nouveau/', views.trajet_create, name='trajet_create'),
    path('factures/', views.facture_list, name='facture_list'),
    path('factures/nouvelle/', views.facture_create, name='facture_create'),
    path('factures/<int:facture_id>/rapprochement/', views.rapprochement_detail, name='rapprochement_detail'),
]
