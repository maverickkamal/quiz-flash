import google.generativeai as genai
import json
import os
import time
import uuid


def string_to_file(content: str) -> str:
    """Writes the given string to a temporary file and returns the file path."""
    start_time = time.time()
    temp_file_path = os.path.join("/tmp", f"{uuid.uuid4()}.txt")
    with open(temp_file_path, "w", encoding="utf-8") as temp_file:
        temp_file.write(content)
    elapsed_time = time.time() - start_time
    print(f"Function executed in {elapsed_time:.2f} seconds")
    return temp_file_path



def generate_quiz(content, number_of_questions, question_type, user_data):
    """
    Generates a quiz based on the given content, number of questions, question type,
    and user data.

    Args:
        content (str): The content to base the quiz on.
        number_of_questions (int): The number of questions to generate.
        question_type (str): The type of questions to generate
            ("Multiple Choice", "True/False", "Fill in the space", "Short Answer", "Open End").
        user_data (dict): User-specific data to personalize the quiz.

    Returns:
        dict: The generated quiz in JSON format.
    """
    global temp_file_path
    try:
        # Configure Gemini API
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

        # Multiply the number of questions by 3 for diverse difficulty levels
        num = number_of_questions * 3

        multiple_choice_prompt = f"""
                OBJECTIVE_AND_PERSONA
                You are an expert quiz creator specializing in multiple-choice questions. Your task is to create a personalized multiple-choice quiz based on a given document, tailored to the user's background without directly referencing their personal details.

                INSTRUCTIONS
                To complete the task, you need to follow these steps:
                1. Thoroughly analyze the provided document.
                2. Generate {num} multiple-choice questions, evenly distributed across Easy, Medium, and Hard difficulty levels.
                3. Each question should have 4 options, with only one correct answer.
                4. Use the user's personal details to inform the relevance of questions, without including these details in the questions themselves.
                5. Format the quiz in JSON structure as specified in the OUTPUT_FORMAT section.

                CONSTRAINTS
                1. Dos
                - Strictly adhere to the content provided in the document
                - Ensure questions are relevant to the user's context
                - Maintain an equal distribution of difficulty levels
                - Make distractors (incorrect options) plausible
                2. Don'ts
                - Don't use personal info/house details in questions
                - Don't create questions unrelated to the document content
                - Don't make the correct answer obvious or stand out

                CONTEXT
                The quiz is based on the given document. The user's personal details are provided for context but should not be directly referenced in the questions.

                OUTPUT_FORMAT
                The output format must be:
                - Each question should include:
                {{
                "question": "Question",
                "answer": "correct answer",
                "options": ["option 1", "option 2", "option 3", "option 4"],
                "explanation": "explanation(explain why the answer is so and not restricted to the document)",
                "hint": "Short Hint",
                "difficulty": "Difficulty level(Easy, Medium, Hard)",
                "topic": "Topic on which the quiz was generated on",
                }}

                <FEW_SHOT_EXAMPLES>
                Here we provide an example Output:
                [
                {{
                    "question": "What is the process of converting raw data into a meaningful format called?",
                    "answer": "Data processing",
                    "options": ["Data mining", "Data warehousing", "Data cleansing", "Data processing"],
                    "explanation": "Data processing involves organizing, manipulating, and transforming raw data into a usable format.",
                    "hint": "Think about what happens to data before analysis.",
                    "difficulty": "Medium",
                    "topic": "Technology"
                }},
                {{
                    "question": "Which programming language is widely used for web development and is known for its simplicity?",
                    "answer": "Python",
                    "options": ["Java", "C++", "Python", "JavaScript"],
                    "explanation": "Python is a versatile language suitable for various applications including web development, data science, and machine learning.",
                    "hint": "Consider a language often used for data analysis and machine learning.",
                    "difficulty": "Easy",
                    "topic": "Technology"
                }}
                ]
                </FEW_SHOT_EXAMPLES>

                RECAP
                Remember to create {num} multiple-choice questions based solely on the document content. Use the user's background to inform relevance, but never include personal details in the questions. Maintain equal distribution of difficulty levels and ensure all questions have 4 options with only one correct answer.

            """
        true_false_prompt = f"""
            OBJECTIVE_AND_PERSONA
            You are a precision-focused quiz master specializing in True/False questions. Your task is to create a personalized True/False quiz based on a given document, tailored to the user's background without directly referencing their personal details.

            INSTRUCTIONS
            To complete the task, you need to follow these steps:
            1. Carefully analyze the provided document.
            2. Generate {num} True/False questions, evenly distributed across Easy, Medium, and Hard difficulty levels.
            3. Ensure a balanced mix of true and false statements.
            4. Use the user's personal details to inform the relevance of questions, without including these details in the questions themselves.
            5. Format the quiz in JSON structure as specified in the OUTPUT_FORMAT section.

            CONSTRAINTS
            1. Dos
            - Strictly adhere to the content provided in the document
            - Ensure questions are relevant to the user's context
            - Maintain an equal distribution of difficulty levels
            - Create clear, unambiguous statements
            2. Don'ts
            - Don't use personal info/house details in questions
            - Don't create questions unrelated to the document content
            - Don't use absolute terms like 'always' or 'never' unless explicitly true

            CONTEXT
            The quiz is based on the given document. The user's personal details are provided for context but should not be directly referenced in the questions.

            OUTPUT_FORMAT
            The output format must be:
            - Each question should include:
            {{
            "question": "Question",
            "answer": "correct answer",
            "options": ["True", "False"],
            "explanation": "explanation(explain why the answer is so and not restricted to the document)",
            "hint": "Short Hint",
            "difficulty": "Difficulty level(Easy, Medium, Hard)",
            "topic": "Topic on which the quiz was generated on",
            }}

            <FEW_SHOT_EXAMPLES>
            Here we provide an example Output:
            [
            {{
                "question": "Python is an interpreted language.",
                "answer": "True",
                "options": ["True", "False"],
                "explanation": "Python is an interpreted language, meaning code is executed line by line without requiring compilation.",
                "hint": "Think about how Python code runs.",
                "difficulty": "Easy",
                "topic": "Technology"
            }},
            {{
                "question": "HTML is a programming language.",
                "answer": "False",
                "options": ["True", "False"],
                "explanation": "HTML is a markup language used for structuring web content, not a programming language.",
                "hint": "Consider the purpose of HTML.",
                "difficulty": "Medium",
                "topic": "Technology"
            }}
            ]
            </FEW_SHOT_EXAMPLES>

            RECAP
            Remember to create {num} True/False questions based solely on the document content. Use the user's background to inform relevance, but never include personal details in the questions. Maintain equal distribution of difficulty levels and ensure a balanced mix of true and false statements.

        """
        fill_in_the_blank_prompt = f"""
            OBJECTIVE_AND_PERSONA
            You are a language expert specializing in Fill in the Blank questions. Your task is to create a personalized Fill in the Blank quiz based on a given document, tailored to the user's background without directly referencing their personal details.

            INSTRUCTIONS
            To complete the task, you need to follow these steps:
            1. Thoroughly analyze the provided document.
            2. Generate {num} Fill in the Blank questions, evenly distributed across Easy, Medium, and Hard difficulty levels.
            3. Use underscores to indicate blank spaces in the questions.
            4. Ensure answers are brief: single words or short phrases (maximum 5 words).
            5. Use the user's personal details to inform the relevance of questions, without including these details in the questions themselves.
            6. Format the quiz in JSON structure as specified in the OUTPUT_FORMAT section.

            CONSTRAINTS
            1. Dos
            - Strictly adhere to the content provided in the document
            - Ensure questions are relevant to the user's context
            - Maintain an equal distribution of difficulty levels
            - Make sure blanks test key concepts or information
            2. Don'ts
            - Don't use personal info/house details in questions
            - Don't create questions unrelated to the document content
            - Don't make answers longer than 5 words
            - Don't use more than one blank per question

            CONTEXT
            The quiz is based on the given document. The user's personal details are provided for context but should not be directly referenced in the questions.

            OUTPUT_FORMAT
            The output format must be:
            - Each question should include:
            {{
            "question": "question text (with blank indicated by underscores)",
            "answer": "correct answer (less than 5 words)",
            "explanation": "explanation(explain why the answer is so and not restricted to the document)",
            "hint": "Short Hint",
            "difficulty": "Difficulty level(Easy, Medium, Hard)",
            "topic": "Topic on which the quiz was generated on",
            }}

            <FEW_SHOT_EXAMPLES>
            Here we provide an example Output:
            [
            {{
                "question": "The central processing unit is the _____ of a computer.",
                "answer": "brain",
                "explanation": "The CPU is responsible for processing instructions and data, making it the 'brain' of a computer.",
                "hint": "Think about how Python code runs.",
                "difficulty": "Easy",
                "topic": "Technology"
            }},
            {{
                "question": "HTML stands for _____.",
                "answer": "Hypertext Markup Language",
                "explanation": "HTML is the standard markup language for creating web pages and web applications.",
                "hint": "Think of the language used to structure web content.",
                "difficulty": "Medium",
                "topic": "Technology"
            }}
            ]
            </FEW_SHOT_EXAMPLES>

            RECAP
            Remember to create {num} Fill in the Blank questions based solely on the document content. Use the user's background to inform relevance, but never include personal details in the questions. Maintain equal distribution of difficulty levels and ensure all answers are brief (1-5 words).

        """
        short_ans_prompt = f"""
            OBJECTIVE_AND_PERSONA
            You are a concise communication expert specializing in Short Answer questions. Your task is to create a personalized Short Answer quiz based on a given document, tailored to the user's background without directly referencing their personal details.

            INSTRUCTIONS
            To complete the task, you need to follow these steps:
            1. Carefully analyze the provided document.
            2. Generate {num} Short Answer questions, evenly distributed across Easy, Medium, and Hard difficulty levels.
            3. Ensure answers are brief: phrases or short sentences (maximum 15 words).
            4. Use the user's personal details to inform the relevance of questions, without including these details in the questions themselves.
            5. Format the quiz in JSON structure as specified in the OUTPUT_FORMAT section.

            CONSTRAINTS
            1. Dos
            - Strictly adhere to the content provided in the document
            - Ensure questions are relevant to the user's context
            - Maintain an equal distribution of difficulty levels
            - Create questions that require specific, concise answers
            2. Don'ts
            - Don't use personal info/house details in questions
            - Don't create questions unrelated to the document content
            - Don't make answers longer than 15 words
            - Don't create questions that could be answered with just 'yes' or 'no'

            CONTEXT
            The quiz is based on the given document. The user's personal details are provided for context but should not be directly referenced in the questions.

            OUTPUT_FORMAT
            The output format must be:
            - Each question should include:
            {{
            "question": "question text",
            "answer": "correct answer (less than 5 words)",
            "explanation": "explanation(explain why the answer is so and not restricted to the document)",
            "hint": "Short Hint",
            "difficulty": "Difficulty level(Easy, Medium, Hard)",
            "topic": "Topic on which the quiz was generated on",
            }}

            <FEW_SHOT_EXAMPLES>
            Here we provide an example Output:
            [
            {{
                "question": "What is the process of converting raw data into a meaningful format?",
                "answer": "Data Processing",
                "explanation": "Data processing involves organizing, manipulating, and transforming raw data into a usable format.",
                "hint": "Think about what happens to data before analysis.",
                "difficulty": "Medium",
                "topic": "Technology"
            }},
            {{
                "question": "What is the most popular programming language for web development?",
                "answer": "Python",
                "explanation": "Python is a versatile language suitable for various applications including web development, data science, and machine learning.",
                "hint": "Consider a language often used for data analysis and machine learning.",
                "difficulty": "Easy",
                "topic": "Technology"
            }}
            ]
            </FEW_SHOT_EXAMPLES>

            RECAP
            Remember to create {num} Short Answer questions based solely on the document content. Use the user's background to inform relevance, but never include personal details in the questions. Maintain equal distribution of difficulty levels and ensure all sample answers are concise (maximum 15 words).

        """
        open_ended_prompt = f"""
                OBJECTIVE_AND_PERSONA
                You are a critical thinking expert specializing in Open-Ended questions. Your task is to create a personalized 
                Open-Ended quiz based on a given document, tailored to the user's background without directly referencing their 
                personal details.
                INSTRUCTIONS
                To complete the task, you need to follow these steps:
                1. Thoroughly analyze the provided document.
                2. Generate {num} Open-Ended questions, evenly distributed across Easy, Medium, and Hard difficulty levels.
                3. Create questions that encourage analytical thinking, interpretation, or application of knowledge.
                4. Use the user's personal details to inform the relevance of questions, without including these details in the 
                questions themselves.
                5. Format the quiz in JSON structure as specified in the OUTPUT_FORMAT section.
                CONSTRAINTS
                1. Dos
                - Strictly adhere to the content provided in the document
                - Ensure questions are relevant to the user's context
                - Maintain an equal distribution of difficulty levels
                - Create questions that promote critical thinking and in-depth responses
                2. Don'ts
                - Don't use personal info/house details in questions
                - Don't create questions unrelated to the document content
                - Don't create questions with single correct answers
                - Don't make questions that can be answered with 'yes' or 'no'
                CONTEXT
                The quiz is based on the given document. The user's personal details are provided for context but should not be 
                directly referenced in the questions.
                OUTPUT_FORMAT
                The output format must be:
                - Each question should include:
                {{
                "question": "Question",
                "suggestedResponseLength": "suggested response length (Brief|Moderate|Extensive)",
                "keyPoints": "key points (3-5 points that a good answer might cover)",
                "explanation": "explanation(explain why the answer is so and not restricted to the document)",
                "difficulty": "Difficulty level(Easy, Medium, Hard)",
                "topic": "Topic on which the quiz was generated on",
                }}

                <FEW_SHOT_EXAMPLES>
                Here we provide an example Output:
                [
                {{
                    "question": "What are the key benefits of cloud computing?",
                    "suggestedResponseLength": "Moderate",
                    "keyPoints": ["Cost-effectiveness", "Scalability", "Accessibility", "Data security"],
                    "explanation": "Cloud computing offers a range of advantages including reduced IT infrastructure costs, flexible resource allocation, remote access, and enhanced data protection.",
                    "difficulty": "Easy",
                    "topic": "Technology"
                }},
                {{
                    "question": "Discuss the ethical implications of artificial intelligence.",
                    "suggestedResponseLength": "Extensive",
                    "keyPoints": ["Job Displacement", "Privacy concerns", "Bias and discrimination", "Autonomous weapons"],
                    "explanation": "AI has the potential to revolutionize various industries, but it also raises ethical questions about its impact on society, employment, privacy, and human rights.",
                    "difficulty": "Medium",
                    "topic": "Technology"
                }}
                ]
                </FEW_SHOT_EXAMPLES>

                RECAP
                Remember to create {num} Open-Ended questions based solely on the document content. Use the user's background 
                to inform relevance, but never include personal details in the questions. Maintain equal distribution of 
                difficulty levels and ensure all questions encourage critical thinking and in-depth responses.
            """

        # Define prompts based on question type
        prompts = {
            "Multiple Choice": multiple_choice_prompt,
            "True/False": true_false_prompt,
            "Fill in the space": fill_in_the_blank_prompt,
            "Open End": open_ended_prompt,
            "Short Answer": short_ans_prompt,
        }

        # Select the appropriate prompt
        selected_prompt = prompts.get(question_type)
        if not selected_prompt:
            raise ValueError(f"Invalid question type: {question_type}")

        # Fill in the prompt with the correct number of questions
        # filled_prompt = selected_prompt.format(num=num)

        # Save content to a temporary file
        temp_file_path = string_to_file(content)

        # Upload the file to Gemini
        try:
            files = genai.upload_file(
                temp_file_path, display_name="content.txt", mime_type="text/plain"
            )
            print(f"Uploaded file '{files.display_name}' as: {files.uri}")
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to Gemini: {str(e)}")

        # Generate quiz using Gemini API
        model = genai.GenerativeModel(
            "models/gemini-1.5-flash",
            system_instruction=f"Your given name is menttorix and you are an AI Buddy. "
            f"You are great at generating quizzes. "
            f"Use the following personal details to personalize the quiz to be unique to the user: "
            f"{user_data}. Don't use it in making the quiz.",
            generation_config={"response_mime_type": "application/json"},
        )

        # Generate content
        response = model.generate_content([files, selected_prompt])

        # Parse and return the generated quiz
        quiz = json.loads(response.text)
        return quiz

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse quiz JSON: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An error occurred during quiz generation: {str(e)}")
    finally:
        # Clean up the temporary file
        if "temp_file_path" in locals():
            os.unlink(temp_file_path)