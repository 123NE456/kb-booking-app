from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import csv
import os
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import sqlite3
import datetime









# -------------------- LOAD ENV --------------------
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEST_EMAIL = os.getenv("DEST_EMAIL")  # Email admin

# -------------------- FASTAPI INIT --------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
DB_PATH = "database.db"

# -------------------- EMAIL UTIL --------------------
def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email envoyé à {to_email} ✅")
    except Exception as e:
        print("Erreur envoi email:", e)

# -------------------- STATIC PAGES --------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request, message: str | None = None):
    return templates.TemplateResponse("products.html", {"request": request, "message": message})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# -------------------- UTIL CHECK SLOT --------------------
def slot_taken(date: str, time: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM reservations WHERE date = ? AND time = ?", (date, time))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

# -------------------- VALID HOURS --------------------
WORK_HOURS = ["08:00", "09:00", "10:00", "11:00", "15:00", "16:00", "17:00"]

def valid_time(time: str) -> bool:
    return time in WORK_HOURS

# -------------------- RESERVATION --------------------
@app.post("/book")
async def book(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    hairstyle: str = Form(...),
    date: str = Form(...),
    time: str = Form(...)
):
    




    # Vérification date passée
    today = datetime.date.today()
    try:
        reservation_date = datetime.date.fromisoformat(date)
    except ValueError:
        return JSONResponse({"success": False, "error": "Format de date invalide. Utilisez AAAA-MM-JJ."})

    if reservation_date < today:
        return JSONResponse({"success": False, "error": "Impossible de réserver une date passée."})





    # Vérification horaire valide
    if not valid_time(time):
        return JSONResponse({"success": False, "error": "Horaire invalide. Choisissez un créneau valide."})

    # Vérification si slot déjà pris
    if slot_taken(date, time):
        return JSONResponse({"success": False, "error": f"Le créneau {date} {time} est déjà réservé."})

    # Enregistrement réservation
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reservations (name, phone, email, hairstyle, date, time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, email, hairstyle, date, time))
    conn.commit()
    conn.close()

    # Email admin
    send_email(
        DEST_EMAIL,
        f"Nouvelle réservation — {hairstyle}",
        f"""
Nouvelle réservation :
Nom : {name}
Téléphone : {phone}
Coiffure : {hairstyle}
Date : {date}
Heure : {time}
Email : {email}
"""
    )

    # Email client
    send_email(
        email,
        "Confirmation de réservation",
        f"""
Bonjour {name},

Votre réservation pour '{hairstyle}' le {date} à {time} a bien été confirmée ! ✅

Merci pour votre confiance.
"""
    )

    return JSONResponse({"success": True, "message": "Réservation confirmée !"})

# -------------------- CONTACT FORM --------------------
@app.post("/send-message", response_class=HTMLResponse)
def send_message(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO messages (name, email, subject, message)
        VALUES (?, ?, ?, ?)
    """, (name, email, subject, message))
    conn.commit()
    conn.close()

    return templates.TemplateResponse(
        "contact.html",
        {"request": request, "success": "Votre message a été envoyé avec succès !"}
    )
