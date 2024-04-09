# Photomosaic

import argparse
from PIL import Image

def openImage(path) -> Image.Image:
    return Image.open(path)

def saveImage(image: Image.Image, path: str) -> None:
    image.save(path)

def createMosaic(originalImage: Image.Image, datasetPath: str, crops: list) -> Image.Image:
    return Image.new("RGB", originalImage.size, color="white")

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

def cropImage(image: Image.Image, cropSize: tuple) -> list:
    crops: list = []
    imageWidth, imageHeight = image.size
    cropWidth, cropHeight = cropSize
    for y in range(0, imageHeight, cropHeight):
        for x in range(0, imageWidth, cropWidth):
            box = (x, y, x + cropWidth, y + cropHeight)
            crops.append(image.crop(box))
    return crops

def main(originalImagePath: str,
         datasetPath: str,
         datasetSummaryPath: str,
         canRepeat: bool,
         numDivisions: int ) -> int:

    print("Hello, World!")
    print("Photomosaic")

    originalImage: Image.Image = openImage(originalImagePath)

    imageWidth, imageHeight = originalImage.size
    print(f"Image size: {imageWidth}x{imageHeight}")

    cropSize: tuple = (imageWidth // numDivisions, imageHeight // numDivisions)
    print(f"Crop size: {cropSize}")
    crop: list = cropImage(originalImage, cropSize)

    print("First 5 crops:")
    for i in range(5):
        print("Crop {0}:".format(i))
        print(" - Size: {0}".format(crop[i].size))
        print(" - Mode: {0}".format(crop[i].mode))
        print(" - Format: {0}".format(crop[i].format))
        print(" - Average Color: {0}".format(getAverageColor(crop[i])))
        crop[i].show()
        input("Press Enter to continue...")

    orgAvgColor = getAverageColor(originalImage)

    print("Original Image Info:")
    print(" - Format: {0}".format(originalImage.format))
    print(" - Mode: {0}".format(originalImage.mode))
    print(" - Size: {0}".format(originalImage.size))
    print(" - Path: {0}".format(originalImagePath))
    print(" - Average Color: {0}".format(orgAvgColor))
    originalImage.show()

    print("Creating new image...")
    mosaicImage: Image.Image = createMosaic(originalImage, datasetPath, crop)
    saveImage(mosaicImage, "output.jpg")

    print("New Image Info:")
    print(" - Format: {0}".format(mosaicImage.format))
    print(" - Mode: {0}".format(mosaicImage.mode))
    print(" - Size: {0}".format(mosaicImage.size))
    print(" - Path: {0}".format("output.jpg"))
    print(" - Average Color: {0}".format(getAverageColor(mosaicImage)))
    print(" - Total images used: {0}".format(0))
    mosaicImage.show()

    print("Done.")
    input("Press Enter to end...")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Photomosaic")
    parser.add_argument("photoPath", default="image.jpg", action="store", nargs='?',  
                            type=str, help="Path to the photo to be converted to a photomosaic")
    parser.add_argument("datasetPath", default="./data", action="store", nargs='?',  
                            type=str, help="Path to the dataset of images")
    parser.add_argument("datasetSummaryPath", default="./data_summary.txt", action="store",  nargs='?',  
                            type=str, help="Path to the dataset summary file")
    parser.add_argument("canRepeat", default=False, action="store", nargs='?',  
                            type=bool, help="Whether or not images can be repeated in the photomosaic (default: False)")
    parser.add_argument("numDivisions", default=10, action="store", nargs='?',  
                            type=int, help="Number of divisions to split the image into (default: 10)")

    # options
    parser.add_argument("-v",  "--verbose", dest="verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("-r", "--canRepeat", dest="repeat", action="store_true", help="Allow images to be repeated in the photomosaic")

    args = parser.parse_args()

    if args.repeat:
        print("Images can be repeated in the photomosaic")
        args.canRepeat = True

    if args.verbose:
        print("Verbose mode activated")

    # DEBUG ARGS
    print(args)

    ret: int = main(
        originalImagePath=args.photoPath,
        datasetPath=args.datasetPath,
        datasetSummaryPath=args.datasetSummaryPath,
        canRepeat=args.canRepeat,
        numDivisions=args.numDivisions,
    )

    exit(ret)
