import asyncio
from typing import Union, List, Optional
from ...Context import shared_context
from ..Messages.PacketFactory import PacketFactory

class BlockContext:
    """Context for a game block (question)"""
    
    def __init__(self, block_index: int, gameBlock: dict):
        self.index = block_index
        self.type = (gameBlock.get("content") or {}).get("type", "unknown")
        self.data = gameBlock.get("content", "unknown")
        self.status = gameBlock.get("status", "unknown")
        self.pointsData = gameBlock.get("results", {}).get("pointsData")
        self.hasAnswer = gameBlock.get("results", {}).get("hasAnswer")
        self.skip = gameBlock.get("results", {}).get("skip")
        self.points = gameBlock.get("results", {}).get("points")
        self.isCorrect = gameBlock.get("results", {}).get("isCorrect")
        self.correctAnswers = gameBlock.get("results", {}).get("correctAnswers")
        self.answers = gameBlock.get("results", {}).get("answers")
        self.gameBlock = gameBlock

        self._answered = False
        self.logger = shared_context.websocket_client.logger if shared_context.websocket_client else None

    def _is_answer_valid(self, answer) -> tuple[bool, str]:
        """Check if answer is valid"""
        gameBlock = shared_context.game_event_handler.gameBlocks.get(self.index)
        if not gameBlock:
            return False, "Question not found in game blocks"
        
        content = gameBlock.get("content")

        if gameBlock.get("status") != "started":
            return False, "Question is not active"
        
        if content.get("type") == "slider":
            minRange = content["minRange"]
            maxRange = content["maxRange"]

            if answer < minRange or answer > maxRange:
                return False, f"Slider value {answer} out of range ({minRange}-{maxRange})"
        elif content.get("type") == "jumble":
            numberOfChoices = content.get("numberOfChoices", 0)

            if not isinstance(answer, list):
                return False, "Answer must be a list for jumble questions"
            
            if len(answer) != numberOfChoices:
                return False, f"Answer must contain exactly {numberOfChoices} items"
            
            # Check if all numbers are within valid range (0 to numberOfChoices-1)
            valid_numbers = set(range(numberOfChoices))
            if not all(num in valid_numbers for num in answer):
                return False, f"Answer must only contain numbers from 0 to {numberOfChoices-1}"
            
            # Check if all numbers are unique
            if len(set(answer)) != numberOfChoices:
                return False, "Answer must contain unique numbers"


        return True, "Valid answer"

    async def answer(self, 
                    choice: Optional[Union[int, List[int], str]] = None,
                    text: Optional[str] = None,
                    value: Optional[int] = None) -> bool:
        """
        Send answer based on question type
        - quiz/multiple_select_quiz: use choice
        - open_ended: use text  
        - slider: use value
        - jumble: use choice (list)
        """
        if self._answered:
            if self.logger:
                self.logger.warning("Question already answered")
            return False
        
        # Choose the appropriate answer argument (prefer choice, then text, then value)
        if choice is not None:
            answer_arg = choice
        elif text is not None:
            answer_arg = text
        else:
            answer_arg = value

        is_answer_valid, is_answer_valid_message = self._is_answer_valid(answer=answer_arg)
        if is_answer_valid == False:
            self.logger.error(f"❌ Invalid answer: {is_answer_valid_message}")
            return False

        try:
            packet_factory = PacketFactory()
            
            if self.type in ['quiz', 'multiple_select_quiz']:
                if choice is None:
                    raise ValueError(f"Choice required for {self.type}")
                
                if self.type == 'quiz':
                    packet = packet_factory.create_classic_answer(self.index, choice)
                else:  # multiple_select_quiz
                    packet = packet_factory.create_multiple_select_answer(self.index, choice)
                    
            elif self.type == 'open_ended':
                if text is None:
                    raise ValueError("Text required for open_ended question")
                packet = packet_factory.create_open_ended_answer(self.index, text)
                
            elif self.type == 'slider':
                if value is None:
                    raise ValueError("Value required for slider question")
                packet = packet_factory.create_slider_answer(self.index, value)
            elif self.type == 'jumble':
                if choice is None or not isinstance(choice, list):
                    raise ValueError("Choice (list) required for jumble question")
                packet = packet_factory.create_jumble_answer(self.index, choice)
                
            else:
                raise ValueError(f"Unsupported question type: {self.type}")

            await shared_context.websocket_client.send_packet(packet)
            self._answered = True
            
            if self.logger:
                self.logger.info(f"✅ Sent answer for question {self.index}: {self.type}")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to send answer: {e}")
            return False

    def is_active(self) -> bool:
        """Check if the question is still active"""
        game_block = shared_context.game_event_handler.gameBlocks.get(self.index, {})
        return game_block.get("status") == "started" and not self._answered