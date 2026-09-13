from django.db import models
from django.contrib.auth.models import User


class Site(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Code site")
    nom = models.CharField(max_length=100, verbose_name="Nom du site")

    class Meta:
        db_table = 'site'
        verbose_name = "Site"
        verbose_name_plural = "Sites"

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Reference(models.Model):
    code_pn = models.CharField(max_length=50, unique=True, verbose_name="Code PN")
    designation = models.CharField(max_length=200, blank=True, null=True, verbose_name="Désignation")

    class Meta:
        db_table = 'reference'
        verbose_name = "Référence"
        verbose_name_plural = "Références"

    def __str__(self):
        return f"{self.code_pn} - {self.designation}" if self.designation else self.code_pn


class Mouvement(models.Model):
    TYPE_MOUVEMENT_CHOICES = [
        ('RECEPTION', 'RECEPTION'),
        ('EXPORT', 'EXPORT'),
    ]

    date_mouvement = models.DateField(verbose_name="Date mouvement")
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT_CHOICES, verbose_name="Type mouvement")
    quantite = models.IntegerField(verbose_name="Quantité")
    nb_palettes = models.IntegerField(blank=True, null=True, verbose_name="Nb palettes")
    batch = models.CharField(max_length=50, blank=True, null=True, verbose_name="Batch")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='mouvements', verbose_name="Site")
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, related_name='mouvements', verbose_name="Référence")
    date_saisie = models.DateTimeField(auto_now_add=True, verbose_name="Date de saisie")

    class Meta:
        db_table = 'mouvement'
        verbose_name = "Mouvement"
        verbose_name_plural = "Mouvements"

    def __str__(self):
        date_str = self.date_mouvement.strftime('%d/%m/%Y') if self.date_mouvement else ""
        pn = self.reference.code_pn if self.reference else "N/A"
        site_code = self.site.code if self.site else "N/A"
        return f"{self.type_mouvement} - {pn} - {date_str} - {site_code}"


class BonLivraison(models.Model):
    numero_bl = models.CharField(max_length=50, unique=True, verbose_name="Numéro BL")
    date_bl = models.DateField(verbose_name="Date BL")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='bons_livraison', verbose_name="Site")
    nb_palettes_total = models.IntegerField(blank=True, null=True, verbose_name="Nb palettes total")
    poids_brut = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Poids brut")
    fichier_scan = models.FileField(upload_to='scans/bl/', max_length=255, blank=True, null=True, verbose_name="Fichier scan")

    class Meta:
        db_table = 'bon_livraison'
        verbose_name = "Bon de livraison"
        verbose_name_plural = "Bons de livraison"

    def __str__(self):
        date_str = self.date_bl.strftime('%d/%m/%Y') if self.date_bl else ""
        site_code = self.site.code if self.site else "N/A"
        return f"BL {self.numero_bl} - {site_code} - {date_str}"


class BonLivraisonMouvement(models.Model):
    bon_livraison = models.ForeignKey(BonLivraison, on_delete=models.CASCADE, related_name='bon_livraison_mouvements', verbose_name="Bon de livraison")
    mouvement = models.ForeignKey(Mouvement, on_delete=models.CASCADE, related_name='bon_livraison_mouvements', verbose_name="Mouvement")

    class Meta:
        db_table = 'bon_livraison_mouvement'
        unique_together = ('bon_livraison', 'mouvement')
        verbose_name = "Liaison Bon de livraison - Mouvement"
        verbose_name_plural = "Liaisons Bons de livraison - Mouvements"

    def __str__(self):
        bl_num = self.bon_livraison.numero_bl if self.bon_livraison else "N/A"
        return f"BL {bl_num} <-> Mouvement #{self.mouvement_id}"


class Trajet(models.Model):
    date_trajet = models.DateField(verbose_name="Date trajet")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='trajets', verbose_name="Site")
    remarque = models.CharField(max_length=100, blank=True, null=True, verbose_name="Remarque")

    class Meta:
        db_table = 'trajet'
        verbose_name = "Trajet"
        verbose_name_plural = "Trajets"

    def __str__(self):
        date_str = self.date_trajet.strftime('%d/%m/%Y') if self.date_trajet else ""
        site_code = self.site.code if self.site else "N/A"
        rem = f" ({self.remarque})" if self.remarque else ""
        return f"Trajet {site_code} du {date_str}{rem}"

    @property
    def quantite_totale_transportee(self):
        return sum(tm.quantite_transportee for tm in self.trajet_mouvements.all())

    @property
    def nb_palettes_totales(self):
        return sum(tm.nb_palettes_transportees or 0 for tm in self.trajet_mouvements.all())


class TrajetMouvement(models.Model):
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='trajet_mouvements', verbose_name="Trajet")
    mouvement = models.ForeignKey(Mouvement, on_delete=models.CASCADE, related_name='trajet_mouvements', verbose_name="Mouvement")
    quantite_transportee = models.IntegerField(verbose_name="Quantité transportée")
    nb_palettes_transportees = models.IntegerField(blank=True, null=True, verbose_name="Nb palettes transportées")

    class Meta:
        db_table = 'trajet_mouvement'
        unique_together = ('trajet', 'mouvement')
        verbose_name = "Liaison Trajet - Mouvement"
        verbose_name_plural = "Liaisons Trajets - Mouvements"

    def __str__(self):
        return f"Trajet #{self.trajet_id} - Mouvement #{self.mouvement_id} (Qté: {self.quantite_transportee})"


class Facture(models.Model):
    numero = models.CharField(max_length=50, verbose_name="Numéro de facture")
    date_facture = models.DateField(verbose_name="Date de facture")
    montant = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Montant")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='factures', verbose_name="Site")
    nb_trajets_factures = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de trajets déclarés par le transporteur sur cette facture",
        verbose_name="Nb trajets déclarés"
    )
    fichier_scan = models.FileField(upload_to='scans/factures/', max_length=255, blank=True, null=True, verbose_name="Fichier scan")

    class Meta:
        db_table = 'facture'
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        site_code = self.site.code if self.site else "N/A"
        montant_str = f" - {self.montant} MAD" if self.montant is not None else ""
        return f"Facture {self.numero} - {site_code}{montant_str}"

    @property
    def statut_rapprochement(self):
        rapps = self.rapprochements.all()
        if not rapps.exists():
            return 'NON_RAPPROCHE'
        if any(r.statut == 'ECART' for r in rapps):
            return 'ECART'
        if self.nb_trajets_factures is not None and rapps.count() != self.nb_trajets_factures:
            return 'ECART'
        return 'OK'


class RapprochementFacture(models.Model):
    STATUT_CHOICES = [
        ('OK', 'OK'),
        ('ECART', 'ECART'),
    ]

    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='rapprochements', verbose_name="Facture")
    trajet = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='rapprochements', verbose_name="Trajet")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='OK', verbose_name="Statut")

    class Meta:
        db_table = 'rapprochement_facture'
        verbose_name = "Rapprochement Facture - Trajet"
        verbose_name_plural = "Rapprochements Factures - Trajets"

    def __str__(self):
        fac_num = self.facture.numero if self.facture else "N/A"
        return f"Facture {fac_num} <-> Trajet #{self.trajet_id} [{self.statut}]"


class Profil(models.Model):
    ROLE_CHOICES = [
        ('SUPERVISEUR', 'Superviseur'),
        ('CHEF_EQUIPE', 'Chef d\'équipe'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil', verbose_name="Utilisateur")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CHEF_EQUIPE', verbose_name="Rôle")

    class Meta:
        db_table = 'profil'
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


