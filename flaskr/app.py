from flask import Flask, render_template, request
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
    flask_type = request.args.get("type")
    page = request.args.get("page")
    if not page:
        page = 1
    notice, submit, end = crawler.notice(driver, page)

    posts = []
    if flask_type == "notice":
        posts = notice
    elif flask_type == "submit":
        posts = submit
    elif flask_type == "end":
        posts = end
    else:
        posts = notice + submit + end

    return render_template("notice/notice.html", posts=posts, selected_type=flask_type)


@app.route("/alert")
def alert():
    return render_template("/alert/alert.html")


@app.route("/task")
def task():
    return render_template("/task/task.html")


@app.route("/study")
def login():
    return render_template("/study/study.html")
