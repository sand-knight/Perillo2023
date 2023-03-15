from perillo_funcs import *
import numpy

the_file = numpy.genfromtxt("../sleeprawlive.csv")
#the_file = numpy.genfromtxt("../raw_2022-03-14_bcg.csv")

# sampling_frequency = 50
# observation_time_seconds = 10
# num_samples = observation_time_seconds * sampling_frequency
# results = []
# for i in range(0, sampling_frequency*5):
#     indices = choi.choi(the_file[100000+i*sampling_frequency:100000+i*sampling_frequency+num_samples], sampling_frequency)
#     heartrate_s = len(indices)/observation_time_seconds
#     heartrate_bpm = heartrate_s * 60
#     results.append(heartrate_bpm)

n_campioni = 50 * 8
starting = 20000
array = the_file[starting:starting+n_campioni]    
print(simple_brueser(array))
print(simple_mean_choi(array))
print(diff_mean_choi(array))
print(simple_mean_choe(array))
print(diff_mean_choe(array))
