import os
from PIL import Image, ImageDraw

# Generar un icono profesional moderno para AutoClip Studio
icon_size = (256, 256)
img = Image.new("RGBA", icon_size, (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Fondo redondeado degradado oscuro
draw.rounded_rectangle([10, 10, 246, 246], radius=45, fill="#0f172a", outline="#00d2ff", width=6)

# Círculo central Neón Cyan
draw.ellipse([45, 45, 211, 211], outline="#00d2ff", width=8)

# Símbolo de mira / crosshair de sniper / play
draw.line([128, 25, 128, 70], fill="#00d2ff", width=8)
draw.line([128, 186, 128, 231], fill="#00d2ff", width=8)
draw.line([25, 128, 70, 128], fill="#00d2ff", width=8)
draw.line([186, 128, 231, 128], fill="#00d2ff", width=8)

# Triángulo Play central en Verde Esmeralda
draw.polygon([(110, 95), (110, 161), (165, 128)], fill="#10b981")

ico_path = r"E:\Videos OBS\AutoClip_AI\app_icon.ico"
img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print(f"Icono creado en: {ico_path}")
