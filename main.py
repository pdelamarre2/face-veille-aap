import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import resend

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
EMAIL_TO       = os.environ["EMAIL_TO"]
EMAIL_FROM     = "onboarding@resend.dev"

resend.api_key = RESEND_API_KEY
source_errors = {}

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
    # Transition ecologique solidaire
    "transition ecologique", "ecologie solidaire",
    # Territoire
    "territoire", "territorial", "collectivite",
]


NEGATIVE_KEYWORDS = [
    "feader", "infrastructure routiere", "infrastructure agricole",
    "facebook.com", "twitter.com", "x.com", "partager sur",
    "partagez sur", "suivez-nous", "newsletter",
    "article de presse", "communique de presse", "revue de presse",
    "festival", "concert", "spectacle",
]

def is_relevant(text):
    t = text.lower()
    if any(kw in t for kw in NEGATIVE_KEYWORDS):
        return False
    return any(kw in t for kw in KEYWORDS)

def scrape_generic(url, source_name, base_url=""):
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; face-veille/2.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article") or soup.find_all(class_=lambda c: c and any(x in c.lower() for x in ["card", "projet", "appel", "item", "result"]))
        if not cards:
            cards = soup.find_all("li", class_=True)
        for card in cards[:25]:
            title_tag = card.find(["h2", "h3", "h4", "h5"])
            link_tag = card.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = base_url + link
            desc = card.get_text(" ", strip=True)
            if is_relevant(title + " " + desc):
                results.append({"source": source_name, "title": title, "url": link, "deadline": "voir le lien", "summary": desc[:300]})
    except Exception as e:
        print(f"  Erreur {source_name}: {e}")
    print(f"  {source_name}: {len(results)} trouves")
    return results

def fetch_aides_territoires():
    print("Aides-territoires...")
    results = []
    url = "https://aides-territoires.beta.gouv.fr/api/aids/"
    since = (datetime.now() - timedelta(hours=48)).strftime("%Y-%m-%d")
    params = {"format": "json", "perimeter": "ile-de-france-26", "date_published__gte": since, "limit": 50}
    try:
        at_token = os.environ.get("AIDES_TERRITOIRES_TOKEN", "")
        at_headers = {"Authorization": "Token " + at_token} if at_token else {}
        resp = requests.get(url, params=params, headers=at_headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for aid in data.get("results", []):
            title = aid.get("name", "")
            description = aid.get("description", "")
            if is_relevant(title + " " + description):
                results.append({"source": "Aides-territoires", "title": title, "url": aid.get("url", ""), "deadline": aid.get("submission_deadline", "non precisee"), "summary": description[:300]})
    except Exception as e:
        print(f"  Erreur: {e}")
    print(f"  Aides-territoires: {len(results)} trouves")
    return results

def fetch_region_idf():
    print("Region IDF...")
    results = []
    url = "https://www.iledefrance.fr/aides-et-appels-a-projets"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=True)
        seen = set()
        for link in links:
            href = link["href"]
            if "/aides-et-appels-a-projets/" in href and href not in seen:
                seen.add(href)
                title = link.get_text(strip=True)
                full_url = "https://www.iledefrance.fr" + href if href.startswith("/") else href
                if title and is_relevant(title):
                    results.append({"source": "Region IDF", "title": title, "url": full_url, "deadline": "voir le lien", "summary": title})
    except Exception as e:
        print(f"  Erreur Region IDF: {e}")
    print(f"  Region IDF: {len(results)} trouves")
    return results

def fetch_mairie_paris():
    print("Mairie de Paris...")
    results = []
    url = "https://www.paris.fr/pages/repondre-a-un-appel-a-projets-5412"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.find_all(["h2", "h3", "h4"]):
            title = tag.get_text(strip=True)
            link_tag = tag.find("a", href=True) or tag.find_next("a", href=True)
            link = link_tag["href"] if link_tag else url
            if link.startswith("/"):
                link = "https://www.paris.fr" + link
            if title and len(title) > 10 and is_relevant(title):
                results.append({"source": "Mairie de Paris", "title": title, "url": link, "deadline": "voir le lien", "summary": title})
    except Exception as e:
        print(f"  Erreur Mairie Paris: {e}")
    print(f"  Mairie de Paris: {len(results)} trouves")
    return results

def fetch_fondation_de_france():
    return scrape_generic("https://www.fondationdefrance.org/fr/appels-a-projets", "Fondation de France", "https://www.fondationdefrance.org")

def fetch_malakoff_humanis():
    return scrape_generic("https://fondationhandicap.malakoffhumanis.com/", "Malakoff Humanis", "https://fondationhandicap.malakoffhumanis.com")

