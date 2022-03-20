from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    else:
        screen_name = request.form["screen_name"]

        if len(screen_name) == 0:
            return render_template("index.html", error="検索ユーザー名が未入力です。")

        return render_template("index.html", screen_name=screen_name)

if __name__ == '__main__':
    app.run()