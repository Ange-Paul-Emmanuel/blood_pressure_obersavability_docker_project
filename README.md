# 🩺 Blood Pressure & Stroke Prediction System

Ce projet a été réalisé dans le cadre du **Master USPN (Big Data)**. Il s'agit d'un écosystème complet de traitement de données de santé en temps réel utilisant une architecture distribuée pour prédire les risques d'AVC (Accident Vasculaire Cérébral).
---

## 🚀 Déploiement (Installation & Run)

Suivez ces étapes pour installer l'environnement et lancer le pipeline de prédiction sur votre machine locale.

### 1. Prérequis
* **Docker Desktop** : Assurez-vous qu'il est installé et que le moteur WSL2 est activé (pour Windows).
* **Python 3.10+** : Vérifiez votre version avec `python --version`.
* **Git** : Pour cloner le répertoire.

### 2. Récupération du Projet
Ouvrez un terminal (PowerShell ou Bash) et exécutez :
```bash
git clone https://github.com/Ange-Paul-Emmanuel/blood_pressure_obersavability_docker_project/tree/master
cd "projet blood pressure"
```
### 3. Lancement de l'Infrastructure (Docker)
Démarrez tous les services (Zookeeper, Kafka, Elasticsearch, Kibana, Kafka-UI) en arrière-plan

```bash
docker-compose up -d
```
- Vérification : Attendez environ 30 secondes, puis tapez docker ps pour vérifier que tous les containers affichent le statut Up

### 4. Configuration de l'environnement Python
```bash
# Création de l'environnement
python -m venv venv

# Activation (Windows)
.\venv\Scripts\activate

# Activation (Mac/Linux)
# source venv/bin/activate

# Installation des bibliothèques nécessaires
pip install -r requirements.txt
```

### 5. Exécution du Pipeline (Ordre de lancement)

Pour que le flux de données soit correctement traité, ouvrez quatre terminaux différents et lancez les scripts dans l'ordre suivant :
```bash
# Excécute le Simulateur de données médicales
generator.py

# Démarre l'envoi des données patients simulées vers Kafka.
python producer.py

# Lance l'IA qui écoute Kafka et prédit les risques d'AVC.
python medical_agent.py

# Prépare la réception et l'indexation dans Elasticsearch.
python consumer.py
```
### 6. Accès aux Interfaces Graphiques
Une fois le pipeline en marche, vous pouvez surveiller le système via :

Kafka UI : http://localhost:8080 (pour voir les messages dans les topics).

Kibana : http://localhost:5601 (pour visualiser les dashboards et les alertes).


---

## 📂 Arborescence du Projet (Project Tree)

```text
PROJET BLOOD PRESSURE/
├── outputs_bp/                 # Artefacts et modèles exportés
│   ├── dataset_enrichi.csv        # Dataset après feature engineering
│   └── my_random_forest_avc.joblib # Modèle Random Forest entraîné
├── venv/                       # Environnement virtuel Python
├── .env                        # Configuration des accès (Clef API)
├── .gitignore                  # Fichiers à exclure du versioning
├── docker-compose.yml          # Orchestration des conteneurs Docker(Kafka, Zookeeper, ES, Kibana)
├── producer.py                 # Ingestion des données patients (Source)
├── medical_agent.py            # Agent IA (Prédiction AVC en temps réel)
├── consumer.py                 # Indexation finale dans Elasticsearch
├── generator.py                # Simulateur de données médicales
├── reset_topic.py              # Script utilitaire de purge Kafka
├── requirements.txt            # Dépendances du projet
├── ML_Model.ipynb              # Notebook d'entraînement et modèle de prédiction
└── patients_sains.json         # Stock localement les données des patients sains
