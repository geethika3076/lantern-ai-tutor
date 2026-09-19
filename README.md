# lantern-ai-tutor
# Lantern — An AI Micro-Tutor for Equitable Learning

**SDG 4: Quality Education · SDG 10: Reduced Inequalities**
Built with **IBM Granite on watsonx.ai**

Lantern is an AI-assisted micro-tutor that provides subject-based questions, answer evaluation, personalized feedback, and learning progress tracking.

## How It Works

```text
Student
   ↓
Lantern Web Interface
   ↓
Flask Backend
   ↓
Demo Mode / IBM Granite
   ↓
Question + Feedback
   ↓
Mastery Update
```

The backend is designed to connect with **IBM Granite through watsonx.ai** while keeping API credentials on the server.

## AI Integration

Lantern supports **IBM Granite** through **IBM watsonx.ai** for:

* Educational question generation
* Difficulty-aware learning
* Answer evaluation
* Personalized feedback

The current prototype also includes a **Demo Mode**, which allows the application to run without IBM credentials using built-in questions and feedback.

> Demo Mode does not generate responses using IBM Granite. Granite is used when valid watsonx.ai credentials are configured and Demo Mode is disabled.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Demo Mode

```powershell
$env:DEMO_MODE="true"
python app.py
```

Open:

```text
http://localhost:5000
```

### 3. IBM Granite Mode

Configure the following environment variables:

```text
WATSONX_API_KEY
WATSONX_PROJECT_ID
WATSONX_URL
```

Then disable Demo Mode and run the application.

**Never upload API keys or credentials to GitHub.**

## Project Structure

```text
Lantern/
├── app.py
├── index.html
├── README.md
```

## Features

* Subject-based learning
* Multiple difficulty levels
* Multiple-choice questions
* Instant feedback
* Personalized explanations
* Mastery/progress tracking
* IBM Granite integration
* Demo Mode for credential-free testing

## Limitations

* Currently supports multiple-choice questions.
* Demo Mode uses predefined questions and feedback.
* AI-generated content should be reviewed before real classroom deployment.
* No multilingual support yet.
* No teacher dashboard yet.
* No learning-efficacy claims have been established through a controlled study.

## Future Enhancements

* Adaptive question generation
* More subjects and question types
* Multilingual learning
* Teacher dashboard
* Detailed learning analytics
* Voice-based learning
* Offline question banks
