try:
    response = model.invoke(messages)
    print("Bot:", response.content)

except Exception as e:
    if "429" in str(e):
        print("Mistral API rate limit reached. Please try again later.")
    else:
        print("Error:", e)