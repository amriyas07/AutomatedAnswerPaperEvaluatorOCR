import streamlit as st
from PIL import Image, ImageFilter
import pytesseract
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string
import pyttsx3
import math
import subprocess
import nltk
import sqlite3
from nltk.corpus import stopwords

# Download NLTK stopwords (you need to do this once)
#nltk.download('stopwords')
def logout():
    subprocess.run(["streamlit", "run", "EMarkLogin.py"])
if st.button("logout"):
    st.session_state.authenticated = False
    logout()
with sqlite3.connect('mydatabase.db') as conn:
    cursor = conn.cursor()

    # Create a table to store marks if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_marks (
            register_number TEXT PRIMARY KEY NOT NULL,
            student_name TEXT,
            subject_name TEXT,
            marks INTEGER
        )
    ''')
    conn.commit()

# Set Tesseract path (update this with your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def text_lowercase(text):
    return text.lower()

def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

def remove_whitespace(text):
    return " ".join(text.split())

def preprocess_text(text):
    text = text_lowercase(text)
    text = remove_punctuation(text)
    text = remove_whitespace(text)
    return text

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = nltk.word_tokenize(text)
    filtered_text = ' '.join([word for word in words if word.lower() not in stop_words])
    return filtered_text

def calculate_similarity(keyword, answer):
    all_text = [keyword, answer]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_text)
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1]).flatten()[0]
    return similarity_score

def save_data(register_number, name, subject_name, marks):
    conn.execute(f"INSERT INTO student_marks VALUES ('{register_number}', '{name}', '{subject_name}', {marks})")
    conn.commit()

def calculate_marks(similarity_score, user_marks, threshold=0.7):
    marks = user_marks if similarity_score >= threshold else 0
    return marks

def text_to_speech(text):
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Set properties (optional)
    engine.setProperty("rate", 150)  # Speed of speech

    # Say the given text
    engine.say(text)

    # Wait for the speech to finish
    engine.runAndWait()

def process_image(input_image, original_width, original_height):
    # Resize the image with a factor of 2
    resized_image = input_image.resize((original_width * 2, original_height * 2))

    # Convert the resized image to grayscale
    grayscale_image = resized_image.convert('L')

    # Apply a Gaussian blur filter to the grayscale image
    filtered_image = grayscale_image.filter(ImageFilter.GaussianBlur(radius=2))

    return filtered_image

def main():
    st.title("Automated Paper Evaluator")
    register_number = st.text_input("Enter Register Number")
    name = st.text_input("Enter Name")
    subject_name = st.text_input("Enter Subject Name")

    # Upload image through Streamlit
    uploaded_file = st.file_uploader("Upload a student test image...", type=["jpg", "png"])

    if uploaded_file is not None:
        # User input for total marks
        user_input_marks = st.number_input("Enter Total Marks For the Question")

        # User input for keywords
        user_keyword = st.text_input("Enter Keywords Separated by Comma:")

        if st.button("Evaluate"):
            # Use st.spinner to display a spinner while processing
            with st.spinner("Processing..."):
                # Perform OCR on the uploaded image
                extracted_text = pytesseract.image_to_string(Image.open(uploaded_file))

                # Preprocess extracted text
                preprocessed_text = preprocess_text(extracted_text)
                preprocessed_text = remove_stopwords(preprocessed_text)

                # Preprocess user keywords
                user_keyword = preprocess_text(user_keyword)
                user_keyword = remove_stopwords(user_keyword)

                # Calculate similarity and marks
                similarity_score = calculate_similarity(user_keyword, preprocessed_text)
                marks = calculate_marks(similarity_score, user_input_marks)

                # Display results
                st.write("Extracted Pre-Processed Text:")
                st.success(preprocessed_text)
                st.write("Pre-Processed User Keywords:")
                st.success(user_keyword)

                rounded_value = 0
                if(similarity_score >= 1):
                    rounded_value = round(similarity_score + 0.5)
                    st.info("You've Got High Mark!")
                    text_to_speech("Congratulations You've Got High Mark!")
                elif(similarity_score >= 0.3):
                    rounded_value = math.ceil(similarity_score)
                    st.info("You've Got Pass Mark!")
                    text_to_speech("You've Got Pass Mark.. Try to get High Marks")
                else:
                    rounded_value = 0
                    st.warning("...Fail...")
                    text_to_speech("Oh! Sorry You've to Take Retest.. Try to get Pass Mark")
                
                st.write(rounded_value)
                st.write(f"Scored Marks: {rounded_value} out of {user_input_marks}")

                # Save data to the database
                #if st.button("Save Data"):
                save_data(register_number, name, subject_name, rounded_value)
                st.success("Student Mark is Saved Successfully into the DataBase")

if __name__ == "__main__":
    main()
