import requests
import json

url = "https://localhost:8443/avro/weatherforecast"

headers = {
  'Authorization': 'Basic dmFncmFudDp2YWdyYW50'
}

response = requests.request("GET", url, headers=headers, verify=False)

print(json.loads(response.text))
