"""
CORE-Daemon: Scout Vision Bridge
Steuert die VISION_SYNC Web-Applikation lokal via Headless Playwright.
"""

import asyncio
import logging
import signal
import sys
from playwright.async_api import async_playwright

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ScoutVisionBridge")

VISION_SYNC_URL = "http://localhost:3006/?headless=true"
RETRY_DELAY = 5.0

class VisionBridge:
    def __init__(self):
        self.running = True
        self.browser = None
        self.context = None
        self.page = None

    def _stop_signal(self, *args):
        logger.info("Beenden-Signal empfangen. Leite Graceful Shutdown ein...")
        self.running = False

    async def run(self):
        # Registriere Signal-Handler
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._stop_signal)
            except NotImplementedError:
                # Fallback
                signal.signal(sig, lambda s, f: self._stop_signal())

        async with async_playwright() as p:
            while self.running:
                try:
                    logger.info("Starte Chromium Headless-Browser...")
                    self.browser = await p.chromium.launch(
                        headless=True,
                        args=[
                            "--use-fake-ui-for-media-stream",  # Umgeht Berechtigungs-Popups für Kamera/Mikrofon
                            "--disable-web-security"           # Vermeidet CORS- oder Zertifikatsprobleme lokal
                        ]
                    )

                    # Kontext mit expliziter Kamera/Mikrofon Erlaubnis
                    self.context = await self.browser.new_context(
                        permissions=['camera', 'microphone']
                    )

                    self.page = await self.context.new_page()

                    # Capture browser console logs
                    self.page.on("console", lambda msg: logger.info(f"BROWSER {msg.type}: {msg.text}"))
                    self.page.on("pageerror", lambda err: logger.error(f"BROWSER ERROR: {err}"))

                    logger.info(f"Navigiere zu {VISION_SYNC_URL} ...")
                    # domcontentloaded verhindert Blockieren durch unendliche Media-Streams
                    await self.page.goto(VISION_SYNC_URL, wait_until="domcontentloaded")
                    logger.info("Seite geladen. Browser-Session ist aktiv.")

                    # Keep-Alive Loop
                    while self.running:
                        if self.page.is_closed():
                            logger.error("Browser-Seite wurde unerwartet geschlossen!")
                            break
                        await asyncio.sleep(1.0)

                except Exception as e:
                    if self.running:
                        logger.error(f"Fehler in der Playwright-Ausführung: {e}")
                        logger.info(f"Warte {RETRY_DELAY} Sekunden vor dem nächsten Versuch...")
                        await asyncio.sleep(RETRY_DELAY)
                finally:
                    logger.info("Räume Playwright-Ressourcen auf...")
                    if self.context:
                        await self.context.close()
                    if self.browser:
                        await self.browser.close()

                    self.context = None
                    self.browser = None
                    self.page = None

        logger.info("Scout Vision Bridge wurde beendet.")

async def main():
    bridge = VisionBridge()
    await bridge.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Wird oft schon vom Signal-Handler gefangen, aber falls nicht:
        pass
    except Exception as e:
        logger.error(f"Daemon abgebrochen: {e}")
        sys.exit(1)
