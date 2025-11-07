from flask import Flask, render_template
import crawler

app = Flask(__name__)


driver = crawler.login()
source = crawler.school_schedule(driver)


@app.route("/")
def hello_world():
    return render_template("home.html", source=source)
