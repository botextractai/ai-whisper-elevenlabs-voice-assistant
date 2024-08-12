# Voice assistant with audio input and audio output using Whisper and Eleven Labs

This example is a question/answer chatbot using an OpenAI GPT model, Activeloop's Deep Lake vector database, and the Whisper API for voice transcription. The chatbot also uses the Eleven Labs API to generate audio responses.

This example first downloads (scrapes) the user manual for the performance test software [Apache JMeter](https://jmeter.apache.org/). This user manual comes in the form of multiple web pages.

The text from the scraped user manual web pages then gets embedded into a Deep Lake vector database, which facilitates efficient indexing and retrieval of text.

[Streamlit](https://streamlit.io/) is a Python based framework for constructing web applications focusing on data visualisation. It offers a user-friendly approach to developing interactive web applications. It is particularly useful for machine learning and data science projects.

You can use the Streamlit web interface to record a query against the ingested knowledge base of the Apache JMeter user manual using your microphone. The audio file from your recording gets transcribed to text by the Whisper API. Alternatively to recording and transcribing your query, you can also simply just type your query.

You will get a response on the Streamlit web interface as text and as audio response. The audio response uses the Eleven Labs API to translate the text response to speech and give it a voice. This speech output, in MP3 format, is then played back on the Streamlit web interface.

For this example, you will need API keys from OpenAI, Eleven Labs, and Activeloop (the Activeloop API key is called a "token"). In addition to this, you will also need to know your Activeloop Organization ID (your Activeloop user name).

You need to insert all of these 4 pieces of information in the `.env.example` file and then rename this file to just `.env` (remove the ".example" ending).

- [Get your OpenAI API key here](https://platform.openai.com/login).
- [Get your Eleven Labs API key here](https://elevenlabs.io/app/sign-in). Please note that the Eleven Labs free plan is limited to 10000 characters per month.
- [Get your Activeloop API key (token) and your Activeloop Organization ID here](https://auth.activeloop.ai/login).

## How to run and use this example

Please follow these steps to set up and run this example:

1. Run the  
   `scrape.py`  
   script to embed articles about the performance test software [Apache JMeter](https://jmeter.apache.org/) into Deep Lake.

2. Start the Streamlit web interface with this command:  
   `streamlit run chat.py`  
   When you execute this command, it will launch a local web server and provide you with a URL where your application can be browsed. Your application will run as long as the command in your terminal is active, and it will terminate when you stop the command, or close the terminal.

3. An example query is:  
   `What are listeners in Apache JMeter?`  
   If you have a microphone, you can click the record button and transcribe your audio. Click the transcribe button to get the text. Alternatively, you can also simply just type your query.  
   The Streamlit web interface will display the response in the chat history, and it will also be spoken using the Eleven Labs API.

![alt text](https://github.com/user-attachments/assets/5b99f8e2-748a-467a-b621-e11a44258756 "Streamlit voice assistant")
