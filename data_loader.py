import requests
import pandas as pd
import time

CSV_PATH = "stock.csv"
usd_cache = {"value": 41.7, "timestamp": 0}

def get_usd_rate():
    """
    Получает курс USD к UAH через ПриватБанк (курс продажи) с кэшем
    """
    if time.time() - usd_cache["timestamp"] < 3600:
        return usd_cache["value"]

    try:
        response = requests.get("https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5", timeout=5)
        data = response.json()
        for item in data:
            if item["ccy"] == "USD":
                usd_cache["value"] = float(item["sale"])
                usd_cache["timestamp"] = time.time()
                return usd_cache["value"]
    except Exception:
        pass
    return usd_cache["value"]

def load_data():
    df = pd.read_csv(CSV_PATH, delimiter=";", encoding="utf-8")
    df.columns = df.columns.str.strip()
    df["Розничная"] = (
        df["Розничная"]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    rate = get_usd_rate()
    df["Ціна в грн"] = (df["Розничная"] * rate).round().astype(int)
    return df[["Наименование", "Серийные номера", "Розничная", "Ціна в грн"]]

def search_model(query):
    df = load_data()
    query_words = query.lower().strip().split()

    def is_strict_match(name):
        name_words = name.lower().strip().split()

        if name_words[:len(query_words)] != query_words:
            return False

        # Если запрос короче, не включаем Pro/Plus/Max как продолжение
        if len(name_words) > len(query_words):
            forbidden = {"pro", "plus", "max"}
            if name_words[len(query_words)] in forbidden:
                return False

        return True

    matched = df[df["Наименование"].apply(is_strict_match)]
    return matched.head(10).to_dict(orient="records")
