
"""
Lantern — AI Micro-Tutor
SDG 4: Quality Education

IBM Granite + watsonx.ai backend with built-in DEMO MODE.

Modes
-----
DEMO_MODE=true
    Runs without IBM credentials.
    Uses built-in educational questions and feedback.

DEMO_MODE=false
    Uses IBM Granite through watsonx.ai.

The browser never receives the IBM API key.
"""

import os
import json
import re

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS


# ============================================================
# FLASK SETUP
# ============================================================

app = Flask(__name__, static_folder=".")
CORS(app)


# ============================================================
# CONFIGURATION
# ============================================================

# Set DEMO_MODE=true for demonstration without IBM credentials.
#
# Set DEMO_MODE=false when you have valid IBM watsonx.ai
# credentials and want to use IBM Granite.
#
# Default is true so the project can run immediately.
DEMO_MODE = os.environ.get("DEMO_MODE", "true").lower() == "true"


# IBM watsonx.ai settings
WATSONX_API_KEY = os.environ.get("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID")

WATSONX_URL = os.environ.get(
    "WATSONX_URL",
    "https://us-south.ml.cloud.ibm.com"
)

# IBM Granite model
GRANITE_MODEL_ID = os.environ.get(
    "GRANITE_MODEL_ID",
    "ibm/granite-3-3-8b-instruct"
)


# ============================================================
# IBM GRANITE INITIALIZATION
# ============================================================

model = None


def initialize_granite():
    """
    Initialize IBM Granite only when DEMO_MODE is disabled.

    This function is deliberately isolated so that the
    application can still run in DEMO_MODE when IBM
    credentials are unavailable.
    """

    global model

    if DEMO_MODE:
        print("DEMO MODE is enabled.")
        print("IBM Granite will not be contacted.")
        return

    if not WATSONX_API_KEY:
        raise RuntimeError(
            "WATSONX_API_KEY is missing.\n"
            "Set the variable before starting the application."
        )

    if not WATSONX_PROJECT_ID:
        raise RuntimeError(
            "WATSONX_PROJECT_ID is missing.\n"
            "Set the variable before starting the application."
        )

    try:

        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        credentials = Credentials(
            url=WATSONX_URL,
            api_key=WATSONX_API_KEY
        )

        model = ModelInference(
            model_id=GRANITE_MODEL_ID,
            credentials=credentials,
            project_id=WATSONX_PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 700,
                "repetition_penalty": 1.05,
            }
        )

        print("IBM Granite initialized successfully.")
        print("Model:", GRANITE_MODEL_ID)

    except Exception as exc:

        raise RuntimeError(
            "IBM Granite could not be initialized.\n"
            f"Error: {exc}"
        )


# ============================================================
# DEMO QUESTIONS
# ============================================================

