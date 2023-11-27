import ljinference
import torch
from scipy.io.wavfile import write
def ljsynthesize(text):
    noise = torch.randn(1,1,256).to('cuda' if torch.cuda.is_available() else 'cpu')
    wav = ljinference.inference(text, noise, diffusion_steps=7, embedding_scale=1)
    write('test.wav', 24000, wav)
ljsynthesize('tɛstɪŋ ˈtɛstɪŋ wʌn tu θri')
