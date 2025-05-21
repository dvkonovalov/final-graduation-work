from src import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

app.app_context().push()


if __name__ == "__main__":
    app.run(debug=True)
    
    # !!!!!!!!!! ПАРОЛЬ от КЛЮЧА #  TODO:: b'40247aa7-4fba-4707-8aa5-8adea370b42f'