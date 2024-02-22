from flask import Flask, request
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import subprocess

app = Flask(__name__)
TOKEN = "6259718751:AAEjFAu83hn_tDDZS8-8kG5nMgDzR1vhviA"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return '', 200

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the PDF Bot! Send me a PDF file to process.")

def process_pdf(update: Update, context: CallbackContext) -> None:
    # Save the received PDF file
    file_id = update.message.document.file_id
    file = context.bot.get_file(file_id)
    file.download('input.pdf')

    # Extract the command argument (number of pages per side)
    args = context.args
    pages_per_side = int(args[0]) if args else 1  # Default to 1 page per side

    # Run the pdftk commands based on the specified number of pages
    cmd = ['pdftk', 'input.pdf', 'cat']
    for i in range(1, pages_per_side + 1):
        cmd.append(f'{i}')

    cmd.extend(['output', 'Side1.pdf'])
    subprocess.run(cmd)

    subprocess.run(['pdftk', 'A=Side1.pdf', 'B=input.pdf', 'cat', 'A', 'B', 'output', 'FinalOutput.pdf'])

    # Send the processed PDF back to the user
    context.bot.send_document(chat_id=update.effective_chat.id, document=open('FinalOutput.pdf', 'rb'))

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("processpdf", process_pdf, pass_args=True))
    dp.add_handler(MessageHandler(filters.document, process_pdf))

    # Start the Flask app
    app.run(threaded=True, port=5000)
