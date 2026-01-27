import pandas as pd
import numpy as np
import random
import time
import json

from faker import Faker
from fhir.resources.organization import Organization
from fhir.resources.humanname import HumanName
from fhir.resources.patient import Patient
from datetime import date, datetime
from fhir.resources.observation import Observation
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.observation import ObservationComponent 


############################################

"""
Notre générateur génère une ressource FHIR LOINC des Observation simulant un bilan de santé pour le risque d'AVC.
        
Cette méthode calcule des constantes physiologiques (tension, glycémie, cholestérol) 
en appliquant des lois normales (Gauss) corrélées à l'âge et au statut diabétique 
du patient. Les données sont ensuite encapsulées dans un objet Observation conforme 
au standard FHIR, incluant des extensions pour les facteurs de risque (sexe, tabac) 
et des composants pour les mesures cliniques.

L'inclusion de variables métaboliques au-delà de la simple tension artérielle 
est cruciale pour permettre à l'algorithme d'IA de capturer le risque 
multifactoriel propre aux pathologies vasculaires. 
        
La sortie est un objet Observation conforme au standard HL7 FHIR R4, utilisant 
le système de codage LOINC pour les mesures et SNOMED-CT pour les diagnostics.

NB : Seul la tension artérielle et le glucode seront en temsp réel pour un patient
d'autant plus qu'un patient ne peut changer de sexe, age, cholesterol, statut diabétique, ect.. 
en un laps de temps d'ou le choix de ne pas mettre ces variable en temps réel.
"""
############################################

fake = Faker(["fr_FR"])

class PatientSimulator:
    def __init__(self):

        # On initie un patient en lui donnant un genre, nom, age et nous lui affectons un id
        self.gender = random.choice(["male", "female"])
        if self.gender == "male":
            self.p_name = fake.name_male()
        else:
            self.p_name = fake.name_female()
            
        self.p_id = fake.bothify(text="??_######", letters="ABCDEFGHIKLMNOPQRSTVXYZ")
        
        # On choisir la distribution triangulaire avec un mode de 65 ans pour modeliser l'age
        self.age = int(random.triangular(18, 95, 65)) 
        self.is_smoker = 1 if random.random() < 0.35 else 0
        
        # Probabilité de diabète
        prob_t2 = 0.30 if self.age > 45 else 0.1
        rand_diab = random.random()
        if rand_diab < 0.05:
            self.diabetes_type = "Type 1"
        elif rand_diab < (0.05 + prob_t2):
            self.diabetes_type = "Type 2"
        else:
            self.diabetes_type = "None"

        # CHOLESTÉROL STABLE : On le génère une seule fois pour un même patient
        mu_chol = 1.9 if self.age < 40 else 2.2
        self.fixed_cholesterol = round(random.gauss(mu_chol, 0.4), 2)
        self.fixed_cholesterol = max(1.0, min(4.5, self.fixed_cholesterol))

    def generate_fhir_observation(self):
        
        # Pour avoir des dates adaptee à tout systeme informatique
        now_iso = datetime.now().astimezone().isoformat() 

        # DONNÉES VARIABLES (Temps réel)
        mu_sys = 100 if self.age < 35 else (110 if self.age < 65 else 130)
        if self.diabetes_type != "None": 
            mu_sys += 10 
        
        # On modelise le blood pressure avec un loi normal(Gaussienne)
        systolic = int(random.gauss(mu_sys, 12))
        diastolic = int(systolic * 0.65 + random.gauss(0, 5))
        
        mu_gly = 165 if self.diabetes_type != "None" else 95
        glucose = round(random.gauss(mu_gly, 20), 1)

        # Sécurité pour les mesures variables
        systolic = max(80, min(220, systolic))
        diastolic = max(50, min(120, diastolic))
        glucose = max(40.0, glucose)
        
        diab_codes = {
            "Type 1": "46635009",
            "Type 2": "44054006",
            "None": "none"
        }

        observation_json = {
            "resourceType": "Observation",
            "id": f"blood-pressure-{random.getrandbits(16)}",
            "status": "final",
            "code": {
                "coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]
            },
            "subject": {
                "reference": f"Patient/{self.p_id}",
                "display": self.p_name
            },
            
            "effectiveDateTime": now_iso,
            
            "extension": [
                {"url": "http://example.org/gender", "valueCode": self.gender},
                {"url": "http://example.org/age", "valueInteger": self.age},
                {"url": "http://example.org/smoker-bit", "valueInteger": self.is_smoker},
                {
                    "url": "http://example.org/diabetes-status",
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "http://snomed.info/sct", 
                            "code": diab_codes[self.diabetes_type],
                            "display": f"Diabetes {self.diabetes_type}"
                        }]
                    }
                }
            ],
            
            "component": [
                {"code": {"coding": [{"code": "8480-6", "system": "http://loinc.org", "display": "Systolic"}]}, "valueQuantity": {"value": systolic, "unit": "mmHg"}},
                {"code": {"coding": [{"code": "8462-4", "system": "http://loinc.org", "display": "Diastolic"}]}, "valueQuantity": {"value": diastolic, "unit": "mmHg"}},
                {"code": {"coding": [{"code": "2339-0", "system": "http://loinc.org", "display": "Glucose"}]}, "valueQuantity": {"value": glucose, "unit": "mg/dL"}},
                {"code": {"coding": [{"code": "2093-3", "system": "http://loinc.org", "display": "Cholesterol"}]}, "valueQuantity": {"value": self.fixed_cholesterol, "unit": "g/L"}}
            ]
        }
        
        return observation_json
    
############################################

sim = PatientSimulator()
fhir_dict = sim.generate_fhir_observation()
print(json.dumps(fhir_dict, indent=2))

"""
 Nous avons mis en palce un SCORING MANUEL afin de labeliser les donnees :
 Logique metier : 
        risk_score = 0
        if systolic > 180: risk_score += 4
        elif systolic > 160: risk_score += 3
        elif systolic > 140: risk_score += 2
        elif systolic > 130: risk_score += 1
        
        if "Type 1" in diabete: risk_score += 2
        elif "Type 2" in diabete: risk_score += 1.5

        if fumeur: risk_score += 1.5

        if age > 75: risk_score += 1.5
        elif age > 50: risk_score += 1

        if cholesterol > 2.4: risk_score += 1
        elif cholesterol > 2.0: risk_score += 0.5

        risk_score = min(10, risk_score)
        'AVC_Risk_Score'= round(risk_score, 2),
        
        'Target_Risk' = "High Risk" if AVC_Risk_Score > 0.5 else "Low Risk"
"""