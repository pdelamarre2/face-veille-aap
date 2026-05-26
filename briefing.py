import os
import resend
from datetime import datetime, date
import pytz

resend.api_key = os.environ["RESEND_API_KEY"]
EMAIL_TO = os.environ["EMAIL_TO"]

PARIS = pytz.timezone("Europe/Paris")
today = datetime.now(PARIS).date()

CONTACTS = [
    {"nom": "Serge Da Silva", "role": "President FACE 92", "tel": "06 84 32 15 75", "email": "serge.da-silva@laposte.fr"},
    {"nom": "Yoann Billon", "role": "Directeur AFPA Nanterre - O2R", "tel": "07 77 34 91 73", "email": ""},
    {"nom": "Isabelle Cassingena", "role": "Deleguee regionale IDF Fondation", "tel": "", "email": "i.cassingena@fondationface.org"},
    {"nom": "Elise Igalas", "role": "Referente Emploi CDD", "tel": "07 83 71 95 05", "email": "e.igalas@fondationface.org"},
    {"nom": "Salima Landais", "role": "Directrice FACE 94", "tel": "06 10 83 36 05", "email": "sa.landais@fondationface.org"},
    {"nom": "Ewens Perian", "role": "Activity - ActionS Retour Emploi", "tel": "06 58 62 32 05", "email": "eperian@agence-activity.fr"},
    {"nom": "Farid Medjoub", "role": "DDFE 92 / DRDFE", "tel": "", "email": "pref-drdfe-gestion@paris.gouv.fr"},
]

AGENDA = {
    "2026-05-18": [
        {"h": "Matin", "titre": "Tour des locaux seul avant l equipe", "lieu": "82 rue Paul Morin, Nanterre", "urgent": False},
        {"h": "Matin", "titre": "Reunion collective equipe (Elise, Mickael, Francois)", "lieu": "Nanterre", "urgent": False},
        {"h": "Aprem", "titre": "Entretiens individuels x3 - 45 min chacun", "lieu": "Nanterre", "urgent": False},
        {"h": "14h", "titre": "Arrivee Serge Da Silva - 30 min debrief", "lieu": "Nanterre", "urgent": False},
        {"h": "URGENT", "titre": "Appeler Yoann BILLON - AFPA Nanterre - projet O2R", "lieu": "07 77 34 91 73", "urgent": True},
    ],
    "2026-05-20": [
        {"h": "10h-17h", "titre": "Journee FRUP - Fondation FACE", "lieu": "Paris", "urgent": False},
        {"h": "Priorite", "titre": "IT : config PC + synchro Outlook/Google + Copilot", "lieu": "Fondation", "urgent": True},
        {"h": "Priorite", "titre": "Demander acces comptes 2025 + etat tresorerie", "lieu": "Isabelle Cassingena", "urgent": True},
    ],
    "2026-05-21": [
        {"h": "Journee", "titre": "Filage Eric Boucaret - Jour 1/2", "lieu": "Nanterre", "urgent": False},
        {"h": "Priorite", "titre": "Questions Eric : DRDFE 2025 ? O2R ? Rebond+ ? Comptes approuves ?", "lieu": "", "urgent": True},
        {"h": "Priorite", "titre": "Brief ActionS Retour Emploi - fichier suivi a rendre le 29/05", "lieu": "", "urgent": True},
    ],
    "2026-05-22": [
        {"h": "11h30", "titre": "Journee FACE Val-de-Marne - Salima Landais", "lieu": "29 rue Waldeck Rousseau, Choisy-le-Roi", "urgent": False},
    ],
    "2026-05-27": [
        {"h": "Journee", "titre": "Filage Eric Boucaret - Jour 2/2 (dernier)", "lieu": "Nanterre", "urgent": False},
        {"h": "ACTION", "titre": "Envoyer convocation CA", "lieu": "", "urgent": True},
    ],
    "2026-05-29": [
        {"h": "Deadline", "titre": "Fichier suivi ActionS Retour Emploi a remettre a Ewens Perian", "lieu": "eperian@agence-activity.fr", "urgent": True},
    ],
    "2026-06-03": [
        {"h": "18h", "titre": "Reunion emploi des jeunes - Prefecture 92", "lieu": "Prefecture Hauts-de-Seine", "urgent": False},
    ],
    "2026-06-08": [
        {"h": "10h", "titre": "Point Activity - ActionS Retour Emploi (Ewens Perian)", "lieu": "06 58 62 32 05", "urgent": True},
    ],
    "2026-06-11": [
        {"h": "MINUIT", "titre": "DEADLINE BOP 137 - Depot dossier DRDFE IDF", "lieu": "demarche.numerique.gouv.fr", "urgent": True},
    ],
    "2026-06-12": [
        {"h": "Matin", "titre": "Renouveler PAT GitHub face-cron-trigger (expire demain)", "lieu": "github.com/settings/tokens", "urgent": True},
    ],
}

