import requests
import os

def download_texture(url, directory, filename):
    filepath = os.path.join(directory, filename)
    try:
        print(f"Downloading {filename} from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the texture directory path relative to the script
    texture_dir = os.path.join(script_dir, "textures")

    # Create a directory for textures if it doesn't exist
    if not os.path.exists(texture_dir):
        os.makedirs(texture_dir)

    # URLs for the textures
    earth_url = "https://www.solarsystemscope.com/textures/download/2k_earth_daymap.jpg"
    moon_url = "https://www.solarsystemscope.com/textures/download/2k_moon.jpg"

    # Download the textures
    download_texture(earth_url, texture_dir, "earth.jpg")
    download_texture(moon_url, texture_dir, "moon.jpg")
