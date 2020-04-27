import requests
import json
import traceback


def get_price_from_id(part_id: str) -> str:
    try:
        # print("trying to get id: [" + part_id + "]")
        r = requests.get("https://api.warframe.market/v1/items/" + part_id + "/orders")
        if not r.ok:
            return "Failed to get " + part_id + ", not ok"

        data = r.json()
        # print(data["payload"])
        orders = data["payload"]["orders"]

        prices = []

        for o in orders:
            if o["platform"] != "pc":
                continue
            if o["order_type"] != "sell":
                continue
            if o["user"]["region"] != "en":
                continue
            if o["user"]["status"] != "ingame":
                continue

            prices.append(o["platinum"])

        prices.sort()

        p = map(lambda f: str(f), prices)
        s = ", ".join(p)
        return "Prices: " + s
    except:
        traceback.print_exc()
        return "Failed to get " + part_id
