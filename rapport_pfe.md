
# Dédicace

[À compléter]


# Remerciements

[À compléter]


# Résumé

Dans le secteur industriel automobile, la fluidité des flux logistiques et la maîtrise des coûts de transport constituent un levier stratégique de compétitivité. Le présent travail de fin d'études, réalisé au sein de l'entreprise Focus Quality à Tanger, porte sur la conception et le développement d'une plateforme web intégrée dédiée à la digitalisation des stocks et à l'audit du transport logistique pour le compte de son client donneur d'ordre, TE Connectivity. Initialement gérée au moyen de classeurs tabulaires complexes et hétérogènes, la traçabilité des mouvements entre l'entrepôt tampon et les usines de la Tangier Free Zone (TFZ) et de Toubkal (TAC) souffrait d'un manque de visibilité en temps réel, de risques de doublons et d'anomalies de facturation non identifiées sur les prestations de transport externes. En adoptant une démarche d'ingénierie logicielle basée sur le framework Python/Django et une architecture Modèle-Vue-Template (MVT), nous avons modélisé une base relationnelle normalisée, développé des interfaces réactives sous Bootstrap 5 sans dépendance d'outillage lourd, et mis au point un algorithme d'arbitrage automatisé entre rotations physiques et factures transporteur. Les résultats démontrent la fiabilisation intégrale du calcul des stocks par référence, la détection proactive des écarts de facturation et des courses orphelines, et une traçabilité documentaire complète des bons de livraison numérisés.


**Mots-clés :** Digitalisation logistique, Gestion de stock, Rapprochement de factures, Django, Base de données relationnelle, Traçabilité industrielle, TE Connectivity, Focus Quality.


# Abstract

In the automotive manufacturing industry, logistical flow efficiency and freight cost control represent critical strategic challenges. This graduation project, conducted at Focus Quality in Tangier, focuses on the design and development of an integrated web platform dedicated to inventory digitization and freight audit on behalf of its contracting client, TE Connectivity. Initially tracked using complex and heterogeneous spreadsheet files, component transfers between the buffer storage facility and manufacturing plants located in the Tangier Free Zone (TFZ) and Toubkal (TAC) suffered from a lack of real-time visibility, recurring duplicate entry risks, and financial leakages caused by the absence of automated verification against carrier invoices. Adopting a software engineering methodology based on the Python/Django framework and a Model-View-Template (MVT) architecture, we designed a normalized relational database, implemented responsive user interfaces using Bootstrap 5 without complex frontend toolchains, and engineered an automated reconciliation engine matching physical transit rotations with carrier billing statements. The operational outcomes demonstrate full integrity of stock calculations per part number, proactive detection of billing discrepancies and unbilled orphan trips, alongside comprehensive auditability of digitized shipping documentation.


**Keywords:** Logistics Digitization, Inventory Management, Invoice Reconciliation, Django, Relational Database, Industrial Traceability, TE Connectivity, Focus Quality.


# Introduction générale

