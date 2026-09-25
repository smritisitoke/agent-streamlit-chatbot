
from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from pydantic import BaseModel
from typing import List, Optional


# -----------------------------------
# 1. Load API key
# -----------------------------------

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY is missing. Add it to your .env file."
    )


# -----------------------------------
# 2. Create Gemini model
# -----------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key
)


# -----------------------------------
# 3. Define the structure
# -----------------------------------

class Movie(BaseModel):

    title: str
    release_year: Optional[int] = None
    genre: List[str]
    director: Optional[str] = None
    cast: List[str]
    rating: Optional[float] = None
    summary: str


# -----------------------------------
# 4. Create Pydantic parser
# -----------------------------------

parser = PydanticOutputParser(
    pydantic_object=Movie
)


# -----------------------------------
# 5. Create prompt
# -----------------------------------

prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        Extract movie information from the paragraph.

        Return the information according to the required format.

        {format_instructions}
        """
    ),

    (
        "human",
        "{paragraph}"
    )

])


# -----------------------------------
# 6. Get paragraph from user
# -----------------------------------

paragraph = input("\nGive your paragraph: ")


# -----------------------------------
# 7. Create final prompt
# -----------------------------------

final_prompt = prompt.invoke({

    "paragraph": paragraph,

    "format_instructions":
        parser.get_format_instructions()

})


# -----------------------------------
# 8. Send to Gemini
# -----------------------------------

response = model.invoke(final_prompt)


# -----------------------------------
# 9. Extract only the text
# -----------------------------------

def extract_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        texts = []

        for item in content:

            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))

        return "\n".join(texts)

    return str(content)


content = extract_text(response.content)


# -----------------------------------
# 10. Convert response into Movie object
# -----------------------------------

movie_data = parser.parse(content)


# -----------------------------------
# 11. Display result
# -----------------------------------

print("\nMovie Information:")
print(movie_data)
