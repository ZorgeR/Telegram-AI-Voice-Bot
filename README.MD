## Telegram AI Voice Bot (Elevenlabs API)

This is a simple Telegram AI Voice Bot using the Elevenlabs API. This bot can convert text to speech in multiple languages.
It works in inline mode and in chat mode. You can change the voice of the bot using the /voice command.

### Requirements
- Python 3.6 or higher
- aiogram
- API Key from Elevenlabs
- Telegram Bot Token

### Installation
1. Clone this repository
2. Install the required packages using pip
```bash
pip install -r requirements.txt
```
3. Create a new bot using BotFather on Telegram and get the bot token
4. Get the API key from Elevenlabs
5. Register You voice on the Elevenlabs website and get ID of the voice
5. Replace the placeholders in the `.env.example` file with your bot token and API key
6. Rename the `.env.example` file to `.env`
7. Replace the placeholder in the voices.json file with the language code you want to use
8. Rename the `voices.json.example` file to `voices.json`
7. Run the bot using the following command
```bash
python bot.py
```

### Usage
1. Send a text message to the bot
2. The bot will reply with the voice message
3. You can change voice of the bot using /voice command
4. You can use inline query in any chat to convert text to speech @YourBotName text

### License
This project is licensed under the MIT License - see the LICENSE file for details

### Author
This project is created by [Artur Shamsiev](https://github.com/ZorgeR/Telegram-AI-Voice-Bot)

### Support
If you have any questions or need help with this project, you can contact me on Telegram: [@ZorgeR](https://t.me/ZorgeR)

### Donate
If you like this project, you can donate to me using the following methods:
- [Donate via PayPal](https://www.paypal.com/paypalme/ashamsiev)
- [Donate via Boosty](https://boosty.to/zorgg/purchase/1708542?ssource=DIRECT&share=subscription_link)
---
- Bitcoin: `bc1qyymy3ufvq3c3uq2q4927ll6x4rhvdw8gxlydwc`
- ![BTC QR code](static/btc.png)
---
- Ethereum: `0x0213A705065B193D14f1A3cd075977e28Da8F9B3`
- ![ETH QR code](static/eth.png)
---
- Dogecoin: `D9RbkgazaGhkT4FHkJtHoh4hDxkzAZwQnK`
- ![ETH QR code](static/doge.png)
---
- Toncoin: `UQBctua3AlzKMQBAcxbiFAhFhtZmlMfxSbJQVvas6AAwA0S-`
- ![TON QR code](static/ton.png)




