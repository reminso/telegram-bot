import re
from typing import List

class ChuvashTransliterator:
    """
    Chuvash to Latin transliteration system.
    Transliterates Chuvash text from Cyrillic to Latin script.
    Handles specific Chuvash transliteration rules including soft sign processing.
    """
    
    def __init__(self):
        # Transliteration map for Chuvash Cyrillic to Latin
        self.map = {
            'А': 'A', 'а': 'a',
            'Ӑ': 'O', 'ӑ': 'o',
            'В': 'V', 'в': 'v',
            'Е': 'E', 'е': 'e',  # Will be handled in iotation
            'Ё': 'Ö', 'ё': 'ö',  # Will be handled in iotation
            'Ӗ': 'Ė', 'ӗ': 'ė',   # E with dot above
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
            'Ҫ': 'Ś', 'ҫ': 'ś',   # Cyrillic C with descender
            'Ç': 'Ś', 'ç': 'ś',    # Latin C with cedilla (treated same as Ҫ)
            'Т': 'T', 'т': 't',
            'У': 'U', 'у': 'u',
            'Ӳ': 'Ü', 'ӳ': 'ü',    # U with diaeresis
            'Х': 'H', 'х': 'h',
            'Ч': 'C', 'ч': 'c',
            'Ш': 'Š', 'ш': 'š',
            'Щ': 'Ś', 'щ': 'ś',    # Treated same as Ҫ
            'Ы': 'Y', 'ы': 'y',
            'Э': 'E', 'э': 'e',
            'Ю': 'Ü', 'ю': 'ü',    # Will be handled in iotation
            'Я': 'Ä', 'я': 'ä',    # Will be handled in iotation
            
            # Additional Russian letters in borrowings
            'Б': 'B', 'б': 'b',
            'Г': 'G', 'г': 'g',
            'Д': 'D', 'д': 'd',
            'Ж': 'Ž', 'ж': 'ž',
            'З': 'Z', 'з': 'z',
            'Ц': 'Ts', 'ц': 'ts',
            'Ф': 'F', 'ф': 'f',
            
            # Signs
            'Ъ': '', 'ъ': '',      # Hard sign (omitted)
            'Ь': '', 'ь': '',      # Soft sign (processed separately)
        }
    
    def process_soft_sign(self, text: str) -> str:
        """
        Process soft signs (Ь/ь) by doubling the preceding consonant.
        Example: "Пирень" -> "Пиренн"
        """
        pattern = r'([А-Яа-яЁёӐӑӖӗҪҫÇçӲӳ])([ьЬ])'
        return re.sub(pattern, lambda m: m.group(1) * 2, text)
    
    def is_consonant(self, char: str) -> bool:
        """Check if character is a consonant."""
        consonants = 'БВГДЖЗЙКЛМНПРСТФХЦЧШЩҪÇбвгджзйклмнпрстфхцчшщҫç'
        return char in consonants
    
    def handle_iotation(self, word: str) -> str:
        """
        Handle iotated vowels (е, ё, ю, я) based on position.
        After consonant: е→e, ё→ö, ю→ü, я→ä
        Otherwise: е→je, ё→jo, ю→ju, я→ja
        """
        result = []
        for i, char in enumerate(word):
            if char in 'еЕ':
                base = 'e' if char.islower() else 'E'
                result.append(base if i > 0 and self.is_consonant(word[i-1]) else f'j{base.lower()}')
            elif char in 'ёЁ':
                base = 'ö' if char.islower() else 'Ö'
                result.append(base if i > 0 and self.is_consonant(word[i-1]) else f'j{base.lower().replace("ö", "o")}')
            elif char in 'юЮ':
                base = 'ü' if char.islower() else 'Ü'
                result.append(base if i > 0 and self.is_consonant(word[i-1]) else f'j{base.lower().replace("ü", "u")}')
            elif char in 'яЯ':
                base = 'ä' if char.islower() else 'Ä'
                result.append(base if i > 0 and self.is_consonant(word[i-1]) else f'j{base.lower().replace("ä", "a")}')
            else:
                result.append(char)
        return ''.join(result)
    
    def transliterate_word(self, word: str) -> str:
        """Transliterate a single word with all rules applied."""
        if not word:
            return word
        
        processed = self.process_soft_sign(word)
        iotated = self.handle_iotation(processed)
        return ''.join(self.map.get(c, c) for c in iotated)
    
    def transliterate(self, text: str) -> str:
        """Transliterate full text while preserving non-Chuvash characters."""
        if not text:
            return text
        
        # Split while keeping punctuation/whitespace
        tokens = re.split(r'([\wӐӑӖӗҪҫÇçӲӳ]+|[\s,.!?—]+)', text)
        return ''.join(
            self.transliterate_word(token) if re.search(r'[а-яёӐӑӖӗҪҫÇçӲӳ]', token, re.I) else token
            for token in tokens
        )

# Example usage
if __name__ == "__main__":
    transliterator = ChuvashTransliterator()
    text = """
    Ҫурхи юрӑ
    Ҫурхи ҫил вӗҫет,
    Пӗҫӗрӗм тӑрӑхать.
    Хӗвел ҫутать,
    Чун тавра ҫаврӑнать.
    Хамӑр ҫуртра,
    Ҫурхи юрӑ юхать.
    Çутӑ ҫутӑ,
    Чунра ӗҫе кӗрет.
    """
    print(transliterator.transliterate(text))
