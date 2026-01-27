import pandas as pd
import json
import os
import joblib
import time

from json import loads, dumps
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

# On appel notre agent IA afin d'inclure sa synthese dans le pipiline temps reel
from medical_agent import MedicalAgent
agent = MedicalAgent(api_key= os.getenv('GROQ_API_KEY'))

# On charge notre modele RandomForest deja entrainer depuis le joblib
MODEL_PATH = "C:\Master USPN\Cours M2 Big Data\DataScience Ecosysteme\projet blood pressure\outputs_bp\my_random_forest_avc.joblib"
pipeline_rf = joblib.load(MODEL_PATH)

os.environ['NO_PROXY'] = '127.0.0.1'

############################################
#    Data streaming                        #
#    Consommation de données depuis Kafka  #
############################################

consumer = KafkaConsumer(
    'fhir-observations',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

############################################

# Initialisation de Elasticsearch
es = Elasticsearch("http://127.0.0.1:9200", verify_certs=False, request_timeout=10)

############################################

# Cette fonction nous permettra de recuperer les donnees 
def extract_fhir_data(raw):
    """Extrait proprement les données du JSON FHIR"""

    data = {'name': raw.get('subject', {}).get('display', 'Inconnu'), 'date': raw.get('effectiveDateTime')}
    
    # Extensions fhir (Age, Sexe, Fumeur, Diabète)
    for ext in raw.get('extension', []):
        url = ext.get('url', '').lower()
        if 'age' in url: data['age'] = ext.get('valueInteger')
        elif 'gender' in url: data['sexe'] = ext.get('valueCode')
        elif 'smoker' in url: data['fumeur'] = ext.get('valueInteger')
        elif 'diabetes' in url:
            data['diabete'] = ext.get('valueCodeableConcept', {}).get('coding', [{}])[0].get('display', 'None').replace("Diabetes ", "")
    
    # Composants (Mesures)
    for comp in raw.get('component', []):
        code = comp['code']['coding'][0]['code']
        val = comp['valueQuantity']['value']
        mapping = {'8480-6': 'sys', '8462-4': 'dia', '2339-0': 'gluc', '2093-3': 'chol'}
        if code in mapping: data[mapping[code]] = val
            
    return data

# on initialise des listes de stockage
data_list_normal = []
display_list = []


############################################
#    Data streaming                        #
#    MINI ETL(Extract, Transform & Load)   #
############################################

print(f"Système démarré. Monitoring en cours...")

try:
    for message in consumer:
        f = extract_fhir_data(message.value)
        
        # EXTRACT
        features = {
            'Age': f.get('age', 0), 
            'Sexe': f.get('sexe', 'N/A'), 
            'Fumeur': int(f.get('fumeur', 0)),
            'Diabete': f.get('diabete', 'None'), 
            'Systolic': f.get('sys', 0), 
            'Diastolic': f.get('dia', 0),
            'Glucose': f.get('gluc', 0), 
            'Cholesterol': f.get('chol', 0),

        # Feature Engineering : de nouvelles variables(Flags) necessaires au modele de prediction
            'sys_high_flag': int(f.get('sys', 0) > 130), 
            'sys_low_flag': int(f.get('sys', 0) < 90),
            'dia_high_flag': int(f.get('dia', 0) > 80), 
            'dia_low_flag': int(f.get('dia', 0) < 60)
        }

        # TRANSFORM

        # Prédiction de la probabilite d'AVC
        prob_ia = pipeline_rf.predict_proba(pd.DataFrame([features]))[0][1]

        # On classifie les patients selon le Blood_Pressure ("Hypertendu" ; "Hypotendu" ; "Normal" )
        if features['Systolic'] > 130 or features['Diastolic'] > 80: Blood_pressure_type = "Hypertendu"
        elif features['Systolic'] < 90 or features['Diastolic'] < 60: Blood_pressure_type = "Hypotendu"
        else: Blood_pressure_type = "Normal"

        # LOAD
        # On charge nos donnees dans un dictionnaire
        record = {**features, 
                  'Date': f['date'], 
                  'Patient': f['name'],
                  'Blood_pressure_type' : Blood_pressure_type,
                  'AVC_Prediction_Prob': round(prob_ia, 3)}
        
        record['Target_Risk'] = "High Risk" if prob_ia > 0.5 else "Low Risk"
        
        record['IA_Synthesis'] = "R.A.S - Patient Sain"

        # ELasticsearch : Indexation de donnes

        if Blood_pressure_type == "Normal":
            data_list_normal.append(record)
        else:
            synthese = agent.diagnostic_generator(record) # Synthese en temps reel de l'agent IA
            record['IA_Synthesis'] = synthese
            try:
                # On convertit tout en types Python standards pour Elastic
                doc_es = {k: (float(v) if isinstance(v, (float, int)) else str(v)) for k, v in record.items()}
                es.index(index="patients-alerts", document=doc_es)
            except: pass 

        # Affichage Console
        display_list.append(record)
        os.system('cls' if os.name == 'nt' else 'clear')
        df_view = pd.DataFrame(display_list).tail(5)
        print("=== TABLEAU DE BORD PATIENTS (FLUX FHIR + IA) ===")
        print(f"Total traités: {len(display_list)} | Sains (Local): {len(data_list_normal)} | Alertes (Elastic): {len(display_list)-len(data_list_normal)}")
        print("-" * 140)
        print(df_view[['Patient', 'Age', 'Diabete', 'Cholesterol', 'Blood_pressure_type','AVC_Prediction_Prob', 'Target_Risk', 'IA_Synthesis']].tail(5).to_string(index=False))
        print("-" * 140)


except KeyboardInterrupt:
    if data_list_normal:
        df_normal = pd.DataFrame(data_list_normal)
        df_normal.to_json("patients_sains.json", orient = "records", indent=4, force_ascii=False)
        print("\n✅ Patients normaux sauvegardés au format json avec succès. Fin du programme !")