# from cryptosteganography import CryptoSteganography

# stego = CryptoSteganography('151556')
# secret = stego.retrieve('output_WhatsApp_Image_2021-09-07_at_9.07.52_AM_1.jpeg')
# print(secret)

from PIL import Image
from steganography import Steganography

merged_image = Steganography.merge(Image.open("register.png"), Image.open("home.png"))
merged_image.save("output.png")