import os
from flask import Flask, request, render_template, jsonify, send_file
import google.generativeai as genai
from google.cloud import secretmanager, firestore
from markdown import Markdown
from io import StringIO

app = Flask(__name__)

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=secret_name)
    return response.payload.data.decode("UTF-8")

# Retrieve the API key from Secret Manager
#api_key = get_secret("OPTI_REQ_API_KEY")

if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "superhero-04-04.json"

os.environ["ASSISTANT_ID"] = "superhero-04-04"

db = firestore.Client()

try:
    secret_doc = db.collection(os.environ["ASSISTANT_ID"]).document("secrets").get()
    if secret_doc.exists:
        os.environ["API_KEY"] = secret_doc.to_dict().get("api_key", "")
        print("API Key successfully retrieved and set.")
    else:
        raise ValueError("Secrets document does not exist.")
except Exception as e:
    print(f"Error retrieving secret: {e}")

api_key = os.getenv("API_KEY")

# print in docker logs
print(f"API Key: {api_key if api_key else 'Not set'}")

genai.configure(api_key=api_key)
app = Flask(__name__)

# Configure the API key
genai.configure(api_key=os.getenv('API_KEY'))

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        input_text = file.read().decode('utf-8')

        prompt = """Correct, improve, add if missing the following requirements, and add certain emojis to the improvements, and translate to English if necessary. 
        Sort them by order of difficulty from easier to harder. In case the requirement is too complex, separate them in different requirements while maintaining its initial goal.
        Add some spacing between the requirements.
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
        
        with open("output.md", 'w', encoding='utf-8') as output_file:
            output_file.write(response.text)
        
        with open("output.txt", 'w', encoding='utf-8') as output_file:
            output_file.write(txt_response)
        
        return jsonify({'output': txt_response})


@app.route('/chat', methods=['POST'])
def chat():
    # Extract the user message from the POST request
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Construct the AI prompt
    prompt = f"You are an AI assistant for Requeriments engeneering. Please respond to the following: {user_message}"

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    ai_response = unmark(response.text)
    return jsonify({'response': ai_response})

@app.route('/download')
def download():
    return send_file('output.md', as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
