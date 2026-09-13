from django import forms
from .models import (
    Site,
    Reference,
    Mouvement,
    BonLivraison,
    BonLivraisonMouvement,
    Trajet,
    Facture,
)


class MouvementForm(forms.ModelForm):
    class Meta:
        model = Mouvement
        fields = [
            'date_mouvement',
            'site',
            'type_mouvement',
            'reference',
            'quantite',
            'nb_palettes',
            'batch',
        ]
        widgets = {
            'date_mouvement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'site': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Quantité en unités'}),
            'nb_palettes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Nombre de palettes (optionnel)'}),
            'batch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lot / Batch (optionnel)'}),
        }

    def clean_quantite(self):
        q = self.cleaned_data.get('quantite')
        if q is None or q <= 0:
            raise forms.ValidationError("La quantité doit être strictement positive.")
        return q

    def clean_nb_palettes(self):
        p = self.cleaned_data.get('nb_palettes')
        if p is not None and p < 0:
            raise forms.ValidationError("Le nombre de palettes ne peut pas être négatif.")
        return p


class BonLivraisonForm(forms.ModelForm):
    mouvements = forms.ModelMultipleChoiceField(
        queryset=Mouvement.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Mouvements d'export à associer"
    )

    class Meta:
        model = BonLivraison
        fields = [
            'numero_bl',
            'date_bl',
            'site',
            'nb_palettes_total',
            'poids_brut',
            'fichier_scan',
        ]
        widgets = {
            'numero_bl': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2026/68'}),
            'date_bl': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'site': forms.Select(attrs={'class': 'form-select', 'id': 'id_site'}),
            'nb_palettes_total': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Nombre total de palettes'}),
            'poids_brut': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Poids brut (kg)'}),
            'fichier_scan': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}),
        }

    def __init__(self, *args, **kwargs):
        site_id = kwargs.pop('site_id', None)
        super().__init__(*args, **kwargs)
        # Filtre strict : Mouvements EXPORT non encore liés à un autre BonLivraison
        qs = Mouvement.objects.filter(
            type_mouvement='EXPORT',
            bon_livraison_mouvements__isnull=True
        ).select_related('reference', 'site').order_by('-date_mouvement', '-id')

        if site_id:
            qs = qs.filter(site_id=site_id)

        self.fields['mouvements'].queryset = qs

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            selected_mouvements = self.cleaned_data.get('mouvements', [])
            for mvt in selected_mouvements:
                BonLivraisonMouvement.objects.get_or_create(
                    bon_livraison=instance,
                    mouvement=mvt
                )
        return instance


class TrajetForm(forms.ModelForm):
    class Meta:
        model = Trajet
        fields = [
            'date_trajet',
            'site',
            'remarque',
        ]
        widgets = {
            'date_trajet': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'site': forms.Select(attrs={'class': 'form-select', 'id': 'id_site'}),
            'remarque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: TAXI, Scrap, etc.'}),
        }


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = [
            'numero',
            'date_facture',
            'site',
            'montant',
            'nb_trajets_factures',
            'fichier_scan',
        ]
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: FAC-2026-001'}),
            'date_facture': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'site': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Montant en MAD'}),
            'nb_trajets_factures': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Ex: 12'}),
            'fichier_scan': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'}),
        }