DEMO_QUESTIONS = {

    "Math": [
        {
            "topic": "Fractions",
            "question": "What is 3/4 + 1/4?",
            "options": [
                "1",
                "1/2",
                "3/4",
                "2"
            ],
            "correctIndex": 0,
            "difficultyLabel": "Foundations"
        },

        {
            "topic": "Algebra",
            "question": "If x + 5 = 12, what is x?",
            "options": [
                "5",
                "6",
                "7",
                "8"
            ],
            "correctIndex": 2,
            "difficultyLabel": "Building up"
        },

        {
            "topic": "Percentages",
            "question": "What is 20% of 50?",
            "options": [
                "5",
                "10",
                "15",
                "20"
            ],
            "correctIndex": 1,
            "difficultyLabel": "On level"
        },

        {
            "topic": "Geometry",
            "question": "What is the area of a 5 × 4 rectangle?",
            "options": [
                "9",
                "18",
                "20",
                "25"
            ],
            "correctIndex": 2,
            "difficultyLabel": "On level"
        },

        {
            "topic": "Algebra",
            "question": "If 2x = 18, what is x?",
            "options": [
                "6",
                "8",
                "9",
                "12"
            ],
            "correctIndex": 2,
            "difficultyLabel": "Stretching"
        }
    ],

    "Science": [
        {
            "topic": "Biology",
            "question": "Which organ pumps blood around the body?",
            "options": [
                "Lungs",
                "Heart",
                "Kidney",
                "Stomach"
            ],
            "correctIndex": 1,
            "difficultyLabel": "Foundations"
        },

        {
            "topic": "Physics",
            "question": "What force pulls objects toward Earth?",
            "options": [
                "Friction",
                "Gravity",
                "Magnetism",
                "Pressure"
            ],
            "correctIndex": 1,
            "difficultyLabel": "Building up"
        },

        {
            "topic": "Chemistry",
            "question": "What is the chemical formula for water?",
            "options": [
                "CO2",
                "O2",
                "H2O",
                "NaCl"
            ],
            "correctIndex": 2,
            "difficultyLabel": "Foundations"
        },

        {
            "topic": "Biology",
            "question": "Which gas do plants absorb during photosynthesis?",
            "options": [
                "Oxygen",
                "Nitrogen",
                "Carbon dioxide",
                "Hydrogen"
            ],
            "correctIndex": 2,
            "difficultyLabel": "On level"
        },

        {
            "topic": "Physics",
            "question": "What is the SI unit of force?",
            "options": [
                "Joule",
                "Newton",
                "Watt",
                "Pascal"
            ],
            "correctIndex": 1,
            "difficultyLabel": "Stretching"
        }
    ],

    "English": [
        {
            "topic": "Grammar",
            "question": "Which word is a noun?",
            "options": [
                "Quickly",
                "Beautiful",
                "Teacher",
                "Run"
            ],
            "correctIndex": 2,
            "difficultyLabel": "Foundations"
        },

        {
            "topic": "Grammar",
            "question": "Choose the correct sentence.",
            "options": [
                "She are happy.",
                "She is happy.",
                "She am happy.",
                "She be happy."
            ],
            "correctIndex": 1,
            "difficultyLabel": "Building up"
        },

        {
            "topic": "Vocabulary",
            "question": "What is the opposite of 'ancient'?",
            "options": [
                "Old",
                "Modern",
                "Historic",
                "Past"
            ],
            "correctIndex": 1,
            "difficultyLabel": "On level"
        },

        {
            "topic": "Grammar",
            "question": "Which word is an adjective?",
            "options": [
                "Happily",
                "Run",
                "Beautiful",
                "Quickly"
            ],
            "correctIndex": 2,
            "difficultyLabel": "Building up"
        },

        {
            "topic": "Vocabulary",
            "question": "What does 'brief' mean?",
            "options": [
                "Very long",
                "Short",
                "Difficult",
                "Loud"
            ],
            "correctIndex": 1,
            "difficultyLabel": "On level"
        }
    ]
}


# ============================================================
# DEMO FEEDBACK
# ============================================================

def demo_feedback(
    correct,
    question,
    chosen_index,
    correct_index,
    difficulty
):
    """
    Generate simple tutor feedback for DEMO MODE.
    """

    if correct:

        feedback = (
            "Correct! Your answer matches the expected answer. "
            "You can now try a slightly more challenging question "
            "to strengthen your understanding."
        )

        if difficulty < 5:
            next_difficulty = "harder"
        else:
            next_difficulty = "same"

    else:

        feedback = (
            f"Not quite. The correct answer is option "
            f"{correct_index + 1}. "
            "Review the main idea from this question and try "
            "another example before moving to a harder level."
        )

        if difficulty > 1:
            next_difficulty = "easier"
        else:
            next_difficulty = "same"

    return {
        "feedback": feedback,
        "nextDifficulty": next_difficulty
    }


# ============================================================
# DEMO QUESTION SELECTION
# ============================================================

