from flask import Flask, render_template, request, send_file
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key="AIzaSyA-2IJxWXwtA0lZlUK4XHrTXWmNHur-3Lw") #replace

app = Flask(__name__)

prompt = """You are a Youtube Video Summarizer. You will be taking transcript text
and summarizing the entire video and providing the important summary in points within 400 words.
Please provide the summary of the text given here: """

translator = Translator()


def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in transcript_text:
            transcript += " " + i['text']
        return transcript
    except Exception as e:
        raise e


def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_notes', methods=['POST'])
def get_notes():
    youtube_link = request.form['youtube_link']
    if youtube_link:
        video_id = youtube_link.split('=')[1]
        image_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            return render_template('result.html', image_url=image_url, summary=summary)
    return "Error occurred!"


@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    lang = request.form['lang']
    translated_text = translator.translate(text, dest=lang).text
    with open("translated_output.txt", "w", encoding="utf-8") as text_file:
        text_file.write(translated_text)
    return send_file("translated_output.txt", as_attachment=True)


@app.route('/download_txt', methods=['POST'])
def download_txt():
    text = request.form['text']
    with open("output.txt", "w", encoding="utf-8") as text_file:
        text_file.write(text)
    return send_file("output.txt", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
