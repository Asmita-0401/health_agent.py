from google import genai

client = genai.Client(api_key="AQ.Ab8RN6Jw7wB6pF-xZ8EjkoUrRxVIBOPZn4nKIHRi18F8FNoCjQ")

for model in client.models.list():
    print(model.name)