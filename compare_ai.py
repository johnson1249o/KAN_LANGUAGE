import google.generativeai as genai

# Setup your Gemini API Key here
genai.configure(api_key="AIzaSyDqKOq-VX_lDxDsZcuY_kxD3aEODPBlMNk")

class AICompare:
    @staticmethod
    def analyze(code):
        try:
            # Initialize the Gemini Flash model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Construct the prompt with instructions for the KAN language
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
        # Cleans up whitespace for a more accurate comparison
        clean_compiler = compiler_output.strip()
        
        if not clean_compiler:
            return "⚠️ No compiler output to compare."

        # Checks if the compiler's specific result string exists within the AI's explanation
        if clean_compiler in ai_output:
            return "✅ MATCH — Gemini agrees with the compiler's result."
        else:
            return "❌ DISCREPANCY — Gemini predicts a different outcome."
