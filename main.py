import asyncio
import logging
from KahootConnect.KahootClient import KahootClient

async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get game details
    game_pin = input("Enter game PIN: ").strip()
    player_name = input("Enter your name: ").strip()
    
    # Create client with new constructor
    client = KahootClient(game_pin, player_name)
    
    # Set up event handlers using new event names
    async def on_gameBlockUpdate(ctx):
        """Handle new question events"""
        question_data = ctx.data
        question_type = ctx.type
        question_index = ctx.index
        question_status = ctx.status

        if question_status == "awaiting":
            print(f"Question {question_index} received but is not active yet! (status: {question_status})")
            return  # Ignore non-started questions
        elif question_status == "ended":
            print(f"Question {question_index} has ended! (status: {question_status})")
            print(f"isCorrect: {"✅" if ctx.isCorrect else "❌"}")
            print(f"Your answer: {ctx.answers}")
            print(f"Correct answer: {ctx.correctAnswers}")
            print(f"Points received: {ctx.points}")
            return  # Ignore ended questions
        
        print(f"\n{'='*50}")
        print(f"❓ Question {question_index}")
        print(f"📝 Type: {question_type}")
        
        # Handle different question types
        if question_type == 'quiz':
            await handle_quiz_question(ctx, question_data)
        elif question_type == 'multiple_select_quiz':
            await handle_multiple_select_question(ctx, question_data)
        elif question_type == 'slider':
            await handle_slider_question(ctx, question_data)
        elif question_type == 'open_ended':
            await handle_open_ended_question(ctx, question_data)
        elif question_type == 'jumble':
            await handle_jumble_question(ctx, question_data)
        else:
            print(f"📄 Unknown Type: {question_type}")
            print("⏳ Waiting for next question...")
    
    async def handle_quiz_question(ctx, data):
        """Handle regular quiz questions"""
        layout = data.get('layout')
        number_of_choices = data.get('numberOfChoices', 4)
        time_available = data.get('timeAvailable', 0) / 1000
        
        if layout == 'TRUE_FALSE':
            print("🔘 True/False Question")
            print(f"⏱️ Time: {time_available}s")
            print("\nOptions:")
            print("0: False")
            print("1: True")
            
            while True:
                try:
                    choice = input("\nEnter your answer (0 for False, 1 for True): ").strip()
                    if choice in ['0', '1']:
                        success = await ctx.answer(choice=0 if choice == '1' else 1) # Must be reversed!
                        if success:
                            print("✅ Answer sent successfully!")
                        else:
                            print("❌ Failed to send answer (too late or invalid)")
                        break
                    else:
                        print("❌ Please enter 0 for False or 1 for True")
                except KeyboardInterrupt:
                    print("\n⏹️ Skipping question...")
                    break
        else:
            print(f"🔢 Multiple Choice (A/B/C/D)")
            print(f"⏱️ Time: {time_available}s")
            print(f"📊 Choices: {number_of_choices}")
            print("\nOptions:")
            for i in range(number_of_choices):
                print(f"{i}: Option {chr(65 + i)}")  # A, B, C, D
            
            while True:
                try:
                    choice = input(f"\nEnter your answer (0-{number_of_choices-1}): ").strip()
                    if choice.isdigit() and 0 <= int(choice) < number_of_choices:
                        success = await ctx.answer(choice=int(choice))
                        if success:
                            print("✅ Answer sent successfully!")
                        else:
                            print("❌ Failed to send answer (too late or invalid)")
                        break
                    else:
                        print(f"❌ Please enter a number between 0 and {number_of_choices-1}")
                except KeyboardInterrupt:
                    print("\n⏹️ Skipping question...")
                    break
    
    async def handle_multiple_select_question(ctx, data):
        """Handle multiple select questions"""
        number_of_choices = data.get('numberOfChoices', 4)
        time_available = data.get('timeAvailable', 0) / 1000
        
        print(f"🔢 Multiple Select Question")
        print(f"⏱️ Time: {time_available}s")
        print(f"📊 Choices: {number_of_choices}")
        print("\nOptions:")
        for i in range(number_of_choices):
            print(f"{i}: Option {i+1}")
        print("\nEnter multiple choices separated by commas (e.g., 0,2,3)")
        
        while True:
            try:
                choices_input = input(f"\nEnter your choices (0-{number_of_choices-1}): ").strip()
                if choices_input.lower() == 'skip':
                    print("⏹️ Skipping question...")
                    break
                
                choices = [int(c.strip()) for c in choices_input.split(',')]
                valid_choices = all(0 <= c < number_of_choices for c in choices)
                
                if valid_choices and choices:
                    success = await ctx.answer(choice=choices)
                    if success:
                        print("✅ Answer sent successfully!")
                    else:
                        print("❌ Failed to send answer (too late or invalid)")
                    break
                else:
                    print(f"❌ Please enter valid numbers between 0 and {number_of_choices-1}")
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid input. Please enter numbers separated by commas")
                break
    
    async def handle_slider_question(ctx, data):
        """Handle slider questions"""
        min_range = data.get('minRange', 0)
        max_range = data.get('maxRange', 100)
        step = data.get('step', 1)
        time_available = data.get('timeAvailable', 0) / 1000
        
        print(f"🎚️ Slider Question")
        print(f"⏱️ Time: {time_available}s")
        print(f"📊 Range: {min_range} to {max_range} (step: {step})")
        
        while True:
            try:
                value = input(f"\nEnter your value ({min_range}-{max_range}): ").strip()
                if value.lower() == 'skip':
                    print("⏹️ Skipping question...")
                    break
                
                value_int = int(value)
                if min_range <= value_int <= max_range:
                    success = await ctx.answer(value=value_int)
                    if success:
                        print("✅ Answer sent successfully!")
                    else:
                        print("❌ Failed to send answer (too late or invalid)")
                    break
                else:
                    print(f"❌ Please enter a value between {min_range} and {max_range}")
            except (ValueError, KeyboardInterrupt):
                print("❌ Please enter a valid number")
                break
    
    async def handle_open_ended_question(ctx, data):
        """Handle open-ended questions"""
        time_available = data.get('timeAvailable', 0) / 1000
        
        print(f"\n📝 Open-Ended Question")
        print(f"⏱️ Time: {time_available}s")
        print("💬 Enter your text answer:")
        
        text_answer = input("Your answer: ").strip()
        if text_answer and text_answer.lower() != 'skip':
            success = await ctx.answer(text=text_answer)
            if success:
                print("✅ Answer sent successfully!")
            else:
                print("❌ Failed to send answer (too late or invalid)")

    async def handle_jumble_question(ctx, data):
        """Handle open-ended questions"""
        time_available = data.get('timeAvailable', 0) / 1000
        
        print(f"\n📝 Jumble Question")
        print(f"⏱️ Time: {time_available}s")
        print("💬 Enter your text answer:")
        
        dict_text_answer = input("Your answer (0,2,1,3): ").strip()
        if dict_text_answer and dict_text_answer.lower() != 'skip':
            dict_answer = [int(x) for x in dict_text_answer.split(',')]
            success = await ctx.answer(choice=dict_answer)
            if success:
                print("✅ Answer sent successfully!")
            else:
                print("❌ Failed to send answer (too late or invalid)")
    
    async def on_leaderboard(data):
        leaderboard = data.get('leaderboard', [])
        print(f"\n🏆 Leaderboard (Top {len(leaderboard)}):")
        for i, player in enumerate(leaderboard[:10]):  # Show top 10
            rank = i + 1
            name = player.get('name', 'Unknown')
            score = player.get('score', 0)
            print(f"{rank}. {name} - {score} points")
    
    async def on_game_over(data):
        print("\n🎉 Game Over!")
        print("Thanks for playing! 👋")
    
    # Set up event handlers with new names
    client.on_gameBlockUpdate(on_gameBlockUpdate)
    client.on_leaderboard(on_leaderboard)
    client.on_gameOver(on_game_over)
    
    # Connect and play
    print(f"\nConnecting to game {game_pin} as {player_name}...")
    if await client.connect():
        print("✅ Connected! Waiting for game to start...")
        await client.listen()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())