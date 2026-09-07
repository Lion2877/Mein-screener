pythonimport pytz
from datetime import datetime
import requests
import yfinance as yf

# ==============================================================================
# 1. IHRE TELEGRAM-ZUGANGSDATEN (Hier Ihre echten Werte eintragen)
# ==============================================================================
TELEGRAM_TOKEN = 8681031361:AAHPa7nLq14_xre5zvOtLU7uvvpyvsa_Kv4
TELEGRAM_CHAT_ID = 6360891445

# ==============================================================================
# 2. TELEGRAM-PUSH-FUNKTION
# ==============================================================================
def send_telegram_alert(message):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"-> Telegram-Fehler: {response.text}")
    except Exception as e:
        print(f"-> Fehler beim Senden: {e}")

# ==============================================================================
# 3. ERWEITERTE AKTIENLISTE (DAX, MDAX & TECDAX)
# ==============================================================================
AKTIEN_LISTE = [
    # --- DAX 40 ---
    "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BMW.DE", "CON.DE", "1COV.DE",
    "DTG.DE", "DB1.DE", "DBK.DE", "DHL.DE", "DTE.DE", "EON.DE", "FRE.DE", "FME.DE",
    "HEI.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "PAH3.DE",
    "RWE.DE", "SAP.DE", "SRT3.DE", "SIE.DE", "SHL.DE", "SY1.DE", "TKA.DE", "VOW3.DE",
    "VNA.DE", "WCH.DE", "ZAL.DE",

    # --- MDAX ---
    "HNR1.DE", "LEG.DE", "KGX.DE", "CBK.DE", "HOT.DE", "LHA.DE", "EVK.DE", "BOSS.DE",
    "PBB.DE", "GXI.DE", "SDF.DE", "TAG.DE", "TEG.DE", "G1A.DE", "JUN3.DE", "FPE3.DE",
    "DOV.DE", "RHM.DE", "NDX1.DE", "WAF.DE", "B4B.DE", "DEQ.DE", "ENC.DE",

    # --- TecDAX ---
    "AFX.DE", "O2D.DE", "ETR.DE", "EVT.DE", "JEN.DE", "NEM.DE", "SOW.DE", "MOR.DE",
    "AIXA.DE", "UTDI.DE", "DRI.DE", "VAR1.DE", "SMHN.DE"
]

def run_my_screener():
    BERLIN_TZ = pytz.timezone("Europe/Berlin")
    now_berlin = datetime.now(BERLIN_TZ)
    
    # Prüfen, ob Wochenende ist (Samstag=5, Sonntag=6)
    if now_berlin.weekday() >= 5:
        print("Wochenende. Kein Scan erforderlich.")
        return

    print("Starte erweiterten Markt-Scan (DAX, MDAX, TecDAX)...")
    ticker_string = " ".join(AKTIEN_LISTE)
    daten = yf.download(tickers=ticker_string, period="1d", interval="1m", group_by='ticker', progress=False)
    
    for ticker in AKTIEN_LISTE:
        try:
            aktien_daten = daten[ticker]
            if aktien_daten.empty:
                continue
                
            letzter_kurs = aktien_daten['Close'].iloc[-1]
            eroeffnungs_kurs = aktien_daten['Open'].iloc[-1]
            
            prozent_aenderung = ((letzter_kurs - eroeffnungs_kurs) / eroeffnungs_kurs) * 100
            
            # Kriterium: Ausschlag von mehr als +3% oder weniger als -3%
            if prozent_aenderung >= 3.0 or prozent_aenderung <= -3.0:
                richtung = "📈 UP" if prozent_aenderung > 0 else "📉 DOWN"
                nachricht = f"🚨 SCREENER-SIGNAL!\nAktie: {ticker}\nKurs: {letzter_kurs:.2f} €\nBewegung: {richtung} ({prozent_aenderung:.2f}%)"
                send_telegram_alert(nachricht)
                
        except Exception as e:
            continue
            
    print("Scan beendet.")

if __name__ == "__main__":
    run_my_screener()
