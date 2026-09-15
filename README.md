# Focus Stock & Transport - Focus Quality

[![CI focus_stock](https://github.com/Kharraz-Mohamed-El-Amine/focus-stock/actions/workflows/ci.yml/badge.svg)](https://github.com/Kharraz-Mohamed-El-Amine/focus-stock/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Django 6.1](https://img.shields.io/badge/django-6.1-green.svg)](https://www.djangoproject.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Application web de gestion des stocks et de contrôle du transport logistique pour le compte du client **TE Connectivity** (sites industriels de **TFZ** et **TOUBKAL** à Tanger).

Développée avec **Django 6.1**, **SQLite 3**, **Bootstrap 5.3 (CDN)** et **JavaScript vanilla** (sans outil de build JS lourd).

---

## Fonctionnalités Principales

* **Gestion des Mouvements de Stock** : Saisie et suivi en temps réel des flux d'entrées (`RÉCEPTION`) et de sorties (`EXPORT`) par Part Number (PN) et usine cliente.
* **Bons de Livraison (BL)** : Regroupement sécurisé des mouvements d'export avec vérification anti-doublon et archivage des scans signés.
* **Rotations de Transport (Trajets)** : Suivi détaillé des charges transportées (quantités et palettes) par course physique (navette ou taxi).
* **Audit & Rapprochement de Facturation** : Comparaison contradictoire entre les trajets déclarés sur les factures transporteur et les trajets réels, détection des écarts (trajets en trop ou manquants) et identification des trajets orphelins non facturés.
* **Tableau de Bord Exécutif** : Vue temps réel du stock net par référence et site ($\sum \text{Réceptions} - \sum \text{Exports}$), indicateurs mensuels et alertes financières.
* **Authentification & Permissions par Rôles** :
  * **`SUPERVISEUR`** : Accès complet à toutes les fonctionnalités (création de BL, trajets, factures et validation du rapprochement).
  * **`CHEF_EQUIPE`** : Consultation des listes et du tableau de bord, saisie des mouvements de stock uniquement.

---

## 1. Exécution Locale Directe (Usage Quotidien Recommandé)

> **Note d'exploitation :** En raison des contraintes matérielles du poste de travail au bureau, l'usage quotidien réel de l'application s'effectue en exécution locale directe (sans conteneur).

### Prérequis
* Python 3.12+ (ou Python 3.14)
* Environnement virtuel Python (`venv`)

### Démarrage rapide sous Windows
Un script batch est fourni à la racine du projet :
```cmd
demarrer.bat
```
Ce script active automatiquement l'environnement virtuel, applique les migrations et lance le serveur local sur `http://127.0.0.1:8000/`.

### Lancement manuel en ligne de commande
```bash
# 1. Activation de l'environnement virtuel
.\venv\Scripts\activate      # Windows (PowerShell / CMD)
# source venv/bin/activate   # Linux / macOS

# 2. Installation des dépendances
pip install -r requirements.txt

# 3. Application des migrations de base de données
python manage.py migrate

# 4. Initialisation des comptes utilisateurs de test
python manage.py seed_users

# 5. Lancement du serveur de développement
python manage.py runserver
```

### Comptes utilisateurs initiaux
La commande `python manage.py seed_users` configure deux comptes de démonstration :
* **Superviseur** : Identifiant `superviseur` | Mot de passe initial `SuperviseurDefault2026!` (ou défini via variable d'environnement).
* **Chef d'équipe** : Identifiant `chef_equipe` | Mot de passe initial `ChefEquipeDefault2026!` (ou défini via variable d'environnement).

---

## 2. Déploiement avec Docker (Démonstration & Portabilité)

> **Cadre technique :** La conteneurisation Docker est fournie pour garantir la portabilité du projet, faciliter les démonstrations techniques et permettre un déploiement standardisé sur tout serveur d'hébergement. L'application utilise **Gunicorn** comme serveur WSGI de production.

### Structure des fichiers Docker
* `Dockerfile` : Image multi-stage légère basée sur `python:3.12-slim` (étape builder pour isoler les dépendances puis image finale minimale).
* `.dockerignore` : Exclusion des fichiers locaux (`venv`, `__pycache__`, `db.sqlite3`, `media/`, `.env`, `.git`).
* `docker-compose.yml` : Configuration d'un service unique avec persistance par volumes externes.

### Étape 1 : Préparation de la configuration d'environnement
Avant le premier lancement, créez votre fichier `.env` local à partir du modèle fourni :
```bash
# Sous Windows (CMD) :
copy .env.example .env

# Sous Linux / macOS / PowerShell :
cp .env.example .env
```
Renseignez dans `.env` vos mots de passe souhaités pour les comptes `superviseur` et `chef_equipe`.

### Étape 2 : Construction de l'image (Build)
Pour construire l'image Docker multi-stage :
```bash
# Via Docker Compose (recommandé) :
docker compose build

# Ou directement via Docker CLI :
docker build -t focus-stock:latest .
```

### Étape 3 : Lancement du conteneur
Démarrez l'application en arrière-plan :
```bash
docker compose up -d
```
Le conteneur `focus_stock_app` démarre et monte automatiquement deux volumes pour garantir la persistance des données sur la machine hôte :
* `./db.sqlite3` : Fichier de base de données SQLite.
* `./media/` : Dossier hébergeant les scans numérisés des BL et des factures.

### Étape 4 : Initialisation au premier lancement (Migrations & Utilisateurs)
Exécutez les migrations de schéma et la commande d'initialisation des utilisateurs directement au sein du conteneur en cours d'exécution :
```bash
# 1. Application des migrations en base de données
docker compose exec web python manage.py migrate

# 2. Création des comptes superviseur et chef d'équipe
docker compose exec web python manage.py seed_users
```

### Étape 5 : Accès à l'application
L'application est immédiatement accessible sur votre navigateur web :
* URL de connexion : **`http://localhost:8000/login/`**
* Tableau de bord : **`http://localhost:8000/`**
* Administration Django : **`http://localhost:8000/admin/`**

### Commandes utiles Docker Compose
```bash
# Consulter les logs en direct (Gunicorn)
docker compose logs -f web

# Arrêter le conteneur
docker compose stop

# Arrêter et supprimer le conteneur (les données SQLite et media sont préservées grâce aux volumes)
docker compose down

# Relancer après une modification
docker compose restart
```

---

## 3. Suite de Tests Automatisés

Le projet comprend une suite complète de **27 tests unitaires** validant la conformité des règles métiers, l'authentification et les restrictions par rôles :

```bash
# En local :
python manage.py test stock

# Dans le conteneur Docker :
docker compose exec web python manage.py test stock
```

Résultat attendu :
```
Ran 27 tests in 12.136s
OK
```
