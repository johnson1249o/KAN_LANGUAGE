from openai import OpenAI

client = OpenAI(api_key= "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")

class AICompare:

    @staticmethod
    def analyze(code):

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert compiler assistant for the KAN programming language. Analyze code and predict execution output."
                },
                {
                    "role": "user",
                    "content": f"Analyze this KAN code and predict its output:\n{code}"
                }
            ]
        )

        return response.choices[0].message.content


    @staticmethod
    def compare(compiler_output, ai_output):

        if compiler_output.strip() in ai_output:
            return "✅ MATCH — AI agrees with compiler"
        else:
            return "❌ DIFFERENT — AI output differs"
