from flask import Flask, render_template
import crawler

app = Flask(__name__)


driver = crawler.login()


@app.route("/")
def home():
    calendar = crawler.school_schedule(driver)
    meal = crawler.meal_contents(driver)
    from datetime import date

    return render_template(
        "home/home.html", calendar=calendar, meal=meal, day=date.today().day
    )


@app.route("/notice")
def notice():
    return render_template("notice/notice.html")


@app.route("/alert")
def alert():
    return render_template("/alert/alert.html")


@app.route("/task")
def task():
    return render_template("/task/task.html")


@app.route("/study")
def login():
    return render_template("/study/study.html")
