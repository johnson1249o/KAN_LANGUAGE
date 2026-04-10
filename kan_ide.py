
from compare_ai import AICompare
from kan_semantic import analyze, format_results

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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
    def display(this):
        # Top Frame (Editor)
        frame1 = tk.Frame(this.root)
        frame1.pack(fill="both", expand=True)

        this.sec = tk.Text(frame1, height=20, font=("Consolas", 11))
        this.sec.pack(fill="both", expand=True, padx=10, pady=10)

        frame2 = tk.Frame(this.root) #frames for button
        frame2.pack(pady=5)

        tk.Button(frame2, text="Run", command=this.Process).grid(row=0, column=0, padx=5)
        tk.Button(frame2, text="Tokens", command=this.Token).grid(row=0, column=1, padx=5)
        tk.Button(frame2, text="Parse Tree", command=this.pr_tree).grid(row=0, column=2, padx=5)
        tk.Button(frame2, text="Ask AI", command=this.compare_ai).grid(row=0, column=3, padx=5)
    

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

    def pr_tree(this):
        from kan_yacc import parse_log
        c_ode = this.sec.get("1.0", tk.END)

        try:
            parse_log.clear()
            parser.parse(c_ode)

            this.output.delete("1.0", tk.END)
            this.output.insert(tk.END, "\n".join(parse_log))

        except Exception as e:
            messagebox.showerror("Parse Tree Error", str(e))

    def compare_ai(this):
        code = this.sec.get("1.0", tk.END)

        try:
            # Run compiler first
            ast = parser.parse(code)
            results = []

            for stmt in ast:
                res = stmt()
                if res is not None:
                    results.append(str(res))

            compiler_output = "\n".join(results)

            # Ask AI
            ai_output = AICompare.analyze(code)

            # Compare
            comparison = AICompare.compare(compiler_output, ai_output)

            # Show results
            this.output.delete("1.0", tk.END)
            this.output.insert(
                tk.END,
                "=== Compiler Output ===\n"
                + compiler_output +
                "\n\n=== AI Output ===\n"
                + ai_output +
                "\n\n=== Comparison ===\n"
                + comparison
            )

        except Exception as e:
            messagebox.showerror("AI Compare Error", str(e))



    def run_code(self):
        code = self.code_area.get("1.0", tk.END)

        errors = analyze(code)

        if errors:
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, format_results(errors))
            return

        try:
            ast = parser.parse(code)

            results = []
            for stmt in ast:
                res = stmt()
                if res is not None:
                    results.append(str(res))

            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "\n".join(results))

        except Exception as e:
            messagebox.showerror("Runtime Error", str(e))
   
    

if __name__ == "__main__":
    root = tk.Tk()
    app = KanGUI(root)
    root.mainloop()

