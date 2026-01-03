import pandas as pd
import json
import os

from kafka import KafkaConsumer



consumer = KafkaConsumer(
    'fhir-observations',
    bootstrap_servers = ['localhost:9092'],
    auto_offset_reset = 'earliest',
    value_deserializer = lambda x: json.loads(x.decode('utf-8'))
)

############################################
#    On fera un mini ETL dépuis la réception
#    des messages jusqu'au chargement
#    dans un DataFrame                               
############################################

data_list = []

print("--- RECEPTION DES DONNEES FHIR ENRICHIES ---")

try:
    for message in consumer:
        raw_data = message.value

        # Données de base
        patient_name = raw_data.get('subject', {}).get('display', 'Inconnu')
        obs_date = raw_data.get('effectiveDateTime')
        
        # EXTRACTION DES VARIABLES STABLES (Extensions FHIR)
        
        age = 0
        sexe = "N/A"
        fumeur = False
        diabete = "None"
        
        extensions = raw_data.get('extension', [])
        for ext in extensions:
            url = ext.get('url', '')
            if 'age' in url:
                age = ext.get('valueInteger')
            elif 'gender' in url:
                sexe = ext.get('valueCode')
            elif 'smoker' in url:
                fumeur = ext.get('valueBoolean')
            elif 'diabetes-status' in url:
                diabete = ext.get('valueCodeableConcept', {}).get('coding', [{}])[0].get('display', 'None')

        # EXTRACTION DES VARIABLES TEMPS RÉEL
        systolic = 0
        diastolic = 0
        glucose = 0
        cholesterol = 0 # Cette valeur sera extraite mais restera identique à chaque message

        for comp in raw_data.get('component', []):
            try:
                code = comp['code']['coding'][0]['code']
                val = comp['valueQuantity']['value']
                
                if code == '8480-6': systolic = val
                elif code == '8462-4': diastolic = val
                elif code == '2339-0': glucose = val
                elif code == '2093-3': cholesterol = val
            except (KeyError, IndexError):
                continue

        # scoring du risque d'AVC (sur 10)
        risk_score = 0
        
        # Tension Systolique
        if systolic > 180: risk_score += 4    
        elif systolic > 160: risk_score += 3  
        elif systolic > 140: risk_score += 2  
        elif systolic > 130: risk_score += 1
        
        # Diabète (Poids fort : max 2 pts)
        if "Type 1" in diabete: risk_score += 2
        elif "Type 2" in diabete: risk_score += 1.5
        
        if fumeur: risk_score += 1.5
        
        if age > 75: risk_score += 1.5
        elif age > 50: risk_score += 1
        
        if cholesterol > 2.4: risk_score += 1
        elif cholesterol > 2.0: risk_score += 0.5

        risk_score = min(10, risk_score)

        # Détermination du Label (pour la classification)
        if risk_score >= 6:
            label = "High Risk"
        else:
            label = "Low Risk"

        
        record = {
            'Date': obs_date,
            'Patient': patient_name,
            'Age': age,
            'Sexe': sexe,
            'Fumeur': fumeur,
            'Diabete': diabete,
            'Systolic': systolic,
            'Diastolic': diastolic,
            'Glucose': glucose,
            'Cholesterol': cholesterol,
            'AVC_Risk_Score': round(risk_score, 2), # Le score numérique
            'Target_Risk': label
        }
        data_list.append(record)
        
        
        df = pd.DataFrame(data_list)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=== TABLEAU DE BORD PATIENTS (FLUX FHIR) ===")
        print(f"Nombre total de mesures : {len(df)}")
        print("-" * 125)
        
        if not df.empty:
            # On affiche les 5 dernières lignes avec plus de colonnes
            cols_to_show = ['Date', 'Patient', 'Diabete', 'Age','Cholesterol','Glucose','Systolic', 'Diastolic', 'AVC_Risk_Score','Target_Risk' ]
            print(df[cols_to_show].tail(5).to_string(index=False))
            print("-" * 125)
            print(f"Moyenne Systolique globale: {df['Systolic'].mean():.1f} mmHg")

except KeyboardInterrupt:
    print("\nArrêt en cours... Sauvegarde des données...")
    if 'df' in locals() and not df.empty:
        df.to_csv("donnees_finales_completes.csv", index=False) 
        print("✅ Fichier 'donnees_finales_completes.csv' enregistré avec succès !")
        print(f"Total des lignes sauvegardées : {len(df)}")