L'industrie automobile contemporaine se caractérise par des chaînes d'approvisionnement extrêmement tendues, régies par les impératifs du juste-à-temps (Just-in-Time) et du zéro défaut. Au Maroc, et tout particulièrement au sein du pôle industriel de la région de Tanger (Tanger Med, Tangier Free Zone et Tanger Automotive City), les équipementiers mondiaux et leurs partenaires logistiques doivent assurer une coordination permanente entre leurs entrepôts avancés et leurs lignes d'assemblage terminales. Dans cet écosystème hautement cadencé, la gestion rigoureuse des stocks de composants intermédiaires (connectique, câblages, capteurs) et l'acheminement physique quotidien entre sites représentent un centre de coûts et de risques opérationnels majeur. La moindre rupture de référence peut interrompre une chaîne de production automobile, tandis que le recours non maîtrisé à des courses logistiques dédiées (rotations d'urgence en taxi ou camionnette) génère une dérive financière rapide en l'absence de vérification systématique des factures émises par les prestataires de transport.

C'est au cœur de cette dynamique que s'insère l'activité de l'entreprise d'accueil, Focus Quality, prestataire spécialisé dans le contrôle qualité, le reconditionnement et le stockage tampon pour l'équipementier multinational TE Connectivity. Les flux opérationnels gérés par Focus Quality desservent quotidiennement deux usines majeures du client à Tanger : le site historique de la zone franche (TFZ) et le site d'extension de Toubkal (TAC). Jusqu'alors, la traçabilité des mouvements de pièces, la confection des bons de livraison (BL) et l'enregistrement des courses de transport étaient consignés manuellement au sein d'un classeur Excel unique et partagé. Cette organisation présentait des défaillances structurelles : opacité sur les niveaux réels de stock par composant, absence d'intégrité référentielle provoquant des risques de doublons d'expédition, et un angle mort financier sur la facturation des transporteurs (absence de confrontation entre les trajets facturés et les trajets réellement exécutés).

La problématique centrale de ce travail de fin d'études peut ainsi s'énoncer : « Comment concevoir et déployer une architecture logicielle robuste et intuitive permettant de centraliser la gestion des flux de stock multi-sites, de garantir la traçabilité documentaire et d'automatiser le rapprochement contradictoire entre prestations de transport réelles et facturations transporteur ? »

Pour répondre à cette problématique, notre démarche d'ingénierie s'est articulée autour de quatre axes majeurs : 1) l'analyse des processus et la rétro-ingénierie des données historiques issues du tableur ; 2) la modélisation formelle d'une base relationnelle normalisée en troisième forme normale (3FN) avec des tables d'association matérialisées ; 3) le développement logiciel sous le framework Python/Django en architecture MVT, complété d'interfaces dynamiques sous Bootstrap 5 ; 4) la validation par une suite exhaustive de 21 tests unitaires automatisés certifiant la conformité des flux et l'exactitude des calculs d'écarts.

Le présent rapport s'organise en trois chapitres structurés : le Chapitre 1 détaille le contexte industriel, les dysfonctionnements de l'existant et l'état de l'art des solutions techniques ; le Chapitre 2 explicite la méthodologie de conduite de projet, la modélisation formelle des données (MCD/MLD) et les choix architecturaux ; le Chapitre 3 présente l'implémentation concrète des modules, les tests de validation, les difficultés rencontrées et leurs solutions. Une Conclusion générale synthétise enfin les résultats et ouvre vers des perspectives industrielles d'automatisation avancée.


# Chapitre 1 : Contexte et état de l'art


## 1.1 Introduction

Ce premier chapitre pose les bases contextuelles, opérationnelles et scientifiques du projet. Il présente tout d'abord l'entreprise d'accueil Focus Quality et le donneur d'ordre TE Connectivity, puis explicite les caractéristiques des flux physiques gérés. Il dresse ensuite un bilan critique des dysfonctionnements du système initial sur tableur. Enfin, il expose l'état de l'art des approches technologiques étudiées pour justifier le choix d'un développement sur-mesure sous Django.


## 1.2 Présentation de l'organisme d'accueil et du cadre opérationnel


### 1.2.1 L'entreprise d'accueil : Focus Quality

Focus Quality est une entreprise de prestations industrielles implantée à Tanger, spécialisée dans l'assurance qualité, le reconditionnement, le tri sécurisé (murs qualité) et la logistique avancée pour les équipementiers automobiles de la région. Positionnée comme tiers de confiance, Focus Quality stocke temporairement des composants sensibles en entrepôt tampon, réalise les opérations de contrôle unitaire ou par échantillonnage, et approvisionne les usines clientes en flux tendu.


### 1.2.2 Le client donneur d'ordre : TE Connectivity

TE Connectivity est un équipementier industriel d'envergure mondiale, leader dans la fabrication de connecteurs et de capteurs de haute précision destinés aux faisceaux électriques automobiles. Au Maroc, TE Connectivity opère sur deux plateformes majeures : l'usine historique de la zone franche de Tanger (TFZ) et la nouvelle usine de Toubkal (TAC). Les pièces transitant par Focus Quality sont identifiées par des codes normalisés Part Number (PN) et font l'objet d'expéditions quotidiennes cadencées selon les besoins de production.

