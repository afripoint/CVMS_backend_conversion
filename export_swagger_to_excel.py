import requests
import pandas as pd

# Replace with your Swagger/OpenAPI JSON endpoint
url = "http://localhost:8000/swagger.json"  # or /api/schema/?format=openapi for drf-spectacular

response = requests.get(url)
swagger = response.json()

rows = []

for path, methods in swagger.get('paths', {}).items():
    for method, operation in methods.items():
        # Sometimes operation might be a list instead of a dict
        if isinstance(operation, dict):
            summary = operation.get('summary', '')
            description = operation.get('description', '')
            tags = ", ".join(operation.get('tags', []))
            rows.append({
                'Method': method.upper(),
                'Endpoint': path,
                'Summary': summary,
                 'Description': description,
                'Tags': tags
            })
        else:
            # Skip or log unexpected format
            print(f"Skipping unexpected operation format for {method.upper()} {path}")

# Save to Excel
df = pd.DataFrame(rows)
df.to_excel('swagger_endpoints.xlsx', index=False)

print("✅ Export complete. File saved as 'swagger_endpoints.xlsx'")
