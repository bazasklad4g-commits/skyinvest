"""Платёжная настройка и бюджеты аккаунта. Только чтение."""
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2 import service_account

client = GoogleAdsClient(
    credentials=service_account.Credentials.from_service_account_file(
        ".secrets/gstar-sa.json", scopes=["https://www.googleapis.com/auth/adwords"]),
    developer_token="t8wOf5cvS7HV5V7gjHnH2w", login_customer_id="8522851042",
    version="v22", use_proto_plus=True)
ga = client.get_service("GoogleAdsService")

for label, query in [
    ("Платёжные настройки", """
        SELECT billing_setup.id, billing_setup.status, billing_setup.payments_account_info.payments_account_name
        FROM billing_setup"""),
    ("Бюджеты аккаунта", """
        SELECT account_budget.id, account_budget.status, account_budget.name,
               account_budget.proposed_spending_limit_micros,
               account_budget.approved_spending_limit_micros,
               account_budget.adjusted_spending_limit_micros
        FROM account_budget"""),
]:
    print(f"=== {label} ===")
    try:
        rows = list(ga.search(customer_id="3432200766", query=query))
        if not rows:
            print("  пусто")
        for row in rows:
            if label.startswith("Платёж"):
                b = row.billing_setup
                print(f"  id={b.id} статус {b.status.name} счёт «{b.payments_account_info.payments_account_name}»")
            else:
                a = row.account_budget
                limit = a.adjusted_spending_limit_micros or a.approved_spending_limit_micros
                print(f"  «{a.name}» статус {a.status.name}, лимит {limit/1_000_000 if limit else 'не задан'}")
    except Exception as err:
        print("  ошибка:", str(err)[:200].replace("\n", " "))
    print()
