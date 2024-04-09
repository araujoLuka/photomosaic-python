# Classify the dataset of images and generate a json with the summary

import argparse
import os
import json
from PIL import Image
from photomosaic import getAverageColor

def classifyDataset(datasetPath: str, datasetSummaryPath: str) -> dict:
    print("Classifying dataset...")
    print("Dataset path: {0}".format(datasetPath))

    numImages = 0
    colorRange = 32

    rgbClassification = {
        "colorRange": colorRange, # "16, 32, 64, 128, 256
        "r": {},
        "g": {},
        "b": {}
    }

    for i in range(0, 256, colorRange):
        rgbClassification["r"]["{0}-{1}".format(i, i+colorRange)] = []
        rgbClassification["g"]["{0}-{1}".format(i, i+colorRange)] = []
        rgbClassification["b"]["{0}-{1}".format(i, i+colorRange)] = []

    for i, filename in enumerate(os.listdir(datasetPath)):
        if not filename.endswith(".jpg") and not filename.endswith(".jpeg") and not filename.endswith(".png"):
            continue
        numImages += 1
        imagePath = os.path.join(datasetPath, filename)
        image = Image.open(imagePath)

        if image.mode != "RGB":
            image = image.convert("RGB")

        print("\rClassifying image {0}: {1} - Size: {2}".format(i, imagePath, image.size), end="")
        averageColor = getAverageColor(image)

        r = averageColor[0]
        g = averageColor[1]
        b = averageColor[2]

        imageData = {
            "path": imagePath,
            "averageColor": averageColor,
            "used": False
        }

        if r > g and r > b:
            rgbClassification["r"]["{0}-{1}".format(r-r%colorRange, r+colorRange-r%colorRange)].append(imageData)
        elif g > r and g > b:
            rgbClassification["g"]["{0}-{1}".format(g-g%colorRange, g+colorRange-g%colorRange)].append(imageData)
        else:
            rgbClassification["b"]["{0}-{1}".format(b-b%colorRange, b+colorRange-b%colorRange)].append(imageData)

    jsonData = {
        "description": "Dataset Summary",
        "datasetPath": datasetPath,
        "numImages": numImages,
        "rgbClassification":rgbClassification
    }

    f = open(datasetSummaryPath, "w")
    f.write(json.dumps(jsonData, indent=4))
    f.close()

    print("Dataset summary path: {0}".format(datasetSummaryPath))
    print("Done.")

    return jsonData

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Photomosaic")
    parser.add_argument("datasetPath", default="./data", action="store", nargs='?',  
                            type=str, help="Path to the dataset of images")
    parser.add_argument("datasetSummaryPath", default="./data_summary.json", action="store",  nargs='?',  
                            type=str, help="Path to the summary of the dataset of images")
    args = parser.parse_args()
    datasetPath = args.datasetPath
    datasetSummaryPath = args.datasetSummaryPath

    if not os.path.exists(datasetPath):
        print("Error: Dataset path does not exist.")
        exit(1)

    if datasetSummaryPath == "" or datasetSummaryPath == None:
        print("Error: Dataset summary path is empty.")
        exit(1)

    if not datasetSummaryPath.endswith(".json"):
        print("Error: Dataset summary path must be a json file.")
        exit(1)

    print("Classifying dataset...")
    jsonData = classifyDataset(datasetPath, datasetSummaryPath)

    print("Done.")
    print("Total of {0} images classified.".format(jsonData["numImages"]))
