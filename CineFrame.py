# app.py
import streamlit as st
from langchain_openai import OpenAI as LangChainOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from openai import OpenAI
from moviepy.editor import ImageClip, concatenate_videoclips
import os
import requests

#Set openAI API Key
api_key = "Enter Your OpenAI API key"

#Intialize openAI Client
client = OpenAI(api_key = api_key)


# Define a function to get a response from ChatGPT
def get_chatgpt_response(input_text, max_tokens=4000):
    # Initialize the OpenAI LLM with your API key
    llm = LangChainOpenAI(openai_api_key=api_key, max_tokens=max_tokens)
    
    # Define a prompt template
    prompt_template = PromptTemplate(input_variables=["input_text"], template="{input_text}")
    
    # Create an LLM chain with the OpenAI LLM and the prompt template
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    # Get the response from the chain
    response = chain.run({"input_text": input_text})
    
    return response

#Define function to generate images using DALL-E
def generate_images(prompt):
    response = client.images.generate(
        model = "dall-e-3",
        prompt = prompt,
        size = "1024x1024",
        quality = "standard",
        n = 1,
        )
    return response.data[0].url 

def update_genres(input_genre):
    genres = ""
    for genre in input_genre:
        genres += genre + ", "
    if genres != "":
        genres = genres[:-2]
    return genres

def update_timing(input_vlength):
    vlength_string = ""
    if input_vlength == "<1min":
        vlength_string = "less than one minute"
    elif input_vlength == "1-3mins":
        vlength_string = "one to three minutes"
    elif input_vlength == "3-5mins":
        vlength_string = "three to five minutes"
    elif input_vlength == "5-10mins":
        vlength_string = "five to ten minutes"
    elif input_vlength == ">10mins":
        vlength_string = "more than ten minutes"
    return vlength_string

def extract_storyboard(script):
    storyboard = []
    seen_lines = set()
    for line in script.split('\n'):
        line = line.strip()
        #Extract lines from storyboard and script
        if any(keyword in line.lower() for keyword in ["shot", "cut","scene"]):
            if line not in seen_lines:
                storyboard.append(line)
                seen_lines.add(line)
    return storyboard
#Function to create video using MoviePy
def create_video(image_paths, output_path):
    clips = []
    for img_path in image_paths:
        clip = ImageClip(img_path).set_duration(2)
        clips.append(clip)

    #Combine all clips into one video
    video = concatenate_videoclips(clips)
    
    #Write the video to a file
    video.write_videofile(output_path, fps = 24)
# Streamlit app
st.title("Storyboarding Incomplete/New Ideas")

# Fixed inputs
genre_options = [
    "Action and Adventure",
    "Comedy",
    "Romance",
    "Drama",
    "Mythology",
    "Non-Fiction", 
    "Science-Fiction", 
    "Horror", 
    "Thriller",
    "Review"]
video_length_options = [
    "<1min",
    "1-3mins",
    "3-5mins",
    "5-10mins",
    ">10mins"
] 
video_type_options = [
    "Gaming",
    "Vlog",
    "Movie",
    "Reaction",
    "Education",
    "Music",
    "Livestream",
    "Travel",
    "Review",
    "Documentary",
    "Behind-the-Scenes",
    "Animal"
]

input_vgenre = st.multiselect(":red[*]Genre: ", genre_options)
input_vlength = st.selectbox("Video Length: ", video_length_options)
input_vtype = st.selectbox("Video Type: ", video_type_options)
input_script = st.text_area("Enter your script (leave blank for new script): ", height=200)
input_storyboard = st.text_area("Enter your storyboard plans (leave blank for new storyboard): ", height=200)

