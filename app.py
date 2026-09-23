from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash
)

import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import (
    create_database,
    get_connection,
    create_progress
)

from ai import (
    generate_career_plan,
    generate_skill_gap,
    generate_interview_question,
    evaluate_interview_answer,
    recommend_projects
)


app = Flask(__name__)

app.secret_key = "change-this-secret-key"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

create_database()


# --------------------------------------------------
# LOGIN REQUIRED
# --------------------------------------------------

def login_required():

    if "user_id" not in session:
        return False

    return True


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    if "user_id" in session:
        return redirect("/dashboard")

    return render_template("index.html")


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:

            flash("Please fill all fields.")

            return redirect("/register")


        hashed_password = generate_password_hash(password)


        connection = get_connection()
        cursor = connection.cursor()


        try:

            cursor.execute("""
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
            """, (
                name,
                email,
                hashed_password
            ))

            connection.commit()

            user_id = cursor.lastrowid

            connection.close()

            create_progress(user_id)

            flash("Registration successful. Please login.")

            return redirect("/login")


        except sqlite3.IntegrityError:

            connection.close()

            flash("Email already registered.")

            return redirect("/register")


    return render_template("register.html")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,))


        user = cursor.fetchone()

        connection.close()


        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            return redirect("/dashboard")


        flash("Invalid email or password.")

        return redirect("/login")


    return render_template("login.html")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# --------------------------------------------------
# PROFILE
# --------------------------------------------------

@app.route("/profile", methods=["POST"])
def profile():

    if not login_required():
        return redirect("/login")


    job = request.form["job"].strip()
    skills = request.form["skills"].strip()
    education = request.form["education"].strip()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        UPDATE users

        SET
            target_job = ?,
            skills = ?,
            education = ?

        WHERE id = ?
    """, (
        job,
        skills,
        education,
        session["user_id"]
    ))


    connection.commit()

    connection.close()


    return redirect("/dashboard")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect("/login")


    user_id = session["user_id"]


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (user_id,))


    user = cursor.fetchone()


    cursor.execute("""
        SELECT *
        FROM progress
        WHERE user_id = ?
    """, (user_id,))


    progress = cursor.fetchone()


    connection.close()


    if progress:

        values = [
            progress["dsa"],
            progress["python"],
            progress["sql"],
            progress["oop"],
            progress["dbms"],
            progress["projects"],
            progress["interview"]
        ]

        overall = sum(values) // len(values)

    else:

        overall = 0


    return render_template(
        "dashboard.html",
        user=user,
        progress=progress,
        overall=overall
    )


# --------------------------------------------------
# GENERATE AI PLAN
# --------------------------------------------------

@app.route("/generate-plan", methods=["POST"])
def generate_plan():

    if not login_required():
        return redirect("/login")


    user_id = session["user_id"]


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT target_job, skills, education
        FROM users
        WHERE id = ?
    """, (user_id,))


    user = cursor.fetchone()


    connection.close()


    if not user["target_job"]:

        flash("Please enter your target job first.")

        return redirect("/dashboard")


    plan = generate_career_plan(
        user["target_job"],
        user["skills"],
        user["education"]
    )


    skill_gap = generate_skill_gap(
        user["target_job"],
        user["skills"]
    )


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO plans
        (user_id, plan, skill_gap)

        VALUES (?, ?, ?)
    """, (
        user_id,
        plan,
        skill_gap
    ))


    connection.commit()

    connection.close()


    return redirect("/plan")


# --------------------------------------------------
# SHOW PLAN
# --------------------------------------------------

@app.route("/plan")
def plan():

    if not login_required():
        return redirect("/login")


    user_id = session["user_id"]


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM plans
        WHERE user_id = ?

        ORDER BY id DESC

        LIMIT 1
    """, (user_id,))


    plan_data = cursor.fetchone()


    connection.close()


    if not plan_data:

        return redirect("/dashboard")


    return render_template(
        "plan.html",
        plan=plan_data["plan"],
        skill_gap=plan_data["skill_gap"]
    )


# --------------------------------------------------
# UPDATE PROGRESS
# --------------------------------------------------

@app.route("/update-progress", methods=["POST"])
def update_progress():

    if not login_required():
        return redirect("/login")


    user_id = session["user_id"]


    dsa = int(request.form["dsa"])
    python = int(request.form["python"])
    sql = int(request.form["sql"])
    oop = int(request.form["oop"])
    dbms = int(request.form["dbms"])
    projects = int(request.form["projects"])
    interview = int(request.form["interview"])


    values = [
        dsa,
        python,
        sql,
        oop,
        dbms,
        projects,
        interview
    ]


    # Keep percentages between 0 and 100

    values = [
        max(0, min(100, value))
        for value in values
    ]


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        UPDATE progress

        SET
            dsa = ?,
            python = ?,
            sql = ?,
            oop = ?,
            dbms = ?,
            projects = ?,
            interview = ?

        WHERE user_id = ?
    """, (
        *values,
        user_id
    ))


    connection.commit()

    connection.close()


    return redirect("/dashboard")


# --------------------------------------------------
# INTERVIEW PAGE
# --------------------------------------------------

@app.route("/interview")
def interview():

    if not login_required():
        return redirect("/login")


    return render_template("interview.html")


# --------------------------------------------------
# GENERATE INTERVIEW QUESTION
# --------------------------------------------------

@app.route("/generate-question", methods=["POST"])
def generate_question():

    if not login_required():
        return redirect("/login")


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT target_job
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    ))


    user = cursor.fetchone()

    connection.close()


    question = generate_interview_question(
        user["target_job"]
    )


    session["interview_question"] = question


    return render_template(
        "interview.html",
        question=question
    )


# --------------------------------------------------
# EVALUATE ANSWER
# --------------------------------------------------

@app.route("/evaluate-answer", methods=["POST"])
def evaluate_answer():

    if not login_required():
        return redirect("/login")


    answer = request.form["answer"]

    question = session.get(
        "interview_question",
        ""
    )


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT target_job
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    ))


    user = cursor.fetchone()


    connection.close()


    feedback = evaluate_interview_answer(
        user["target_job"],
        question,
        answer
    )


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO interviews
        (user_id, question, answer, feedback)

        VALUES (?, ?, ?, ?)
    """, (
        session["user_id"],
        question,
        answer,
        feedback
    ))


    connection.commit()

    connection.close()


    return render_template(
        "interview.html",
        question=question,
        answer=answer,
        feedback=feedback
    )


# --------------------------------------------------
# PROJECT RECOMMENDATIONS
# --------------------------------------------------

@app.route("/projects")
def projects():

    if not login_required():
        return redirect("/login")


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT target_job, skills
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    ))


    user = cursor.fetchone()


    connection.close()


    recommendations = recommend_projects(
        user["target_job"],
        user["skills"]
    )


    return render_template(
        "projects.html",
        recommendations=recommendations
    )


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )