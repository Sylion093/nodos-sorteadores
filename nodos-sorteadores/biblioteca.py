import tkinter as tk
from tkinter import messagebox, filedialog
import os
import csv
from PyPDF2 import PdfReader

# Paths
BASE_PATH = r"C:\Users\emili\OneDrive\Escritorio\nodos-sorteadores"
DICTIONARIES = {
    "Spanish": os.path.join(BASE_PATH, "Spanish.txt"),
    "Geography": os.path.join(BASE_PATH, "Geography.txt"),
    "History": os.path.join(BASE_PATH, "History.txt"),
    "Math": os.path.join(BASE_PATH, "Math.txt"),
}
SUGGESTIONS_FILE = os.path.join(BASE_PATH, "Suggestions.txt")

# Ensure necessary files exist
for path in list(DICTIONARIES.values()) + [SUGGESTIONS_FILE]:
    if not os.path.exists(path):
        with open(path, "w") as f:
            pass

# Function to read PDF content
def extract_pdf_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read PDF: {e}")
        return None

# Function to classify a PDF
def classify_pdf(file_path):
    text = extract_pdf_text(file_path)
    if not text:
        return

    word_counts = {}
    for word in text.split():
        word = word.lower().strip(".,!?()[]{}")
        if word.isdigit():  # Skip numbers
            continue
        word_counts[word] = word_counts.get(word, 0) + 1

    # Compare against dictionaries
    matches = {category: 0 for category in DICTIONARIES}
    for category, dictionary_path in DICTIONARIES.items():
        with open(dictionary_path, "r") as f:
            keywords = set(line.strip().lower() for line in f)
            matches[category] = sum(word_counts.get(word, 0) for word in keywords)

    # Determine the best category
    best_category = max(matches, key=matches.get)
    output_folder = os.path.join(BASE_PATH, best_category)
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, os.path.basename(file_path))
    os.rename(file_path, output_path)

    # Update Suggestions.txt
    with open(SUGGESTIONS_FILE, "a") as f:
        for word in word_counts:
            if not word.isdigit():  # Skip adding numbers to suggestions
                f.write(f"{word}\n")

    messagebox.showinfo("Classification", f"PDF moved to {best_category} folder.")

# Function to upload a PDF
def upload_action():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        classify_pdf(file_path)

# Function to manage suggestions
def suggestions_action():
    def add_to_dictionary():
        selected_word = listbox.get(listbox.curselection())
        selected_category = category_var.get()
        if selected_word and selected_category:
            with open(DICTIONARIES[selected_category], "a") as f:
                f.write(f"{selected_word}\n")
            listbox.delete(listbox.curselection())
            messagebox.showinfo("Success", f"{selected_word} added to {selected_category} dictionary.")

    suggestions_window = tk.Toplevel(root)
    suggestions_window.title("Manage Suggestions")
    suggestions_window.geometry("400x400")

    listbox = tk.Listbox(suggestions_window, selectmode=tk.SINGLE)
    listbox.pack(fill=tk.BOTH, expand=True)

    # Load suggestions
    with open(SUGGESTIONS_FILE, "r") as f:
        for line in f:
            if not line.strip().isdigit():  # Skip numbers
                listbox.insert(tk.END, line.strip())

    category_var = tk.StringVar(value="Spanish")
    tk.Label(suggestions_window, text="Select Category:").pack()
    for category in DICTIONARIES:
        tk.Radiobutton(suggestions_window, text=category, variable=category_var, value=category).pack()

    add_button = tk.Button(suggestions_window, text="Add to Dictionary", command=add_to_dictionary)
    add_button.pack()

# Function for Query button
def query_action():
    query_window = tk.Toplevel(root)
    query_window.title("Query Books")
    query_window.geometry("400x300")

    def process_query():
        query = query_entry.get().lower().split()
        book_scores = {}

        # Search for matches in uploaded books
        for category_folder in DICTIONARIES.keys():
            folder_path = os.path.join(BASE_PATH, category_folder)
            if not os.path.exists(folder_path):
                continue

            for file_name in os.listdir(folder_path):
                if file_name.endswith(".txt"):  # Ensure only text files are scanned
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, "r") as f:
                        file_words = f.read().lower().split()
                        score = sum(file_words.count(word) for word in query)
                        if score > 0:
                            book_scores[file_name] = score

        # Display the best match
        if book_scores:
            best_match = max(book_scores, key=book_scores.get)
            result_label.config(text=f"Recommended: {best_match}")
        else:
            result_label.config(text="No matching books found.")

    tk.Label(query_window, text="Ask for a book:").pack(pady=5)
    query_entry = tk.Entry(query_window, width=50)
    query_entry.pack(pady=5)

    search_button = tk.Button(query_window, text="Search", command=process_query)
    search_button.pack(pady=10)

    result_label = tk.Label(query_window, text="")
    result_label.pack(pady=10)

# Main GUI window
root = tk.Tk()
root.title("Book Classifier")
root.geometry("400x250")

upload_button = tk.Button(root, text="Upload", width=20, height=2, command=upload_action)
upload_button.pack(pady=10)

query_button = tk.Button(root, text="Query", width=20, height=2, command=query_action)
query_button.pack(pady=10)

suggestions_button = tk.Button(root, text="Suggestions", width=20, height=2, command=suggestions_action)
suggestions_button.pack(pady=10)

root.mainloop()