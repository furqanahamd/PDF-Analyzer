from flask import Flask, render_template, request
import pymupdf
import os
from groq import Groq

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Groq API
client = Groq(api_key="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")


@app.route("/analyze", methods=["POST"])
def analyze():

    # PDF receive karna
    pdf = request.files["pdf"]

    # Check PDF select hui hai ya nahi
    if pdf.filename == "":
        return "Please select a PDF file"

    # PDF save karna
    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        pdf.filename
    )

    pdf.save(filepath)

    # PDF open karna
    document = pymupdf.open(filepath)

    # Text extract karna
    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    # Check PDF mein text hai ya nahi
    if text.strip() == "":
        return "PDF mein koi readable text nahi mila."

    # AI prompt
    prompt = f"""
You are a PDF analyzer.

Analyze this PDF and provide:

1. Short Summary
2. Important Points
3. Main Topics

PDF TEXT:

{text}
"""

    # Groq AI
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    # AI result
    result = response.choices[0].message.content

    # Same page par result bhejna
    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True)