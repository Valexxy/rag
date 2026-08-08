"""
TESTING RAILWAY PROJECT ID & PROJECT TOKEN CONFIGURATION
"""

import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')

TOKEN_OR_ID = "eb39cc9d-444c-45e6-b2f6-a8413d2aaf0b"
GRAPHQL_URL = "https://backboard.railway.app/graphql/v2"

# Test 1: As Project ID with Bearer
q1 = f"""
query {{
  project(id: "{TOKEN_OR_ID}") {{
    id
    name
    services {{
      edges {{
        node {{
          id
          name
        }}
      }}
    }}
  }}
}}
"""

print("--- TEST 1: Project Query with Bearer ---")
r1 = requests.post(GRAPHQL_URL, json={"query": q1}, headers={"Authorization": f"Bearer {TOKEN_OR_ID}", "Content-Type": "application/json"}, timeout=10)
print(json.dumps(r1.json(), indent=2))

# Test 2: As projectToken header
print("\n--- TEST 2: projectToken Header ---")
r2 = requests.post(GRAPHQL_URL, json={"query": q1}, headers={"projectToken": TOKEN_OR_ID, "Content-Type": "application/json"}, timeout=10)
print(json.dumps(r2.json(), indent=2))
