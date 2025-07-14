import re
from typing import List

class RussianTransliterator:
    """
    Custom Russian to Latin transliteration system ported from PHP.
    Handles complex rules for soft signs, vowel combinations, and context-sensitive transliteration.
    """
    
    def __init__(self):
        # Basic character mapping
        self.map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'е': 'e', 'ё': 'e', 'ж': 'j', 'з': 'z', 'и': 'i',
            'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'q', 'ч': 'c',
            'ш': 'x', 'щ': 'sc', 'ъ': 'i', 'ы': 'y', 'ь': 'i',
            'э': 'æ', 'ю': 'eu', 'я': 'ea'
        }
        
        # Character categories
        self.vowels = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я']
        self.soft_signs = ['ь', 'ъ']
        self.consonants_pattern = re.compile(r'[бвгджзйклмнпрстфхцчшщ]')
    
    def transliterate_word(self, word: str) -> str:
        """
        Transliterate a single Russian word to Latin script.
        
        Args:
            word: Russian word to transliterate
            
        Returns:
            Transliterated word in Latin script
        """
        if not word:
            return word
            
        word_lower = word.lower()
        
        # Handle -ый ending
        if word_lower.endswith('ый'):
            base = word[:-2]
            transliterated_base = self.transliterate_word(base)
            return transliterated_base + 'y'
        
        # Split word into individual characters
        letters = list(word_lower)
        result = []
        
        i = 0
        while i < len(letters):
            ch = letters[i]
            prev = letters[i - 1] if i > 0 else ''
            next_ch = letters[i + 1] if i < len(letters) - 1 else ''
            
            # Handle и + (я/ё/ю) combinations
            if ch == 'и' and next_ch in ['я', 'ё', 'ю']:
                if next_ch == 'я':
                    result.append('ia')
                elif next_ch == 'ё':
                    result.append('io')
                elif next_ch == 'ю':
                    result.append('iu')
                i += 2  # Skip next character
                continue
            
            # Handle soft signs (ь, ъ)
            if ch in self.soft_signs:
                is_soft = ch == 'ь'
                if i > 0:
                    if self.consonants_pattern.match(prev):
                        if is_soft:
                            # Add duplicate consonant for soft sign - this is the key fix!
                            result.append(self.map.get(prev, prev))
                        if next_ch in ['а', 'э', 'ы', 'о', 'у', 'и']:
                            result.append('i' + self.map[next_ch])
                            i += 2
                            continue
                        elif next_ch == 'ю':
                            result.append('i')
                            result.append('u')
                            i += 2
                            continue
                        elif next_ch == 'я':
                            result.append('i')
                            result.append('a')
                            i += 2
                            continue
                        elif next_ch == 'ё':
                            result.append('i')
                            result.append('o')
                            i += 2
                            continue
                        elif next_ch == 'е':
                            result.append('i')
                            result.append('e')
                            i += 2
                            continue
                        else:
                            i += 1
                            continue
                result.append('i')
                i += 1
                continue
            
            # Handle й
            if ch == 'й':
                if prev == 'и':
                    result[-1] = 'e'
                    result.append('i')
                else:
                    result.append('i')
                i += 1
                continue
            
            # Handle и
            if ch == 'и':
                if prev == 'и':
                    result.append('i')
                elif prev in self.vowels and next_ch not in ['я', 'ё', 'ю']:
                    result.append('ii')
                else:
                    result.append('i')
                i += 1
                continue
            
            # Handle я
            if ch == 'я':
                if self.consonants_pattern.match(prev):
                    result.append('ä')
                elif prev == 'и':
                    result.append('ia')
                elif prev in self.vowels:
                    result.append('a')
                else:
                    result.append('ea')
                i += 1
                continue
            
            # Handle ё
            if ch == 'ё':
                if self.consonants_pattern.match(prev):
                    result.append('e')
                elif prev == 'и':
                    result.append('io')
                elif prev in self.vowels:
                    result.append('e')
                else:
                    result.append('e')
                i += 1
                continue
            
            # Handle ю
            if ch == 'ю':
                if self.consonants_pattern.match(prev):
                    result.append('ü')
                elif prev == 'и':
                    result.append('iu')
                elif prev in self.vowels:
                    result.append('u')
                else:
                    result.append('eu')
                i += 1
                continue
            
            # Handle у
            if ch == 'у':
                if prev in self.vowels:
                    result.append('w')
                else:
                    result.append('u')
                i += 1
                continue
            
            # Handle а after vowels (except и, е) - but not after same vowel
            if ch == 'а' and prev in self.vowels and prev not in ['и', 'е'] and prev != 'а':
                result.append('wa')
                i += 1
                continue
            
            # Handle о after vowels (except и, е) - but not after same vowel
            if ch == 'о' and prev in self.vowels and prev not in ['и', 'е'] and prev != 'о':
                result.append('wo')
                i += 1
                continue
            
            # Default mapping
            result.append(self.map.get(ch, ch))
            i += 1
        
        # Join the result
        transliterated_word = ''.join(result)
        
        # Preserve capitalization
        if len(word) > 0 and word[0].isupper():
            transliterated_word = transliterated_word.capitalize()
        
        return transliterated_word
    
    def transliterate(self, text: str) -> str:
        """
        Transliterate Russian text to Latin script.
        
        Args:
            text: Russian text to transliterate
            
        Returns:
            Transliterated text in Latin script
        """
        if not text:
            return text
        
        # Split text into tokens (words and punctuation/spaces)
        tokens = re.split(r'([\s,.!?]+)', text)
        output = ''
        
        for token in tokens:
            # Check if token contains Cyrillic characters
            if re.search(r'[а-яё]', token, re.IGNORECASE):
                output += self.transliterate_word(token)
            else:
                output += token
        
        return output
