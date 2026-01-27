from kafka.admin import KafkaAdminClient

admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092", 
    client_id='test'
)

topic_name = "fhir-observations"

try:
    # On supprime le topic
    admin_client.delete_topics(topics=[topic_name])
    print(f"Topic {topic_name} supprimé.")
except Exception as e:
    print(f"Erreur ou topic inexistant : {e}")