def get_demo_question(subject, difficulty, history):
    """
    Select a built-in question based on subject and
    approximately match the requested difficulty.
    """

    questions = DEMO_QUESTIONS.get(
        subject,
        DEMO_QUESTIONS["Math"]
    )

    # Try to avoid repeating the most recent question.
    recent_topics = []

    if history:
        # History contains correct/incorrect only in the
        # current frontend, so this is intentionally simple.
        recent_topics = []

    # Convert difficulty 1-5 to question index.
    index = max(
        0,
        min(
            len(questions) - 1,
            difficulty - 1
        )
    )

    question = questions[index]

    return question


# ============================================================
# GRANITE GENERATION
# ============================================================

def generate_with_granite(system_prompt, user_prompt):
    """
    Send a request to IBM Granite and return JSON.
    """

    if model is None:
        raise RuntimeError(
            "IBM Granite is not initialized."
        )

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = model.chat(
        messages=messages
    )

    text = response["choices"][0]["message"]["content"].strip()

    # Remove markdown JSON fences if present.
    text = re.sub(
        r"```(?:json)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.replace("```", "").strip()

    # Extract JSON object.
    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if not match:
        raise ValueError(
            "No JSON object found in Granite response: "
            + text[:500]
        )

    return json.loads(match.group(0))


# ============================================================
# GRANITE QUESTION PROMPT
# ============================================================

QUESTION_SYSTEM = """
You are an adaptive tutoring engine for secondary-school students.

Generate exactly ONE multiple-choice question.

Subjects:
- Math
- Science
- English

Difficulty:
1 = foundational
2 = basic
3 = on level
4 = challenging
5 = advanced

The question must:
- Be self-contained.
- Be suitable for a secondary-school student.
- Have exactly four options.
- Have exactly one correct answer.
- Keep each option under 12 words.
- Vary the topic.
- Clearly identify the correct option.

Return ONLY a valid JSON object.

Required format:

{
  "topic": "short topic name",
  "question": "question text",
  "options": [
    "option A",
    "option B",
    "option C",
    "option D"
  ],
  "correctIndex": 0,
  "difficultyLabel": "Foundations"
}

difficultyLabel must be one of:

Foundations
Building up
On level
Stretching
Advanced
"""


# ============================================================
# GRANITE FEEDBACK PROMPT
# ============================================================

FEEDBACK_SYSTEM = """
You are a warm and encouraging AI tutor.

A student has answered a multiple-choice question.

If the student is correct:
- Briefly explain why.
- Add one sentence that extends the concept.

If the student is incorrect:
- Explain the correct answer.
- Explain the reasoning using the question.
- Use simple language.
- Never shame the student.

Then decide whether the next question should be:
- easier
- same
- harder

Return ONLY a valid JSON object.

Required format:

{
  "feedback": "2-4 sentences",
  "nextDifficulty": "easier"
}

nextDifficulty must be exactly:

easier
same
harder
"""


# ============================================================
# QUESTION API
# ============================================================

@app.route("/api/question", methods=["POST"])
def question():

    data = request.get_json(force=True)

    subject = data.get(
        "subject",
        "Math"
    )

    try:
        difficulty = int(
            data.get(
                "difficulty",
                3
            )
        )
    except (TypeError, ValueError):
        difficulty = 3

    difficulty = max(
        1,
        min(5, difficulty)
    )

    history = data.get(
        "history",
        []
    )

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if DEMO_MODE:

        try:

            result = get_demo_question(
                subject,
                difficulty,
                history
            )

            return jsonify(result)

        except Exception as exc:

            app.logger.exception(
                "Demo question failed"
            )

            return jsonify({
                "error": str(exc)
            }), 500

    # --------------------------------------------------------
    # IBM GRANITE MODE
    # --------------------------------------------------------

    user_prompt = (
        f"Subject: {subject}\n"
        f"Target difficulty: {difficulty} out of 5\n"
        f"Student's recent results: "
        f"{', '.join(history[-4:]) if history else 'no attempts yet'}\n\n"
        f"Generate the next question."
    )

    try:

        result = generate_with_granite(
            QUESTION_SYSTEM,
            user_prompt
        )

        required_fields = [
            "topic",
            "question",
            "options",
            "correctIndex",
            "difficultyLabel"
        ]

        for field in required_fields:

            if field not in result:
                raise ValueError(
                    f"Granite response missing: {field}"
                )

        if len(result["options"]) != 4:
            raise ValueError(
                "Granite must return exactly four options."
            )

        return jsonify(result)

    except Exception as exc:

        app.logger.exception(
            "Granite question generation failed"
        )

        return jsonify({
            "error": str(exc)
        }), 500


# ============================================================
# FEEDBACK API
# ============================================================

@app.route("/api/feedback", methods=["POST"])
def feedback():

    data = request.get_json(force=True)

    subject = data.get(
        "subject",
        "Math"
    )

    question_text = data.get(
        "question",
        ""
    )

    options = data.get(
        "options",
        []
    )

    correct_index = data.get(
        "correctIndex"
    )

    chosen_index = data.get(
        "chosenIndex"
    )

    correct = bool(
        data.get(
            "correct",
            False
        )
    )

    try:

        difficulty = int(
            data.get(
                "difficulty",
                3
            )
        )

    except (TypeError, ValueError):

        difficulty = 3

    difficulty = max(
        1,
        min(5, difficulty)
    )

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if DEMO_MODE:

        try:

            result = demo_feedback(
                correct=correct,
                question=question_text,
                chosen_index=chosen_index,
                correct_index=correct_index,
                difficulty=difficulty
            )

            return jsonify(result)

        except Exception as exc:

            app.logger.exception(
                "Demo feedback failed"
            )

            return jsonify({
                "error": str(exc)
            }), 500

    # --------------------------------------------------------
    # IBM GRANITE MODE
    # --------------------------------------------------------

    options_text = " | ".join(
        f"{i}: {option}"
        for i, option in enumerate(options)
    )

    user_prompt = (
        f"Subject: {subject}\n"
        f"Question: {question_text}\n"
        f"Options: {options_text}\n"
        f"Correct index: {correct_index}\n"
        f"Student chose index: {chosen_index}\n"
        f"Result: "
        f"{'correct' if correct else 'incorrect'}\n"
        f"Current difficulty: {difficulty} of 5\n\n"
        f"Provide personalized feedback."
    )

    try:

        result = generate_with_granite(
            FEEDBACK_SYSTEM,
            user_prompt
        )

        if "feedback" not in result:
            raise ValueError(
                "Granite response missing feedback."
            )

        if "nextDifficulty" not in result:
            raise ValueError(
                "Granite response missing nextDifficulty."
            )

        return jsonify(result)

    except Exception as exc:

        app.logger.exception(
            "Granite feedback generation failed"
        )

        return jsonify({
            "error": str(exc)
        }), 500


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def index():

    return send_from_directory(
        ".",
        "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/status", methods=["GET"])
def status():

    return jsonify({
        "application": "Lantern",
        "sdg": "SDG 4 - Quality Education",
        "mode": "DEMO" if DEMO_MODE else "IBM Granite",
        "model": (
            "Built-in educational demo"
            if DEMO_MODE
            else GRANITE_MODEL_ID
        )
    })


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("              LANTERN — AI MICRO-TUTOR")
    print("=" * 60)
    print()

    if DEMO_MODE:

        print("MODE: DEMO MODE")
        print()
        print(
            "Lantern is running without IBM credentials."
        )
        print(
            "Built-in questions and feedback are being used."
        )

    else:

        print("MODE: IBM GRANITE")
        print()
        print(
            "Connecting to IBM watsonx.ai..."
        )

        try:

            initialize_granite()

        except Exception as exc:

            print()
            print("IBM Granite initialization failed.")
            print()
            print(str(exc))
            print()
            print(
                "To run the application in DEMO MODE:"
            )
            print()
            print(
                'PowerShell: $env:DEMO_MODE="true"'
            )
            print()
            raise SystemExit(1)

    print()
    print("Server:")
    print("http://localhost:5000")
    print()
    print("Status:")
    print("http://localhost:5000/api/status")
    print()
    print("=" * 60)
    print()

    app.run(
        debug=True,
        port=5000
    )

