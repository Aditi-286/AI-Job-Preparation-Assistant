import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


def ask_ai(prompt):

    if client is None:
        return """
AI is not configured yet.

Please add your OPENAI_API_KEY to the .env file.
"""


    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        return response.output_text

    except Exception as e:

        return f"AI error: {str(e)}"


def generate_career_plan(job, skills, education):

    prompt = f"""
You are an expert IT career and placement preparation assistant.

Student information:

Target job:
{job}

Current skills:
{skills}

Education:
{education}

Create a practical placement preparation plan.

Include:

1. Current skill assessment
2. Missing skills
3. Most important technologies to learn
4. DSA preparation
5. SQL/DBMS preparation
6. Programming preparation
7. Projects to build
8. Interview preparation
9. A 12-week roadmap
10. Recommended order of learning

The student is preparing for an entry-level IT job.

Keep the answer practical and beginner-friendly.
"""

    return ask_ai(prompt)


def generate_skill_gap(job, skills):

    prompt = f"""
Analyze the following student's skills for an entry-level IT position.

Target job:
{job}

Current skills:
{skills}

Return:

CURRENT SKILLS
- ...

MISSING SKILLS
- ...

HIGH PRIORITY
- ...

MEDIUM PRIORITY
- ...

LOW PRIORITY
- ...

Do not exaggerate requirements.
Focus on skills commonly expected for entry-level candidates.
"""

    return ask_ai(prompt)


def generate_interview_question(job):

    prompt = f"""
Generate ONE technical interview question for an entry-level candidate
applying for this job:

{job}

Requirements:

- Ask only one question.
- Make it realistic.
- Mix programming, SQL, DSA, OOP, DBMS, projects and job-specific topics.
- Do not provide the answer.
"""

    return ask_ai(prompt)


def evaluate_interview_answer(job, question, answer):

    prompt = f"""
You are an interview coach.

Target job:
{job}

Interview question:
{question}

Candidate answer:
{answer}

Evaluate the answer.

Give:

1. Score out of 10
2. What was good
3. What was missing
4. Technical corrections
5. A better answer structure
6. One improvement for the next interview

Be constructive and beginner-friendly.
"""

    return ask_ai(prompt)


def recommend_projects(job, skills):

    prompt = f"""
Recommend practical portfolio projects for an MCA/BCA student.

Target job:
{job}

Current skills:
{skills}

Give 5 projects.

For each project provide:

Project name
Purpose
Technologies
Main features
What the student will learn
Difficulty

Prioritize projects that demonstrate real development ability.
"""

    return ask_ai(prompt)