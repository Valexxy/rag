import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')

RAILWAY_TOKEN = "6555663e-48e1-49c9-a7d0-3ff9244287c1"
GRAPHQL_URL = "https://backboard.railway.app/graphql/v2"
HEADERS = {"Authorization": f"Bearer {RAILWAY_TOKEN}", "Content-Type": "application/json"}

query_me = """
query {
  me {
    id
    name
    email
    workspaces {
      id
      name
    }
  }
}
"""

r = requests.post(GRAPHQL_URL, json={"query": query_me}, headers=HEADERS, timeout=10)
print(json.dumps(r.json(), indent=2))
