from datetime import date
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum, Count, Q, F, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
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
from .forms import (
    MouvementForm,
    BonLivraisonForm,
    TrajetForm,
    FactureForm,
)


from django.urls import reverse


def role_required(allowed_roles):
    """
    Décorateur restreignant l'accès aux utilisateurs connectés ayant un rôle spécifique.
    Les superutilisateurs ont accès sans restriction.
    Si le rôle est insuffisant, lève PermissionDenied (HTTP 403).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.path}")
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            profil = getattr(request.user, 'profil', None)
            if profil and profil.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Vous n'avez pas les droits nécessaires pour accéder à cette page.")
        return _wrapped_view
    return decorator


def logout_view(request):
    """Déconnexion de l'utilisateur avec message de confirmation."""
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')


@login_required
def home(request):
    """Tableau de bord d'accueil avec indicateurs clés, stock actuel et contrôles."""
    today = date.today()
    MOIS_FR = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    mois_courant_nom = f"{MOIS_FR[today.month - 1]} {today.year}"

    # 1. Stock actuel par référence et par site (total réceptions - total exports)
    stock_data = (
        Mouvement.objects.values(
            'reference__id',
            'reference__code_pn',
            'reference__designation',
            'site__id',
            'site__code',
            'site__nom',
        )
        .annotate(
            total_receptions=Coalesce(Sum('quantite', filter=Q(type_mouvement='RECEPTION')), Value(0)),
            total_exports=Coalesce(Sum('quantite', filter=Q(type_mouvement='EXPORT')), Value(0)),
        )
        .annotate(
            stock_actuel=F('total_receptions') - F('total_exports')
        )
        .order_by('reference__code_pn', 'site__code')
    )

    # 2. Nombre de trajets du mois en cours par site
    all_sites = Site.objects.all().order_by('code')
    trajets_mois_map = {
        item['site__code']: item['total']
        for item in Trajet.objects.filter(
            date_trajet__year=today.year,
            date_trajet__month=today.month
        ).values('site__code').annotate(total=Count('id'))
    }
    trajets_mois_par_site = [
        {
            'site': s,
            'nb_trajets': trajets_mois_map.get(s.code, 0)
        }
        for s in all_sites
        if s.code in ['TFZ', 'TOUBKAL'] or trajets_mois_map.get(s.code, 0) > 0
    ]
    total_trajets_mois = sum(item['nb_trajets'] for item in trajets_mois_par_site)

    # 3. Nombre de factures avec statut ECART non résolu
    factures = Facture.objects.prefetch_related('rapprochements').all()
    factures_ecart = [f for f in factures if f.statut_rapprochement == 'ECART']
    nb_factures_ecart = len(factures_ecart)

    # 4. Nombre de trajets orphelins (jamais liés à aucune facture) par site, toutes dates confondues
    orphelins_qs = Trajet.objects.filter(rapprochements__isnull=True)
    total_trajets_orphelins = orphelins_qs.count()

    orphelins_map = {
        item['site__code']: item['total']
        for item in orphelins_qs.values('site__code').annotate(total=Count('id'))
    }
    orphelins_par_site = [
        {
            'site': s,
            'nb_orphelins': orphelins_map.get(s.code, 0)
        }
        for s in all_sites
        if s.code in ['TFZ', 'TOUBKAL'] or orphelins_map.get(s.code, 0) > 0
    ]

    # 5. Les 10 derniers mouvements enregistrés
    derniers_mouvements = Mouvement.objects.select_related('reference', 'site').order_by('-date_mouvement', '-id')[:10]

    # Données globales additionnelles
    total_mouvements = Mouvement.objects.count()
    total_receptions = Mouvement.objects.filter(type_mouvement='RECEPTION').count()
    total_exports = Mouvement.objects.filter(type_mouvement='EXPORT').count()

    context = {
        'stock_data': stock_data,
        'mois_courant_nom': mois_courant_nom,
        'trajets_mois_par_site': trajets_mois_par_site,
        'total_trajets_mois': total_trajets_mois,
        'nb_factures_ecart': nb_factures_ecart,
        'factures_ecart': factures_ecart,
        'total_trajets_orphelins': total_trajets_orphelins,
        'orphelins_par_site': orphelins_par_site,
        'derniers_mouvements': derniers_mouvements,
        'total_mouvements': total_mouvements,
        'total_receptions': total_receptions,
        'total_exports': total_exports,
    }
    return render(request, 'stock/home.html', context)


