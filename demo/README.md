# rrdoctor Streamlit demo

This tiny web demo lets a user paste a public GitHub repository URL, shallow-clones it into a temporary directory, runs the static `rrdoctor scan` command, and displays the reproducibility score plus the top findings. It is designed for Streamlit Community Cloud or Hugging Face Spaces; install `demo/requirements.txt`, run `streamlit run demo/app.py`, and make sure the runtime has `git` available. On Streamlit Community Cloud, the public app may show a wake-up screen after inactivity before the rrdoctor input box appears.
