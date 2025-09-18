import numpy as np
from PIL import Image
import math
import os

# --- Helper functions (no changes here) ---
def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def reveal_message(image_path):
    try:
        image = Image.open(image_path, 'r').convert("RGB")
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    
    binary_message = ""
    delimiter = "_STOP_"
    binary_delimiter = text_to_binary(delimiter)
    
    pixels = np.array(image)
    height, width, _ = pixels.shape

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y, x]
            binary_message += str(r & 1)
            if binary_delimiter in binary_message:
                return binary_to_text(binary_message[:binary_message.find(binary_delimiter)])
            binary_message += str(g & 1)
            if binary_delimiter in binary_message:
                return binary_to_text(binary_message[:binary_message.find(binary_delimiter)])
            binary_message += str(b & 1)
            if binary_delimiter in binary_message:
                return binary_to_text(binary_message[:binary_message.find(binary_delimiter)])
    print("Error: Could not find a hidden message.")
    return None

# --- Evaluation Functions (no changes here) ---
def calculate_psnr(original_image_path, stego_image_path):
    try:
        original = Image.open(original_image_path).convert("RGB")
        stego = Image.open(stego_image_path).convert("RGB")
    except FileNotFoundError:
        print("Error: One of the image files was not found.")
        return None

    original_arr = np.array(original)
    stego_arr = np.array(stego)

    if original_arr.shape != stego_arr.shape:
        print("Error: Images have different dimensions.")
        return None

    mse = np.mean((original_arr - stego_arr) ** 2)
    if mse == 0: return float('inf')
    max_pixel_value = 255.0
    psnr = 20 * math.log10(max_pixel_value / math.sqrt(mse))
    return psnr

def calculate_ber(original_message, extracted_message):
    if extracted_message is None: return 1.0
    binary_original = text_to_binary(original_message)
    binary_extracted = text_to_binary(extracted_message)
    max_len = max(len(binary_original), len(binary_extracted))
    binary_original = binary_original.ljust(max_len, '0')
    binary_extracted = binary_extracted.ljust(max_len, '0')
    error_count = sum(1 for ob, eb in zip(binary_original, binary_extracted) if ob != eb)
    total_bits = len(binary_original)
    if total_bits == 0: return 0.0
    ber = error_count / total_bits
    return ber

# --- Main part to run the evaluation ---
# --- THIS SECTION IS MODIFIED ---
if __name__ == "__main__":
    print("--- Steganography Evaluation ---")
    
    original_img = input("Enter the path to the ORIGINAL image: ")
    
    stego_img = None
    original_msg = None
    
    # --- NEW: Look for the record in table.txt ---
    log_file = "table.txt"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f:
                # Skip header and separator lines
                if "Original Image Path" in line or "---" in line:
                    continue
                
                parts = line.strip().split(' | ')
                if len(parts) == 3 and parts[0] == original_img:
                    stego_img = parts[1]
                    original_msg = parts[2]
                    print(f"\n✅ Record found in {log_file}!")
                    print(f"   - Stego Image: {stego_img}")
                    print(f"   - Secret Message: {original_msg}")
                    break
    
    # --- If no record was found, ask for details manually ---
    if stego_img is None:
        print(f"\nℹ️ No record found for '{original_img}' in {log_file}. Please enter details manually.")
        stego_img = input("Enter the path to the STEGO image: ")
        original_msg = input("Enter the ORIGINAL secret message that was hidden: ")

    # --- Proceed with calculations using the found or manually entered data ---
    print("\nCalculating PSNR...")
    psnr_value = calculate_psnr(original_img, stego_img)
    
    if psnr_value is not None:
        if psnr_value == float('inf'):
            print("  PSNR Result: Infinite (The images are identical).")
        else:
            print(f"  PSNR Result: {psnr_value:.2f} dB (Higher is better)")

    print("\nCalculating BER...")
    extracted_msg = reveal_message(stego_img)
    
    if extracted_msg:
        print(f"  Extracted message: '{extracted_msg}'")
    else:
        print("  Could not extract a message.")

    ber_value = calculate_ber(original_msg, extracted_msg)
    print(f"  BER Result: {ber_value:.5f} (0.0 is a perfect extraction)")