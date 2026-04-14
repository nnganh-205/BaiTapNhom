import os
import google.generativeai as genai
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class LLM:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def invoke(self, messages: list) -> AIMessage:
        # Separate system message from the rest of the conversation
        system_instruction = ""
        chat_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_instruction += msg.content + "\n"
            else:
                chat_messages.append(msg)

        # Convert LangChain messages to Gemini format
        gemini_history = []
        for i, msg in enumerate(chat_messages):
            if isinstance(msg, HumanMessage):
                # Prepend system instruction to the first user message if it exists
                content = msg.content
                if i == 0 and system_instruction:
                    content = f"{system_instruction.strip()}\n\n{content}"
                gemini_history.append({"role": "user", "parts": [content]})
            elif isinstance(msg, AIMessage):
                gemini_history.append({"role": "model", "parts": [msg.content]})

        # The last message in chat_messages is the new query
        new_query_content = ""
        if chat_messages and isinstance(chat_messages[-1], HumanMessage):
            new_query_content = chat_messages[-1].content
            # Remove the last message from history as it's the current query
            gemini_history = gemini_history[:-1]
        else:
            return AIMessage(content="Error: No user query found in messages.")

        try:
            chat_session = self.model.start_chat(history=gemini_history)
            response = chat_session.send_message(new_query_content)
            return AIMessage(content=response.text)
        except Exception as e:
            # Re-raise exception so the caller (_call_gemini) can fall back to the internal rule-based responder
            print(f"Error calling Gemini API: {e}")
            raise
