import subprocess


def read_from_antennas(name):
    '''
    Runs read_data.py and waits 20 seconds before closing.
    This is done like this because the computer where we are using only
    has GNURadio installed in the python3.6.
    '''
    subprocess.run(["timeout", "20", "python3.6",
                    "gnuradio/read_data.py", name])
    return name
