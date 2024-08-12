## Menttorix: Your AI-Powered Study Buddy - Made by Students for Students

**Menttorix is an alleged python application designed to revolutionize the way students learn, crafted with a deep understanding of the challenges students face.**  Built for the Google Gemini Hackathon, Menttorix leverages the power of Google Gemini AI to provide a comprehensive learning experience that includes an AI-powered chat agent equipped with advanced mathematical tools, intelligent quiz generation, and personalized spaced repetition flashcards.

**Live Demo pf quiz/flashcard:**  https://quiz-flash.onrender.com

### **Hackathon Category:**

This application primarily targets the **"Most Useful App"** category due to its direct and practical impact on everyday student life:

* **Automates repetitive tasks:** Quiz generation from various sources, AI-powered flashcard creation, and code execution in a safe sandbox environment.
* **Streamlines essential activities:** Personalized spaced repetition flashcards optimize study time, and the AI chat agent provides immediate support and answers.
* **Provides tailored experiences:**  Quizzes and flashcards are adapted to the user's background and learning progress, offering a customized learning journey. 

**Menttorix also embodies the spirit of the "Most Creative App" category:**

* **Shatters expectations:**  Combines the power of an AI chat agent with advanced tools, quiz generation, spaced repetition, and audio interaction into a uniquely comprehensive learning tool.
* **Redefines the boundaries:**  Utilizes Google Gemini's cutting-edge capabilities to offer a personalized, interactive, and intuitive learning experience that rivals more established platforms.

### **Addressing Socioeconomic Inequality:**

As students ourselves, we understand that access to quality educational resources can be a significant barrier for students facing socioeconomic disadvantages. Menttorix aims to bridge this gap by providing a **free and readily accessible platform** that offers:

* **Personalized Learning Support:** The AI chat agent acts as a readily available tutor, providing assistance with complex mathematical problems, generating diagrams, and explaining concepts in a clear and concise manner.
* **Adaptive Quizzing & Flashcards:** These tools adapt to individual learning paces and identify knowledge gaps, ensuring students from all backgrounds can progress at their own pace and achieve mastery of the material.
* **Reduced Dependence on Expensive Resources:** By offering AI-powered tools that can answer questions, solve problems, and generate study materials, Menttorix reduces the need for costly tutors or supplementary resources.

### **Key Features:**

* **AI Chat Agent with Advanced Tools:** Engage in natural conversations with Menttorix, your friendly AI study buddy. 
    * Ask questions across various subjects, including complex mathematical queries.
    * Leverage integrated mathematical tools for solving equations, factorizations, derivatives, limits, matrix operations, and even physics problems (kinematics, projectile motion, etc.). 
    * Request basic diagrams to visualize concepts and relationships.
    * Execute code safely within a sandbox environment to explore programming concepts.
* **Intelligent Quiz Generation:** Generate personalized quizzes from diverse sources:
    * **Topic & Subject:**  Test your knowledge on specific topics within a broader subject.
    * **Text Documents:**  Upload or paste text and let Menttorix create challenging questions based on the content.
    * **Images:**  Analyze images and generate visually-oriented quizzes.
    * **Web Links:**  Provide a URL, and Menttorix will crawl the webpage and craft a quiz based on its content.
* **Spaced Repetition Flashcards:** Create flashcards from missed quiz questions or manually input your own. Menttorix's spaced repetition algorithm optimizes your review schedule, focusing your efforts on the cards you need to practice most.
* **Live Audio Interaction:**  Experience a more natural and engaging learning session with Menttorix's voice interaction. Ask questions and receive spoken responses, making learning more interactive and accessible.
* **Personalized Learning:** Menttorix adapts to your individual learning style and progress, tailoring quizzes and flashcard review schedules to maximize your understanding and retention.

### **The Algorithm - Powering Personalized Learning:**

Menttorix utilizes a combination of cutting-edge algorithms:

* **Spaced Repetition Algorithm:**  Optimizes flashcard review schedules to enhance knowledge retention. The algorithm adjusts the intervals between reviews based on your performance, ensuring efficient and effective learning. 
* **Difficulty Level Adjustment (Quizzes):**  Quizzes are dynamically adjusted based on your performance. The system analyzes your answers and adapts the difficulty level of subsequent questions to challenge you appropriately.

### **How Google Gemini Makes it Possible:**

