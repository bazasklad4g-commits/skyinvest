"""Приглашения и пользователи аккаунта Ads. Только чтение."""
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")

for cid, label in (("3432200766", "рекламный аккаунт"), ("8522851042", "MCC_3G")):
    print(f"=== Ожидающие приглашения: {label} {cid} ===")
    try:
        rows = list(ga.search(customer_id=cid, query="""
            SELECT customer_user_access_invitation.invitation_id,
                   customer_user_access_invitation.email_address,
                   customer_user_access_invitation.access_role,
                   customer_user_access_invitation.invitation_status,
                   customer_user_access_invitation.creation_date_time
            FROM customer_user_access_invitation
        """))
        if not rows:
            print("  нет ожидающих приглашений")
        for row in rows:
            i = row.customer_user_access_invitation
            print(f"  {i.email_address}: {i.access_role.name}, {i.invitation_status.name}, {i.creation_date_time[:10]}")
    except Exception as err:
        print("  ", str(err)[:180].replace("\n", " "))
    print()
