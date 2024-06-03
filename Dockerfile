# Utiliser l'image de base Python
FROM continuumio/miniconda3

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le code de l'application dans le conteneur
COPY dashboard.py .

# Définir un répertoire de données
# VOLUME /app/data

# Installer les dépendances
RUN pip install streamlit geopandas plotly matplotlib ipywidgets pandas

# Commande pour exécuter l'application quand le conteneur démarre
CMD streamlit run --server.port $PORT dashboard.py