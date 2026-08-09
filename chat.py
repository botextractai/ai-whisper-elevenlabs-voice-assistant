import openai
import os
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from streamlit_chat import message

# Load environment variables from the .env file
load_dotenv()

# Constants
TEMP_AUDIO_PATH = "temp_audio.wav"
AUDIO_FORMAT = "audio/wav"

openai_api_key = os.environ.get('OPENAI_API_KEY')
speechify_api_key = os.environ.get('SPEECHIFY_API_KEY')
dataset_path = 'hub://' + os.environ.get('ACTIVELOOP_ORG_ID') + '/voice-assistant'

# Initialize Speechify client
speechify_client = Speechify(token=speechify_api_key) if speechify_api_key else None

def filter_voice_models(voices, *, gender=None, locale=None, tags=None):
    """
    Filter Speechify voices by gender, locale, and/or tags,
    and return the list of voice IDs for matching voices.

    Args:
        voices (list): List of voice objects.
        gender (str, optional): e.g. 'male', 'female'.
        locale (str, optional): e.g. 'en-US'.
        tags (list, optional): list of tags, e.g. ['timbre:deep', 'use-case:advertisement'].

    Returns:
        list[str]: IDs of matching voices.
    """
    results = []

    for voice in voices:
        # gender filter
        if gender and getattr(voice, 'gender', '').lower() != gender.lower():
            continue

        # For now, we'll include all voices since the structure might be different
        # We can refine this later based on the actual voice object structure
        voice_id = getattr(voice, 'id', None)
        if voice_id:
            results.append(voice_id)

    return results

def get_available_voices():
    """
    Get available voices from Speechify API.
    Returns a list of voice objects or None if API key is not configured.
    """
    if not speechify_client:
        return None
    
    try:
        voices_response = speechify_client.tts.voices.list()
        return voices_response  # The response is already a list
    except Exception as e:
        print(f"Error fetching voices: {str(e)}")
        return None

def load_embeddings_and_database(active_loop_data_set_path):
    embeddings = OpenAIEmbeddings()
    db = DeepLake(
        dataset_path=active_loop_data_set_path,
        read_only=True,
        embedding_function=embeddings
    )
    return db

# Transcribe audio using OpenAI Whisper API
def transcribe_audio(audio_file_path, openai_key):
    openai.api_key = openai_key
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
        return response["text"]
    except Exception as e:
        print(f"Error calling Whisper API: {str(e)}")
        return None

# Record audio using audio_recorder and transcribe using transcribe_audio
def record_and_transcribe_audio():
    audio_bytes = audio_recorder()
    transcription = None
    if audio_bytes:
        st.audio(audio_bytes, format=AUDIO_FORMAT)
        with open(TEMP_AUDIO_PATH, "wb") as f:
            f.write(audio_bytes)
        if st.button("Transcribe"):
            transcription = transcribe_audio(TEMP_AUDIO_PATH, openai_api_key)
            os.remove(TEMP_AUDIO_PATH)
            display_transcription(transcription)
    return transcription

# Display the transcription of the audio on the app
def display_transcription(transcription):
    if transcription:
        st.write(f"Transcription: {transcription}")
        with open("audio_transcription.txt", "w+") as f:
            f.write(transcription)
    else:
        st.write("Error transcribing audio.")

# Get user input from Streamlit text input field
def get_user_input(transcription):
    return st.text_input("", value=transcription if transcription else "", key="input")

# Search the database for a response based on the user's query
def search_db(user_input, db):
    print(user_input)
    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 100
    retriever.search_kwargs['maximal_marginal_relevance'] = True
    retriever.search_kwargs['k'] = 4
    model = ChatOpenAI(model_name='gpt-3.5-turbo')
    qa = RetrievalQA.from_llm(model, retriever=retriever, 
    return_source_documents=True)
    return qa({'query': user_input})

# Display conversation history using Streamlit messages
def display_conversation(history):
    for i in range(len(history["generated"])):
        message(history["past"][i], is_user=True, key=str(i) + "_user")
        message(history["generated"][i],key=str(i))
        # Voice using Speechify API
        if speechify_client:
            text = history["generated"][i]
            try:
                audio_response = speechify_client.tts.audio.speech(
                    audio_format="mp3",
                    input=text,
                    language="en-US",
                    model="simba-english",
                    options=GetSpeechOptionsRequest(
                        loudness_normalization=True,
                        text_normalization=True
                    ),
                    voice_id=st.session_state.get("selected_voice_id", "voice_id")
                )
                audio_bytes = base64.b64decode(audio_response.audio_data)
                st.audio(audio_bytes, format='audio/mp3')
            except Exception as e:
                st.error(f"Error generating speech: {str(e)}")
        else:
            st.warning("Speechify API key not configured. Audio generation disabled.")

# Main function to run the app
def main():
    # Initialise Streamlit app with a title
    st.write("# Voice Assistant")
    
    # Voice selection sidebar
    st.sidebar.header("Voice Settings")
    selected_voice_id = "voice_id"  # Default fallback
    
    if speechify_client:
        voices = get_available_voices()
        if voices:
            # Get all available voice IDs
            available_voices = filter_voice_models(voices)
            if available_voices:
                # Create a mapping of voice IDs to display names
                voice_options = {f"Voice {i+1} ({voices[i].gender if hasattr(voices[i], 'gender') else 'Unknown'})": voice_id 
                               for i, voice_id in enumerate(available_voices[:20])}  # Limit to first 20 voices
                
                selected_voice_name = st.sidebar.selectbox(
                    "Select Voice",
                    options=list(voice_options.keys()),
                    index=0
                )
                selected_voice_id = voice_options[selected_voice_name]
            else:
                st.sidebar.warning("No voices found")
        else:
            st.sidebar.warning("Could not fetch voices from Speechify")
    else:
        st.sidebar.warning("Speechify API key not configured")
    
    # Store selected voice in session state
    if "selected_voice_id" not in st.session_state:
        st.session_state["selected_voice_id"] = selected_voice_id
    else:
        st.session_state["selected_voice_id"] = selected_voice_id
    
    # Load embeddings and the DeepLake database
    db = load_embeddings_and_database(dataset_path)
    # Record and transcribe audio
    transcription = record_and_transcribe_audio()
    # Get user input from text input or audio transcription
    user_input = get_user_input(transcription)
    # Initialise session state for generated responses and past messages
    if "generated" not in st.session_state:
        st.session_state["generated"] = ["I am ready to help you"]
    if "past" not in st.session_state:
        st.session_state["past"] = ["Hey there!"]
    # Search the database for a response based on user input and update the session state
    if user_input:
        output = search_db(user_input, db)
        print(output['source_documents'])
        st.session_state.past.append(user_input)
        response = str(output["result"])
        st.session_state.generated.append(response)
    # Display conversation history using Streamlit messages
    if st.session_state["generated"]:
        display_conversation(st.session_state)

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
