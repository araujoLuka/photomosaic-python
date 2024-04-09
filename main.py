# Photomosaic

from PIL import Image

def openImage(path) -> Image.Image:
    return Image.open(path)

def saveImage(image: Image.Image, path: str) -> None:
    image.save(path)

def main(originalImagePath: str = "image.jpg", datasetPath: str = "./data") -> int:
    print("Hello, World!")
    print("Photomosaic")

    originalImage: Image.Image = openImage(originalImagePath)

    imageWidth, imageHeight = originalImage.size
    print(f"Image size: {imageWidth}x{imageHeight}")

    print("Original Image Info:")
    print(" - Format: {0}".format(originalImage.format))
    print(" - Mode: {0}".format(originalImage.mode))
    print(" - Size: {0}".format(originalImage.size))
    print(" - Path: {0}".format(originalImagePath))
    originalImage.show()

    print("Creating new image...")
    newImage = Image.new("RGB", (imageWidth, imageHeight))
    saveImage(newImage, "output.jpg")

    print("New Image Info:")
    print(" - Format: {0}".format(newImage.format))
    print(" - Mode: {0}".format(newImage.mode))
    print(" - Size: {0}".format(newImage.size))
    print(" - Path: {0}".format("output.jpg"))
    print(" - Total images used: {0}".format(0))
    newImage.show()

    return 0

if __name__ == "__main__":
    ret: int = main()
    exit(ret)
