from FRCNN_predict.predict import run_prediction
from gnuradio.main import read_from_antennas
from processing.main import run_processing
from visualization.main import visualize
import boto3
import requests
import datetime
import sys
import time

SECRET = 'SECRET-HERE'


def main():
    # If no extra parameters provided, enter in infinite loop to process
    if len(sys.argv) < 2:
        print('Processing in infinite loop. Press Ctrl + C to stop')
        while(True):
            timestamp = str(int(time.time() * 1000))
            print('Starting to process filename=' + timestamp)
            update_status('READING')
            read_from_antennas(timestamp)
            update_status('TRACKING')
            run_processing(timestamp)
            update_status('IDENTIFYING')
            coordinates = run_prediction(timestamp)
            visualize(coordinates, timestamp)
            upload_entry(timestamp)
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


def update_status(status):
    data = {
        "status": status,
        "secret": SECRET
    }
    url = "http://aviguardx.vercel.app/api/status"
    response = requests.patch(url, data)
    return


def upload_file(file_name, bucket):
    bucket = 'aviguardx'
    file_path = os.path.join(os.getcwd(), "results", file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(
            file_path,
            bucket,
            file_name,
            ExtraArgs={'ACL': 'public-read'})
        print('Response upload file', response)
        return "https://aviguardx.s3.eu-north-1.amazonaws.com/{0}".format(file_name)
    except e:
        print('Error to upload file', e)
        return ""


def upload_entry(name):
    simple_tracked_url = upload_file(name + '.jpeg')
    tracked_url = upload_file(name + '_labeled.jpeg')
    predicted_url = upload_file(name + '_predicted.jpeg')
    map_url = upload_file(name + '_map.jpeg')
    data = {
        "map_url": map_url,
        "tracked_url": tracked_url,
        "predicted_url": predicted_url,
        "simple_tracked_url": simple_tracked_url,
        "name": name,
        "recorded_at": datetime.datetime.now().isoformat(),
        "jsonData": "{}",
        "secret": SECRET
    }
    url = "http://aviguardx.vercel.app/api/entries"
    response = requests.post(url, data)
    return


if __name__ == '__main__':
    main()