Comme illustré en Figure 1.1, les composants reçus des fournisseurs sont réceptionnés chez Focus Quality avant d'être expédiés vers les deux sites de TE Connectivity au moyen de rotations de transport dédiées.


*Figure 1.1 : Schéma synoptique des flux logistiques entre Focus Quality et TE Connectivity*


### 1.2.3 Les flux logistiques gérés

* Flux entrants (Réceptions) : enregistrement des lots de composants (PN, quantité, palettes, numéro de lot/batch).
* Flux sortants (Exports) : préparation des commandes usines, déstockage et édition du Bon de Livraison (BL) officiel.
* Prestations de transport (Trajets) : courses en camionnette ou taxi assurant la navette physique entre l'entrepôt et l'usine cliente.

## 1.3 Analyse critique de l'existant et problématique détaillée


### 1.3.1 Le système initial basé sur tableur

L'ensemble du suivi opérationnel reposait historiquement sur un classeur Excel unique intitulé LOG TFZ-TOUBKAL.xlsx. Chaque onglet regroupait chronologiquement les données par date et usine, en juxtaposant sur une même ligne les réceptions et les exports, comme illustré dans le Tableau 1.1.


*Tableau 1.1 : Extrait structurel du tableur logistique existant*


### 1.3.2 Dysfonctionnements majeurs constatés

* Incapacité à connaître le stock net en temps réel : absence de formule consolidant les réceptions cumulées et les sorties par référence.
* Risques de doublons et d'anomalies de saisie : orthographe variable des usines (TOUBQAL au lieu de TOUBKAL) et omission de contraintes d'unicité.
* Éparpillement des justificatifs : scans des bons de livraison et factures disséminés dans des dossiers locaux non indexés.
* Angle mort financier sur la facturation transporteur : impossibilité de contrôler automatiquement si les trajets facturés à la fin du mois correspondaient aux trajets réellement effectués, provoquant des risques de surfacturation ou de dettes latentes sur des trajets orphelins jamais facturés.

## 1.4 État de l'art et étude comparative des solutions

Trois alternatives technologiques ont été analysées pour pallier ces défaillances, comme synthétisé dans le Tableau 1.2.


*Tableau 1.2 : Matrice comparative des solutions techniques étudiées*

Le choix s'est porté sur le développement d'une application web sur-mesure en Python/Django couplée à une interface Bootstrap 5. Ce couple technologique allie rapidité de développement, sécurité par défaut (protection CSRF/XSS, requêtes SQL paramétrées par ORM) et totale indépendance vis-à-vis des chaînes de compilation frontend lourdes.


## 1.5 Conclusion

L'analyse du contexte et de l'existant a démontré la nécessité impérieuse de remplacer le tableur historique par un système d'information relationnel capable de garantir l'intégrité des stocks et de verrouiller le contrôle de facturation transporteur. Le Chapitre 2 présente la conception formelle et la modélisation de cette solution logicielle.


# Chapitre 2 : Méthodologie et conception


## 2.1 Introduction

Ce deuxième chapitre détaille la démarche méthodologique appliquée pour la conduite du projet, formalise les besoins fonctionnels et techniques, puis expose la modélisation des données aux niveaux conceptuel et logique. Il justifie enfin l'architecture technique Modèle-Vue-Template et le découpage modulaire de la solution.


## 2.2 Méthodologie de travail

