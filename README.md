# ⚕️Blood Pressure and AVC Risk Monitoring🩺🫀

Ce projet a été réalisé dans le cadre du **Master USPN (Big Data)**. Il s'agit d'un écosystème complet de traitement de données de santé en temps réel utilisant une architecture distribuée pour prédire les risques d'AVC (Accident Vasculaire Cérébral).
---

## 🚀 Déploiement (Installation & Run)

Suivez ces étapes pour installer l'environnement et lancer le pipeline de prédiction sur votre machine locale.

## 1. Prérequis
* **Docker Desktop** : Assurez-vous qu'il est installé et que le moteur WSL2 est activé (pour Windows).
* **Python 3.10+** : Vérifiez votre version avec `python --version`.
* **Git** : Pour cloner le répertoire.
* **Clé API**

## 2. Récupération du Projet
Ouvrez un terminal (PowerShell ou Bash) et exécutez :
```bash
git clone https://github.com/Ange-Paul-Emmanuel/blood_pressure_obersavability_docker_project/tree/master
cd "PROJET BLOOD PRESSURE" 
```
## 3. Lancement de l'Infrastructure (Docker)
Démarrez tous les services (Zookeeper, Kafka, Elasticsearch, Kibana, Kafka-UI) en arrière-plan

```bash
docker-compose up -d
```
Exemple de sortie du terminal
```bash
[+] Running 5/5
 ✔ Container zookeeper      Started                                     3.7s 
 ✔ Container elasticsearch  Started                                     3.7s 
 ✔ Container kibana         Started                                     2.3s 
 ✔ Container kafka          Started                                     2.2s 
 ✔ Container kafka-ui       Started                                     2.0s
```
- Vérification : Attendez environ 30 secondes, puis tapez docker ``` docker-compose ps ``` pour vérifier que tous les containers affichent le statut Up

Exemple de sortie du terminal

```bash
NAME            IMAGE                                                  COMMAND                  SERVICE         CREATED       STATUS          PORTS
elasticsearch   docker.elastic.co/elasticsearch/elasticsearch:8.10.2   "/bin/tini -- /usr/l…"   elasticsearch   6 days ago    Up 10 minutes   0.0.0.0:9200->9200/tcp, [::]:9200->9200/tcp
kafka           confluentinc/cp-kafka:6.2.0                            "/etc/confluent/dock…"   kafka           6 days ago    Up 8 minutes    0.0.0.0:9092->9092/tcp, [::]:9092->9092/tcp
kafka-ui        provectuslabs/kafka-ui:latest                          "/bin/sh -c 'java --…"   kafka-ui        6 days ago    Up 10 minutes   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
kibana          docker.elastic.co/kibana/kibana:8.10.2                 "/bin/tini -- /usr/l…"   kibana          6 days ago    Up 10 minutes   0.0.0.0:5601->5601/tcp, [::]:5601->5601/tcp
zookeeper       confluentinc/cp-zookeeper:6.2.0                        "/etc/confluent/dock…"   zookeeper       6 days ago    Up 10 minutes   2181/tcp, 2888/tcp, 3888/tcp
```

## 4. Configuration de l'environnement Python
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
## 5. 🔑 Configuration et accès au LLM

Le projet utilise l'agent ```MedicalAgent``` de ```medical_agent.py``` qui s'appuie sur le LLM OpenSource ```llama-3.1-8b-instant``` ultra-rapides de Groq pour analyser les risques médicaux. 
Pour que l'analyse fonctionne, tu dois posséder une clé API valide.

Obtenir une clé API gratuite :
- Rendez-vous sur le Groq Cloud Console : https://console.groq.com/.
- Connectez-vous avec votre compte Google ou GitHub.
- Dans le menu latéral gauche, cliquez sur "API Keys".
- Cliquez sur le bouton "Create API Key".
- Donnez-lui un nom (ex: Blood_pressure_Project_IA) et copiez la clé générée.

Configurer la variable d'environnement :
Pour que le script ```medical_agent.py``` puisse lire la clé via ```os.getenv('GROQ_API_KEY')```, tu dois l'ajouter à ton fichier .env.

- À la racine du projet crée le fichier nommé .env.
- Ajoute la ligne suivante à l'intérieur : ```GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx```

## 6. Exécution du Pipeline (Ordre de lancement)

Pour que le flux de données soit correctement traité, ouvrez quatre terminaux différents et lancez les scripts dans l'ordre suivant :
```bash
# Excécute le Simulateur de données médicales
generator.py

# Démarre l'envoi des données patients simulées vers Kafka.
python producer.py

# Lance l'IA qui écoute Kafka et prédit les risques d'AVC.
python medical_agent.py

# Prépare la réception et l'indexation dans Elasticsearch.
python consummer.py
```
## 7. Accès aux Interfaces Graphiques : 

  ### Kafka UI
Une fois le pipeline en marche, vous pouvez surveiller le système via :
Kafka UI : http://localhost:8080 (pour voir les messages dans les topics).

- Cliquer sur ```Topics``` dans le menu de gauche.

- Puis Cliquer sur ```fhir-observations``` 

- Aller dans l'onglet ```Messages```

### ELASTIC : Kibana
Kibana : http://localhost:5601 (pour visualiser les dashboards et les alertes).

- Allez dans ```Management``` > ```Stack Management```

- Puis Cliquer sur ```Data Views``` sous la section *Kibana*

- Cliquez sur ```Create data view```

- Dans le champ *Name*, saisissez ```patients-alerts``` puis ```patients-alerts-*``` dans *Index pattern*

### Comment accéder au Dashboard pré-configuré

Une fois que les services sont lancés et que les données circulent, vous n'avez pas besoin de recréer les graphiques. Voici comment ouvrir le tableau de bord existant :

Accès direct via l'interface
1. Ouvrez votre navigateur sur [http://localhost:5601](http://localhost:5601).
2. Dans le menu latéral gauche, cliquez sur l'icône **Dashboard** (ou tapez "Dashboard" dans la barre de recherche en haut).
3. Dans la liste qui s'affiche, recherchez et cliquez sur le nom de votre dashboard ( `Patient Monitoring`).
4. Aperçu de tableau de bord
   
<img width="1260" height="804" alt="Capture d’écran 2026-01-29 184556" src="https://github.com/user-attachments/assets/147f20a4-8898-4e23-b46e-b2f9bb181932" />

<img width="1260" height="491" alt="Capture d’écran 2026-01-29 184803" src="https://github.com/user-attachments/assets/d13c3433-5335-4657-8db2-6b10a7285063" />

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
