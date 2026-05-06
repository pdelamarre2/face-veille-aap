import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import resend

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
EMAIL_TO       = os.environ["EMAIL_TO"]
EMAIL_FROM     = "onboarding@resend.dev"

resend.api_key = RESEND_API_KEY

KEYWORDS = [
    # Emploi & insertion
    "emploi", "insertion", "recrutement", "chomage", "demandeur emploi",
    "eloigne emploi", "retour emploi", "parcours emploi", "insertion professionnelle",
    # Seniors (Grande Cause FACE 2024-2025)
    "senior", "seniors", "emploi senior", "45 ans", "diversite intergenerationnelle",
    "seconde carriere", "age",
    # Jeunes & education
    "jeunes", "jeune", "orientation", "alternance", "apprentissage", "stage",
    "mentorat", "quartier", "QPV", "egalite chances",
    # Discrimination & diversite
    "discrimination", "diversite", "egalite", "RSE", "inclusion", "handicap",
    # Publics specifiques FACE
    "refugie", "femme", "violence", "precaire", "precarite", "acces aux droits",
    "illettrisme", "numerique", "exclusion", "pauvrete",
    # Entreprises & mecenat
    "mecenat", "mecenat competences", "entreprises engagees", "partenariat entreprise",
    # Transition ecologique solidaire (4e axe FACE)
    "transition ecologique", "ecologie solidaire",
    # Territoire & collectivites
    "territoire", "territorial", "collectivite", "Hauts-de-Seine", "Seine-Saint-Denis",
]

def is_relevant(text):
    t = text.lower()
    return any(kw in t for kw in KEYWORDS)

def fetch_aides_territoires():
    print("Aides-territoires...")
    results = []
    url = "https://aides-territoires.beta.gouv.fr/api/aids/"
    since = (datetime.now() - timedelta(hours=48)).strftime("%Y-%m-%d")
    params = {"format": "json", "perimeter": "ile-de-france-26", "date_published__gte": since, "limit": 50}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for aid in data.get("results", []):
            title = aid.get("name", "")
            description = aid.get("description", "")
            if is_relevant(title + " " + description):
                results.append({
                    "source": "Aides-territoires",
                    "title": title,
                    "url": aid.get("url", ""),
                    "deadline": aid.get("submission_deadline", "non precisee"),
                    "summary": description[:300]
                })
    except Exception as e:
        print(f"  Erreur: {e}")
    print(f"  {len(results)} trouves")
    return results

def fetch_fondation_de_france():
    print("Fondation de France...")
    results = []
    url = "https://www.fondationdefrance.org/nos-actualites/appels-a-projets/"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article")
        for card in cards[:20]:
            title_tag = card.find(["h2", "h3", "h4"])
            link_tag = card.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = "https://www.fondationdefrance.org" + link
            desc = card.get_text(" ", strip=True)
            if is_relevant(title + " " + desc):
                results.append({"source": "Fondation de France", "title": title, "url": link, "deadline": "voir le lien", "summary": desc[:300]})
    except Exception as e:
        print(f"  Erreur: {e}")
    print(f"  {len(results)} trouves")
    return results

def fetch_malakoff_humanis():
    print("Malakoff Humanis...")
    results = []
    url = "https://fondation.malakoffhumanis.com/nos-actions/appels-a-projets/"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article")
        for card in cards[:20]:
            title_tag = card.find(["h2", "h3", "h4"])
            link_tag = card.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = "https://fondation.malakoffhumanis.com" + link
            desc = card.get_text(" ", strip=True)
            if is_relevant(title + " " + desc):
                results.append({"source": "Malakoff Humanis", "title": title, "url": link, "deadline": "voir le lien", "summary": desc[:300]})
    except Exception as e:
        print(f"  Erreur: {e}")
    print(f"  {len(results)} trouves")
    return results

def fetch_banque_territoires():
    print("Banque des Territoires...")
    results = []
    url = "https://www.banquedesterritoires.fr/appels-a-projets-et-manifestations-d-interet"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article")
        for card in cards[:20]:
            title_tag = card.find(["h2", "h3", "h4"])
            link_tag = card.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = "https://www.banquedesterritoires.fr" + link
            desc = card.get_text(" ", strip=True)
            if is_relevant(title + " " + desc):
                results.append({"source": "Banque des Territoires", "title": title, "url": link, "deadline": "voir le lien", "summary": desc[:300]})
    except Exception as e:
        print(f"  Erreur: {e}")
    print(f"  {len(results)} trouves")
    return results

def build_email_html(aaps):
    today = datetime.now().strftime("%d %B %Y")
    if not aaps:
        return f"<h2>Veille AAP FACE</h2><p>{today}</p><p>Aucun AAP pertinent aujourd'hui.</p>"
    cards_html = ""
    for aap in aaps:
        cards_html += f'<div style="border-left:4px solid #1a56db;padding:12px 16px;margin-bottom:20px;background:#f8faff;"><p style="margin:0 0 4px;font-size:12px;color:#666;">{aap["source"]}</p><h3 style="margin:0 0 6px;font-size:16px;"><a href="{aap["url"]}" style="color:#1a56db;text-decoration:none;">{aap["title"]}</a></h3><p style="margin:0 0 6px;font-size:13px;">{aap["summary"]}</p><p style="margin:0;font-size:12px;color:#888;">Date limite : {aap["deadline"]}</p></div>'
    return f'<div style="font-family:Arial,sans-serif;max-width:650px;margin:auto;padding:24px;"><h2 style="color:#1a56db;">Veille AAP - FACE Paris Hauts-de-Seine</h2><p style="color:#666;">{today} - {len(aaps)} AAP pertinent(s)</p>{cards_html}</div>'

def send_email(aaps):
    subject = f"Veille AAP FACE - {len(aaps)} resultat(s) - {datetime.now().strftime('%d/%m/%Y')}" if aaps else f"Veille AAP FACE - RAS - {datetime.now().strftime('%d/%m/%Y')}"
    print(f"Envoi email ({len(aaps)} AAP)...")
    resend.Emails.send({"from": EMAIL_FROM, "to": [EMAIL_TO], "subject": subject, "html": build_email_html(aaps)})
    print("Email envoye.")

if __name__ == "__main__":
    print(f"\n=== Veille AAP - {datetime.now().strftime('%d/%m/%Y %H:%M')} ===\n")
    all_aaps = []
    all_aaps.extend(fetch_aides_territoires())
    all_aaps.extend(fetch_fondation_de_france())
    all_aaps.extend(fetch_malakoff_humanis())
    all_aaps.extend(fetch_banque_territoires())
    print(f"\nTotal : {len(all_aaps)} AAP pertinents\n")
    send_email(all_aaps)
    print("\nTermine.")
