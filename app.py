from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    tasks = ["Maths homework", "Physics revision", "CS project"]
    return render_template("index.html", tasks=tasks)

if __name__ == "__main__":
    app.run(debug=True)