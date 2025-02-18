import time

import gradio as gr
from fastapi import FastAPI
from gradio.routes import mount_gradio_app


def greet(name, intensity):
    time.sleep(5)  # Simulating processing time
    return "Hello, " + name + "!" * int(intensity)


demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
)
demo.queue(max_size=5)  # Enable queue for handling multiple requests

web_app = FastAPI()
app = mount_gradio_app(
    app=web_app,
    blocks=demo,
    path="/",
)

if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str)
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
