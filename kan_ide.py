
from compare_ai import AICompare
from kan_semantic import analyze, format_results
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from graphviz import Digraph
import tempfile
import os

from kan_lex import lexer
from kan_yacc import parser


class KanGUI:
    def __init__(this, root):
        this.root = root
        this.root.title("KAN Language GUI Display")

        this.iden = 0

        this.display()

    # =========================
    # UI LAYOUT
    # =========================
    def semantic(this):
        c_ode = this.sec.get("1.0", tk.END)
        errors = analyze(c_ode)
        result = format_results(errors)
        this.output.delete("1.0", tk.END)
        this.output.insert(tk.END, result)

    def compare_ai(this):
        c_ode = this.sec.get("1.0", tk.END)
        
        compiler_output = this.output.get("1.0", tk.END).strip()
        
        ai_output = AICompare.analyze(c_ode)
        
        result = AICompare.compare(compiler_output, ai_output)
        
        this.output.delete("1.0", tk.END)
        this.output.insert(tk.END, f"🤖 AI Prediction:\n{ai_output}\n\n{result}")

    def display(this):
        # Top Frame (Editor)
        frame1 = tk.Frame(this.root)
        frame1.pack(fill="both", expand=True)

        this.sec = tk.Text(frame1, height=20, font=("Consolas", 11))
        this.sec.pack(fill="both", expand=True, padx=10, pady=10)

        frame2 = tk.Frame(this.root) #frames for button
        frame2.pack(pady=5)

        tk.Button(frame2, text="▶ Run", command=this.Process).grid(row=0, column=0, padx=5)
        tk.Button(frame2, text="🔍 Tokens", command=this.Token).grid(row=0, column=1, padx=5)
        tk.Button(frame2, text="🌳 Parse Tree", command=this.pr_tree).grid(row=0, column=2, padx=5)
        tk.Button(frame2, text="🤖 Ask AI", command=this.compare_ai).grid(row=0, column=3, padx=5)
    

        # Output Console
        this.output = tk.Text(this.root, height=10, bg="black", fg="lime", font=("Consolas", 10))
        this.output.pack(fill="both", expand=False, padx=10, pady=10)

    
    def Process(this):
        c_ode = this.sec.get("1.0", tk.END)

        try:
            ast = parser.parse(c_ode)

            answers = []
            for stmt in ast:
                resu = stmt()
                if resu is not None:
                    answers.append(str(resu))

            this.output.delete("1.0", tk.END)
            this.output.insert(tk.END, "\n".join(answers))

        except Exception as e:
            messagebox.showerror("Error is at Runtime ", str(e))

    # =========================
    # SHOW TOKENS
    # =========================
    def Token(this):
        c_ode = this.sec.get("1.0", tk.END)
        lexer.input(c_ode)

        tokens_output = []

        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens_output.append(f"{tok.type} : {tok.value}")

        this.output.delete("1.0", tk.END)
        this.output.insert(tk.END, "\n".join(tokens_output))

    # =========================
    # PARSE TREE (GRAPH)
    # =========================
    def pr_tree(this):
        c_ode = this.sec.get("1.0", tk.END)

        try:
            ast = parser.parse(c_ode)

            dot = Digraph()
            this.iden = 0

            for node in ast:
                this.build_graph(dot, node)

            temp_file = os.path.join(tempfile.gettempdir(), "kan_ast")
            dot.render(temp_file, format="png", view=True)

        except Exception as e:
            messagebox.showerror("Parse tree Error occured", str(e))


    def build_graph(this, dot, node, parent=None):
        current_id = str(this.iden)
        this.iden += 1

        label = type(node).__name__
        dot.node(current_id, label)

        if parent is not None:
            dot.edge(parent, current_id)

        if hasattr(node, "__dict__"):
            for key, value in node.__dict__.items():

                if isinstance(value, list):
                    for item in value:
                        this.build_graph(dot, item, current_id)

                elif hasattr(value, "__dict__"):
                    this.build_graph(dot, value, current_id)

                else:
                    leaf_id = str(this.iden)
                    this.iden += 1
                    dot.node(leaf_id, f"{key}: {value}")
                    dot.edge(current_id, leaf_id)

   
   
    
# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = KanGUI(root)
    root.mainloop()
