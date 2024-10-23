from transformers import pipeline
import torch
from datasets import load_dataset

import timeit
import soundfile as sf

pipe = torch.compile(pipeline("text-to-speech", model="facebook/mms-tts-eng", torch_dtype="auto", device="cuda:0"))

for i in range(10):
    start_time = timeit.default_timer()
    speech = pipe("Hello, my dog is cooler than you!")
    end_time = timeit.default_timer()
    print(f"Time taken for text-to-speech: {end_time - start_time} seconds")
print(speech)

sf.write("speech2.wav", speech["audio"][0], samplerate=speech["sampling_rate"])
