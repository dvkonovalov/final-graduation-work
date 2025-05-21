from src import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

app.app_context().push()


if __name__ == "__main__":
    app.run(debug=True)