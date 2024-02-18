from PyPDF2 import PdfFileReader, PdfFileWriter
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Define your Telegram bot token
TOKEN = '6371494303:AAGMaUGJltbs9rBI9p3jPX77rBfPGpahvnc'

# Dictionary to store user data
user_data = {}

# Step 1 - Set Serial and Combine PDFs
def set_serial(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data[user_id] = {'serial': update.message.text, 'pdfs': []}
    update.message.reply_text(f'Serial set to {update.message.text}. Now send the PDFs you want to combine.')

def combine_pdfs(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_serial = user_data.get(user_id, {}).get('serial')

    if not user_serial:
        update.message.reply_text('Please set a serial using /setserial command first.')
        return

    pdf_files = context.user_data.setdefault(user_id, [])
    document = PdfFileWriter()

    for document_id in pdf_files:
        document.addPage(PdfFileReader(document_id).getPage(0))

    output_path = f'combined_{user_serial}.pdf'
    with open(output_path, 'wb') as output_file:
        document.write(output_file)

    update.message.reply_document(open(output_path, 'rb'), caption=f'Combined PDF with Serial: {user_serial}')
    pdf_files.clear()

# Step 2 - Write Page Number on Combined PDF
def write_page_number(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_serial = user_data.get(user_id, {}).get('serial')

    if not user_serial:
        update.message.reply_text('Please set a serial using /setserial command first.')
        return

    page_number = update.message.text
    input_path = f'combined_{user_serial}.pdf'
    output_path = f'numbered_combined_{user_serial}.pdf'

    with open(input_path, 'rb') as input_file:
        pdf_reader = PdfFileReader(input_file)
        pdf_writer = PdfFileWriter()

        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))
            pdf_writer.getPage(page).mergePage(PdfFileReader(user_data[user_id]['pdfs'][0]).getPage(0))

        pdf_writer.write(open(output_path, 'wb'))

    update.message.reply_document(open(output_path, 'rb'), caption=f'Combined and Numbered PDF with Serial: {user_serial}')
    user_data.pop(user_id, None)

# Set up the Telegram bot
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Add command handlers
dispatcher.add_handler(CommandHandler("setserial", set_serial))
dispatcher.add_handler(CommandHandler("combinepdfs", combine_pdfs))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, write_page_number))

# Start the bot
updater.start_polling()

# Keep the bot running
updater.idle()