#!/usr/bin/env python3
"""
Generate a set of sample images with numbered labels.

Uses Pillow (PIL) for image creation, text rendering, and JPEG export.
Install with: pip install Pillow
"""

import argparse
import os
import random
from PIL import Image, ImageDraw, ImageFont


def parse_aspect_ratio(ratio_str):
    """Parse aspect ratio string like '3:2' into (horizontal, vertical) tuple."""
    parts = ratio_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid aspect ratio format: {ratio_str}. Use format 'H:V' (e.g., '3:2')")
    return int(parts[0]), int(parts[1])


def parse_color(color_str):
    """Parse color string - supports hex (#RRGGBB) or named colors."""
    if color_str.startswith('#'):
        # Hex color
        hex_color = color_str.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        elif len(hex_color) == 3:
            return tuple(int(c*2, 16) for c in hex_color)
    # Try as RGB tuple string like "128,128,128"
    if ',' in color_str:
        parts = color_str.split(',')
        if len(parts) == 3:
            return tuple(int(p.strip()) for p in parts)
    # Named colors
    named_colors = {
        'darkgray': (64, 64, 64),
        'dark_gray': (64, 64, 64),
        'lightgray': (192, 192, 192),
        'light_gray': (192, 192, 192),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
    }
    lower_color = color_str.lower().replace(' ', '_')
    if lower_color in named_colors:
        return named_colors[lower_color]
    raise ValueError(f"Unknown color format: {color_str}")


def get_font_size_to_fill(draw, text, max_width, max_height, font_path=None):
    """Find the largest font size that fits the text within the given dimensions."""
    # Start with a reasonable font size and binary search
    min_size = 10
    max_size = min(max_width, max_height) * 2  # Upper bound
    best_size = min_size
    
    while min_size <= max_size:
        mid_size = (min_size + max_size) // 2
        try:
            if font_path:
                font = ImageFont.truetype(font_path, mid_size)
            else:
                # Try to use a default system font
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", mid_size)
                except OSError:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", mid_size)
                    except OSError:
                        font = ImageFont.load_default()
                        # Default font doesn't scale, so just return it
                        return font
        except OSError:
            font = ImageFont.load_default()
            return font
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if text_width <= max_width and text_height <= max_height:
            best_size = mid_size
            min_size = mid_size + 1
        else:
            max_size = mid_size - 1
    
    # Return font at best size
    try:
        if font_path:
            return ImageFont.truetype(font_path, best_size)
        else:
            try:
                return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", best_size)
            except OSError:
                try:
                    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", best_size)
                except OSError:
                    return ImageFont.load_default()
    except OSError:
        return ImageFont.load_default()


def generate_image(number, width, height, bg_color, fg_color, output_path):
    """Generate a single image with the number centered."""
    # Create image with background color
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Text to render
    text = str(number)
    
    # Calculate maximum text area (80% of image dimensions for padding)
    max_text_width = int(width * 0.8)
    max_text_height = int(height * 0.8)
    
    # Get font that fills most of the space
    font = get_font_size_to_fill(draw, text, max_text_width, max_text_height)
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center text
    x = (width - text_width) // 2 - bbox[0]
    y = (height - text_height) // 2 - bbox[1]
    
    # Draw the text
    draw.text((x, y), text, font=font, fill=fg_color)
    
    # Save as JPEG
    image.save(output_path, 'JPEG', quality=85)


def main():
    parser = argparse.ArgumentParser(
        description='Generate sample images with numbered labels.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-o', '--output',
        default='samples/',
        help='Destination folder for generated images'
    )
    
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=40,
        help='Number of images to generate'
    )
    
    parser.add_argument(
        '-p', '--portrait-fraction',
        type=float,
        default=0.5,
        help='Fraction of images in portrait orientation (0.0 to 1.0)'
    )
    
    parser.add_argument(
        '-a', '--aspect-ratio',
        default='3:2',
        help='Aspect ratio in format horizontal:vertical (e.g., 3:2)'
    )
    
    parser.add_argument(
        '-l', '--long-edge',
        type=int,
        default=3000,
        help='Long edge pixel count'
    )
    
    parser.add_argument(
        '-b', '--background',
        default='darkgray',
        help='Background color (hex #RRGGBB, RGB "R,G,B", or named color)'
    )
    
    parser.add_argument(
        '-f', '--foreground',
        default='lightgray',
        help='Foreground/text color (hex #RRGGBB, RGB "R,G,B", or named color)'
    )
    
    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=None,
        help='Random seed for reproducible orientation selection'
    )
    
    args = parser.parse_args()
    
    # Validate portrait fraction
    if not 0.0 <= args.portrait_fraction <= 1.0:
        parser.error("Portrait fraction must be between 0.0 and 1.0")
    
    # Parse aspect ratio
    try:
        h_ratio, v_ratio = parse_aspect_ratio(args.aspect_ratio)
    except ValueError as e:
        parser.error(str(e))
    
    # Parse colors
    try:
        bg_color = parse_color(args.background)
    except ValueError as e:
        parser.error(f"Invalid background color: {e}")
    
    try:
        fg_color = parse_color(args.foreground)
    except ValueError as e:
        parser.error(f"Invalid foreground color: {e}")
    
    # Calculate dimensions
    # For landscape: long edge is horizontal
    # For portrait: long edge is vertical
    aspect = h_ratio / v_ratio
    
    if aspect >= 1:
        # Horizontal ratio >= vertical, so landscape has long edge horizontal
        landscape_width = args.long_edge
        landscape_height = int(args.long_edge / aspect)
    else:
        # Vertical ratio > horizontal, so landscape still has long edge horizontal
        landscape_width = args.long_edge
        landscape_height = int(args.long_edge / aspect)
    
    # Portrait is rotated landscape
    portrait_width = landscape_height
    portrait_height = landscape_width
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
    
    # Generate images
    print(f"Generating {args.count} images...")
    print(f"  Output folder: {args.output}")
    print(f"  Aspect ratio: {args.aspect_ratio}")
    print(f"  Long edge: {args.long_edge}px")
    print(f"  Portrait fraction: {args.portrait_fraction}")
    print(f"  Landscape dimensions: {landscape_width}x{landscape_height}")
    print(f"  Portrait dimensions: {portrait_width}x{portrait_height}")
    print(f"  Background: {bg_color}")
    print(f"  Foreground: {fg_color}")
    print()
    
    for i in range(1, args.count + 1):
        # Determine orientation based on portrait fraction
        is_portrait = random.random() < args.portrait_fraction
        
        if is_portrait:
            width, height = portrait_width, portrait_height
            orientation = "portrait"
        else:
            width, height = landscape_width, landscape_height
            orientation = "landscape"
        
        # Generate filename with zero-padded number
        filename = f"{i:04d}.jpg"
        output_path = os.path.join(args.output, filename)
        
        # Generate the image
        generate_image(i, width, height, bg_color, fg_color, output_path)
        
        print(f"  [{i}/{args.count}] {filename} ({orientation}, {width}x{height})")
    
    print()
    print(f"Done! Generated {args.count} images in '{args.output}'")


if __name__ == '__main__':
    main()
