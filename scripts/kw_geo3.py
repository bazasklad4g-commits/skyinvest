from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account
client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")
want = "IE AU NZ BE DK NO PT SA QA KW IN ZA SG MY GR HR CY FR".split()
codes = "','".join(want)
found = {}
for row in ga.search(customer_id="3432200766", query=f"""
    SELECT geo_target_constant.id, geo_target_constant.name, geo_target_constant.country_code
    FROM geo_target_constant
    WHERE geo_target_constant.country_code IN ('{codes}')
      AND geo_target_constant.target_type = 'Country'
"""):
    g = row.geo_target_constant
    found[g.country_code] = (g.id, g.name)
for code in want:
    if code in found:
        print(f"{code}={found[code][0]}", end="  ")
print()
print("не найдено:", [c for c in want if c not in found])
