# Telegram Bot for ServiceDesk Plus

This is a Telegram bot that interacts with ServiceDesk Plus API.

## Features

-   List last requests
-   Show request details
-   Open request in browser

## Requirements

-   Python 3.9+
-   Telegram Bot Token
-   ServiceDesk Plus API Token

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/yourusername/your-repo.git
    ```

2.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  Create a `.env` file in the root directory with the following content:

    ```
    BOT_TOKEN=YOUR_BOT_TOKEN
    AUTH_TOKEN=YOUR_API_TOKEN
    API_URL=YOUR_API_URL
    ```

    Replace `YOUR_BOT_TOKEN`, `YOUR_API_TOKEN`, and `YOUR_API_URL` with your actual values.

## Usage

1.  Run the bot:

    ```bash
    python main.py
    ```

2.  Start a conversation with your bot in Telegram and use the `/start` command.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
