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
      "emploi", "insertion", "inclusion", "discrimination",
      "chomage", "recrutement", "entreprise", "territoire",
      "handicap", "diversite", "egalite des chances", "jeunes",
      "formation", "RSA", "demandeur d emploi", "precarite",
      "solidarite", "mecenat", "partenariat entreprise",
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
                                                results.append({"source": "Aides-territoires", "title": title, "url": aid.get("url", ""), "deadline": aid.get("submission_deadline", "non precisee"), "summary": description[:300]})
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
              cards = soup.find_all("article") or soup.find_all(class_=lambda c: c and "card" in c.lower())
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
              cards = soup.find_all("article") or soup.find_all(class_=lambda c: c and "projet" in c.lower())
              for card in cards[:20]:
                            title_tag = card.find(["h2", "h3", "h4"])
                            link_tag = card.find("a", href=True)
                            if not title_tag:
                                              continue
                                          titl
