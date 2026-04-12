import os

from src import create_app

app = create_app()


if __name__ == '__main__':
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "5050"))
    app.run(host=host, port=port, debug=True)
