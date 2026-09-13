# =============================================================================
# Dockerfile - Focus Stock & Transport (Focus Quality)
# =============================================================================
# NOTE IMPORTANTE :
# Cette conteneurisation est fournie pour la portabilité et la démonstration
# technique du projet. L'usage quotidien réel de l'application au sein de
# l'entreprise reste en exécution locale directe (sans Docker), en raison des
# contraintes matérielles et de l'environnement bureautique du poste de travail.
# =============================================================================

# -----------------------------------------------------------------------------
# Étape 1 : Build (Installation des dépendances Python dans un venv isolé)
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Optimisations Python pour la construction
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Création d'un environnement virtuel isolé
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copie et installation des dépendances du projet
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Étape 2 : Image finale légère d'exécution
# -----------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Variables d'environnement pour l'exécution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Copie uniquement l'environnement virtuel préparé depuis l'étape de build
COPY --from=builder /opt/venv /opt/venv

# Création des dossiers nécessaires aux médias et aux fichiers statiques
RUN mkdir -p /app/media /app/static

# Copie du code source de l'application
COPY . .

# Port d'écoute HTTP du conteneur
EXPOSE 8000

# Démarrage avec Gunicorn comme serveur WSGI de production (3 workers)
CMD ["gunicorn", "focus_stock.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
