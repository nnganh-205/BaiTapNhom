import subprocess
import time
import os

def run_web_app():
    """Runs the Flask web application."""
    print("Starting Flask web application...")
    # Assuming app.py is in the root directory
    # Set FLASK_APP environment variable if needed, though app.run() in app.py might handle it
    env = os.environ.copy()
    env["APP_HOST"] = "127.0.0.1"
    env["APP_PORT"] = "5050"
    process = subprocess.Popen(["python", "app.py"], env=env)
    return process

def run_ai_chatbot_api():
    """Runs the FastAPI AI chatbot API."""
    print("Starting FastAPI AI chatbot API...")
    # Assuming main.py is in ai_chatbot/api/
    # You might need to install uvicorn: pip install uvicorn
    env = os.environ.copy()
    env["CHAT_HISTORY_LIMIT"] = "40" # Example, adjust as needed
    process = subprocess.Popen(["uvicorn", "ai_chatbot.api.main:app", "--host", "0.0.0.0", "--port", "8000"], env=env)
    return process

if __name__ == "__main__":
    web_app_process = None
    ai_chatbot_api_process = None
    try:
        web_app_process = run_web_app()
        time.sleep(5)  # Give the web app a moment to start
        ai_chatbot_api_process = run_ai_chatbot_api()

        print("Both web application and AI chatbot API are running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
            if web_app_process.poll() is not None:
                print("Web application stopped unexpectedly.")
                break
            if ai_chatbot_api_process.poll() is not None:
                print("AI chatbot API stopped unexpectedly.")
                break

    except KeyboardInterrupt:
        print("Stopping processes...")
    finally:
        if web_app_process:
            web_app_process.terminate()
            web_app_process.wait()
            print("Web application stopped.")
        if ai_chatbot_api_process:
            ai_chatbot_api_process.terminate()
            ai_chatbot_api_process.wait()
            print("AI chatbot API stopped.")
    print("All processes stopped.")
