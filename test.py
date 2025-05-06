import base64
from openai import OpenAI
import os
import logging
import cv2
import dotenv

dotenv.load_dotenv()

client = OpenAI()
RTSP_STREAM_URL1 = os.getenv("RTSP_STREAM_URL1")
RTSP_STREAM_URL2 = os.getenv("RTSP_STREAM_URL2")


def capture_encode_frame(stream_url1: str, stream_url2: str) -> dict:
    """
    Captures a single frame from the specified RTSP stream and returns it as a base64 encoded string.

    Args:
        stream_url1: The RTSP URL of the first camera stream.
        stream_url2: The RTSP URL of the second camera stream.

    Returns:
        A dictionary with either a base64_image or an error message.
    """
    cap1, cap2 = None, None
    try:
        cap1 = cv2.VideoCapture(stream_url1)
        cap2 = cv2.VideoCapture(stream_url2)
        if not cap1.isOpened():
            error_msg = f"Could not open video stream: {stream_url1}"
            logging.error(error_msg)
            return {"error": error_msg}
        if not cap2.isOpened():
            error_msg = f"Could not open video stream: {stream_url2}"
            logging.error(error_msg)
            return {"error": error_msg}

        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        if not ret1 or frame1 is None:
            error_msg = "Could not read frame from stream."
            logging.error(error_msg)
            return {"error": error_msg}
        else:
            logging.info(
                f"Successfully captured frame from stream with shape {frame1.shape}."
            )
            # Save image
            cv2.imwrite("frame1.jpg", frame1)

        if not ret2 or frame2 is None:
            error_msg = "Could not read frame from stream."
            logging.error(error_msg)
            return {"error": error_msg}
        else:
            logging.info(
                f"Successfully captured frame from stream with shape {frame2.shape}."
            )
            # Save image
            cv2.imwrite("frame2.jpg", frame2)

        success1, buffer1 = cv2.imencode(".jpg", frame1)
        success2, buffer2 = cv2.imencode(".jpg", frame2)
        if not success1:
            error_msg = "Could not encode frame to JPEG."
            logging.error(error_msg)
            return {"error": error_msg}
        if not success2:
            error_msg = "Could not encode frame to JPEG."
            logging.error(error_msg)
            return {"error": error_msg}

        base64_image1 = base64.b64encode(buffer1).decode("utf-8")
        base64_image2 = base64.b64encode(buffer2).decode("utf-8")

        return {"base64_image1": base64_image1, "base64_image2": base64_image2}
    except Exception as e:
        error_msg = f"Exception during frame capture/encoding: {e}"
        logging.error(error_msg, exc_info=True)
        return {"error": error_msg}
    finally:
        if cap1 and cap1.isOpened():
            cap1.release()
            logging.info("Video capture released.")
        if cap2 and cap2.isOpened():
            cap2.release()
            logging.info("Video capture released.")


result = capture_encode_frame(RTSP_STREAM_URL1, RTSP_STREAM_URL2)
base64_image1 = result["base64_image1"]

response1 = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "what's in this image?"},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image1}",
                    "detail": "low",
                },
            ],
        }
    ],
)

print(response1.output_text)
