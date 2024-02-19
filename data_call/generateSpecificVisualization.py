import sys
import data as dc

def generateVisualization(serialNumber):
    # do your generation here @Chloe and @Alex TODO
    dc.dataAnalysis()


if len(sys.argv <= 1):
    print("need a serial number")

serialNumber = sys.argv[1]
generateVisualization(serialNumber)
