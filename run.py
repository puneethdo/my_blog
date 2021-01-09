from flaskblog import create_app
#Added comment that's it

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
