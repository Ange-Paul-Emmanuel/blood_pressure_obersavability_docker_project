import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# CONTEXTE: Alerte médicale temps réel.

class MedicalAgent :
    def __init__(self, api_key):
        self.client = OpenAI(api_key= api_key,
                             base_url="https://api.groq.com/openai/v1")

    def diagnostic_generator(self, data) :
        prompt = f"""

        DATA: Patient {data['Patient']}, {data['Systolic']}/{data['Diastolic']} mmHg, 
        Glucose {data['Glucose']}, Risque AVC  de label {data['Target_Risk']} avec probabilité {data['AVC_Prediction_Prob']:.2%}.
        TACHE: Synthèse critique en 2 PHRASES MAXIMUM ! PAS PLUS !. Action immédiate si nécessaire.
        Un risque est éléévé que si {data['AVC_Prediction_Prob']:.2%} est supérieur ou égale à 50%
        
        RÈGLES DE SYNTHÈSE :
        1. Si la probabilité est >= 50%, le risque est CRITIQUE.
        2. Si la probabilité est < 50%, le risque est MODÉRÉ ou FAIBLE.
        3. TA RÉPONSE DOIT FAIRE 2 PHRASES MAXIMUM.
        4. Écris sur une seule ligne, sans sauts de ligne (\n), sans guillemets.
        5. Recommande une action médicale
        
        EXEMPLE DE STYLE :
        Le patient présente une tension de {data['Systolic']}/{data['Diastolic']} mmHg et un risque d'AVC de 62%, ce qui est jugé critique. Il est essentiel de prendre des mesures immédiates pour réduire ce risque, notamment en ajustant la médication et en recommandant une échographie cardiaque.
 
        """
        try :
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": "Tu es un cardiologue expert."},
                          {"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0,
                max_tokens=500
            )
            text =  response.choices[0].message.content.strip()
            text = text.replace("\n", " ")
            text = " ".join(text.split())
            text = text.strip('"').strip("'")

            return text 
        
        except :
            return "Analyse indisponible"