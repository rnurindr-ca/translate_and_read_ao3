import argostranslate.package
import argostranslate.translate
import edge_tts
import asyncio
import requests
from bs4 import BeautifulSoup
import edge_tts
from IPython.display import Audio
import os

def setup_argos(from_code="zh", to_code="en"):
    # Update package index and download the language pack
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(lambda x: x.from_code == from_code and x.to_code == to_code, available_packages)
    )
    argostranslate.package.install_from_path(package_to_install.download())

def translate_locally(text, from_code="zh", to_code="en"):
    return argostranslate.translate.translate(text, from_code, to_code)

def scrape_ao3(ao3_url, output_file="story_cn.txt"):
    # 1. Add 'view_full_work' to ensure we get all chapters
    if "view_full_work=true" not in ao3_url:
        ao3_url += "?view_full_work=true"

    # 2. Fetch the page
    headers = {"User-Agent": "Mozilla/5.0"} # Prevents some basic blocks
    print("reading file...")
    response = requests.get(ao3_url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch the page. Check the URL!")
        return

    # 3. Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # AO3 story text is usually inside a div with id="chapters"
    story_div = soup.find('div', id='chapters')
    
    if not story_div:
        print("Couldn't find the story content.")
        return

    # Extract text from paragraphs
    paragraphs = [p.get_text() for p in story_div.find_all('p')]
    full_text = "\n".join(paragraphs)

    # # 5. Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"Done! Saved to {output_file}")
    return(output_file)

def scrape_and_translate_text(text_path="story_cn.txt", output_file="translated_story.txt"):
    print("opening the text")
    with open(text_path, 'r', encoding='utf-8') as file:
        full_text = file.read()

    from_code = "zh"
    to_code = "en"

    print("translating now")
    # Translation happens here (handling chunks of 4500 chars)
    translated_text = ""
    chunk_size = 4500 
    for i in range(0, len(full_text), chunk_size):
        chunk = full_text[i:i+chunk_size]
        translated_chunk = argostranslate.translate.translate(chunk, from_code, to_code) + "\n"
        translated_text += translated_chunk

    # 5. Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(translated_text)
    
    print(f"Done! Saved to {output_file}")

async def speak():
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)


if __name__ == "__main__":
    # Setup once
    setup_argos()
    # Then call translate_locally(paragraph) in your loop

    output_file = "story_cn.txt"
    if not os.path.exists(output_file):
        url = input("Paste the AO3 link: ")
        output_file = scrape_ao3(url)
    else:
        print("story found, skipping...")

    translated_file = "translated_story.txt"
    if not os.path.exists(translated_file):
        scrape_and_translate_text(output_file)
    else:
        print("translation found, skipping")
 
    with open(translated_file, 'r', encoding='utf-8') as file:
        TEXT = file.read()
    VOICE = "en-CA-LiamNeural"  # Try changing this to another name from the list!
    OUTPUT_FILE = "translated_story.mp3"

    print("converting to mp3... this will take a while")
    asyncio.run(speak())
    print("completed!")