Menttorix relies on the power of Google Gemini's advanced AI capabilities:

* **Natural Language Understanding & Generation:**  Powers the conversational chat agent, allowing it to comprehend complex questions and provide detailed, supportive responses.
* **Contextual Reasoning & Knowledge Extraction:**  Enables quiz generation from diverse sources by analyzing text, images, and web content, identifying key concepts, and formulating challenging questions.
* **Multi Modal Capabilities like Image Understanding & Analysis:**  Allows Menttorix to extract information from images and create visual-based quizzes.
* **Personalized Recommendations & Adaptations:**  Delivers adaptive learning experiences by personalizing quiz difficulty and flashcard review schedules based on individual performance.

### **Technical Implementation:**

Menttorix is built using a robust technology stack:

* **Backend:**  FastAPI (Python)
* **Database:**  Firestore (Firebase)
* **AI Engine:**  Google Gemini (Gemini-1.5-flash model)
* **Web Scraping:**  Firecrawl & Tavily
* **Audio Interaction:**  Deepgram
* **Agent framework:** LangGraph and Langchain
* **Tracking:** Langsmith

### **Running the Application:**

1. **Clone the repository:**  `git clone https://github.com/your-username/menttorix`
2. **Install dependencies:**  `pip install -r requirements.txt`
4. **Set up environment variables:** Create a `.env` file and add your Deepgram, Gemini, and Firecrawl API keys:
```
GOOGLE_API_KEY=your gemini api key
LANGCHAIN_API_KEY=langsmith api key
LANGCHAIN_TRACING_V2='true'
LANGCHAIN_PROJECT="Menttorix AI"
TAVILY_API_KEY=
DEEPGRAM_API_KEY=
```
5. **Run the app.py:**  run the app.py and follow the on screen instruction

### **Using the Flashcard/Quiz Routes:**

The following routes are available for interacting with the flashcard and quiz features that is already deployed:
Flashcards:
POST /users/{user_id}/flashcards: Create a new flashcard.
POST /users/{user_id}/flashcards/bulk: Create multiple flashcards in bulk.
POST /users/{user_id}/flashcards/generate: Generate flashcards based on a text message, uploaded document, or image using AI.
GET /users/{user_id}/flashcards/due: Retrieve flashcards due for review.
PUT /users/{user_id}/flashcards/{flashcard_id}: Update a flashcard's review information (quality rating).
Quizzes:
POST /users/{user_id}/quizzes: Create a quiz folder to store generated quizzes.
POST /users/{user_id}/quizzes/{quiz_id}/generate_quiz: Generate a quiz from text content.
POST /users/{user_id}/quizzes/{quiz_id}/generate_quiz_link: Generate a quiz from a web link.
POST /users/{user_id}/quizzes/{quiz_id}/generate_quiz_topic: Generate a quiz on a specific topic.
POST /users/{user_id}/quizzes/{quiz_id}/generate_quiz_image: Generate a quiz from an image.
POST /users/{user_id}/quizzes/{quiz_id}/generate_quiz_document: Generate a quiz from an uploaded document.

### **Impact and Potential:**

Menttorix has the potential to revolutionize the learning landscape by:

* **Democratizing access to quality learning:** By providing free and effective AI-powered tools, Menttorix helps level the playing field for students from all socioeconomic backgrounds.
* **Creating a more engaging and effective learning experience:** Menttorix fosters active learning through interactive quizzes, AI-powered flashcards, and a supportive chat agent, making the learning process more enjoyable and productive.
* **Boosting knowledge retention and academic performance:** Spaced repetition and adaptive quizzing algorithms promote long-term understanding and help students achieve better academic outcomes. 

**Future Improvements:**

* **Interactive and responsive UI** Develop a relatable and interactive UI for the app 
* **Enhanced AI Chat Agent:**  Develop a more robust and versatile AI agent capable of handling a wider range of tasks, such as providing personalized study plans, generating summaries, and offering real-time feedback.
* **Real-time Interaction:** Explore integration with real-time audio/video streaming technologies, similar to Google Project Astra and OpenAI's GPT Omni, to enable even more natural and interactive learning experiences.

**Menttorix is a testament to the power of student innovation, driven by a mission to empower learners of all backgrounds with the tools they need to succeed.**  By leveraging the cutting-edge capabilities of Google Gemini AI, we're creating a future where learning is personalized, accessible, and engaging for everyone.