DEADLINES = [
    {"date": "2026-05-27", "label": "Envoyer convocation au CA"},
    {"date": "2026-05-29", "label": "Fichier suivi ActionS Retour Emploi - Ewens Perian"},
    {"date": "2026-06-08", "label": "Point Activity 10h - ActionS Retour Emploi"},
    {"date": "2026-06-11", "label": "Depot BOP 137 DRDFE - 11 000 euros"},
    {"date": "2026-06-12", "label": "Renouveler PAT GitHub face-cron-trigger"},
]

today_str = today.strftime("%Y-%m-%d")
today_label = today.strftime("%A %d %B %Y").capitalize()
rdvs = AGENDA.get(today_str, [])
upcoming = []
for dl in DEADLINES:
    dl_date = date.fromisoformat(dl["date"])
    delta = (dl_date - today).days
    if 0 <= delta <= 7:
        upcoming.append({"label": dl["label"], "delta": delta})

ROUGE = "#dc2626"
BLEU = "#1e3a5f"
GRIS = "#6b7280"

def rdv_row(h, titre, lieu, urgent):
    color = ROUGE if urgent else BLEU
    prefix = "! " if urgent else ""
    lieu_str = f"<br><span style='font-size:12px;color:{GRIS}'>{lieu}</span>" if lieu else ""
    return f"<tr><td style='padding:7px 12px;font-size:12px;color:{GRIS};white-space:nowrap;vertical-align:top;width:70px'>{h}</td><td style='padding:7px 12px;font-size:14px;color:{color};font-weight:{'bold' if urgent else 'normal'}'>{prefix}{titre}{lieu_str}</td></tr>"

def contact_row(nom, role, tel, email):
    tel_str = f" - {tel}" if tel else ""
    email_str = f" - {email}" if email else ""
    return f"<tr><td style='padding:5px 12px;font-size:13px;color:#1e293b;width:160px'><b>{nom}</b></td><td style='padding:5px 12px;font-size:12px;color:{GRIS}'>{role}{tel_str}{email_str}</td></tr>"

rdv_rows = "".join([rdv_row(r["h"], r["titre"], r["lieu"], r["urgent"]) for r in rdvs])
if not rdv_rows:
    rdv_rows = "<tr><td colspan='2' style='padding:8px 12px;color:#9ca3af;font-style:italic'>Pas de RDV pre-programme aujourd hui</td></tr>"
contact_rows = "".join([contact_row(c["nom"], c["role"], c["tel"], c["email"]) for c in CONTACTS])
deadline_html = ""
if upcoming:
    items = ""
    for dl in upcoming:
        if dl["delta"] == 0: lbl = f"<b style='color:{ROUGE}'>AUJOURD HUI</b>"
        elif dl["delta"] == 1: lbl = "<b style='color:#d97706'>DEMAIN</b>"
        else: lbl = f"<span style='color:{GRIS}'>Dans {dl['delta']} jours</span>"
        items += f"<li style='margin-bottom:6px'>{lbl} - {dl['label']}</li>"
    deadline_html = f"<div style='margin-top:24px;background:#fef9c3;border-left:4px solid #ca8a04;padding:14px 18px;border-radius:4px'><div style='font-size:11px;color:#92400e;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px'>Deadlines proches</div><ul style='margin:0;padding-left:18px;font-size:13px;color:#1e293b'>{items}</ul></div>"

html = f"""<!DOCTYPE html><html><body style='margin:0;padding:0;background:#f1f5f9;font-family:Georgia,serif'>
<div style='max-width:600px;margin:32px auto;background:#fff;border-radius:6px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06)'>
<div style='background:{BLEU};padding:20px 28px'>
<div style='font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:0.15em;text-transform:uppercase'>FACE Paris Hauts-de-Seine</div>
<div style='font-size:20px;color:#fff;margin-top:4px'>Briefing - {today_label}</div>
</div>
<div style='padding:24px 28px'>
<div style='font-size:11px;color:{GRIS};letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px'>Agenda du jour</div>
<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse:collapse'>{rdv_rows}</table>
{deadline_html}
<div style='margin-top:28px'>
<div style='font-size:11px;color:{GRIS};letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px'>Contacts cles</div>
<table width='100%' cellspacing='0' cellpadding='0' style='border-collapse:collapse'>{contact_rows}</table>
</div>
<div style='margin-top:28px;padding-top:18px;border-top:1px solid #e2e8f0;font-size:12px;color:{GRIS}'>Veille AAP dans ton inbox - FACE Paris 92</div>
</div></div></body></html>"""

r = resend.Emails.send({"from": "onboarding@resend.dev", "to": [EMAIL_TO], "subject": f"Briefing {today_label}", "html": html})
print(f"Briefing envoye: {r}")
