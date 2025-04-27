# WhatsCAMM - WhatsApp Camera Monitoring System

WhatsCAMM is a security camera monitoring system that captures frames from RTSP camera streams, analyzes them for suspicious activity using OpenAI's vision models, and sends notifications with images via WhatsApp.

## Features

* Monitors multiple RTSP camera streams simultaneously
* Uses OpenAI's vision models to analyze camera frames for suspicious activity
* Automatically sends notifications with images to a WhatsApp group or individual
* Configurable monitoring intervals
* Easy to set up with environment variables

## Prerequisites

* Python 3.8+
* OpenAI API key
* RTSP camera streams
* WhatsApp MCP server setup for sending messages

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/whatscamm.git
cd whatscamm
```

2. Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:

```makefile
OPENAI_API_KEY="your_openai_api_key"
RTSP_STREAM_URL1="rtsp://username:password@camera_ip:port/stream1"
RTSP_STREAM_URL2="rtsp://username:password@camera_ip:port/stream1" # Optional
WHATSAPP_RECIPIENT="whatsapp_group_id_or_individual_contact"
```

## Usage

Run the main script to start monitoring:

```bash
python main.py
```

The system will:

1. Capture frames from the configured RTSP streams
2. Analyze the frames using OpenAI's vision models
3. Send notifications with the analysis and images via WhatsApp
4. Wait for the configured interval before repeating

## Configuration

All configuration is done through environment variables in the `.env` file:

* `OPENAI_API_KEY`: Your OpenAI API key
* `RTSP_STREAM_URL1`: RTSP URL for the first camera
* `RTSP_STREAM_URL2`: RTSP URL for the second camera (optional)
* `WHATSAPP_RECIPIENT`: WhatsApp recipient ID (group or individual)

## Testing

You can test the system by running:

```bash
python test.py
```

This will capture frames from the configured RTSP streams and test the OpenAI vision model analysis without sending WhatsApp messages.

## WhatsApp Integration

This project uses a WhatsApp MCP (Model Context Protocol) server for sending messages. Make sure you have the WhatsApp MCP server properly set up and configured.
For detailed information on setting up the WhatsApp MCP server, refer to the [official documentation](https://github.com/lharries/whatsapp-mcp).

## Security Considerations

* Never commit your `.env` file to version control
* Ensure your camera credentials are strong and unique
* Consider using a dedicated OpenAI API key with appropriate usage limits

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
