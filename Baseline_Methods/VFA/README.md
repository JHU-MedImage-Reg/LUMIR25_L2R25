## Image synthesis using SynthSR + Vector Field Attention

Please refer to [MIR package](https://github.com/junyuchen245/MIR) for the model implementation scripts.

The pipeline first applies SynthSR to images of various modalities, followed by applying the pretrained VFA model on the synthesized outputs.

1. First step:
`bash infer_SynthSR.sh`
2. Then:
`python -u infer_VFA_w_SynthSR.py`
