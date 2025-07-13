from app import create_app

app = create_app()

if __name__ == '__main__': 
    app.logger.info("Starting Flask development server...")
    app.run(debug=True)