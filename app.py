# Install libraries
!pip install gradio reportlab

import ast
import gradio as gr
from datetime import datetime

# -----------------------------
# DocGenie Analyzer Class
# -----------------------------
class DocGenieAnalyzer:

    def __init__(self):
        self.history = []

    # Extract function details
    def extract_functions(self, code):

        tree = ast.parse(code)
        functions = []

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):

                name = node.name
                params = []

                for arg in node.args.args:
                    params.append(arg.arg)

                functions.append({
                    "name": name,
                    "params": params
                })

        return functions


    # Analyze logic inside function
    def analyze_logic(self, code):

        tree = ast.parse(code)

        loops = False
        conditions = False
        operations = []

        for node in ast.walk(tree):

            if isinstance(node, (ast.For, ast.While)):
                loops = True

            if isinstance(node, ast.If):
                conditions = True

            if isinstance(node, ast.BinOp):

                if isinstance(node.op, ast.Add):
                    operations.append("addition")

                if isinstance(node.op, ast.Sub):
                    operations.append("subtraction")

                if isinstance(node.op, ast.Mult):
                    operations.append("multiplication")

                if isinstance(node.op, ast.Div):
                    operations.append("division")

        return {
            "loops": loops,
            "conditions": conditions,
            "operations": operations
        }


    # Generate Google style docstring
    def google_docstring(self, name, params, analysis):

        doc = f'"""{name} function.\n\n'
        doc += "Automatically generated documentation.\n\n"

        doc += "Args:\n"
        for p in params:
            doc += f"    {p} (int): Input parameter\n"

        doc += "\nReturns:\n"
        doc += "    result: Output value\n"

        if analysis["loops"]:
            doc += "\nNote: This function contains loop logic\n"

        if analysis["conditions"]:
            doc += "Note: This function contains conditional logic\n"

        doc += '"""'

        return doc


    # Generate NumPy style docstring
    def numpy_docstring(self, name, params, analysis):

        doc = f'"""{name} function.\n\n'

        doc += "Parameters\n"
        doc += "----------\n"

        for p in params:
            doc += f"{p} : int\n"
            doc += f"    Description of {p}\n"

        doc += "\nReturns\n"
        doc += "-------\n"
        doc += "result\n"
        doc += "    Output value\n"

        doc += '"""'

        return doc


# -----------------------------
# Main Processing Function
# -----------------------------
def generate_documentation(code, style):

    analyzer = DocGenieAnalyzer()

    try:

        functions = analyzer.extract_functions(code)
        analysis = analyzer.analyze_logic(code)

        result = ""

        for func in functions:

            name = func["name"]
            params = func["params"]

            if style == "google":
                doc = analyzer.google_docstring(name, params, analysis)

            else:
                doc = analyzer.numpy_docstring(name, params, analysis)

            result += f"\nFunction: {name}\n"
            result += doc + "\n\n"

        return result

    except Exception as e:
        return f"Error: {str(e)}"


# -----------------------------
# Export TXT
# -----------------------------
def export_txt(text):

    filename = f"docgenie_{datetime.now().strftime('%H%M%S')}.txt"

    with open(filename, "w") as f:
        f.write(text)

    return filename


# -----------------------------
# Gradio Interface
# -----------------------------
with gr.Blocks() as demo:

    gr.Markdown("# Doc-Genie")
    gr.Markdown("Automatic Python Docstring Generator using AST")

    code_input = gr.Textbox(
        label="Enter Python Code",
        lines=15,
        placeholder="Paste your Python function here..."
    )

    style = gr.Radio(
        ["google", "numpy"],
        label="Select Docstring Style",
        value="google"
    )

    generate_btn = gr.Button("Generate Documentation")

    output_box = gr.Textbox(
        label="Generated Docstring",
        lines=15
    )

    export_btn = gr.Button("Export as TXT")
    file_output = gr.File()

    generate_btn.click(
        generate_documentation,
        inputs=[code_input, style],
        outputs=output_box
    )

    export_btn.click(
        export_txt,
        inputs=output_box,
        outputs=file_output
    )

demo.launch(share=True)