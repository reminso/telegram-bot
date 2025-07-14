import os
import requests
import json
import time
import hashlib
from typing import Dict, Any, List
from transliterator import RussianTransliterator
from chuvash_transliterator import ChuvashTransliterator

class TelegramBot:
    """
    Telegram bot for Russian to Latin transliteration.
    """
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            # Fallback to hardcoded token for development
            self.token = '7806556716:AAHWEGa3PbYYfYraQBhMrxyVRxxbym_DfZo'
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.russian_transliterator = RussianTransliterator()
        self.chuvash_transliterator = ChuvashTransliterator()
        
        # User preferences: track selected language for each user
        self.user_language = {}  # user_id -> 'russian' or 'chuvash'
        
        # Anti-spam: track last message time for each user
        self.user_last_message = {}
        self.spam_cooldown = 8  # seconds between messages
    
    def send_message(self, chat_id: int, text: str, reply_to_message_id: int = None) -> Dict[str, Any]:
        """
        Send a message to a Telegram chat.
        
        Args:
            chat_id: ID of the chat to send message to
            text: Text of the message
            reply_to_message_id: ID of the message to reply to
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.api_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_to_message_id:
            data['reply_to_message_id'] = reply_to_message_id
        
        try:
            print(f"Sending message to chat {chat_id}: {text[:50]}...")
            response = requests.post(url, json=data)
            result = response.json()
            print(f"Send message response: {result}")
            return result
        except Exception as e:
            print(f"Error sending message: {e}")
            return {}
    
    def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """
        Set webhook URL for the bot.
        
        Args:
            webhook_url: URL to set as webhook
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.api_url}/setWebhook"
        data = {'url': webhook_url}
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Error setting webhook: {e}")
            return {}
    
    def handle_start_command(self, chat_id: int, user_id: int) -> None:
        """
        Handle /start command.
        
        Args:
            chat_id: ID of the chat that sent the command
            user_id: ID of the user
        """
        # Set default language to Russian
        self.user_language[user_id] = 'russian'
        
        welcome_text = """
🔄 <b>Добро пожаловать в Multilingual Transliterator Bot!</b>

Этот бот поможет вам транслитерировать текст в латиницу.

<b>Поддерживаемые языки:</b>
• Русский (по умолчанию)
• Чувашский

<b>Способы использования:</b>
1️⃣ <b>В личных сообщениях:</b>
   • Выберите язык: /russian или /chuvash
   • Отправьте текст для транслитерации

2️⃣ <b>Inline режим (в любом чате):</b>
   • Напишите @RusLatin_Bot и ваш текст
   • Выберите нужный результат из списка
   • Автоматическое определение языка

<b>Команды:</b>
/russian - русская транслитерация
/chuvash - чувашская транслитерация  
/language - показать текущий язык

Попробуйте inline режим: @RusLatin_Bot привет
        """
        self.send_message(chat_id, welcome_text)
    
    def handle_language_command(self, chat_id: int, user_id: int, command: str) -> None:
        """
        Handle language selection commands.
        
        Args:
            chat_id: ID of the chat that sent the command
            user_id: ID of the user
            command: The command sent (/russian, /chuvash, /language)
        """
        if command == '/russian':
            self.user_language[user_id] = 'russian'
            response = "Русский: Выбран русский язык. Отправьте русский текст для транслитерации."
        elif command == '/chuvash':
            self.user_language[user_id] = 'chuvash'
            response = "Чувашский: Выбран чувашский язык. Отправьте чувашский текст для транслитерации."
        elif command == '/language':
            current_lang = self.user_language.get(user_id, 'russian')
            lang_name = 'Русский' if current_lang == 'russian' else 'Чувашский'
            response = f"Язык: Текущий язык: {lang_name}\n\nДля смены языка используйте:\n/russian - русский\n/chuvash - чувашский"
        else:
            response = "❌ Неизвестная команда. Используйте /russian, /chuvash или /language"
        
        self.send_message(chat_id, response)
    
    def check_spam_limit(self, user_id: int) -> bool:
        """
        Check if user is sending messages too frequently.
        
        Args:
            user_id: ID of the user
            
        Returns:
            True if user can send message, False if spam limit reached
        """
        current_time = time.time()
        
        if user_id in self.user_last_message:
            time_diff = current_time - self.user_last_message[user_id]
            if time_diff < self.spam_cooldown:
                return False
        
        self.user_last_message[user_id] = current_time
        return True

    def handle_text_message(self, chat_id: int, text: str, message_id: int, user_id: int) -> None:
        """
        Handle regular text messages for transliteration.
        
        Args:
            chat_id: ID of the chat that sent the message
            text: Text content of the message
            message_id: ID of the message to reply to
            user_id: ID of the user who sent the message
        """
        try:
            # Check spam limit
            if not self.check_spam_limit(user_id):
                remaining_time = self.spam_cooldown - (time.time() - self.user_last_message[user_id])
                response = f"⏱ Пожалуйста, подождите {int(remaining_time) + 1} сек. перед следующим сообщением."
                self.send_message(chat_id, response, message_id)
                return
            
            # Get user's selected language (default to Russian)
            user_lang = self.user_language.get(user_id, 'russian')
            
            # Check if text contains appropriate characters for selected language
            import re
            if user_lang == 'russian':
                if not re.search(r'[а-яё]', text, re.IGNORECASE):
                    response = "❌ Текст не содержит русских букв для транслитерации."
                    self.send_message(chat_id, response, message_id)
                    return
                transliterated = self.russian_transliterator.transliterate(text)
                lang_name = "Русский"
            elif user_lang == 'chuvash':
                if not re.search(r'[а-яёӑӳҫ]', text, re.IGNORECASE):
                    response = "❌ Текст не содержит чувашских букв для транслитерации."
                    self.send_message(chat_id, response, message_id)
                    return
                transliterated = self.chuvash_transliterator.transliterate(text)
                lang_name = "Чувашский"
            else:
                response = "❌ Неизвестный язык. Используйте /russian или /chuvash для выбора языка."
                self.send_message(chat_id, response, message_id)
                return
            
            # Format response
            response = f"{lang_name} <b>Транслитерация:</b>\n\n{transliterated}"
            
            self.send_message(chat_id, response, message_id)
            
        except Exception as e:
            error_message = f"❌ Произошла ошибка при транслитерации: {str(e)}"
            self.send_message(chat_id, error_message, message_id)
    
    def answer_inline_query(self, inline_query_id: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Answer an inline query.
        
        Args:
            inline_query_id: ID of the inline query
            results: List of results to show
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.api_url}/answerInlineQuery"
        data = {
            'inline_query_id': inline_query_id,
            'results': results,
            'cache_time': 0
        }
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Error answering inline query: {e}")
            return {}
    
    def handle_inline_query(self, inline_query: Dict[str, Any]) -> None:
        """
        Handle inline query for transliteration.
        
        Args:
            inline_query: Inline query object from Telegram
        """
        try:
            query_id = inline_query['id']
            query_text = inline_query.get('query', '').strip()
            user_id = inline_query['from']['id']
            
            if not query_text:
                # Show help message when query is empty
                results = [{
                    'type': 'article',
                    'id': 'help',
                    'title': 'Введите текст для транслитерации',
                    'description': 'Поддержка: русский и чувашский языки',
                    'input_message_content': {
                        'message_text': 'Введите текст после @RusLatin_Bot для транслитерации'
                    }
                }]
                self.answer_inline_query(query_id, results)
                return
            
            # Get user's language preference (default to auto-detect)
            user_lang = self.user_language.get(user_id, 'auto')
            
            results = []
            
            # Auto-detect language or use user preference
            import re
            has_chuvash = bool(re.search(r'[ӑӳҫӗ]', query_text, re.IGNORECASE))
            has_cyrillic = bool(re.search(r'[а-яё]', query_text, re.IGNORECASE))
            
            if has_chuvash or user_lang == 'chuvash':
                # Chuvash transliteration
                try:
                    transliterated = self.chuvash_transliterator.transliterate(query_text)
                    results.append({
                        'type': 'article',
                        'id': hashlib.md5(f"chuvash_{query_text}".encode()).hexdigest(),
                        'title': f'Чувашский: {transliterated}',
                        'description': f'Транслитерация: {query_text}',
                        'input_message_content': {
                            'message_text': transliterated
                        }
                    })
                except Exception as e:
                    print(f"Chuvash transliteration error: {e}")
            
            if has_cyrillic and not has_chuvash:
                # Russian transliteration
                try:
                    transliterated = self.russian_transliterator.transliterate(query_text)
                    results.append({
                        'type': 'article',
                        'id': hashlib.md5(f"russian_{query_text}".encode()).hexdigest(),
                        'title': f'Русский: {transliterated}',
                        'description': f'Транслитерация: {query_text}',
                        'input_message_content': {
                            'message_text': transliterated
                        }
                    })
                except Exception as e:
                    print(f"Russian transliteration error: {e}")
            
            # If both languages detected, show both options
            if has_cyrillic and has_chuvash:
                try:
                    russian_result = self.russian_transliterator.transliterate(query_text)
                    results.append({
                        'type': 'article',
                        'id': hashlib.md5(f"russian_alt_{query_text}".encode()).hexdigest(),
                        'title': f'Как русский: {russian_result}',
                        'description': 'Альтернативная русская транслитерация',
                        'input_message_content': {
                            'message_text': russian_result
                        }
                    })
                except Exception as e:
                    print(f"Russian alternative transliteration error: {e}")
            
            # If no results, show error
            if not results:
                results = [{
                    'type': 'article',
                    'id': 'no_cyrillic',
                    'title': 'Текст не содержит кириллических букв',
                    'description': 'Поддерживаются русский и чувашский языки',
                    'input_message_content': {
                        'message_text': 'Ошибка: текст должен содержать кириллические буквы'
                    }
                }]
            
            self.answer_inline_query(query_id, results)
            
        except Exception as e:
            print(f"Error handling inline query: {e}")
    
    def handle_update(self, update: Dict[str, Any]) -> None:
        """
        Handle incoming Telegram update.
        
        Args:
            update: Update object from Telegram
        """
        try:
            # Debug: Print update type
            print(f"Update received: {list(update.keys())}")
            
            # Handle inline queries
            if 'inline_query' in update:
                print(f"Processing inline query: {update['inline_query'].get('query', 'empty')}")
                self.handle_inline_query(update['inline_query'])
                return
            
            # Check if update contains a message
            if 'message' not in update:
                return
            
            message = update['message']
            chat_id = message['chat']['id']
            message_id = message['message_id']
            
            # Handle commands
            if 'text' in message and message['text'].startswith('/'):
                command = message['text'].split()[0]
                user_id = message['from']['id']
                
                if command == '/start':
                    self.handle_start_command(chat_id, user_id)
                    return
                elif command in ['/russian', '/chuvash', '/language']:
                    self.handle_language_command(chat_id, user_id, command)
                    return
            
            # Handle regular text messages
            if 'text' in message:
                text = message['text']
                user_id = message['from']['id']
                self.handle_text_message(chat_id, text, message_id, user_id)
                return
            
            # Handle other message types
            self.send_message(
                chat_id, 
                "❌ Пожалуйста, отправьте текстовое сообщение для транслитерации.",
                message_id
            )
            
        except Exception as e:
            print(f"Error handling update: {e}")
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                self.send_message(
                    chat_id, 
                    "❌ Произошла внутренняя ошибка. Попробуйте еще раз."
                )
