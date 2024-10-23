# Gradio demo of StyleTTS 2 by @fakerybakery
import gradio as gr
import msinference
import ljinference
import torch
import os
from tortoise.utils.text import split_and_recombine_text
import numpy as np
import pickle
import timeit

theme = gr.themes.Base(
    font=[
        gr.themes.GoogleFont("Libre Franklin"),
        gr.themes.GoogleFont("Public Sans"),
        "system-ui",
        "sans-serif",
    ],
)
voicelist = [
    "kyubey",
    "f-us-1",
    "f-us-2",
    "f-us-3",
    "f-us-4",
    "m-us-1",
    "m-us-2",
    "m-us-3",
    "m-us-4",
]
voices = {}
import phonemizer

global_phonemizer = phonemizer.backend.EspeakBackend(
    language="en-us", preserve_punctuation=True, with_stress=True
)
# todo: cache computed style, load using pickle
# if os.path.exists('voices.pkl'):
# with open('voices.pkl', 'rb') as f:
# voices = pickle.load(f)
# else:
for v in voicelist:
    voices[v] = msinference.compute_style(f"voices/{v}.wav")


def synthesize(text, voice, lngsteps, password, progress=gr.Progress()):
    if text.strip() == "":
        raise gr.Error("You must enter some text")
    if lngsteps > 25:
        raise gr.Error("Max 25 steps")
    if lngsteps < 5:
        raise gr.Error("Min 5 steps")
    texts = split_and_recombine_text(text)
    v = voice.lower()
    audios = []
    for t in progress.tqdm(texts):
        audios.append(
            msinference.inference(
                t,
                voices[v],
                alpha=0.3,
                beta=0.7,
                diffusion_steps=lngsteps,
                embedding_scale=1,
            )
        )
    return (24000, np.concatenate(audios))


def clsynthesize(text, voice, vcsteps):
    if text.strip() == "":
        raise gr.Error("You must enter some text")
    # if global_phonemizer.phonemize([text]) > 300:
    if len(text) > 400:
        raise gr.Error("Text must be under 400 characters")
    style = msinference.compute_style(voice)
    start = timeit.default_timer()
    out = (
        24000,
        msinference.inference(
            text, style, alpha=0.3, beta=0.7, diffusion_steps=vcsteps, embedding_scale=1
        ),
    )
    duration = timeit.default_timer() - start
    print(f"Time taken for text-to-speech: {duration} seconds")
    return out


def ljsynthesize(text):
    if text.strip() == "":
        raise gr.Error("You must enter some text")
    # if global_phonemizer.phonemize([text]) > 300:
    if len(text) > 400:
        raise gr.Error("Text must be under 400 characters")
    noise = torch.randn(1, 1, 256).to("cuda" if torch.cuda.is_available() else "cpu")
    return (
        24000,
        ljinference.inference(text, noise, diffusion_steps=7, embedding_scale=1),
    )


with gr.Blocks() as vctk:  # just realized it isn't vctk but libritts but i'm too lazy to change it rn
    with gr.Row():
        with gr.Column(scale=1):
            inp = gr.Textbox(
                label="Text",
                info="What would you like StyleTTS 2 to read? It works better on full sentences.",
                interactive=True,
            )
            voice = gr.Dropdown(
                voicelist,
                label="Voice",
                info="Select a default voice.",
                value="kyubey",
                interactive=True,
            )
            multispeakersteps = gr.Slider(
                minimum=5,
                maximum=15,
                value=7,
                step=1,
                label="Diffusion Steps",
                info="Higher = better quality, but slower",
                interactive=True,
            )
            # use_gruut = gr.Checkbox(label="Use alternate phonemizer (Gruut) - Experimental")
        with gr.Column(scale=1):
            btn = gr.Button("Synthesize", variant="primary")
            audio = gr.Audio(interactive=False, label="Synthesized Audio")
            btn.click(
                synthesize,
                inputs=[inp, voice, multispeakersteps],
                outputs=[audio],
                concurrency_limit=4,
            )
with gr.Blocks() as clone:
    with gr.Row():
        with gr.Column(scale=1):
            clinp = gr.Textbox(
                label="Text",
                info="What would you like StyleTTS 2 to read? It works better on full sentences.",
                interactive=True,
            )
            clvoice = gr.Audio(
                label="Voice", interactive=True, type="filepath", max_length=300
            )
            vcsteps = gr.Slider(
                minimum=5,
                maximum=20,
                value=20,
                step=1,
                label="Diffusion Steps",
                info="Higher = better quality, but slower",
                interactive=True,
            )
        with gr.Column(scale=1):
            clbtn = gr.Button("Synthesize", variant="primary")
            claudio = gr.Audio(interactive=False, label="Synthesized Audio")
            clbtn.click(
                clsynthesize,
                inputs=[clinp, clvoice, vcsteps],
                outputs=[claudio],
                concurrency_limit=4,
            )
with gr.Blocks() as lj:
    with gr.Row():
        with gr.Column(scale=1):
            ljinp = gr.Textbox(
                label="Text",
                info="What would you like StyleTTS 2 to read? It works better on full sentences.",
                interactive=True,
            )
        with gr.Column(scale=1):
            ljbtn = gr.Button("Synthesize", variant="primary")
            ljaudio = gr.Audio(interactive=False, label="Synthesized Audio")
            ljbtn.click(
                ljsynthesize, inputs=[ljinp], outputs=[ljaudio], concurrency_limit=4
            )
with gr.Blocks(title="StyleTTS 2", theme=theme) as demo:
    gr.TabbedInterface([vctk, clone, lj], ["Multi-Voice", "Voice Cloning", "LJSpeech"])


API = True
if __name__ == "__main__":
    demo.queue(api_open=API, max_size=15).launch(show_api=API)
