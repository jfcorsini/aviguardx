from FRCNN_predict.predict import run_prediction
from gnuradio.main import read_from_antennas
from processing.main import run_processing
from visualization.main import visualize
import sys
import time


def main():
    # If no extra parameters provided, enter in infinite loop to process
    if len(sys.argv) < 2:
        print('Processing in infinite loop. Press Ctrl + C to stop')
        while(True):
            timestamp = str(int(time.time() * 1000))
            print('Starting to process filename=' + timestamp)
            read_from_antennas(timestamp)
            run_processing(timestamp)
            coordinates = run_prediction(timestamp)
            visualize(coordinates, timestamp)
        return

    output_name = str(int(time.time() * 1000))
    if len(sys.argv) > 2:
        output_name = sys.argv[2]

    param = sys.argv[1]
    if param == 'ML':
        return run_prediction(output_name)
    elif param == 'gnuradio':
        return read_from_antennas(output_name)
    elif param == 'process':
        return run_processing(output_name)
    elif param == 'ui':
        return visualize([], output_name)
    else:
        output_name = param
        print('Starting to process filename=' + output_name)
        read_from_antennas(output_name)
        run_processing(output_name)
        coordinates = run_prediction(output_name)
        visualize(coordinates, output_name)


if __name__ == '__main__':
    main()
