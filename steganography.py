from PIL import Image
import os # --- NEW: Import the 'os' module to check for file existence ---

def text_to_binary(text):
    """Converts a string of text into a binary string."""
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    """Converts a binary string back into a text string."""
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def hide_message(image_path, secret_message, output_path):
    """Hides a secret message within an image and logs the details."""
    try:
        image = Image.open(image_path, 'r')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return

    image = image.convert("RGB")
    
    # We use the original secret_message for logging before adding the delimiter
    original_message_for_log = secret_message 
    
    secret_message_with_delimiter = secret_message + "_STOP_"
    binary_message = text_to_binary(secret_message_with_delimiter)
    message_index = 0
    
    width, height = image.size
    pixels = image.load()

    if len(binary_message) > width * height * 3:
        print("Error: The message is too long to be hidden in this image.")
        return

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            if message_index < len(binary_message):
                r = (r & 0b11111110) | int(binary_message[message_index])
                message_index += 1
            
            if message_index < len(binary_message):
                g = (g & 0b11111110) | int(binary_message[message_index])
                message_index += 1

            if message_index < len(binary_message):
                b = (b & 0b11111110) | int(binary_message[message_index])
                message_index += 1

            pixels[x, y] = (r, g, b)

            if message_index >= len(binary_message):
                break
        if message_index >= len(binary_message):
            break
            
    try:
        image.save(output_path)
        print(f"Message hidden successfully in {output_path}")

        # --- NEW CODE START ---
        # Log the operation details to table.txt
        log_file = "table.txt"
        header = "Original Image Path | Stego Image Path | Secret Message\n"
        log_entry = f"{image_path} | {output_path} | {original_message_for_log}\n"

        # If the log file doesn't exist, create it and write the header first
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                f.write(header)
                f.write("--- | --- | ---\n") # Separator for markdown-like tables
                f.write(log_entry)
        else:
            # If it exists, just append the new entry
            with open(log_file, "a") as f:
                f.write(log_entry)
        
        print(f"Details logged to {log_file}")
        # --- NEW CODE END ---

    except (ValueError, IOError) as e:
        print(f"Error saving file: {e}. Please ensure the output path is a valid filename.")


def reveal_message(image_path):
    """Reveals a hidden message from an image."""
    try:
        image = Image.open(image_path, 'r').convert("RGB")
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None

    binary_message = ""
    delimiter = "_STOP_"
    binary_delimiter = text_to_binary(delimiter)
    
    width, height = image.size
    pixels = image.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

            if binary_delimiter in binary_message:
                message_part = binary_message[:binary_message.find(binary_delimiter)]
                return binary_to_text(message_part)
                
    print("Error: Could not find a hidden message.")
    return None

# --- Main part to run the code (no changes here) ---
if __name__ == "__main__":
    mode = input("Do you want to (h)ide or (r)eveal a message? ").lower()
    if mode.startswith('h'):
        original_image = input("Enter the path to the original image (e.g., my_image.png): ")
        secret_text = input("Enter the secret message you want to hide: ")
        output_image = input("Enter the output image path (e.g., secret_image.png): ")
        hide_message(original_image, secret_text, output_image)
    elif mode.startswith('r'):
        stego_image = input("Enter the path to the image with the hidden message: ")
        revealed_text = reveal_message(stego_image)
        if revealed_text:
            print(f"The hidden message is: {revealed_text}")
    else:
        print("Invalid mode selected. Please choose 'hide' or 'reveal'.")