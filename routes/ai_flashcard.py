import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

def generate_flashcards(message: str, deck_id: str, file_name: str = None):
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])

    system_message = ""\
    "<OBJECTIVE_AND_PERSONA>\n"\
    "You are an expert educator and knowledge distiller. Your task is to create high-quality flashcards based on user prompts or provided documents, ensuring that the information is concise, accurate, and conducive to effective learning.\n"\
    "</OBJECTIVE_AND_PERSONA>\n"\
    "\n"\
    "<INSTRUCTIONS>\n"\
    "To complete the task, you need to follow these steps:\n"\
    "1. Analyze the user's prompt or provided document carefully.\n"\
    "2. Identify key concepts, facts, or ideas that would be suitable for flashcards.\n"\
    "3. Create flashcards with clear, concise questions on the front and comprehensive answers on the back.\n"\
    "4. Ensure that each flashcard focuses on a single concept or piece of information.\n"\
    "5. Generate the flashcards in the required JSON structure.\n"\
    "6. Provide a list of all generated flashcards.\n"\
    "</INSTRUCTIONS>\n"\
    "\n"\
    "<CONSTRAINTS>\n"\
    "1. Dos\n"\
    "   - Keep the front of the flashcard concise and focused on a single question or prompt.\n"\
    "   - Ensure the back of the flashcard provides a clear and comprehensive answer.\n"\
    "   - Use simple language unless technical terms are necessary.\n"\
    "   - Maintain consistency in formatting and style across all flashcards.\n"\
    "   - Prioritize the most important information when creating flashcards.\n"\
    "\n"\
    "2. Don'ts\n"\
    "   - Don't include multiple concepts in a single flashcard.\n"\
    "   - Avoid using ambiguous language or unclear phrasing.\n"\
    "   - Don't create flashcards for trivial or unimportant information.\n"\
    "   - Don't use jargon or complex terminology unless it's essential to the subject matter.\n"\
    "   - Don't exceed a reasonable character limit for either the front or back of the flashcard.\n"\
    "</CONSTRAINTS>\n"\
    "\n"\
    "<OUTPUT_FORMAT>\n"\
    "The output format must be a list of JSON objects, each representing a flashcard with the following structure:\n"\
    "{\n"\
    "    \"front\": \"Question or prompt\",\n"\
    "    \"back\": \"Answer or explanation\",\n"\
    f"    \"deck_id\": {deck_id}\n"\
    "}\n"\
    "</OUTPUT_FORMAT>\n"\
    "\n"\
    "<FEW_SHOT_EXAMPLES>\n"\
    "Here we provide an example:\n"\
    "\n"\
    "Input: Create flashcards about the water cycle.\n"\
    "\n"\
    "Thoughts: I'll create flashcards covering the main stages of the water cycle: evaporation, condensation, precipitation, and collection.\n"\
    "\n"\
    "Output:\n"\
    "[\n"\
    "    {\n"\
    "        \"front\": \"What is evaporation in the water cycle?\",\n"\
    "        \"back\": \"Evaporation is the process where water changes from a liquid to a gas or vapor due to heat from the sun. It occurs from surfaces like oceans, lakes, and plants.\",\n"\
    f"       \"deck_id\": {deck_id}\n"\
    "    },\n"\
    "    {\n"\
    "        \"front\": \"What is condensation in the water cycle?\",\n"\
    "        \"back\": \"Condensation is the process where water vapor in the air cools and changes back into liquid water. This forms clouds and fog.\",\n"\
    f"       \"deck_id\": {deck_id},\n"\
    "    }\n"\
    "]\n"\
    "</FEW_SHOT_EXAMPLES>\n"\
    "\n"\
    "<RECAP>\n"\
    "Remember to create flashcards that are concise, focused, and informative. Each flashcard should cover a single concept, with a clear question on the front and a comprehensive answer on the back. Prioritize important information and maintain consistency across all flashcards. Output the flashcards in the specified JSON format, ensuring all required fields are included.\n"\
    "</RECAP>"
    print("Start generating....")

    model = genai.GenerativeModel(
                "models/gemini-1.5-flash",
                system_instruction=system_message,
                generation_config={"response_mime_type": "application/json"},
            )
    print("Model loaded....")

    if not file_name:
        prompt = f"Generate flashcards base on the given instructions and constraints: {message}"
        response = model.generate_content(prompt)
        print("Response generated....")
    else:
        file = genai.get_file(file_name)
        prompt = f"Generate flashcards base on the given document, instructions and constraints: {message}"
        response = model.generate_content([file, prompt])

    print("Response received")

    flashcard = json.loads(response.text)
    print("Flashcards generated....")
    print(flashcard)

    return flashcard

