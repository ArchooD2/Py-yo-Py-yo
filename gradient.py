import sys
import tkinter as tk
from tkinter import colorchooser, simpledialog
from tkinter import ttk
from colour import Color
import pyperclip

def hex_to_rgb(hex_color):
    """Converts a hex color to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    """Converts an RGB tuple to a hex color."""
    return '#{:02X}{:02X}{:02X}'.format(*rgb_color)

def interpolate_color(color1, color2, fraction):
    """Interpolates between two RGB colors by a given fraction."""
    return tuple(
        int(color1[i] + (color2[i] - color1[i]) * fraction)
        for i in range(3)
    )

def generate_gradient_tags(color1_hex, color2_hex, text, word_mode=False):
    """Generates color tags for text based on a gradient between two hex colors,
    ignoring syllable spacers ('/') and spaces.
    """
    color1_rgb = hex_to_rgb(color1_hex)
    color2_rgb = hex_to_rgb(color2_hex)

    gradient_tags = ""
    colored_char_count = len([char for char in text if char not in ['/', ' ']])

    if colored_char_count == 0:
        return text  # Return the input directly if there are no colorable characters

    color_index = 0  # To keep track of how many colorable characters have been processed

    for i, char in enumerate(text):
        if char in ['/', ' ']:
            # For syllable spacers and spaces, add them directly without color tags
            gradient_tags += char
        else:
            fraction = color_index / (colored_char_count - 1) if colored_char_count > 1 else 0
            interpolated_color = interpolate_color(color1_rgb, color2_rgb, fraction)
            color_hex = rgb_to_hex(interpolated_color)
            
            # Add color tags around the character
            gradient_tags += f"<color={color_hex}>{char}</color>"
            color_index += 1

    return gradient_tags.strip()

def copy_to_clipboard(text):
    """Copies text to the clipboard."""
    pyperclip.copy(text)

def create_ui():
    root = tk.Tk()
    root.title("Gradient Text Generator")
    root.geometry("500x450")

    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat", background="#cccccc")
    
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Color picker and text entry widgets
    ttk.Label(main_frame, text="Start Color:").grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
    start_color_entry = tk.Entry(main_frame)
    start_color_entry.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

    def pick_start_color():
        color_code = colorchooser.askcolor(title="Choose Start Color")[1]
        if color_code:
            start_color_entry.delete(0, tk.END)
            start_color_entry.insert(0, color_code)
            start_color_preview.config(bg=color_code)

    pick_start_button = ttk.Button(main_frame, text="Pick Color", command=pick_start_color)
    pick_start_button.grid(column=2, row=0, padx=5, pady=5)

    start_color_preview = tk.Label(main_frame, text="", width=2, bg="#ffffff")
    start_color_preview.grid(column=3, row=0, padx=5, pady=5)

    ttk.Label(main_frame, text="End Color:").grid(column=0, row=1, padx=5, pady=5, sticky=tk.W)
    end_color_entry = tk.Entry(main_frame)
    end_color_entry.grid(column=1, row=1, padx=5, pady=5, sticky=(tk.W, tk.E))

    def pick_end_color():
        color_code = colorchooser.askcolor(title="Choose End Color")[1]
        if color_code:
            end_color_entry.delete(0, tk.END)
            end_color_entry.insert(0, color_code)
            end_color_preview.config(bg=color_code)

    pick_end_button = ttk.Button(main_frame, text="Pick Color", command=pick_end_color)
    pick_end_button.grid(column=2, row=1, padx=5, pady=5)

    end_color_preview = tk.Label(main_frame, text="", width=2, bg="#ffffff")
    end_color_preview.grid(column=3, row=1, padx=5, pady=5)

    ttk.Label(main_frame, text="Text:").grid(column=0, row=2, padx=5, pady=5, sticky=tk.W)
    text_entry = tk.Entry(main_frame, width=40)
    text_entry.grid(column=1, row=2, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

    word_mode = tk.BooleanVar()
    word_mode_check = ttk.Checkbutton(main_frame, text="Word Mode", variable=word_mode)
    word_mode_check.grid(column=0, row=3, columnspan=2, pady=5, sticky=tk.W)

    def generate_output():
        start_color = start_color_entry.get()
        end_color = end_color_entry.get()
        text = text_entry.get()
        result = generate_gradient_tags(start_color, end_color, text, word_mode=word_mode.get())
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, result)
        preview_label.config(text=text, fg=start_color)  # Quick visual with the start color
        copy_to_clipboard(result)

    generate_button = ttk.Button(main_frame, text="Generate and Copy", command=generate_output)
    generate_button.grid(column=1, row=4, columnspan=3, pady=10)

    ttk.Label(main_frame, text="Output:").grid(column=0, row=5, padx=5, pady=5, sticky=tk.W)
    output_text = tk.Text(main_frame, height=5, width=60, wrap="word")
    output_text.grid(column=0, row=6, columnspan=4, padx=5, pady=5, sticky=(tk.W, tk.E))

    preview_label = tk.Label(main_frame, text="", font=("Helvetica", 12, "bold"))
    preview_label.grid(column=0, row=7, columnspan=4, padx=5, pady=5)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.columnconfigure(2, weight=1)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        color1 = sys.argv[1]  # Start color
        color2 = sys.argv[2]  # End color
        text = sys.argv[3]    # Text input
        result = generate_gradient_tags(color1, color2, text)
        print(result)
    else:
        create_ui()
