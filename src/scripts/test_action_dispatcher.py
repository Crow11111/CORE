"""
Test für Action Dispatcher.
"""
from src.services.action_dispatcher import ActionDispatcher

def test_dispatcher():
    dispatcher = ActionDispatcher()
    # Wir nutzen eine harmlose Aktion: Notification
    text = "Ich werde eine Test-Notification senden. [HA: notify.mobile_app_iphone_von_mth( , {\"message\": \"ATLAS Autonomous Test\", \"title\": \"ATLAS 1.0\"})]"
    print(f"Sende Text an Dispatcher: {text}")
    res = dispatcher.dispatch(text)
    print(f"Ergebnis: {res}")

if __name__ == "__main__":
    test_dispatcher()
