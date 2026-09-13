from django.contrib import admin
from .models import (
    Site,
    Reference,
    Mouvement,
    BonLivraison,
    BonLivraisonMouvement,
    Trajet,
    TrajetMouvement,
    Facture,
    RapprochementFacture,
    Profil,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'nom')
    search_fields = ('code', 'nom')
    ordering = ('code',)


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'code_pn', 'designation')
    search_fields = ('code_pn', 'designation')
    ordering = ('code_pn',)


@admin.register(Mouvement)
class MouvementAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date_mouvement',
        'type_mouvement',
        'reference',
        'quantite',
        'nb_palettes',
        'batch',
        'site',
        'date_saisie',
    )
    list_filter = ('site', 'type_mouvement', 'date_mouvement')
    search_fields = ('reference__code_pn', 'reference__designation', 'batch')
    date_hierarchy = 'date_mouvement'
    autocomplete_fields = ['site', 'reference']


class BonLivraisonMouvementInline(admin.TabularInline):
    model = BonLivraisonMouvement
    extra = 1
    autocomplete_fields = ['mouvement']


@admin.register(BonLivraison)
class BonLivraisonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'numero_bl',
        'date_bl',
        'site',
        'nb_palettes_total',
        'poids_brut',
        'fichier_scan',
    )
    list_filter = ('site', 'date_bl')
    search_fields = ('numero_bl',)
    date_hierarchy = 'date_bl'
    autocomplete_fields = ['site']
    inlines = [BonLivraisonMouvementInline]


@admin.register(BonLivraisonMouvement)
class BonLivraisonMouvementAdmin(admin.ModelAdmin):
    list_display = ('id', 'bon_livraison', 'mouvement')
    list_filter = ('bon_livraison__site',)
    search_fields = ('bon_livraison__numero_bl', 'mouvement__reference__code_pn')


class TrajetMouvementInline(admin.TabularInline):
    model = TrajetMouvement
    extra = 1
    autocomplete_fields = ['mouvement']


@admin.register(Trajet)
class TrajetAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_trajet', 'site', 'remarque')
    list_filter = ('site', 'date_trajet')
    search_fields = ('remarque',)
    date_hierarchy = 'date_trajet'
    autocomplete_fields = ['site']
    inlines = [TrajetMouvementInline]


@admin.register(TrajetMouvement)
class TrajetMouvementAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'trajet',
        'mouvement',
        'quantite_transportee',
        'nb_palettes_transportees',
    )
    list_filter = ('trajet__site',)
    search_fields = ('trajet__site__code', 'mouvement__reference__code_pn')


class RapprochementFactureInline(admin.TabularInline):
    model = RapprochementFacture
    extra = 1
    autocomplete_fields = ['trajet']


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'date_facture', 'site', 'montant', 'nb_trajets_factures', 'fichier_scan')
    list_filter = ('site', 'date_facture')
    search_fields = ('numero',)
    date_hierarchy = 'date_facture'
    autocomplete_fields = ['site']
    inlines = [RapprochementFactureInline]


@admin.register(RapprochementFacture)
class RapprochementFactureAdmin(admin.ModelAdmin):
    list_display = ('id', 'facture', 'trajet', 'statut')
    list_filter = ('statut', 'facture__site')
    search_fields = ('facture__numero',)
    autocomplete_fields = ['facture', 'trajet']


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')


