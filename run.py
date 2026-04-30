"""Entry point to run the Flask application."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Accessible from any device on the network (great for mobile testing)
    app.run(host="0.0.0.0", port=5000, debug=False )