def fetch_banque_territoires():
    return scrape_generic("https://www.banquedesterritoires.fr/france-2030/appels-projets-en-cours", "Banque des Territoires", "https://www.banquedesterritoires.fr")

def fetch_fondation_abbe_pierre():
    return scrape_generic("https://www.fondation-abbe-pierre.fr/nos-actions/soutenir-financer-et-fonder-des-projets", "Fondation Abbe Pierre", "https://www.fondation-abbe-pierre.fr")

def fetch_fondation_ag2r():
    return scrape_generic("https://www.ag2rlamondiale.fr/fondation-d-entreprise/votre-projet", "Fondation AG2R La Mondiale", "https://www.ag2rlamondiale.fr")

def fetch_fondation_sncf():
    return scrape_generic("https://www.fondation-sncf.org/fr/nos-appels-a-projets/", "Fondation SNCF", "https://www.fondation-sncf.org")

def fetch_fondation_mozaik():
    return scrape_generic("https://www.fondation-mozaik.org/appels-a-projets/", "Fondation Mozaik", "https://www.fondation-mozaik.org")

def fetch_associations_gouv():
    return scrape_generic("https://associations.gouv.fr/appels-projets", "Associations.gouv.fr", "https://associations.gouv.fr")

def build_email_html(aaps):
    today = datetime.now().strftime("%d %B %Y")
    if not aaps:
        return f"<h2>Veille AAP FACE</h2><p>{today}</p><p>Aucun AAP pertinent aujourd'hui.</p>"
    cards_html = ""
    for aap in aaps:
        cards_html += f'<div style="border-left:4px solid #1a56db;padding:12px 16px;margin-bottom:20px;background:#f8faff;"><p style="margin:0 0 4px;font-size:12px;color:#666;">{aap["source"]}</p><h3 style="margin:0 0 6px;font-size:16px;"><a href="{aap["url"]}" style="color:#1a56db;text-decoration:none;">{aap["title"]}</a></h3><p style="margin:0 0 6px;font-size:13px;">{aap["summary"]}</p><p style="margin:0;font-size:12px;color:#888;">Date limite : {aap["deadline"]}</p></div>'
    return f'<div style="font-family:Arial,sans-serif;max-width:650px;margin:auto;padding:24px;"><h2 style="color:#1a56db;">Veille AAP - FACE Paris Hauts-de-Seine</h2><p style="color:#666;">{today} - {len(aaps)} AAP pertinent(s)</p>{cards_html}<hr style="margin-top:32px;border:none;border-top:1px solid #eee;"><p style="font-size:11px;color:#aaa;">Sources : Aides-territoires ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Region IDF ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Mairie de Paris ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Fondation de France ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Malakoff Humanis ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Banque des Territoires ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Fondation Abbe Pierre ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· AG2R La Mondiale ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Fondation SNCF ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Fondation Mozaik ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ· Associations.gouv.fr</p></div>'


def fetch_drieets_idf():
    print("DRIEETS IDF...")
    results = []
    url = "https://drieets.ile-de-france.gouv.fr/les-actions/appels-a-projets-et-a-manifestation-d-interet"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=True)
        seen = set()
        for link in links:
            title = link.get_text(strip=True)
            href = link["href"]
            if href.startswith("/"):
                href = "https://drieets.ile-de-france.gouv.fr" + href
            if title and href not in seen and is_relevant(title):
                seen.add(href)
                results.append({"source": "DRIEETS IDF", "title": title, "url": href, "deadline": "voir le lien", "summary": title})
    except Exception as e:
        print(f"  Erreur DRIEETS IDF: {e}")
        source_errors["DRIEETS IDF"] = str(e)
    print(f"  DRIEETS IDF: {len(results)} trouves")
    return results


def fetch_cd92():
    print("CD92 Hauts-de-Seine...")
    results = []
    url = "https://www.hauts-de-seine.fr/les-aides/aides-aux-associations"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article") or soup.find_all(class_=lambda c: c and any(x in c.lower() for x in ["card", "aide", "item"]))
        if not cards:
            cards = soup.find_all("li", class_=True)
        for card in cards[:30]:
            title_tag = card.find(["h2", "h3", "h4"])
            link_tag = card.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = link_tag["href"] if link_tag else url
            if href.startswith("/"):
                href = "https://www.hauts-de-seine.fr" + href
            desc = card.get_text(" ", strip=True)
            if is_relevant(title + " " + desc):
                results.append({"source": "CD92", "title": title, "url": href, "deadline": "voir le lien", "summary": desc[:300]})
    except Exception as e:
        print(f"  Erreur CD92: {e}")
        source_errors["CD92"] = str(e)
    print(f"  CD92: {len(results)} trouves")
    return results


