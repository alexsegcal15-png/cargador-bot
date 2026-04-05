import requests
import time
import threading

# --- TUS DATOS CONFIGURADOS ---
OCM_KEY = "41748d03-7bff-438d-bb82-f35c087ad6df"
TELEGRAM_TOKEN = "8584477801:AAFN7yUIl6Djaxb2EsEv_M-BQqfRDNTjbWw"
CHAT_ID = 7762201229  # Asegúrate de que sea un número

CARGADORES = {
    "202583": "Matzem",
    "274829": "Ajuntament",
    "202582": "Policia"
}

# --- FUNCIONES DE AYUDA ---

def obtener_estado(poi_id):
    """Consulta la API y devuelve el estado de un cargador."""
    try:
        url = f"https://api.openchargemap.io/v3/poi/?output=json&poiid={poi_id}&key={OCM_KEY}"
        r = requests.get(url, timeout=10)
        datos = r.json()
        if datos and len(datos) > 0:
            return datos[0]['Connections'][0]['StatusType']['Title']
    except:
        return "Error"
    return "Unknown"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje})

# --- LÓGICA DEL COMANDO /CHECK ---

def revisar_mensajes():
    """Esta función corre en paralelo buscando el comando /check."""
    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_update_id + 1}"
            updates = requests.get(url, timeout=10).json()
            
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    texto = update["message"]["text"]
                    
                    if texto == "/check":
                        print("Recibido comando /check. Consultando...")
                        informe = "📊 *Estado actual:*\n"
                        for cid, nombre in CARGADORES.items():
                            estado = obtener_estado(cid)
                            icono = "✅" if estado == "Available" else "❌" if estado == "Occupied" else "⚙️"
                            informe += f"{icono} {nombre}: {estado}\n"
                        enviar_telegram(informe)
        except:
            pass
        time.sleep(2) # Revisa si le has escrito cada 2 segundos

# --- LÓGICA DE VIGILANCIA AUTOMÁTICA ---

def vigilar_cargadores():
    estados_anteriores = {id_c: None for id_c in CARGADORES}
    print("🚀 Vigilancia automática activada...")

    while True:
        for poi_id, nombre in CARGADORES.items():
            estado_actual = obtener_estado(poi_id)
            
            if estados_anteriores[poi_id] is not None:
                # Si cambia a disponible, avisamos
                if estado_actual == "Available" and estados_anteriores[poi_id] != "Available":
                    enviar_telegram(f"⚡ ¡LIBRE! El cargador de {nombre} ya está disponible.")
            
            estados_anteriores[poi_id] = estado_actual
        
        time.sleep(120) # Revisa automáticamente cada 2 minutos

# --- ARRANCAR TODO ---

if __name__ == "__main__":
    # Iniciamos el hilo que escucha tus mensajes
    hilo_mensajes = threading.Thread(target=revisar_mensajes, daemon=True)
    hilo_mensajes.start()
    
    enviar_telegram("✅ Bot online. Escribe /check cuando quieras saber el estado actual.")
    # Iniciamos la vigilancia en el hilo principal
    vigilar_cargadores()
