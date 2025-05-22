from src import create_app

app = create_app()
app.app_context().push()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
    
    # !!!!!!!!!! ПАРОЛЬ от КЛЮЧА #  TODO:: b'40247aa7-4fba-4707-8aa5-8adea370b42f'