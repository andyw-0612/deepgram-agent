from groq import Groq
from utils import print_debug
import asyncio

class GroqLLM:
    """
    handles interaction with groq language model
    maintains conversation history and generates responses
    """
    def __init__(self, api_key: str):
        # initialize groq client and conversation history
        self.client = Groq(api_key=api_key)
        self.conversation_history = []
        print_debug("SYSTEM", "Groq LLM initialized")

    async def generate_response(self, text: str) -> str:
        """
        generate response from groq llm using conversation history
        returns error message if generation fails
        """
        # add user message to conversation history
        self.conversation_history.append({"role": "user", "content": text})

        try:
            print_debug("DEBUG", "Sending request to Groq...")
            # generate response using groq api
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="llama-3.2-3b-preview",
                messages=self.conversation_history,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None
            )

            response = completion.choices[0].message.content
            # add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            return response

        except Exception as e:
            print_debug("SYSTEM", f"Groq LLM Error: {e}")
            return f"Error generating response: {str(e)}"
