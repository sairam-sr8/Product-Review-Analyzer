"""
NLTK Data Downloader
Run this script to download all required NLTK data
"""

import nltk

def download_nltk_data():
    """Download all required NLTK data"""
    print("Downloading NLTK data...")
    
    required_packages = [
        'punkt',
        'punkt_tab',
        'stopwords',
        'wordnet',
        'averaged_perceptron_tagger'
    ]
    
    for package in required_packages:
        try:
            print(f"Downloading {package}...")
            nltk.download(package, quiet=False)
            print(f"✅ {package} downloaded")
        except Exception as e:
            print(f"❌ Error downloading {package}: {e}")
    
    print("\n✅ All NLTK data downloaded!")

if __name__ == "__main__":
    download_nltk_data()

