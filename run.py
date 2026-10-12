"""Start Astra locally:  python run.py"""
from astra import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
