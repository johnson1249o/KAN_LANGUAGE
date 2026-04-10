import google.generativeai as genai

# Setup your Gemini API Key here
genai.configure(api_key="AIzaSyCaqwRGbbTDSK26XRqtVJWQjET3lcg5OuQ")

class AICompare:
    @staticmethod
    def analyze(code):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            prompt = (
                "You are an expert compiler assistant for the KAN programming language. "
                "Analyze the following code and predict its execution output. "
                "Provide a brief analysis followed by the predicted output.\n\n"
                f"KAN Code:\n{code}"
            )
            
            # Generate the response
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"AI Error: {str(e)}"

    @staticmethod
    def compare(compiler_output, ai_output):
        clean_compiler = compiler_output.strip()

        if not clean_compiler:
            return "No compiler output to compare."

        if ai_output.startswith("AI Error:"):
            return "Comparison unavailable — AI did not respond successfully."

        if clean_compiler in ai_output:
            return "MATCH — Gemini agrees with the compiler's result."
        else:
            return "DISCREPANCY — Gemini predicts a different outcome."
