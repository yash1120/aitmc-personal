from flask import Flask,render_template,request
from app.config import LocalDevelopementConfig,ProductionDevelopementConfig


app =Flask(__name__)
app.config.from_object(LocalDevelopementConfig)
@app.route("/")
def home():
    return render_template("index.html")

if __name__== "__main__":
    app.run(
        host="0.0.0.0"
    )