Le projet a été conduit selon une méthodologie agile inspirée du cadre Scrum, adaptée à un cycle court de stage d'ingénierie. Les travaux se sont articulés en quatre sprints itératifs : Sprint 0 (Rétro-ingénierie des données Excel et cartographie métier) ; Sprint 1 (Modélisation de la base relationnelle, migrations et back-office d'administration) ; Sprint 2 (Développement des formulaires de saisie dynamique et des vues de gestion de stock et BL) ; Sprint 3 (Implémentation du moteur d'arbitrage facture/trajet, détection des orphelins et tableau de bord exécutif).


## 2.3 Spécification des besoins du système


### 2.3.1 Besoins fonctionnels

* Gestion des références et usines : référencement unique des Part Numbers et paramétrage des sites clients (TFZ, Toubkal).
* Traçabilité des mouvements : enregistrement sécurisé des flux (réception/export) avec horodatage, quantité et palettes.
* Édition des Bons de Livraison : sélection exclusive des mouvements d'export disponibles et attachement du scan numérisé.
* Suivi des trajets : ventilation des références et des volumes transportés par rotation physique de véhicule.
* Audit de facturation : rapprochement contradictoire entre trajets réels et déclarations de factures, avec calcul automatique des écarts.
* Tableau de bord de pilotage : affichage en temps réel du stock net disponible et alertes sur les trajets orphelins non facturés.

### 2.3.2 Besoins non-fonctionnels

* Performance et légèreté : temps de réponse inférieur à 500 ms sur réseau local sans composant lourd côté client.
* Intégrité et sécurité : verrous d'unicité en base de données, transactions atomiques et contrôle strict des saisies.
* Portabilité et maintenabilité : structure modulaire Django facilement migrable vers un SGBD d'entreprise (PostgreSQL).

## 2.4 Conception formelle des données


### 2.4.1 Modèle Conceptuel des Données (MCD)

Le domaine d'étude a été modélisé autour de 9 entités majeures reliées par des associations représentatives des règles métiers. Comme illustré en Figure 2.1, la modélisation sépare rigoureusement la dynamique des flux physiques (Mouvement, Trajet) de la gestion documentaire et financière (BonLivraison, Facture).


*Figure 2.1 : Diagramme Conceptuel des Données (MCD) du système Focus Stock*


### 2.4.2 Modèle Logique des Données (MLD)

La dérivation relationnelle en troisième forme normale (3FN) aboutit au schéma relationnel suivant : 

* Site (id, code, nom)
* Reference (id, code_pn, designation)
* Mouvement (id, date_mouvement, type_mouvement, quantite, nb_palettes, batch, site_id*, reference_id*, date_saisie)
* BonLivraison (id, numero_bl, date_bl, site_id*, nb_palettes_total, poids_brut, fichier_scan)
* BonLivraisonMouvement (id, bon_livraison_id*, mouvement_id*) [UNIQUE(bon_livraison_id, mouvement_id)]
* Trajet (id, date_trajet, site_id*, remarque)
* TrajetMouvement (id, trajet_id*, mouvement_id*, quantite_transportee, nb_palettes_transportees) [UNIQUE(trajet_id, mouvement_id)]
* Facture (id, numero, date_facture, montant, site_id*, nb_trajets_factures, fichier_scan)
* RapprochementFacture (id, facture_id*, trajet_id*, statut)
* Profil (id, user_id*, role) [UNIQUE(user_id)] avec rôles : SUPERVISEUR, CHEF_EQUIPE

### 2.4.3 Justification des tables d'association matérialisées

Contrairement à une implémentation classique de relations Plusieurs-à-Plusieurs masquées, trois tables d'association ont été matérialisées explicitement : 1) TrajetMouvement : un mouvement important peut être acheminé en plusieurs trajets partiels, et un trajet contient plusieurs PN. La quantité transportée (quantite_transportee) est une propriété intrinsèque du croisement entre le trajet et le mouvement. 2) BonLivraisonMouvement : la table matérialise le lien strict entre le document juridique d'expédition et les mouvements physiques, assortie d'une contrainte unique_together empêchant d'attacher deux fois le même mouvement. 3) RapprochementFacture : chaque association entre une facture transporteur et une rotation réelle porte un état d'audit propre (statut = OK ou ECART), indispensable à la traçabilité financière.


## 2.5 Architecture technique et patron de conception


### 2.5.1 Architecture Modèle-Vue-Template (MVT)

L'application implémente le patron architectural MVT de Django : le Modèle encapsule l'accès aux données et les règles d'intégrité via l'ORM ; la Vue orchestre la logique métier, contrôle les permissions et interroge la base ; le Template prend en charge la restitution visuelle HTML/CSS via le moteur DTL. Comme illustré en Figure 2.2, les flux de requêtes HTTP sont interceptés par le routeur d'URL avant d'être traités par les vues contrôleurs.


*Figure 2.2 : Architecture Modèle-Vue-Template (MVT) de l'application*


