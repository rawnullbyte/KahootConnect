# KahootConnect/Crypto/TokenDecryptor.py
import re
import base64
import logging
import urllib.parse

class TokenDecryptor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_message(self, challenge: str) -> str:
        """Extract message from challenge JavaScript"""
        match = re.search(r"decode\.call\(this,\s*'([^']+)'", challenge)
        if match:
            return match.group(1)
        self.logger.error("Message not found in challenge\nChallenge: {challenge}")
        raise ValueError("Message not found in challenge")

    def get_offset(self, challenge: str) -> int:
        """Extract and calculate offset from challenge - handles multiple patterns"""
        clean_challenge = re.sub(r'[ \s]+', ' ', challenge)
        
        patterns = [
            {
                'pattern': r'offset\s*=\s*\(\(\s*(\d+)\s*\+\s*(\d+)\s*\)\s*\+\s*(\d+)\s*\+\s*\(\s*(\d+)\s*\+\s*(\d+)\s*\)\)\s*\+\s*(\d+)',
                'calculation': lambda groups: ((int(groups[0]) + int(groups[1])) + int(groups[2]) + (int(groups[3]) + int(groups[4]))) + int(groups[5]),
                'name': '((a+b)+c+(d+e))+f'
            },
            {
                'pattern': r'offset\s*=\s*\(\(\s*(\d+)\s*\+\s*(\d+)\s*\)\s*\*\s*\(\s*(\d+)\s*\+\s*(\d+)\s*\)\)',
                'calculation': lambda groups: (int(groups[0]) + int(groups[1])) * (int(groups[2]) + int(groups[3])),
                'name': '(a+b)*(c+d)'
            },
            {
                'pattern': r'offset\s*=\s*\(\(\s*(\d+)\s*\+\s*(\d+)\s*\)\s*\*\s*(\d+)\s*\*\s*\(\s*(\d+)\s*\+\s*(\d+)\s*\)\)',
                'calculation': lambda groups: (int(groups[0]) + int(groups[1])) * int(groups[2]) * (int(groups[3]) + int(groups[4])),
                'name': '((a+b)*c*(d+e))'
            },
            {
                'pattern': r'offset\s*=\s*(\([^;]+);',
                'calculation': lambda groups: self._eval_expression(groups[0]),
                'name': 'arithmetic_expression'
            },
        ]
        
        for pattern_info in patterns:
            match = re.search(pattern_info['pattern'], clean_challenge)
            if match:
                self.logger.debug(f"Pattern matched: {pattern_info['name']}")
                try:
                    offset = pattern_info['calculation'](match.groups())
                    self.logger.debug(f"Calculated offset: {offset}")
                    return offset
                except Exception as e:
                    self.logger.error(f"Calculation failed for pattern {pattern_info['name']}: {e}")
                    continue
        
        numbers = self._extract_all_numbers(clean_challenge)
        if numbers:
            self.logger.debug(f"Fallback: Found numbers: {numbers}")
            offset = self._guess_calculation(numbers)
            if offset is not None:
                self.logger.debug(f"Guessed offset: {offset}")
                return offset
        
        self.logger.error(f"Could not find offset in challenge")
        raise ValueError("Offset not found in challenge")

    def _eval_expression(self, expression: str) -> int:
        """Evaluate arithmetic expression safely"""
        expr_clean = re.sub(r'[^0-9+*()]', '', expression.strip())
        self.logger.debug(f"Evaluating expression: {expr_clean}")
        return eval(expr_clean)

    def _extract_all_numbers(self, text: str) -> list:
        """Extract all numbers from text"""
        numbers = re.findall(r'\b\d+\b', text)
        return [int(n) for n in numbers]

    def _guess_calculation(self, numbers: list) -> int:
        """Try to guess the calculation from numbers"""
        if len(numbers) >= 6:
            try:
                return ((numbers[0] + numbers[1]) + numbers[2] + (numbers[3] + numbers[4])) + numbers[5]
            except:
                pass
        
        if len(numbers) >= 4:
            try:
                return (numbers[0] + numbers[1]) * (numbers[2] + numbers[3])
            except:
                pass
        
        if len(numbers) >= 5:
            try:
                return (numbers[0] + numbers[1]) * numbers[2] * (numbers[3] + numbers[4])
            except:
                pass
        
        if numbers:
            return sum(numbers)
        
        return None

    def generate_key(self, message: str, offset: int) -> str:
        """Generate XOR key for decryption"""
        key = ""
        for position, char in enumerate(message):
            key_char = chr((ord(char) * position + offset) % 77 + 48)
            key += key_char
        return key

    def xor_decrypt(self, encrypted_token: str, key: str) -> str:
        """Perform XOR decryption"""
        try:
            decoded_token = base64.b64decode(encrypted_token).decode('utf-8')
            
            result = ""
            for i in range(len(decoded_token)):
                char_code = ord(decoded_token[i])
                key_code = ord(key[i % len(key)])
                result += chr(char_code ^ key_code)
            
            return result
        except Exception as e:
            self.logger.error(f"XOR decryption failed: {e}")
            raise

    def decrypt(self, encrypted_token: str, challenge: str) -> str:
        """Complete token decryption process"""
        try:
            self.logger.debug(f"Challenge preview: {challenge[:200]}...")
            
            message = self.get_message(challenge)
            self.logger.debug(f"Extracted message: {message}")
            
            offset = self.get_offset(challenge)
            self.logger.debug(f"Calculated offset: {offset}")
            
            key = self.generate_key(message, offset)
            self.logger.debug(f"Generated key length: {len(key)}")
            
            decrypted_token = self.xor_decrypt(encrypted_token, key)
            self.logger.debug(f"Raw decrypted token: {decrypted_token}")
            
            # URL-encode the token to handle special characters
            url_safe_token = urllib.parse.quote(decrypted_token, safe='')
            self.logger.debug(f"URL-safe token: {url_safe_token}")
            
            self.logger.info("Successfully decrypted session token")
            
            return url_safe_token
            
        except Exception as e:
            self.logger.error(f"Token decryption failed: {e}")
            raise