if st.button("Extract Answer"):
    input_genres = update_genres(input_vgenre)
    input_time = update_timing(input_vlength)
    if input_script == "" and input_storyboard == "" and input_genres != "":
        st.write("Creating new ideas for " + input_genres + " as your genre(s) and " + input_vtype + " as your video type for a video that is " + input_time + " long")
        input = "Based on the current trending videos on Tiktok and Youtube, and using " + input_genres + " as the genre of a video, create a script and storyboard for a " + input_vtype + " video that is " + input_time + " long"
        st.write(input)
    elif input_script == "" and input_storyboard != "" and input_genres != "":
        st.write("Creating script using the storyboard provided with " + input_genres + " genre(s) and " + input_vtype + " as your video type for a video that is " + input_time + " long")
        input = "Based on the current trending videos on Tiktok and Youtube, use the storyboard provided below with " + input_genres + " as the genres of a video, create a script and updated storyboard for a " + input_vtype + " video that is " + input_time + " long \n\n" + input_storyboard
        st.write(input)
    elif input_script != "" and input_storyboard == "" and input_genres != "":
        st.write("Creating storyboard using the script provided with " + input_genres + " genre(s) and " + input_vtype + " as your video type for a video that is " + input_time + " long")
        input = "Based on the current trending videos on Tiktok and Youtube, use the script provided below with " + input_genres + " as the genres of a video, ideate a completed storyboard and updated script for a " + input_vtype + " video that is " + input_time + " long \n\n" + input_script
        st.write(input)
    elif input_script != "" and input_storyboard != "" and input_genres != "":
        st.write("Proofreading the storyboard and script provided with " + input_genres + " as the genre(s) for your " + input_vtype + " video type for a video that should be " + input_time + " long")
        input = "Based on current Youtube and Tiktok trends, and using the storyboard and script provided below with " + input_genres + " as the genres of a " + input_vtype + " video, proofread and fix the script and storyboard for a video to be " + input_time + " long \n\nScript: \n\n" + input_script + "\n\nStoryboard: \n\n" + input_storyboard
        st.write(input)
    else:
        st.write("Please choose at least one genre")
    response = get_chatgpt_response(input)
    #response2 = "Title: Behind-the-Scenes of a Comedy Skit\n\nOpening shot of a group of friends laughing and having a good time.\n\nVoiceover: \"Welcome to the behind-the-scenes of our latest comedy skit. We're taking you behind the camera to show you the making of our hilarious video.\"\n\nCut to the group of friends brainstorming ideas for the skit.\n\nFriend 1: \"Okay, so how about we do a parody of a popular song?\"\n\nFriend 2: \"Yes, and we can add our own funny lyrics to it!\"\n\nVoiceover: \"Coming up with ideas for our videos is always a fun and collaborative process.\"\n\nCut to the group filming the skit.\n\nFriend 3: \"Wait, I think I messed up my line.\"\n\nDirector: \"Cut! Let's take it from the top.\"\n\nVoiceover: \"Sometimes, it takes a few tries to get the perfect take.\"\n\nCut to the group doing a silly dance as part of the skit.\n\nFriend 4: \"I can't stop laughing, this is too funny!\"\n\nVoiceover: \"Making each other laugh is definitely one of the perks of filming comedy videos.\n\nCut to the editing process.\n\nFriend 5: \"Okay, let's add some sound effects here\""
    st.text_area("Response", response, height=400)
    
     # Extract storyboard scenes and generate images for each scene
    storyboard = extract_storyboard(response)
    
    if storyboard:
        images = [generate_images(scene) for scene in storyboard]
        image_paths = []
        for idx, (scene, img_url) in enumerate(zip(storyboard,images)):
            st.write(scene)
            st.image(img_url, width = 400)
            img_path = f"image_{idx}.png"
            image_paths.append(img_path)
            #Download and save image
            img_data = requests.get(img_url).content 
            with open(img_path, 'wb') as handler:
                handler.write(img_data)
        # Generate video using MoviePy
        video_output_path = 'output_video.mp4'
        create_video(image_paths, video_output_path)
        
         # Display the generated video
        st.write("Generated Video:")
        st.video(video_output_path)
        
         # Clean up downloaded images
        for img_path in image_paths:
            os.remove(img_path)
    else:
        st.write("No storyboard scenes found.")
