# Photomosaic

import argparse
from PIL import Image

verbose: bool = False

def openImage(path) -> Image.Image:
    return Image.open(path)

def saveImage(image: Image.Image, path: str) -> None:
    image.save(path)

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

def imageInfo(image: Image.Image, id: str = "", imagePath: str = "", dataUsed: int = 0) -> None:
    print("Image Info:")
    if id != "":
        print(" - ID: {0}".format(id))
    print(" - Format: {0}".format(image.format))
    print(" - Mode: {0}".format(image.mode))
    print(" - Size: {0}".format(image.size))
    print(" - Average Color: {0}".format(getAverageColor(image)))
    if imagePath != "":
        print(" - Path: {0}".format(imagePath))
    if dataUsed != 0:
        print(" - Total images used: {0}".format(dataUsed))

def createMosaic(originalImage: Image.Image, 
                 datasetPath: str, 
                 datasetSummaryPath: str,
                 canRepeat: bool,
                 crops: list,
                 orgAvgColor: tuple = (80, 80, 80)) -> Image.Image:

    return Image.new("RGB", originalImage.size, color=orgAvgColor)

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

    # DEBUG
    # print("First 5 crops:")
    # for i in range(5):
    #     imageInfo(crop[i], id="Crop {0}".format(i))
    #     crop[i].show()
    #     input("Press Enter to continue...")

    imageInfo(originalImage, id="Original Image", imagePath=originalImagePath)
    originalImage.show()

    print("Creating new image...")
    mosaicImage: Image.Image = createMosaic(originalImage, datasetPath, datasetSummaryPath, canRepeat, crop, getAverageColor(originalImage))
    saveImage(mosaicImage, "output.jpg")

    imageInfo(mosaicImage, id="Mosaic Image", imagePath="output.jpg", dataUsed=len(crop))
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
    parser.add_argument("datasetSummaryPath", default="./data_summary.json", action="store",  nargs='?',  
                            type=str, help="Path to the dataset summary file")
    parser.add_argument("canRepeat", default=False, action="store", nargs='?',  
                            type=bool, help="Whether or not images can be repeated in the photomosaic (default: False)")
    parser.add_argument("numDivisions", default=10, action="store", nargs='?',  
                            type=int, help="Number of divisions to split the image into (default: 10)")

    # options
    parser.add_argument("-v",  "--verbose", dest="verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("-r", "--canRepeat", dest="canRepeat", action="store_true", help="Allow images to be repeated in the photomosaic")

    args = parser.parse_args()

    verbose = args.verbose

    if not args.datasetSummaryPath.endswith(".json"):
        print("Error: Dataset summary path must be a json file.")
        exit(1)

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
