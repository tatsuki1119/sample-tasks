import os

import firebase_admin
from firebase_admin import auth, credentials, db
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション管理のための秘密鍵

# Firebaseの初期化
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://sample-tasks-1119-default-rtdb.firebaseio.com/"}
)


# ログインページのルート
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = auth.get_user_by_email(email)
            session["user_id"] = user.uid
            return redirect(url_for("task_list"))
        except Exception as e:
            return "Invalid email or password"

    return render_template("login.html")


# タスクリストのルート
@app.route("/tasks", methods=["GET", "POST"])
def task_list():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    ref = db.reference(f"tasks/{user_id}")

    if request.method == "POST":
        task_name = request.form["task_name"]
        task_status = "incomplete"

        new_task_ref = ref.push()
        new_task_ref.set({"name": task_name, "status": task_status})

    tasks = ref.get() or {}
    return render_template("tasks.html", tasks=tasks)


# タスクの削除
@app.route("/delete_task/<task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    ref = db.reference(f"tasks/{user_id}/{task_id}")
    ref.delete()

    return redirect(url_for("task_list"))


# タスクの編集
@app.route("/edit_task/<task_id>", methods=["POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    ref = db.reference(f"tasks/{user_id}/{task_id}")

    task_name = request.form["task_name"]
    task_status = request.form["task_status"]

    ref.update({"name": task_name, "status": task_status})

    return redirect(url_for("task_list"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000,debug=True)