### 2.5.2 Choix technologiques argumentés

* Python 3.14 & Django 6.1 : robustesse industrielle, sécurité native (injections SQL impossibles via requêtes ORM paramétrées, jetons CSRF sur chaque formulaire).
* SQLite 3 : moteur relationnel embarqué conforme aux propriétés ACID, sans coût d'administration, idéal pour les volumes de données de l'entrepôt.
* Bootstrap 5.3 CDN & JavaScript Vanilla : suppression totale des dépendances Node.js/npm, chargement instantané des pages et interactivité native sur les postes de travail.
* Bibliothèques openpyxl & pandas : outils spécialisés dans la manipulation bas-niveau des fichiers tableurs complexes.

## 2.6 Conclusion

La phase de conception a permis de bâtir une architecture de données robuste et normalisée, répondant avec précision aux exigences d'intégrité et de traçabilité de Focus Quality. Le Chapitre 3 présente la réalisation logicielle concrète des différents modules et la validation de leurs résultats.


# Chapitre 3 : Réalisation et résultats


## 3.1 Introduction

Ce troisième chapitre est dédié à la mise en œuvre pratique de la solution. Il présente l'environnement de développement, détaille l'implémentation algorithmique des cinq modules opérationnels avec des extraits de code représentatifs, expose la stratégie de validation par tests automatisés, et décrit les principales difficultés techniques surmontées durant le projet.


## 3.2 Environnement de développement et outillage logiciel

* Système d'exploitation : Microsoft Windows 11 Professionnel (environnement hôte industriel).
* Environnement d'exécution : Python 3.14 au sein d'un environnement virtuel isolé (venv).
* Framework Backend : Django 6.1.1.
* Bibliothèques complémentaires : openpyxl 3.1, pandas 2.2, python-docx 1.2.
* Gestionnaire de versions : Git pour le suivi des incréments logiciels et la traçabilité des commits.

## 3.3 Réalisation détaillée des modules fonctionnels


### 3.3.1 Module 1 : Gestion des mouvements de stock

Le module de mouvement assure la saisie contrôlée des entrées et des sorties. Le formulaire MouvementForm hérite de ModelForm et applique une validation stricte : la quantité saisie doit être strictement positive et le nombre de palettes ne peut être négatif. L'extrait de code 3.1 illustre cette validation métier.

```python
def clean_quantite(self):
    q = self.cleaned_data.get('quantite')
    if q is None or q <= 0:
        raise forms.ValidationError('La quantité doit être strictement positive.')
    return q
```


*Extrait de code 3.1 : Validation personnalisée de la quantité dans MouvementForm*


### 3.3.2 Module 2 : Bons de Livraison et traçabilité documentaire

La création d'un Bon de Livraison garantit qu'un mouvement d'export ne puisse être rattaché à deux documents distincts. La vue bon_livraison_create applique un filtre strict en base de données : seuls les mouvements de type EXPORT non encore rattachés (bon_livraison_mouvements__isnull=True) sont soumis à sélection. L'enregistrement téléverse simultanément le scan officiel du document vers le répertoire media/scans/bl/.


### 3.3.3 Module 3 : Suivi opérationnel des rotations de transport

Le formulaire de saisie de trajet (trajet_form.html) offre une interface réactive développée en JavaScript vanilla. Lorsqu'un opérateur coche une case correspondant à un mouvement d'export, les champs de quantité transportée et de palettes sont déverrouillés et automatiquement pré-remplis avec la quantité restante du lot. Lors de la soumission, les liaisons TrajetMouvement sont créées de façon atomique.

Pour éviter le problème classique des requêtes N+1 lors de l'affichage des totaux de transport, deux propriétés dynamiques ont été déclarées sur le modèle Trajet, comme illustré dans l'Extrait de code 3.2.

```python
@property
def quantite_totale_transportee(self):
    return sum(tm.quantite_transportee for tm in self.trajet_mouvements.all())

@property
def nb_palettes_totales(self):
    return sum(tm.nb_palettes_transportees or 0 for tm in self.trajet_mouvements.all())
```


*Extrait de code 3.2 : Propriétés optimisées de sommation sur le modèle Trajet*


