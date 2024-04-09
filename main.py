# Photomosaic

from PIL import Image

def openImage(path) -> Image.Image:
    return Image.open(path)

def saveImage(image: Image.Image, path: str) -> None:
    image.save(path)

def createMosaic(originalImage: Image.Image, datasetPath: str) -> Image.Image:
    return Image.new("RGB", originalImage.size)

def getAverageColor(image: Image.Image) -> tuple:
    histogram = image.histogram()
    r = histogram[0:256]
    g = histogram[256:512]
    b = histogram[512:768]
    pixels = image.size[0] * image.size[1]
    avgR = sum(i * r[i] for i in range(256)) // pixels
    avgG = sum(i * g[i] for i in range(256)) // pixels
    avgB = sum(i * b[i] for i in range(256)) // pixels
    return (avgR, avgG, avgB)

def main(originalImagePath: str = "image.jpg", datasetPath: str = "./data") -> int:
    print("Hello, World!")
    print("Photomosaic")

    originalImage: Image.Image = openImage(originalImagePath)

    imageWidth, imageHeight = originalImage.size
    print(f"Image size: {imageWidth}x{imageHeight}")

    orgAvgColor = getAverageColor(originalImage)

    print("Original Image Info:")
    print(" - Format: {0}".format(originalImage.format))
    print(" - Mode: {0}".format(originalImage.mode))
    print(" - Size: {0}".format(originalImage.size))
    print(" - Path: {0}".format(originalImagePath))
    print(" - Average Color: {0}".format(orgAvgColor))
    originalImage.show()

    print("Creating new image...")
    newImage = Image.new("RGB", (imageWidth, imageHeight), color = orgAvgColor)
    saveImage(newImage, "output.jpg")

    print("New Image Info:")
    print(" - Format: {0}".format(newImage.format))
    print(" - Mode: {0}".format(newImage.mode))
    print(" - Size: {0}".format(newImage.size))
    print(" - Path: {0}".format("output.jpg"))
    print(" - Average Color: {0}".format(getAverageColor(newImage)))
    print(" - Total images used: {0}".format(0))
    newImage.show()

    print("Done.")
    input("Press Enter to end...")

    return 0

if __name__ == "__main__":
    ret: int = main()
    exit(ret)
