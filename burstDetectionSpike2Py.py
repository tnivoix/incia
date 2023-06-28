import spike2py as s2p
from spike2py.trial import TrialInfo, Trial

channels = ["Ev-GVS"]
trial_info = TrialInfo(file="tmp/230407-galv-s54_000.mat")
sample = Trial(trial_info)
print(sample.channels)