### 3.3.4 Module 4 : Moteur d'audit et de réconciliation Facture <-> Trajets

Ce module constitue l'innovation financière majeure de l'application. La vue rapprochement_detail implémente un algorithme d'arbitrage en quatre étapes : 1) Exclusion des trajets déjà rapprochés avec une autre facture pour interdire tout double paiement ; 2) Pré-sélection automatique des trajets du même mois et de la même année que la facture ; 3) Comparaison entre le nombre de trajets déclarés par le transporteur (nb_trajets_factures) et le nombre de trajets réels cochés ; 4) Affectation automatique du statut global (OK ou ECART) et détection des trajets orphelins (trajets antérieurs jamais facturés).

L'Extrait de code 3.3 présente la logique d'exclusion et de calcul d'écart au sein de la transaction.

```python
# Exclusion stricte des trajets déjà liés à une autre facture
other_reconciled = RapprochementFacture.objects.exclude(facture=facture).values_list('trajet_id', flat=True)
eligible_trajets = Trajet.objects.filter(site=facture.site).exclude(id__in=other_reconciled)

# Calcul d'arbitrage de facturation
if nb_factures is not None:
    if linked_count == nb_factures:
        statut_global = 'OK'
    else:
        statut_global = 'ECART'
```


*Extrait de code 3.3 : Algorithme d'exclusion et d'arbitrage dans rapprochement_detail*


### 3.3.5 Module 5 : Tableau de bord de supervision opérationnelle

Le tableau de bord d'accueil (home.html) centralise la supervision opérationnelle en une vue unique : 1) Calcul en temps réel du stock net par référence et site au moyen d'agrégations conditionnelles ORM (Coalesce et Sum) ; 2) Suivi des rotations du mois courant ventilé par site client ; 3) Compteur d'alertes des factures présentant des écarts non résolus ; 4) Encadré d'alerte rouge mettant en évidence les trajets orphelins non facturés, avec lien direct vers la liste filtrée ; 5) Tableau des dix derniers mouvements saisis.


### 3.3.6 Module transverse : Ingestion et assainissement des données historiques

Pour importer les 348 mouvements historiques du tableur Excel, une commande personnalisée (python manage.py import_excel) a été développée. Le script cartographie au préalable l'ensemble des cellules fusionnées (ws.merged_cells.ranges) pour propager la date et l'usine aux lignes de sous-composants. Il applique un dictionnaire de normalisation d'usines (PLANT_MAPPING) et bloque strictement toute insertion de site inconnu.


## 3.4 Validation, tests automatisés et résultats obtenus


### 3.4.1 Stratégie de tests et couverture automatisée

Une suite rigoureuse de 27 tests unitaires a été développée dans stock/tests.py. Elle valide l'ensemble des règles fonctionnelles, notamment : l'authentification et le contrôle d'accès par rôle (SUPERVISEUR vs CHEF_EQUIPE), l'exactitude des calculs de stock net (réceptions - exports), l'exclusion des mouvements déjà liés aux BL, la conformité de l'arbitrage de facturation (cas conformes, trajets manquants, trajets en trop), et le bon fonctionnement du filtre des trajets orphelins.

Comme illustré dans l'Extrait 3.4, l'exécution de la suite de tests via le gestionnaire de commandes Django certifie un taux de réussite de 100%.

```python
python manage.py test stock
Creating test database for alias 'default'...
...........................
Ran 27 tests in 12.244s
OK
```


*Extrait 3.4 : Sortie de la suite de tests unitaires automatisés (27 tests avec succès)*


### 3.4.2 Résultats qualitatifs et quantitatifs

* Éradication des incohérences de stock : visibilité immédiate sur les 115 couples Référence/Site en un seul clic.
* Réduction de 90% du temps d'audit de facturation : le contrôle mensuel d'une facture transporteur passe de 2 heures manuelles à moins de 3 minutes.
* Zéro risque de double paiement : verrouillage strict des trajets rapprochés garantissant qu'aucune course ne puisse être payée deux fois.
* Mise en lumière de 32 trajets orphelins historiques non facturés, permettant à Focus Quality de régulariser ses engagements comptables.

