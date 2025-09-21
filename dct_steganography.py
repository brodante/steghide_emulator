import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct
import sys

# --- Helper functions ---
def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

# --- 2D DCT/IDCT functions ---
def dct2(block):
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block):
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

def hide_message_dct(image_path, secret_message, output_path):
    """Hides a secret message in an image using DCT, with a capacity check."""
    try:
        image = Image.open(image_path).convert('L')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return
        
    pixels = np.array(image)
    
    # Capacity Check
    secret_message_with_delimiter = secret_message + "_STOP_"
    binary_message = text_to_binary(secret_message_with_delimiter)
    required_bits = len(binary_message)
    
    height, width = pixels.shape
    height_blocks, width_blocks = height // 8, width // 8
    coeffs_per_block = 4
    
    image_capacity_bits = height_blocks * width_blocks * coeffs_per_block

    if required_bits > image_capacity_bits:
        print("--- Error: Message is too long to be hidden in this image. ---")
        print(f"Image capacity: {image_capacity_bits} bits")
        print(f"Required for message: {required_bits} bits")
        return

    message_index = 0
    message_hidden = False
    coeffs_to_modify = [(4, 1), (3, 2), (2, 3), (1, 4)]
    
    # Create a copy to avoid modifying the original array during iteration
    modified_pixels = pixels.copy().astype(np.float32)
    
    for i in range(height_blocks):
        for j in range(width_blocks):
            if message_index >= len(binary_message):
                message_hidden = True
                break
            
            # Extract block
            block = modified_pixels[i*8:(i+1)*8, j*8:(j+1)*8]
            block -= 128
            dct_block = dct2(block)
            
            for k in range(len(coeffs_to_modify)):
                if message_index < len(binary_message):
                    row, col = coeffs_to_modify[k]
                    coeff_val = dct_block[row, col]
                    
                    # Get the integer part for LSB manipulation
                    coeff_int = int(round(coeff_val))
                    
                    # Modify the coefficient to embed the bit
                    target_bit = int(binary_message[message_index])
                    current_lsb = coeff_int & 1
                    
                    if target_bit != current_lsb:
                        # Flip the LSB
                        dct_block[row, col] = coeff_val + (1 if current_lsb == 0 else -1)
                    
                    message_index += 1
                else:
                    break
            
            # Apply inverse DCT and update the block
            modified_block = idct2(dct_block) + 128
            modified_block = np.clip(modified_block, 0, 255)
            modified_pixels[i*8:(i+1)*8, j*8:(j+1)*8] = modified_block

        if message_hidden:
            break

    # Convert back to uint8 for saving
    stego_pixels = modified_pixels.astype(np.uint8)
    stego_image = Image.fromarray(stego_pixels)
    
    # Save with maximum quality to preserve coefficients
    stego_image.save(output_path, format='PNG', compress_level=0)
    print(f"Message hidden successfully in {output_path}")
    
def reveal_message_dct(image_path):
    """Reveals a hidden message from an image using DCT."""
    try:
        image = Image.open(image_path).convert('L')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
        
    pixels = np.array(image).astype(np.float32)
    
    binary_message = ""
    delimiter = text_to_binary("_STOP_")
    delimiter_length = len(delimiter)
    
    height, width = pixels.shape
    height_blocks, width_blocks = height // 8, width // 8
    coeffs_to_modify = [(4, 1), (3, 2), (2, 3), (1, 4)]
    
    # Flag to break out of all loops
    message_found = False
    
    for i in range(height_blocks):
        for j in range(width_blocks):
            block = pixels[i*8:(i+1)*8, j*8:(j+1)*8]
            block -= 128
            dct_block = dct2(block)
            
            for k in range(len(coeffs_to_modify)):
                row, col = coeffs_to_modify[k]
                
                # Extract the coefficient and get its LSB
                coeff_val = dct_block[row, col]
                coeff_int = int(round(coeff_val))
                binary_message += str(coeff_int & 1)
                
                # Efficient delimiter check - only check the end of the string
                if len(binary_message) >= delimiter_length:
                    if binary_message[-delimiter_length:] == delimiter:
                        message_found = True
                        break
            
            if message_found:
                break
        
        if message_found:
            break
    
    if message_found:
        # Remove the delimiter before converting to text
        message_without_delimiter = binary_message[:-delimiter_length]
        return binary_to_text(message_without_delimiter)
    else:
        print("\nError: Reached end of image but could not find the delimiter.")
        print(f"Extracted binary (first 100 bits): {binary_message[:100]}")
        return None

# --- Main part to run the code ---
if __name__ == "__main__":
    mode = input("Do you want to (h)ide or (r)eveal a DCT message? ").lower()
    if mode.startswith('h'):
        original_image = input("Enter the path to the original image: ")
        secret_text = input("Enter the secret message: ")
        output_image = input("Enter the output image path (e.g., secret_dct.png): ")
        hide_message_dct(original_image, secret_text, output_image)
    elif mode.startswith('r'):
        stego_image = input("Enter the path to the image with the hidden message: ")
        revealed_text = reveal_message_dct(stego_image)
        if revealed_text:
            print(f"The revealed message is: {revealed_text}")
        else:
            print("Failed to reveal a message.")
    else:
        print("Invalid mode selected.")