def fetch_fondation_orange():
    print("Fondation Orange...")
    results = []
    url = "https://www.fondationorange.com/fr/le-calendrier-des-appels-projets"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.find_all(["h2", "h3", "h4"]):
            title = tag.get_text(strip=True)
            link_tag = tag.find("a", href=True) or tag.find_next("a", href=True)
            href = link_tag["href"] if link_tag else url
            if href.startswith("/"):
                href = "https://www.fondationorange.com" + href
            if title and is_relevant(title):
                results.append({"source": "Fondation Orange", "title": title, "url": href, "deadline": "voir le lien", "summary": title})
    except Exception as e:
        print(f"  Erreur Fondation Orange: {e}")
        source_errors["Fondation Orange"] = str(e)
    print(f"  Fondation Orange: {len(results)} trouves")
    return results


def fetch_fondation_ceidf():
    print("Fondation CEIDF...")
    results = []
    url = "https://www.fondation-ceidf.fr/nos-appels-a-projets/"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article") or soup.find_all(class_=lambda c: c and any(x in c.lower() for x in ["card", "projet", "appel"]))
        for card in cards[:20]:
            title_tag = card.find(["h2", "h3"])
            link_tag = card.find("a", href=True)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = link_tag["href"] if link_tag else url
            if href.startswith("/"):
                href = "https://www.fondation-ceidf.fr" + href
            desc = card.get_text(" ", strip=True)
            if is_relevant(title + " " + desc):
                results.append({"source": "Fondation CEIDF", "title": title, "url": href, "deadline": "voir le lien", "summary": desc[:300]})
    except Exception as e:
        print(f"  Erreur Fondation CEIDF: {e}")
        source_errors["Fondation CEIDF"] = str(e)
    print(f"  Fondation CEIDF: {len(results)} trouves")
    return results


def fetch_fdva92():
    results = []
    url = "https://www.hauts-de-seine.gouv.fr/Actions-de-l-Etat/Jeunesse-sport/Aides-et-subventions"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            if is_relevant(text) or any(k in text.lower() for k in ["fdva", "subvention", "appel", "association"]):
                href = a["href"]
                if href.startswith("/"):
                    href = "https://www.hauts-de-seine.gouv.fr" + href
                if href.startswith("http") and text:
                    results.append({"source": "FDVA 92 / Prefecture", "title": text, "url": href, "deadline": "voir le lien", "summary": text})
        results = [r for r in results if is_relevant(r["title"])]
    except Exception as e:
        print(f"  Erreur FDVA 92: {e}")
        source_errors["FDVA 92"] = str(e)
    print(f"  FDVA 92: {len(results)} trouves")
    return results

def fetch_fondation_edf():
    return scrape_generic("https://fondation.edf.com/deposez-un-projet/", "Fondation EDF", "https://fondation.edf.com")

def fetch_fondation_totalenergies():
    return scrape_generic("https://fondation.totalenergies.com/fr/appel-a-projets-2026", "Fondation TotalEnergies", "https://fondation.totalenergies.com")

def send_email(aaps):
    subject = f"Veille AAP FACE - {len(aaps)} resultat(s) - {datetime.now().strftime('%d/%m/%Y')}" if aaps else f"Veille AAP FACE - RAS - {datetime.now().strftime('%d/%m/%Y')}"
    print(f"Envoi email ({len(aaps)} AAP)...")
    resend.Emails.send({"from": EMAIL_FROM, "to": [EMAIL_TO], "subject": subject, "html": build_email_html(aaps)})
    print("Email envoye.")

if __name__ == "__main__":
    print(f"\n=== Veille AAP FACE - {datetime.now().strftime('%d/%m/%Y %H:%M')} ===\n")
    all_aaps = []
    all_aaps.extend(fetch_aides_territoires())
    all_aaps.extend(fetch_region_idf())
    all_aaps.extend(fetch_mairie_paris())
    all_aaps.extend(fetch_fondation_de_france())
    all_aaps.extend(fetch_malakoff_humanis())
    all_aaps.extend(fetch_banque_territoires())
    all_aaps.extend(fetch_fondation_abbe_pierre())
    all_aaps.extend(fetch_fondation_ag2r())
    all_aaps.extend(fetch_fondation_sncf())
    all_aaps.extend(fetch_fondation_mozaik())
    all_aaps.extend(fetch_associations_gouv())
    all_aaps.extend(fetch_drieets_idf())
    all_aaps.extend(fetch_cd92())
    all_aaps.extend(fetch_fondation_orange())
    all_aaps.extend(fetch_fondation_ceidf())
    all_aaps.extend(fetch_fdva92())
    all_aaps.extend(fetch_fondation_edf())
    all_aaps.extend(fetch_fondation_totalenergies())
    print(f"\nTotal : {len(all_aaps)} AAP pertinents\n")
    send_email(all_aaps)
    print("\nTermine.")
