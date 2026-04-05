import asyncio
import re
import requests
from playwright.async_api import async_playwright

TOKEN = "8786576272:AAH3oI62TRJnrWFORvnWSCCJTSiLabr6Py4"
CHAT_ID = "7762201229"

URL = "https://www.iberdrola.es/movilidad-electrica/puntos-de-recarga"

cargadores = {
    "Ajuntament": "140674",
    "Policía": "5896",
    "Matzem": "5897"
}

estado_anterior = {nombre: None for nombre in cargadores}

def enviar(msg):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

def detectar(texto):
    match = re.search(r'(\d+)/(\d+)\s+Disponibles', texto)
    if match:
        return int(match.group(1)) > 0
    return False

async def main():
    enviar("🚀 Bot iniciado")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while True:
            for nombre, id_cargador in cargadores.items():
                try:
                    await page.goto(URL)
                    await page.fill("input", id_cargador)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(6000)

                    texto = await page.inner_text("body")
                    libre = detectar(texto)

                    if estado_anterior[nombre] == False and libre == True:
                        enviar(f"⚡ {nombre} LIBRE!")

                    estado_anterior[nombre] = libre

                except Exception as e:
                    print(e)

            await asyncio.sleep(30)

asyncio.run(main())
