# get all config files
import glob
import os

def main():
    for file in glob.glob("../config/*.ini"):
        print("working on: ", file)
        os.system("python3 run-experiment.py "+file)
        print("-----------------------")
if __name__ == "__main__":
    main()
