import json
import time
import random

from datetime import datetime, date
from kafka import KafkaProducer
from generator import PatientSimulator 

############################################

def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.astimezone().isoformat()
    raise TypeError(f"Type {type(obj)} non sérialisable")

############################################

producer  = KafkaProducer(
    bootstrap_servers = ['localhost:9092'],
    value_serializer = lambda v : json.dumps(v, default=json_serializer).encode('utf-8')
)

############################################

def data_streaming():
    print("Démarrage du flux de données vers Kafka...")

    # On Créer les 10 patients stables une seule fois
    liste_patients = [PatientSimulator() for _ in range(10)]
    print(f"{len(liste_patients)} patients initialisés avec données stables.")

    try:
        while True:
            
            patient_choisi = random.choice(liste_patients)

            data = patient_choisi.generate_fhir_observation()
            
            # Envoi vers Kafka
            producer.send('fhir-observations', data)

            # Affichage console pour vérification
            print(f"Envoyé : {data['subject']['display']} | ID: {data['id']}")
            
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nArrêt du flux !")   
    finally:
        producer.close()

if __name__ == "__main__":
    data_streaming()
