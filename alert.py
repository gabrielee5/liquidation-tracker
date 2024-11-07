import os
import time

def play_alert(sound_name='Ping'):
    """
    Play a system sound alert on macOS.
    
    Args:
        sound_name (str): Name of the system sound to play.
        Available options include: 
        - Ping
        - Tink
        - Pop
        - Purr
        - Glass
        - Blow
        - Funk
        - Hero
        - Morse
        - Submarine
        - Sosumi
    """
    sound_path = f'/System/Library/Sounds/{sound_name}.aiff'
    if os.path.exists(sound_path):
        os.system(f'afplay {sound_path}')
    else:
        print(f"Sound '{sound_name}' not found. Using default 'Ping' sound.")
        os.system('afplay /System/Library/Sounds/Ping.aiff')

def example_usage():
    """Example of how to use the alert in your code"""
    threshold = 100
    current_value = 150
    
    # Check condition and trigger alert
    if current_value > threshold:
        print("Alert: Threshold exceeded!")
        play_alert('Blow')  # Play a more attention-grabbing sound
        
        # For multiple alerts, you might want to add a delay
        time.sleep(1)
        play_alert('Ping')

# Test different system sounds
if __name__ == "__main__":
    print("Testing different system sounds...")
    sounds = ['Ping', 'Tink', 'Pop', 'Purr', 'Glass', 'Blow', 'Funk', 'Hero', 'Morse', 'Submarine', 'Sosumi']
    for sound in sounds:
        print(f"Playing {sound}...")
        play_alert(sound)
        time.sleep(0.2)  # Wait between sounds