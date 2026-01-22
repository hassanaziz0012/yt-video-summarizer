import argparse
import logging
import sys
import os
from dotenv import load_dotenv

# Add the current directory to sys.path to ensure src imports work
sys.path.append(os.getcwd())

from src.utils import (
    extract_video_id,
    get_transcript,
    get_video_info,
)
from src.utils.gemini import ask, SUMMARIZE_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()

    # Parse arguments
    parser = argparse.ArgumentParser(description="YouTube Video Summarizer CLI")
    parser.add_argument("video_url", help="URL of the YouTube video to summarize")
    args = parser.parse_args()

    video_url = args.video_url

    try:
        # Check API Key
        if not os.environ.get("ARMY_ACCESS_KEY"):
            logger.error("ARMY_ACCESS_KEY environment variable is not set.")
            sys.exit(1)

        # Step 1: Extract Video ID
        logger.info("Extracting video ID...")
        video_id = extract_video_id(video_url)
        logger.info(f"Video ID: {video_id}")

        # Step 2: Get Video Info
        logger.info("Fetching video info...")
        video_info = get_video_info(video_id)
        title = video_info.get("title", "Unknown Title")
        logger.info(f"Video Title: {title}")

        # Step 3: Get Transcript
        logger.info("Fetching transcript...")
        transcript = get_transcript(video_id)
        logger.info("Transcript fetched successfully.")

        # Step 4: Summarize
        logger.info("Summarizing with Gemini...")
        prompt = SUMMARIZE_PROMPT.format(transcript=transcript)
        summary = ask(prompt=prompt)

        # Output
        print("\n" + "="*50)
        print(f"SUMMARY: {title}")
        print("="*50 + "\n")
        print(summary)
        print("\n" + "="*50)

    except ValueError as e:
        logger.error(f"Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
