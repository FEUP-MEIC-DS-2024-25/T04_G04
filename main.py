import tkinter as tk
from tkinter import filedialog, Text
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["API_KEY"])

def process_file():
    file_path = filedialog.askopenfilename(
        initialdir="/", title="Select File", filetypes=(("Text Files", "*.txt"),)
    )
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            input_text = file.read()

        prompt = """Correct, improve, add if missing the follow requirements, and add certain emojis to the improvements, and translate to english if necessary. Follwow this syntax:
        **Requisito 3:** O sistema deve permitir a exportação de relatórios em formato PDF e Excel.

        **Comentários:**

        * ✅ Este requisito está bem definido e claro.
        * 🔒 "Previamente registados" foi adicionado para maior clareza.
        
        
        **Considerações Adicionais:**

        * **Especificações Detalhadas:** Os requisitos podem ser enriquecidos com mais detalhes, como por exemplo, a funcionalidade específica de pesquisa (por exemplo, se a pesquisa é por correspondência exata ou por palavras-chave).
        * **Priorização:** É importante definir a prioridade de cada requisito para que a equipa de desenvolvimento possa focar-se nas funcionalidades mais importantes.
        * **Teste:** Para cada requisito, devem ser definidos cenários de teste que garantam que a funcionalidade está a funcionar como esperado.


        **Melhorias no geral:**

        * Linguagem mais clara e concisa;
        * Maior precisão na definição dos requisitos;
        * Consideração por detalhes importantes.
        \n\n""" + input_text

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, response.text)
        
        with open("output.md", 'w', encoding='utf-8') as output_file:
            output_file.write(response.text)

root = tk.Tk()
root.title("OptiReq")

upload_btn = tk.Button(root, text="Carregar Ficheiro .txt", padx=10, pady=5, fg="white", bg="blue", command=process_file)
upload_btn.pack()

result_text = Text(root, height=10, width=50)
result_text.pack()

root.mainloop()
