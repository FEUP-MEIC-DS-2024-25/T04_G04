import tkinter as tk
from tkinter import filedialog, Text
import google.generativeai as genai
import os
from markdown import Markdown
from io import StringIO

# Configure the API key
genai.configure(api_key=os.environ["API_KEY"])

def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def unmark(text):
    return __md.convert(text)

def process_file():
    file_path = filedialog.askopenfilename(
        initialdir="/", title="Select File", filetypes=(("Text Files", "*.txt"),)
    )
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            input_text = file.read()

        prompt = """Correct, improve, add if missing the following requirements, and add certain emojis to the improvements, and translate to English if necessary. 
        Sort them by order of difficulty from easier to harder. In case the requirement is too complex, separate them in different requirements while maintaining its initial goal.
        Follow this syntax:
        **Requirement 3:** The system must allow the export of reports in PDF and Excel format.

        **Comments:**

        * ✅ This requirement is well-defined and clear.
        * 🔒 "Previously registered" was added for greater clarity.
        
        **Additional Considerations:**

        * **Detailed Specifications:** Requirements can be enriched with more details, such as the specific functionality of search (for example, whether the search is for exact matches or keywords).
        * **Prioritization:** It is important to define the priority of each requirement so that the development team can focus on the most important features.
        * **Testing:** For each requirement, test scenarios should be defined to ensure that the functionality works as expected.


        **General Improvements:**

        * Clearer and more concise language;
        * Greater accuracy in defining requirements;
        * Consideration of important details.
        \n\n""" + input_text

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        txt_response = unmark(response.text)
        
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, txt_response)
        
        with open("output.md", 'w', encoding='utf-8') as output_file:
            output_file.write(response.text)
        
        with open("output.txt", 'w', encoding='utf-8') as output_file:
            output_file.write(txt_response)

# Create the main application window
root = tk.Tk()
root.title("OptiReq")

# Set the size of the window
root.geometry("550x700")  # l x h

# Button to select the file
upload_btn = tk.Button(root, text="Load .txt File", padx=10, pady=5, fg="white", bg="blue", command=process_file)
upload_btn.pack(pady=10)  # Add some vertical space around the button

# Text area to display the result of the API
result_text = Text(root, height=45, width=65)  # Adjust dimensions to fit a mobile-like screen
result_text.pack(padx=10, pady=10)  # Add padding around the text area

# Start the application
root.mainloop()