# ==========================================
# 1. MOUVEMENTS
# ==========================================

@login_required
def mouvement_list(request):
    """Liste des mouvements avec tri par date décroissante et filtres."""
    qs = Mouvement.objects.select_related('reference', 'site').order_by('-date_mouvement', '-id')

    # Filtres optionnels
    site_filter = request.GET.get('site')
    type_filter = request.GET.get('type')
    search_query = request.GET.get('q', '').strip()

    if site_filter:
        qs = qs.filter(site_id=site_filter)
    if type_filter:
        qs = qs.filter(type_mouvement=type_filter)
    if search_query:
        qs = qs.filter(
            Q(reference__code_pn__icontains=search_query) |
            Q(batch__icontains=search_query)
        )

    paginator = Paginator(qs, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sites = Site.objects.all().order_by('code')

    context = {
        'page_obj': page_obj,
        'sites': sites,
        'current_site': site_filter,
        'current_type': type_filter,
        'search_query': search_query,
        'total_count': qs.count(),
    }
    return render(request, 'stock/mouvement_list.html', context)


@role_required(['SUPERVISEUR', 'CHEF_EQUIPE'])
def mouvement_create(request):
    """Création d'un mouvement de stock."""
    if request.method == 'POST':
        form = MouvementForm(request.POST)
        if form.is_valid():
            mouvement = form.save()
            messages.success(
                request,
                f"Mouvement {mouvement.type_mouvement} pour {mouvement.reference.code_pn} ({mouvement.quantite} pièces) enregistré avec succès."
            )
            return redirect('stock:mouvement_list')
    else:
        form = MouvementForm()

    return render(request, 'stock/mouvement_form.html', {'form': form})


# ==========================================
# 2. BONS DE LIVRAISON
# ==========================================

@login_required
def bon_livraison_list(request):
    """Liste des bons de livraison triés par date décroissante."""
    bons_livraison = BonLivraison.objects.select_related('site').prefetch_related(
        'bon_livraison_mouvements__mouvement__reference'
    ).order_by('-date_bl', '-id')

    paginator = Paginator(bons_livraison, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'stock/bon_livraison_list.html', {
        'page_obj': page_obj,
        'total_count': bons_livraison.count()
    })


@role_required(['SUPERVISEUR'])
def bon_livraison_create(request):
    """Création d'un Bon de Livraison avec sélection des mouvements d'export éligibles."""
    if request.method == 'POST':
        form = BonLivraisonForm(request.POST, request.FILES)
        if form.is_valid():
            bl = form.save()
            messages.success(request, f"Bon de livraison {bl.numero_bl} ({bl.site.code}) enregistré avec succès.")
            return redirect('stock:bon_livraison_list')
    else:
        form = BonLivraisonForm()

    # Mouvements éligibles : EXPORT, non liés à un autre BL, triés par date décroissante
    eligible_mouvements = Mouvement.objects.filter(
        type_mouvement='EXPORT',
        bon_livraison_mouvements__isnull=True
    ).select_related('reference', 'site').order_by('-date_mouvement', '-id')

    sites = Site.objects.all().order_by('code')

    return render(request, 'stock/bon_livraison_form.html', {
        'form': form,
        'eligible_mouvements': eligible_mouvements,
        'sites': sites,
    })


# ==========================================
# 3. TRAJETS
# ==========================================

@login_required
def trajet_list(request):
    """Liste des trajets avec mouvements transportés, triés par date décroissante."""
    trajets = Trajet.objects.select_related('site').prefetch_related(
        'trajet_mouvements__mouvement__reference',
        'rapprochements__facture'
    ).order_by('-date_trajet', '-id')

    orphelin_filter = request.GET.get('orphelin')
    site_code_filter = request.GET.get('site')

    if orphelin_filter == '1':
        trajets = trajets.filter(rapprochements__isnull=True)
    if site_code_filter:
        trajets = trajets.filter(site__code=site_code_filter)

    total_count = trajets.count()
    paginator = Paginator(trajets, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sites = Site.objects.all().order_by('code')

    return render(request, 'stock/trajet_list.html', {
        'page_obj': page_obj,
        'total_count': total_count,
        'orphelin_filter': orphelin_filter,
        'site_code_filter': site_code_filter,
        'sites': sites,
    })


@role_required(['SUPERVISEUR'])
def trajet_create(request):
    """Création d'un trajet avec saisie dynamique des quantités transportées."""
    if request.method == 'POST':
        form = TrajetForm(request.POST)
        if form.is_valid():
            # 1. Contrôle des quantités AVANT tout enregistrement : la quantité transportée
            #    doit être > 0 et ne pas dépasser le reste à transporter du mouvement
            #    (quantité exportée - quantités déjà affectées à d'autres trajets).
            lignes = []
            erreurs_qte = []
            for mvt_id in request.POST.getlist('mouvements'):
                mouvement = Mouvement.objects.filter(id=mvt_id, type_mouvement='EXPORT').first()
                if mouvement is None:
                    continue
                raw_qty = request.POST.get(f'qty_{mvt_id}')
                raw_pal = request.POST.get(f'pal_{mvt_id}')
                qty = int(raw_qty) if raw_qty and raw_qty.isdigit() else mouvement.quantite
                pal = int(raw_pal) if raw_pal and raw_pal.isdigit() else mouvement.nb_palettes
                deja = mouvement.trajet_mouvements.aggregate(t=Sum('quantite_transportee'))['t'] or 0
                reste = mouvement.quantite - deja
                if qty <= 0 or qty > reste:
                    erreurs_qte.append(
                        f"{mouvement.reference.code_pn} du {mouvement.date_mouvement:%d/%m/%Y} : "
                        f"{qty} demandé(s), reste à transporter {reste}."
                    )
                else:
                    lignes.append((mouvement, qty, pal))

            if erreurs_qte:
                for err in erreurs_qte:
                    messages.error(request, f"Quantité transportée invalide — {err}")
            else:
                trajet = form.save()
                for mouvement, qty, pal in lignes:
                    TrajetMouvement.objects.get_or_create(
                        trajet=trajet,
                        mouvement=mouvement,
                        defaults={
                            'quantite_transportee': qty,
                            'nb_palettes_transportees': pal,
                        }
                    )
                linked_count = len(lignes)

                date_fmt = trajet.date_trajet.strftime('%d/%m/%Y')
                rem_str = f" ({trajet.remarque})" if trajet.remarque else ""
                messages.success(
                    request,
                    f"Trajet du {date_fmt} - Site {trajet.site.code}{rem_str} enregistré avec succès ({linked_count} mouvement(s) associé(s))."
                )
                return redirect('stock:trajet_list')
    else:
        form = TrajetForm()

    # Mouvements éligibles au transport : EXPORT, triés par date décroissante
    eligible_mouvements = Mouvement.objects.filter(
        type_mouvement='EXPORT'
    ).select_related('reference', 'site').order_by('-date_mouvement', '-id')

    sites = Site.objects.all().order_by('code')

    return render(request, 'stock/trajet_form.html', {
        'form': form,
        'eligible_mouvements': eligible_mouvements,
        'sites': sites,
    })


# ==========================================
# 4. FACTURES
# ==========================================

@login_required
def facture_list(request):
    """Liste des factures transporteur triées par date décroissante."""
    factures = Facture.objects.select_related('site').prefetch_related('rapprochements').order_by('-date_facture', '-id')

    paginator = Paginator(factures, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'stock/facture_list.html', {
        'page_obj': page_obj,
        'total_count': factures.count()
    })


@role_required(['SUPERVISEUR'])
def facture_create(request):
    """Création d'une facture transporteur."""
    if request.method == 'POST':
        form = FactureForm(request.POST, request.FILES)
        if form.is_valid():
            facture = form.save()
            messages.success(request, f"Facture {facture.numero} ({facture.site.code}) enregistrée avec succès.")
            return redirect('stock:facture_list')
    else:
        form = FactureForm()

    return render(request, 'stock/facture_form.html', {'form': form})


@role_required(['SUPERVISEUR'])
def rapprochement_detail(request, facture_id):
    """
    Vue de détail et de rapprochement pour une Facture :
    - Affiche les détails de la facture.
    - Liste les trajets éligibles du même site en excluant ceux déjà liés à une autre facture.
    - Coche par défaut les trajets du même mois que date_facture (ou ceux déjà liés).
    - À la validation : enregistre les RapprochementFacture, calcule l'écart et met à jour le statut.
    - Affiche les trajets non facturés (antérieurs à la facture et sans aucune liaison).
    """
    facture = get_object_or_404(Facture.objects.select_related('site'), id=facture_id)

    # 1. Trajets déjà rapprochés avec une AUTRE facture (à exclure strictement)
    other_reconciled_trajet_ids = set(
        RapprochementFacture.objects.exclude(facture=facture).values_list('trajet_id', flat=True)
    )

    # 2. Trajets éligibles pour cette facture (même site, non liés à une autre facture)
    eligible_trajets = Trajet.objects.filter(
        site=facture.site
    ).exclude(
        id__in=other_reconciled_trajet_ids
    ).prefetch_related(
        'trajet_mouvements__mouvement__reference'
    ).order_by('-date_trajet', '-id')

    # Trajets actuellement liés à CETTE facture
    currently_linked_trajet_ids = set(
        RapprochementFacture.objects.filter(facture=facture).values_list('trajet_id', flat=True)
    )
    has_existing_reconciliation = len(currently_linked_trajet_ids) > 0

    if request.method == 'POST':
        selected_ids = request.POST.getlist('trajets')
        selected_trajet_ids = [int(tid) for tid in selected_ids if tid.isdigit()]

        # Filtrer pour ne garder que les IDs faisant bien partie des trajets éligibles
        valid_selected_ids = [tid for tid in selected_trajet_ids if tid not in other_reconciled_trajet_ids]

        linked_count = len(valid_selected_ids)
        nb_factures = facture.nb_trajets_factures

        statut_global = 'OK'
        ecart_message = "OK - Conforme"

        if nb_factures is not None:
            if linked_count == nb_factures:
                statut_global = 'OK'
                ecart_message = f"OK ({linked_count}/{nb_factures} trajets conformes)"
            elif linked_count < nb_factures:
                diff = nb_factures - linked_count
                statut_global = 'ECART'
                ecart_message = f"ECART - {diff} trajet(s) manquant(s)"
            else:
                diff = linked_count - nb_factures
                statut_global = 'ECART'
                ecart_message = f"ECART - {diff} trajet(s) en trop"
        else:
            statut_global = 'OK'
            ecart_message = f"OK ({linked_count} trajet(s) associé(s))"

        with transaction.atomic():
            # Supprimer les rapprochements de cette facture qui ont été décochés
            RapprochementFacture.objects.filter(facture=facture).exclude(trajet_id__in=valid_selected_ids).delete()

            # Créer ou mettre à jour les liaisons pour les trajets cochés
            for tid in valid_selected_ids:
                RapprochementFacture.objects.update_or_create(
                    facture=facture,
                    trajet_id=tid,
                    defaults={'statut': statut_global}
                )

        # Mettre à jour les ensembles en mémoire pour l'affichage immédiat
        currently_linked_trajet_ids = set(valid_selected_ids)
        has_existing_reconciliation = len(currently_linked_trajet_ids) > 0

        if statut_global == 'OK':
            messages.success(request, f"Rapprochement enregistré : {ecart_message}.")
        else:
            messages.warning(request, f"Rapprochement enregistré avec anomalie : {ecart_message} ({linked_count} réels vs {nb_factures} déclarés).")

    # Résultat du rapprochement pour affichage
    linked_count = len(currently_linked_trajet_ids)
    nb_factures = facture.nb_trajets_factures
    reconciliation_result = None

    if has_existing_reconciliation or request.method == 'POST':
        if nb_factures is not None:
            if linked_count == nb_factures:
                reconciliation_result = {
                    'statut': 'OK',
                    'badge_class': 'bg-success',
                    'badge_text': 'OK',
                    'detail': f"{linked_count} trajet(s) réel(s) pour {nb_factures} trajet(s) facturé(s)",
                    'linked_count': linked_count,
                    'nb_factures': nb_factures,
                }
            elif linked_count < nb_factures:
                diff = nb_factures - linked_count
                reconciliation_result = {
                    'statut': 'ECART',
                    'badge_class': 'bg-danger',
                    'badge_text': f"ECART - {diff} trajet{'s' if diff > 1 else ''} manquant{'s' if diff > 1 else ''}",
                    'detail': f"{linked_count} trajet(s) réel(s) pour {nb_factures} trajet(s) facturé(s)",
                    'linked_count': linked_count,
                    'nb_factures': nb_factures,
                    'diff': diff,
                }
            else:
                diff = linked_count - nb_factures
                reconciliation_result = {
                    'statut': 'ECART',
                    'badge_class': 'bg-danger',
                    'badge_text': f"ECART - {diff} trajet{'s' if diff > 1 else ''} en trop",
                    'detail': f"{linked_count} trajet(s) réel(s) pour {nb_factures} trajet(s) facturé(s)",
                    'linked_count': linked_count,
                    'nb_factures': nb_factures,
                    'diff': diff,
                }
        else:
            reconciliation_result = {
                'statut': 'OK',
                'badge_class': 'bg-success',
                'badge_text': 'OK',
                'detail': f"{linked_count} trajet(s) associé(s) (aucun nombre de trajets spécifié sur la facture)",
                'linked_count': linked_count,
                'nb_factures': None,
            }

    # Déterminer les cases cochées pour chaque trajet éligible :
    # Si la facture a déjà des liaisons : cocher ceux qui sont liés
    # Sinon : cocher par défaut ceux du même mois que date_facture
    for trajet in eligible_trajets:
        if has_existing_reconciliation:
            trajet.is_checked = trajet.id in currently_linked_trajet_ids
        else:
            trajet.is_checked = (
                trajet.date_trajet.year == facture.date_facture.year and
                trajet.date_trajet.month == facture.date_facture.month
            )

    # 4. Trajets non facturés :
    # Tous les Trajets du site qui datent d'avant la date de la facture et qui ne sont liés à AUCUNE facture
    all_reconciled_trajet_ids = set(RapprochementFacture.objects.values_list('trajet_id', flat=True))
    trajets_non_factures = Trajet.objects.filter(
        site=facture.site,
        date_trajet__lt=facture.date_facture
    ).exclude(
        id__in=all_reconciled_trajet_ids
    ).prefetch_related(
        'trajet_mouvements__mouvement__reference'
    ).order_by('-date_trajet', '-id')

    return render(request, 'stock/rapprochement_detail.html', {
        'facture': facture,
        'eligible_trajets': eligible_trajets,
        'trajets_non_factures': trajets_non_factures,
        'reconciliation_result': reconciliation_result,
        'has_existing_reconciliation': has_existing_reconciliation,
        'linked_count': linked_count,
    })

