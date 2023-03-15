from algorithms import choi, heartrate, brueser, choe
import numpy
import utils
import tensorflow._api.v2.compat.v1 as tf
import warnings

sampling_frequency = 50.0

def simple_mean_choi(value_array):
    """ apply choi algorithm on the provided array assuming sampling
    frequency of 50Hz, then divides peaks number for observation time

    Returns:
        estimated heartrate in bpm
    """

    observation_time_seconds = float(len(value_array))/sampling_frequency
    indices = choi.choi(value_array, sampling_frequency)
    peak_peak = value_array[indices[0]:indices[-1]]
    observation_time_seconds = float(len(peak_peak))/sampling_frequency
    heartrate_s = float(len(indices))/observation_time_seconds
    heartrate_bpm = heartrate_s * 60.0
    return(heartrate_bpm)

def diff_mean_choi(value_array):
    """ apply choi algorithm on the provided array assuming sampling
    frequency of 50Hz, then uses a differential mean

    Returns:
        estimated heartrate in bpm
    """

    indices = choi.choi(value_array, sampling_frequency)
    return heartrate.heartrate_from_indices(indices, sampling_frequency)
    
def simple_brueser(value_array):
    """ apply brueser algorithm on the provided array assuming sampling
    frequency of 50Hz

    Returns:
        estimated heartrate in bpm
    """

    return brueser.brueser(value_array, sampling_frequency)[0]

def diff_mean_choe(value_array):
    """ apply cho algorithm on the provided array assuming sampling
    frequency of 50Hz, then uses a differential mean

    Returns:
        estimated heartrate in bpm
    """

    indices = choe.choe(value_array, sampling_frequency)
    return heartrate.heartrate_from_indices(indices, sampling_frequency)

def simple_mean_choe(value_array):
    """ apply choe algorithm on the provided array assuming sampling
    frequency of 50Hz, then divides peaks number for observation time

    Returns:
        estimated heartrate in bpm
    """

    observation_time_seconds = float(len(value_array))/sampling_frequency
    indices = choe.choe(value_array, sampling_frequency)
    peak_peak = value_array[indices[0]:indices[-1]]
    observation_time_seconds = float(len(peak_peak))/sampling_frequency
    heartrate_s = float(len(indices))/observation_time_seconds
    heartrate_bpm = heartrate_s * 60.0
    return(heartrate_bpm)

def deeper_fcn(value_array):
    if len(value_array) != 400:
        return None

    
    tf.logging.set_verbosity(tf.logging.ERROR)
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    tf.keras.backend.set_session(tf.Session(config=config))
    warnings.filterwarnings("ignore")

    model = utils.get_model_from_json("components/deeper_fcn9")
    model.load_weights("components/deeper_fcn9/weights")
    #modelpath = "output/models.deeper_fcn-x1"
    #model = utils.get_model_from_json(modelpath)
    #model.load_weights("output/models.deeper_fcn-x1/final/weights-00.h5")
    array = numpy.expand_dims(value_array, axis=0)
    array = numpy.expand_dims(array, axis=2)
    result = model.predict(array)
    return result[0,0]
