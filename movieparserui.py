
import streamlit as st
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
    st.error("GOOGLE_API_KEY is missing. Check your .env file.")
    st.stop()


# -----------------------------------
# 2. Create Gemini model
# -----------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key
)


# -----------------------------------
# 3. Define Movie structure
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
# 4. Create parser
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
# 6. Streamlit page
# -----------------------------------

st.set_page_config(
    page_title="Movie Information Extractor",
    page_icon="🎬",
    layout="centered"
)


# -----------------------------------
# 7. Title
# -----------------------------------

st.title("🎬 Movie Information Extractor")

st.write(
    "Enter a movie paragraph and Gemini will extract "
    "structured movie information from it."
)


# -----------------------------------
# 8. Input paragraph
# -----------------------------------

paragraph = st.text_area(
    "Enter movie paragraph:",
    placeholder="Example: Inception is a 2010 science fiction film..."
)


# -----------------------------------
# 9. Extract button
# -----------------------------------

if st.button("🎯 Extract Movie Information"):

    if not paragraph.strip():

        st.warning("Please enter a movie paragraph first.")

    else:

        with st.spinner("Analyzing movie information..."):

            try:

                # Create prompt
                final_prompt = prompt.invoke({

                    "paragraph": paragraph,

                    "format_instructions":
                        parser.get_format_instructions()

                })

                # Send to Gemini
                response = model.invoke(final_prompt)


                # -----------------------------------
                # Extract actual text from response
                # -----------------------------------

                content = response.content

                if isinstance(content, list):

                    content = "".join(
                        item.get("text", "")
                        for item in content
                        if isinstance(item, dict)
                        and item.get("type") == "text"
                    )


                # -----------------------------------
                # Parse into Movie object
                # -----------------------------------

                movie_data = parser.parse(content)


                # -----------------------------------
                # Display result
                # -----------------------------------

                st.success("Movie information extracted successfully!")

                st.subheader("🎬 Movie Information")


                st.write(
                    f"**Title:** {movie_data.title}"
                )

                st.write(
                    f"**Release Year:** "
                    f"{movie_data.release_year or 'Not available'}"
                )

                st.write(
                    f"**Genre:** "
                    f"{', '.join(movie_data.genre)}"
                )

                st.write(
                    f"**Director:** "
                    f"{movie_data.director or 'Not available'}"
                )

                st.write(
                    f"**Cast:** "
                    f"{', '.join(movie_data.cast)}"
                )

                st.write(
                    f"**Rating:** "
                    f"{movie_data.rating or 'Not available'}"
                )


                st.subheader("📝 Summary")

                st.write(movie_data.summary)


                # -----------------------------------
                # Show raw structured object
                # -----------------------------------

                with st.expander("View structured Movie object"):

                    st.json(movie_data.model_dump())


            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )
