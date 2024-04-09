# Photomosaic

import argparse
from PIL import Image

verbose: bool = False
showImages: bool = True
diffThreshold: int = 50

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

def getColorRange(color: tuple, colorRange) -> tuple[int, int, int]:
    r, g, b = 0, 0, 0
    for i in range(0, 256, colorRange):
        if color[0] >= i and color[0] < i+colorRange:
            r = i
        if color[1] >= i and color[1] < i+colorRange:
            g = i
        if color[2] >= i and color[2] < i+colorRange:
            b = i
    return (r, g, b)

def getDatasetImage(cropAvgColor: tuple, 
                    cropColorRange: tuple[int, int, int], 
                    cropSize: tuple, datasetSummary: dict, 
                    canRepeat: bool, 
                    usedImages: list) -> Image.Image:
    if canRepeat:
        return getDatasetRandomImage(cropAvgColor, cropColorRange, cropSize, datasetSummary)
    return getDatasetUniqueImage(cropAvgColor, cropColorRange, cropSize, datasetSummary)

def getDatasetRandomImage(cropAvgColor: tuple, cropColorRange: tuple[int, int, int], cropSize: tuple, datasetSummary: dict) -> Image.Image:
    closestImageData: dict = {} 
    closestDiffs = [999999, 999999, 999999]
    for i, x in enumerate(['r', 'g', 'b']):
        rangeIndex = "{0}-{1}".format(cropColorRange[i], cropColorRange[i] + datasetSummary["rgbClassification"]["colorRange"])
        rgbSummary = datasetSummary["rgbClassification"][x][rangeIndex]
        for imageData in rgbSummary:
            rDiff = abs(cropAvgColor[0] - imageData["averageColor"][0])
            gDiff = abs(cropAvgColor[1] - imageData["averageColor"][1])
            bDiff = abs(cropAvgColor[2] - imageData["averageColor"][2])
            if rDiff < closestDiffs[0] and gDiff < closestDiffs[1] and bDiff < closestDiffs[2]:
                closestDiffs = [rDiff, gDiff, bDiff]
                closestImageData = imageData

    image: Image.Image = Image.open(closestImageData["path"])

    # cut image to adjust to crop ratio
    cropRatio = cropSize[0] / cropSize[1]
    imageRatio = image.size[0] / image.size[1]
    if cropRatio > imageRatio:
        newWidth = image.size[0]
        newHeight = int(newWidth / cropRatio)
    else:
        newHeight = image.size[1]
        newWidth = int(newHeight * cropRatio)
    image = image.resize((newWidth, newHeight))
    
    # create thumbnail with crop size
    image.thumbnail(cropSize, Image.ANTIALIAS)

    print("\rImage found:", closestImageData, end="             ")

    return image

def getDatasetUniqueImage(cropAvgColor: tuple, cropColorRange: tuple[int, int, int], cropSize: tuple, datasetSummary: dict) -> Image.Image:
    closestImageData: dict = {} 
    closestDiffs = [999999, 999999, 999999]
    closestIdxs = []
    for i, x in enumerate(['r', 'g', 'b']):
        rangeIndex = "{0}-{1}".format(cropColorRange[i], cropColorRange[i] + datasetSummary["rgbClassification"]["colorRange"])
        rgbSummary = datasetSummary["rgbClassification"][x][rangeIndex]
        for j, imageData in enumerate(rgbSummary):
            if imageData["used"]:
                continue
            rDiff = abs(cropAvgColor[0] - imageData["averageColor"][0])
            gDiff = abs(cropAvgColor[1] - imageData["averageColor"][1])
            bDiff = abs(cropAvgColor[2] - imageData["averageColor"][2])
            if rDiff < closestDiffs[0] and gDiff < closestDiffs[1] and bDiff < closestDiffs[2]:
                closestDiffs = [rDiff, gDiff, bDiff]
                closestImageData = imageData
                closestIdxs = [x, rangeIndex, j]

    if closestImageData == {} or closestDiffs[0] > diffThreshold or closestDiffs[1] > diffThreshold or closestDiffs[2] > diffThreshold:
        return getUnusedDatasetImage(cropAvgColor, cropColorRange, cropSize, datasetSummary)

    image: Image.Image = Image.open(closestImageData["path"])

    # cut image to adjust to crop ratio
    cropRatio = cropSize[0] / cropSize[1]
    imageRatio = image.size[0] / image.size[1]
    if cropRatio > imageRatio:
        newWidth = image.size[0]
        newHeight = int(newWidth / cropRatio)
    else:
        newHeight = image.size[1]
        newWidth = int(newHeight * cropRatio)
    image = image.resize((newWidth, newHeight))
    
    # create thumbnail with crop size
    image.thumbnail(cropSize, Image.ANTIALIAS)

    # mark image as used, by adding a flag in the dataset summary
    datasetSummary["rgbClassification"][closestIdxs[0]][closestIdxs[1]][closestIdxs[2]]["used"] = True

    print("\rImage found:", closestImageData, end="             ")

    return image

# Search an image with rgb diff <= diffThreshold and that has not been used
def getUnusedDatasetImage(cropAvgColor: tuple, cropColorRange: tuple[int, int, int], cropSize: tuple, datasetSummary: dict, extraRange: int = 2, ignoreRanges: list = [[], [], []]) -> Image.Image:
    closestImageData: dict = {} 
    closestIdxs = []
    closestDiff = 999999
    rangeIndexes = []
    colorRange = datasetSummary["rgbClassification"]["colorRange"]
    for g, cr in enumerate(cropColorRange):
        # create two range before and two after cropColorRange
        rangesList = []
        for i in range(cr - extraRange*colorRange, cr + extraRange*colorRange, colorRange):
            if i < 0 or i >= 255:
                continue
            if i == cr:
                continue
            rIndex = "{0}-{1}".format(i, i + colorRange)
            if rIndex not in ignoreRanges[g]: 
                rangesList.append(rIndex)
        rangeIndexes.append(rangesList)

    for i, x in enumerate(['r', 'g', 'b']):
        for rangeIndex in rangeIndexes[i]:
            if rangeIndex not in datasetSummary["rgbClassification"][x]:
                continue

            rgbSummary = datasetSummary["rgbClassification"][x][rangeIndex]
            for j, imageData in enumerate(rgbSummary):
                if imageData["used"]:
                    continue
                rDiff = abs(cropAvgColor[0] - imageData["averageColor"][0])
                gDiff = abs(cropAvgColor[1] - imageData["averageColor"][1])
                bDiff = abs(cropAvgColor[2] - imageData["averageColor"][2])
                if (rDiff < diffThreshold and gDiff < diffThreshold and bDiff < diffThreshold) or (extraRange >= 6 and rDiff + gDiff + bDiff < closestDiff):
                    closestImageData = imageData
                    closestIdxs = [x, rangeIndex, j]
                    closestDiff = rDiff + gDiff + bDiff

    if closestImageData == {}:
        if extraRange >= 7:
            print("No image found with range {}. Returning random image.".format(extraRange))
            print("Warning: Not enough images in the dataset to create the photomosaic.")
            return getDatasetRandomImage(cropAvgColor, cropColorRange, cropSize, datasetSummary)
        print("No image found (range {}). Trying with higher color range...".format(extraRange))
        return getUnusedDatasetImage(cropAvgColor, cropColorRange, cropSize, datasetSummary, extraRange+2, ignoreRanges)

    image: Image.Image = Image.open(closestImageData["path"])

    # cut image to adjust to crop ratio
    cropRatio = cropSize[0] / cropSize[1]
    imageRatio = image.size[0] / image.size[1]
    if cropRatio > imageRatio:
        newWidth = image.size[0]
        newHeight = int(newWidth / cropRatio)
    else:
        newHeight = image.size[1]
        newWidth = int(newHeight * cropRatio)
    image = image.resize((newWidth, newHeight))
    
    # create thumbnail with crop size
    image.thumbnail(cropSize, Image.ANTIALIAS)

    # mark image as used, by adding a flag in the dataset summary
    datasetSummary["rgbClassification"][closestIdxs[0]][closestIdxs[1]][closestIdxs[2]]["used"] = True

    print("\rImage found:", closestImageData, end="             ")

    return image

def createMosaic(originalImage: Image.Image, 
                 datasetPath: str, 
                 datasetSummaryPath: str,
                 canRepeat: bool,
                 crops: list,
                 cropSize: tuple,
                 orgAvgColor: tuple = (80, 80, 80)) -> Image.Image:

    mosaicCrops: list = []
    import json
    with open(datasetSummaryPath, "r") as f:
        datasetSummary = json.load(f)
        colorRange = datasetSummary["rgbClassification"]["colorRange"]
        numImages = datasetSummary["numImages"]

    if numImages < len(crops):
        print("Warning: Not enough images in the dataset to create the photomosaic.")
        print("Some images will be repeated.")

    usedImages = []

    for crop in crops:
        cropAvgColor = getAverageColor(crop)
        cropColorRange: tuple[int, int, int] = getColorRange(cropAvgColor, colorRange)
        cropImage = getDatasetImage(cropAvgColor, cropColorRange, cropSize, datasetSummary, canRepeat, usedImages)
        mosaicCrops.append(cropImage)

    print()

    finalImage = Image.new("RGB", originalImage.size, color=orgAvgColor)

    x, y = 0, 0
    for _, crop in enumerate(mosaicCrops):
        finalImage.paste(crop, (x, y))
        x += cropSize[0]
        if x >= originalImage.size[0]:
            x = 0
            y += cropSize[1]

    return finalImage

def main(originalImagePath: str,
         datasetPath: str,
         datasetSummaryPath: str,
         canRepeat: bool,
         numDivisions: int ) -> int:

    print("Hello, World!")
    print("Photomosaic")

    print(f"Number of divisions: {numDivisions}")

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
    if showImages: originalImage.show()

    print("Creating new image...")
    mosaicImage: Image.Image = createMosaic(originalImage, datasetPath, datasetSummaryPath, canRepeat, crop, cropSize, getAverageColor(originalImage))
    saveImage(mosaicImage, "output.jpg")

    imageInfo(mosaicImage, id="Mosaic Image", imagePath="output.jpg", dataUsed=len(crop))
    if showImages: mosaicImage.show()

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
    parser.add_argument("canRepeat", default=True, action="store", nargs='?',  
                            type=bool, help="Whether or not images can be repeated in the photomosaic (default: True)")
    parser.add_argument("numDivisions", default=50, action="store", nargs='?',
                            type=int, help="Number of divisions to split the image into (default: 50)")

    # options
    parser.add_argument("-v",  "--verbose", dest="verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("--noRepeat", dest="canRepeatOpt", action="store_false", help="Disables images to be repeated in the photomosaic")
    parser.add_argument("--numDiv", dest="numDivisionsOpt", action="store", type=int, help="Number of divisions to split the image into (default: 50)")
    parser.add_argument("--noImageShow", dest="showImages", action="store_false", default=True, help="Disables image display (default: True)")

    args = parser.parse_args()

    verbose = args.verbose
    showImages = args.showImages

    if not args.datasetSummaryPath.endswith(".json"):
        print("Error: Dataset summary path must be a json file.")
        exit(1)

    if args.numDivisionsOpt:
        args.numDivisions = args.numDivisionsOpt

    if not args.canRepeatOpt:
        args.canRepeat = False

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
