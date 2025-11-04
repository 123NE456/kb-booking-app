from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import csv
import os
from typing import Optional

app = FastAPI()

# --------------------
# TEMPLATES & STATIC
# --------------------
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --------------------
# CSV CONFIG
# --------------------
CSV_FILE = "reservations.csv"

# Crée le fichier CSV s'il n'existe pas et ajoute l'entête
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nom", "Téléphone", "Coiffure", "Date"])

# --------------------
# UTIL: simulation d'envoi d'email (pour tests)
# --------------------
def send_email_simulation(name: str, phone: str, hairstyle: str, date: str, dest_email: str = "contact@karenbraids.com"):
    """
    Simule l'envoi d'un e-mail : affiche dans la console le message que
    nous enverrions en production. Utile pour tester sans envoyer d'e-mails réels.
    """
    print("\n=== Simulation d'envoi d'email ===")
    print(f"À      : {dest_email}")
    print(f"Sujet  : Nouvelle réservation — {hairstyle}")
    print("Contenu:")
    print(f"  Nom     : {name}")
    print(f"  Téléphone: {phone}")
    print(f"  Coiffure : {hairstyle}")
    print(f"  Date     : {date}")
    print("=== Fin du mail simulé ===\n")

# --------------------
# ROUTES PAGES
# --------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request, message: Optional[str] = None):
    # Si tu veux afficher message côté template, passe 'message' (utilisé si tu retournes TemplateResponse)
    return templates.TemplateResponse("products.html", {"request": request, "message": message})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# --------------------
# ENDPOINTS RÉSERVATION
# --------------------

# 1) endpoint classique HTML (souvent pour redirection HTML)
@app.post("/book", response_class=HTMLResponse)
async def book(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    hairstyle: str = Form(...),
    date: str = Form(...)
):
    # Sauvegarde dans CSV
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, phone, hairstyle, date])

    # Simulation d'envoi d'email (print dans la console)
    send_email_simulation(name, phone, hairstyle, date)

    # On peut renvoyer un TemplateResponse avec un message si tu veux
    message = f"Réservation pour {hairstyle} envoyée ✅"
    return templates.TemplateResponse("products.html", {"request": request, "message": message})

# 2) endpoint JSON pour fetch (JS)
@app.post("/book-json")
async def book_json(
    name: str = Form(...),
    phone: str = Form(...),
    hairstyle: str = Form(...),
    date: str = Form(...)
):
    # Sauvegarde dans CSV
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, phone, hairstyle, date])

    # Simulation d'envoi d'email (print dans la console)
    send_email_simulation(name, phone, hairstyle, date)

    # Renvoie JSON pour que le fetch côté client affiche le message
    return JSONResponse({"message": f"Réservation pour {hairstyle} envoyée ✅"})




CONTACT_CSV = "messages.csv"
# Crée le fichier si inexistant
import os
if not os.path.exists(CONTACT_CSV):
    with open(CONTACT_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nom", "Email", "Sujet", "Message"])

@app.post("/contact")
async def contact_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    with open(CONTACT_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, email, subject, message])
    return templates.TemplateResponse("contact.html", {"request": request, "success": "Message envoyé ✅"})