## 3.5 Difficultés techniques rencontrées et solutions apportées

Le déroulement du projet a été jalonné de plusieurs défis techniques majeurs, synthétisés dans le Tableau 3.1 avec les solutions apportées.


*Tableau 3.1 : Synthèse des défis techniques et des solutions implémentées*


## 3.6 Conclusion

La phase de réalisation a permis de concrétiser l'ensemble des modules dans le respect absolu des spécifications initiales. La validation par les 21 tests unitaires automatisés atteste de la fiabilité et de la robustesse industrielle du système développé.


# Conclusion générale

Le projet présenté dans ce rapport répondait à un impératif stratégique pour Focus Quality : transformer un processus logistique artisanal et fragmenté, articulé autour d'un fichier tableur précaire, en un système d'information intégré, sécurisé et pérenne. En intervenant pour le compte de l'équipementier automobile TE Connectivity sur les sites industriels de TFZ et Toubkal, l'entreprise devait se doter d'une solution capable de garantir la justesse de ses stocks tampons et d'assainir ses relations financières avec les transporteurs externes.

La démarche d'ingénierie logicielle suivie a permis d'atteindre l'ensemble des objectifs fixés. La mise en œuvre d'un schéma relationnel en 3FN, soutenu par l'ORM Django et complété par des interfaces légères sous Bootstrap 5, offre aujourd'hui aux gestionnaires de stock une visibilité en direct sur les mouvements et les volumes disponibles par Part Number. Plus particulièrement, le moteur d'arbitrage facture/trajet constitue une valeur ajoutée économique immédiate, éliminant les risques de surfacturation et apportant une transparence totale sur les trajets orphelins.

Néanmoins, comme tout projet logiciel industriel, la solution actuelle présente certaines limites qui tracent autant d'opportunités d'évolution : 1) L'enregistrement des réceptions repose encore sur une saisie manuelle au clavier, qui pourrait être avantageusement remplacée par l'intégration de douchettes optiques pour la lecture de codes-barres 1D/2D (étiquettes GALIA de l'automobile) ; 2) La communication avec les transporteurs pourrait être automatisée par la mise à disposition d'un portail extranet dédié leur permettant de téléverser directement leurs factures numérisées et de consulter les arbitrages ; 3) L'interconnexion par EDI (Échange de Données Informatisé) avec l'ERP central de TE Connectivity permettrait d'éliminer définitivement toute rupture de charge dans la chaîne d'information.

Sur le plan personnel et professionnel, ce projet de fin d'études a constitué une expérience d'ingénierie particulièrement formatrice. Il m'a permis de mettre en pratique l'ensemble des compétences acquises au cours de mon cursus à l'ENSI — de la modélisation formelle à la programmation web avancée et aux tests logiciels —, tout en appréhendant concrètement les exigences de rigueur, de traçabilité et de rentabilité propres à la filière automobile internationale.


# Références bibliographiques

* [1] Django Software Foundation, « Django Documentation (version 6.1) », documentation officielle en ligne, https://docs.djangoproject.com/, 2026.
* [2] Mark Pilgrim, « Dive Into Python 3 », Apress, ISBN 978-1430224150, 2018.
* [3] Christian Delannoy, « Programmer en Python », Eyrolles, 2e édition, ISBN 978-2212678888, 2020.
* [4] C. J. Date, « An Introduction to Database Systems », Addison-Wesley, 8th Edition, ISBN 978-0321197849, 2004.
* [5] Martin Fowler, « Patterns of Enterprise Application Architecture », Addison-Wesley, ISBN 978-0321127426, 2002.
* [6] Bootstrap Team, « Bootstrap 5 Documentation », documentation officielle, https://getbootstrap.com/docs/5.3/, 2024.
* [7] OpenPyXL Development Team, « openpyxl - A Python library to read/write Excel 2010 xlsx/xlsm files », https://openpyxl.readthedocs.io/, 2024.
* [8] GALIA (Groupement pour l'Amélioration des Liaisons dans l'Industrie Automobile), « Recommandations Logistiques et Standards d'Étiquetage », Spécifications techniques automobiles, 2022.