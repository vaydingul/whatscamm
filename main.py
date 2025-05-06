# /Users/volkanaydingul/Documents/Codes/whatscamm/main.py
import os
import base64
import time
from agents.mcp import MCPServerStdio
import cv2
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from agents import Agent, Runner, function_tool,image_function_tool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

import logging
import asyncio


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RTSP_STREAM_URL1 = os.getenv("RTSP_STREAM_URL1")
RTSP_STREAM_URL2 = os.getenv("RTSP_STREAM_URL2")
WHATSAPP_RECIPIENT = os.getenv("WHATSAPP_RECIPIENT")

if not all([OPENAI_API_KEY, RTSP_STREAM_URL1, RTSP_STREAM_URL2, WHATSAPP_RECIPIENT]):
    raise ValueError("Missing required environment variables (OPENAI_API_KEY, RTSP_STREAM_URL1, RTSP_STREAM_URL2, WHATSAPP_RECIPIENT).")

# Initialize OpenAI client (global for tools to access)
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

@image_function_tool
def capture_encode_frame(stream_url: str, image_path: str) -> str:
    """
    Captures a single frame from the specified RTSP stream and returns it as a base64 encoded string.
    
    Args:
        stream_url: The RTSP URL of the camera stream.
        
    Returns:
        A base64 encoded string of the frame.
    """
    cap1 = None
    try:
        cap1 = cv2.VideoCapture(stream_url)
        if not cap1.isOpened():
            error_msg = f"Could not open video stream: {stream_url}"
            logging.error(error_msg)
            return {"error": error_msg}
        

        ret1, frame1 = cap1.read()
        if not ret1 or frame1 is None:
            error_msg = "Could not read frame from stream."
            logging.error(error_msg)
            return {"error": error_msg}
        else:
            logging.info(f"Successfully captured frame from stream with shape {frame1.shape}.")
            # Save image
            cv2.imwrite(image_path, frame1)
    

        success1, buffer1 = cv2.imencode('.jpg', frame1)
        if not success1:
            error_msg = "Could not encode frame to JPEG."
            logging.error(error_msg)
            return {"error": error_msg}
       

        base64_image1 = base64.b64encode(buffer1).decode('utf-8')
        
        return f"data:image/jpeg;base64,{base64_image1}"

    except Exception as e:
        error_msg = f"Exception during frame capture/encoding: {e}"
        logging.error(error_msg, exc_info=True)
        return {"error": error_msg}
    finally:
        if cap1 and cap1.isOpened():
            cap1.release()
            logging.info("Video capture released.")

async def run_monitoring_cycle():

    # --- Agent Setup ---
    async with MCPServerStdio(
        name = "WhatsApp Server via uv",
        params={
            "command": "/Users/volkanaydingul/.local/bin/uv",
            "args": [
                "--directory",
                "/Users/volkanaydingul/Documents/Codes/whatsapp-mcp/whatsapp-mcp-server",
                "run",
                "main.py"
            ]
        }
    ) as mcp_server:
        # --- Agent Setup ---
        security_agent = Agent(
            name="WhatsCAMM Security Monitor Agent",
            model="gpt-4.1",
        instructions=(
            RECOMMENDED_PROMPT_PREFIX +
            "You are a security camera monitoring agent. Your goal is to analyze frames for suspicious activity, and report the current situation via WhatsApp in every situation regardless of the activity, whether it is normal or suspicious.\n"
            "You can obtain the frames from the following URLs: " + RTSP_STREAM_URL1 + " and " + RTSP_STREAM_URL2 + ".\n"
            f"The recipient is '{WHATSAPP_RECIPIENT}'. Craft a detailed but concise message summarizing the key findings from the judgment for each room.\n"
            "Please follow the format below: \n"
            "Alarm Triggered: [yes/no] (if yes put an emoji)\n"
            "Date/Time: [detailed date and time information]\n"
            "Room [Room Name] (appropriate emoji): [detailed description of the room]\n"
            "If there is a suspicious activity, please send the camera media stored in /Users/volkanaydingul/Documents/Codes/whatscamm/frame1.jpg and /Users/volkanaydingul/Documents/Codes/whatscamm/frame2.jpg.\n"
            "Do not ask for an additional confirmation or permission. Just send the message after compiling your judgment!"
        ),
        tools=[capture_encode_frame],
        mcp_servers=[mcp_server],
    )

        logging.info("Starting new monitoring cycle...")

        goal = "Monitor the security cameras and report the current situation via WhatsApp in every situation regardless of the activity, whether it is normal or suspicious."
        result = await Runner.run(security_agent, goal)
        logging.info(f"Cycle finished. Agent output: {result.final_output}")
        return result

async def main_async():
    """Main async function to run the monitoring loop."""
    try:
        while True:
            await run_monitoring_cycle()
            
            # Wait between cycles
            sleep_interval = 600  # seconds
            logging.info(f"Waiting {sleep_interval} seconds before next cycle...")
            await asyncio.sleep(sleep_interval)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)

def main():
    """Main entry point for the application."""
    logging.info("Starting WhatsCAMM security monitoring...")
    asyncio.run(main_async())

if __name__ == "__main__":
    main()