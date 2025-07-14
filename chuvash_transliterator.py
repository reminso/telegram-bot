import re
from typing import List

class ChuvashTransliterator:
    """
    Chuvash to Latin transliteration system.
    Transliterates Chuvash text from Cyrillic to Latin script.
    Handles specific Chuvash transliteration rules including soft sign processing.
    """
    
    def __init__(self):
        # Transliteration map based on your JavaScript code
        self.map = {
            'А': 'A', 'а': 'a',
            'Ӑ': 'O', 'ӑ': 'o',
            'В': 'V', 'в': 'v',

            'Ӗ': 'Ė', 'ӗ': 'ė',  # e with dot above
            'И': 'I', 'и': 'i',
            'Й': 'J', 'й': 'j',
            'К': 'K', 'к': 'k',
            'Л': 'L', 'л': 'l',
            'М': 'M', 'м': 'm',
            'Н': 'N', 'н': 'n',
            'О': 'O', 'о': 'o',
            'П': 'P', 'п': 'p',
            'Р': 'R', 'р': 'r',
            'С': 'S', 'с': 's',
            'Ҫ': 'Ś', 'ҫ': 'ś',  # s with acute
            'Т': 'T', 'т': 't',
            'У': 'U', 'у': 'u',
            'Ӳ': 'Ü', 'ӳ': 'ü',  # u with diaeresis
            'Х': 'H', 'х': 'h',
            'Ч': 'C', 'ч': 'c',
            'Ç': 'Ś', 'ç': 'ś',
            'Ш': 'Š', 'ш': 'š',
            'Ы': 'Y', 'ы': 'y',
            'Э': 'E', 'э': 'e',

            # Additional symbols
            'Ж': 'Ž', 'ж': 'ž',  # z with caron
            'Щ': 'Ś', 'щ': 'ś',  # s with acute (like Ҫ)
            # Russian letters that may appear in borrowings
            'Б': 'B', 'б': 'b',
            'Г': 'G', 'г': 'g',
            'Д': 'D', 'д': 'd',
            'З': 'Z', 'з': 'z',
            'Ц': 'Ts', 'ц': 'ts',
            'Ф': 'F', 'ф': 'f',

            'Ъ': '', 'ъ': '',  # hard sign - usually omitted
            'Ь': '', 'ь': '',  # soft sign - handled separately by process_soft_sign
        }
    
    def process_soft_sign(self, text: str) -> str:
        """
        Process soft signs (Ь/ь) by doubling the preceding consonant.
        Example: "Пирень" -> "Пиренн"
        
        Args:
            text: Input text with soft signs
            
        Returns:
            Text with processed soft signs
        """
        # Use regex to find patterns: [Cyrillic letter][soft sign]
        # Replace with doubled Cyrillic letter
        pattern = r'([А-Яа-яЁёӐӑӖӗҪҫӲӳ])([ьЬ])'
        
        def replace_soft_sign(match):
            preceding_char = match.group(1)
            # Double the preceding character (remove soft sign)
            return preceding_char + preceding_char
        
        return re.sub(pattern, replace_soft_sign, text)
    
    def is_consonant(self, char: str) -> bool:
        """
        Check if character is a consonant.
        
        Args:
            char: Character to check
            
        Returns:
            True if character is a consonant
        """
        consonants = 'БВГДЖЗЙКЛМНПРСҪТФХЦЧШЩбвгджзйклмнпрсҫтфхцчшщ'
        return char in consonants
    
    def handle_iotation(self, word: str) -> str:
        """
        Handle iotated vowels (е, ё, ю, я) based on position.
        
        Args:
            word: Word to process
            
        Returns:
            Word with proper iotation handling
        """
        result = []
        for i, char in enumerate(word):
            if char in 'еЕ':
                # е after consonant = e, otherwise = je
                if i > 0 and self.is_consonant(word[i-1]):
                    result.append('E' if char.isupper() else 'e')
                else:
                    result.append('Je' if char.isupper() else 'je')
            elif char in 'ёЁ':
                # ё after consonant = ö, otherwise = jo
                if i > 0 and self.is_consonant(word[i-1]):
                    result.append('Ö' if char.isupper() else 'ö')
                else:
                    result.append('Jo' if char.isupper() else 'jo')
            elif char in 'юЮ':
                # ю after consonant = ü, otherwise = ju
                if i > 0 and self.is_consonant(word[i-1]):
                    result.append('Ü' if char.isupper() else 'ü')
                else:
                    result.append('Ju' if char.isupper() else 'ju')
            elif char in 'яЯ':
                # я after consonant = ä, otherwise = ja
                if i > 0 and self.is_consonant(word[i-1]):
                    result.append('Ä' if char.isupper() else 'ä')
                else:
                    result.append('Ja' if char.isupper() else 'ja')
            else:
                result.append(char)
        
        return ''.join(result)
    
    def transliterate_word(self, word: str) -> str:
        """
        Transliterate a single Chuvash word to Latin script.
        
        Args:
            word: Chuvash word to transliterate
            
        Returns:
            Transliterated word in Latin script
        """
        if not word:
            return word
        
        # Step 1: Process soft signs first
        processed_word = self.process_soft_sign(word)
        
        # Step 2: Handle iotation for е, ё, ю, я
        iotated_word = self.handle_iotation(processed_word)
        
        # Step 3: Character-by-character transliteration
        result = []
        for char in iotated_word:
            # Use map if character exists, otherwise keep as is
            result.append(self.map.get(char, char))
        
        return ''.join(result)
    
    def transliterate(self, text: str) -> str:
        """
        Transliterate Chuvash text to Latin script.
        
        Args:
            text: Chuvash text to transliterate
            
        Returns:
            Transliterated text in Latin script
        """
        if not text:
            return text
        
        # Split text into tokens (words and punctuation/spaces)
        tokens = re.split(r'([\s,.!?]+)', text)
        output = ''
        
        for token in tokens:
            # Check if token contains Cyrillic or Chuvash specific characters
            if re.search(r'[а-яёӑӗҫӳ]', token, re.IGNORECASE):
                output += self.transliterate_word(token)
            else:
                output += token
        
        return output
