import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FF_XML_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"CSV_PATH = "ftmo_news.csv"
UTC = timezone.utc

def fetch_xml():
    resp = requests.get(FF_XML_URL, timeout=10)
    resp.raise_for_status()
    return resp.content

def parse_events(xml_bytes):
    root = ET.fromstring(xml_bytes)
    events = []

    for item in root.findall(".//event"):
        title   = (item.findtext("title") or "").strip()
        country = (item.findtext("country") or "").strip()
        impact  = (item.findtext("impact") or "").strip()
        date    = (item.findtext("date") or "").strip()
        time    = (item.findtext("time") or "").strip()

        if country != "USD":
            continue
        if "High" not in impact:
            continue
        if not date or not time:
            continue

        try:
            dt_str = f"{date} {time}"
            dt = datetime.strptime(dt_str, "%b %d, %Y %I:%M%p")
            dt = dt.replace(tzinfo=UTC)
        except Exception:
            continue

        dt_fmt = dt.strftime("%Y-%m-%d %H:%M")

        events.append({
            "datetime": dt_fmt,
            "currency": country,
            "impact": "HIGH",
            "title": title
        })

    return events

def write_csv(events):
    lines = []
    lines.append("# datetime;currency;impact;event")
    for ev in sorted(events, key=lambda x: x["datetime"]):
        line = f'{ev["datetime"]};{ev["currency"]};{ev["impact"]};{ev["title"]}'
        lines.append(line)

    csv_content = "\n".join(lines) + "\n"

    with open(CSV_PATH, "w", encoding="utf-8") as f:
        f.write(csv_content)

def main():
    xml_bytes = fetch_xml()
    events = parse_events(xml_bytes)
    write_csv(events)
    print(f"Aggiornato {CSV_PATH} con {len(events)} eventi USD HIGH IMPACT.")

if __name__ == "__main__":
    main()
