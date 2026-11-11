---
id: m9-vla-foundation-models
lang: en
title: "Robot foundation models and VLAs (RT-2, OpenVLA, π0, SmolVLA)"
summary: Understand the structure of VLA (Vision-Language-Action) models, which attach action output to a pretrained vision-language model, split into action tokenization and continuous action heads (flow matching), and sort out the openness and compute requirements of RT-2, OpenVLA, the π0 family, SmolVLA, and GR00T. A numpy example shows the quantization error and the token count problem of action tokenization.
objectives:
  - Explain a VLA's inputs (images, language, proprioceptive state) and outputs (an action or an action chunk), and why the VLM backbone is reused.
  - Compare the advantages and disadvantages of discrete action tokenization (RT-2, OpenVLA) and a continuous action head (π0's flow matching) in terms of quantization error and inference speed.
  - Choose a model to run inference on or fine-tune in a given GPU environment, based on open weights, licenses, and VRAM requirements.
tags: [vla, foundation-models, rt-2, openvla, pi0, smolvla, action-tokenization]
---

# Robot foundation models and VLAs (RT-2, OpenVLA, π0, SmolVLA)

The ACT of the previous lesson collects demonstrations from scratch whenever the task changes.
Just as a language model is pretrained and then adapts from little data, robot foundation models
propose fine-tuning **a policy pretrained on large-scale data from many robots and tasks**. The
mainstream form of that is the VLA (Vision-Language-Action) model.

## Concepts

### The structure of a VLA

A VLA takes camera images, a language instruction ("put the cup on the plate"), and the robot's
joint state, and produces an action. Its body is a pretrained **vision-language model (VLM)**. By
reusing what the VLM already knows about objects, spatial relations, and language, it gains the
generalization to "objects never seen before" that robot data alone cannot teach. The difference
lies in how the action is output.

- **Action tokenization (RT-2, OpenVLA):** divide each dimension of the continuous action into
  256 bins to make integer tokens, and have the VLM generate action tokens the way it generates
  text. Almost no structural change is needed, but there is quantization error, and generating
  tokens one at a time is slow. RT-2's weights were not released; OpenVLA (about 7B, MIT) is an
  open model.
- **Continuous action heads (π0, π0.5, SmolVLA, GR00T):** put a separate "action expert" network
  on top of the VLM and generate an **action chunk** of continuous values in one shot with flow
  matching (a diffusion-family method). It amounts to moving ACT's chunks and Diffusion Policy's
  distributional representation on top of a VLM. π0-FAST went the other way, keeping the
  autoregressive approach by reducing the token count with a compressing tokenizer (FAST).

### What you can actually run (as surveyed, November 2026)

| Model | Openness | Rough requirement |
|---|---|---|
| SmolVLA | 450M, Apache-2.0 | fine-tuning 10-16 GB |
| π0 / π0.5 (openpi, LeRobot) | code Apache-2.0 | inference >8 GB, LoRA >22.5 GB, full >70 GB |
| GR00T N1.7 | code Apache-2.0, weights under the NVIDIA license | inference 16 GB+, fine-tuning 40 GB+ |
| OpenVLA / OpenVLA-OFT | MIT | 7B class |
| RT-2 | weights not released | — |

With a single 24 GB consumer GPU, SmolVLA fine-tuning and π0.5 and GR00T inference are realistic.
Full fine-tuning means renting a 40-80 GB GPU.

### Fine-tuning is the normal way to use them

Even a pretrained VLA is usually fine-tuned on dozens to hundreds of demonstrations for your own
robot and camera placement. The data collection tips of the previous lesson matter just as much
here. Matching the action space (joint versus end-effector, absolute versus relative) and the
normalization to the pretraining data is a common failure point.

## Key formulas

Action tokenization ($[\ell_j, h_j]$ is the range of the $j$-th dimension, $B$ the number of
bins) and the maximum quantization error:

$$k_j = \Big\lfloor B \cdot \frac{a_j - \ell_j}{h_j - \ell_j} \Big\rfloor,\qquad |a_j - \hat a_j| \le \frac{h_j - \ell_j}{2B}$$

The flow matching action head: learn a velocity field $v_\theta$ connecting noise $\epsilon$ to
the ground-truth chunk $A$, and integrate it at inference.

$$A^\tau = \tau A + (1 - \tau)\epsilon,\qquad \mathcal{L} = \mathbb{E}\,\big\lVert v_\theta(A^\tau, o, \tau) - (A - \epsilon) \big\rVert^2$$

## Example

Tokenize a 7-dimensional action at various bin counts, reconstruct it to measure the error, and
count the tokens an action chunk produces.

```python
import numpy as np

# fake teleoperation data: 2000 steps of 7-dimensional actions
# (dx, dy, dz, droll, dpitch, dyaw, gripper)
rng = np.random.default_rng(0)
t = np.arange(2000) * 0.02
arm = [0.05 * np.sin(t + k) + 0.005 * rng.standard_normal(t.size) for k in range(6)]
actions = np.column_stack(arm + [(np.sin(0.5 * t) > 0).astype(float)])


class BinTokenizer:
    """Split each dimension's 1st-99th percentile range into n_bins bins and map to integer tokens."""

    def __init__(self, data, n_bins=256):
        self.lo, self.hi = np.percentile(data, 1, axis=0), np.percentile(data, 99, axis=0)
        self.n = n_bins

    def encode(self, a):
        z = (np.clip(a, self.lo, self.hi) - self.lo) / (self.hi - self.lo)
        return np.minimum((z * self.n).astype(int), self.n - 1)

    def decode(self, tok):
        return self.lo + (tok + 0.5) / self.n * (self.hi - self.lo)  # bin center


for n_bins in (16, 64, 256):
    tk = BinTokenizer(actions, n_bins)
    err = np.abs(tk.decode(tk.encode(actions)) - actions)[:, :3]
    print(
        f"{n_bins:3d} bins: mean position-delta error {1000 * err.mean():.3f} mm, "
        f"max {1000 * err.max():.2f} mm"
    )

H = 50  # action chunk length (1 second at 50 Hz, say)
print(
    f"a chunk of {H} steps x {actions.shape[1]} dimensions = {H * actions.shape[1]} tokens "
    f"to generate one at a time"
)
```

Output:

```text
 16 bins: mean position-delta error 1.805 mm, max 13.07 mm
 64 bins: mean position-delta error 0.480 mm, max 10.44 mm
256 bins: mean position-delta error 0.147 mm, max 9.79 mm
a chunk of 50 steps x 7 dimensions = 350 tokens to generate one at a time
```

The mean error falls inversely with the bin count, but the maximum error stays near 10 mm,
because large actions outside the 1st-99th percentile range are clipped away. It is a trade-off
between an outlier-robust range and precision. Emitting a whole chunk as tokens means generating
hundreds of tokens sequentially, so high-rate control favors a continuous head or a compressing
tokenizer.

**Exercise:** (1) Change the range to the minimum and maximum values and see how the mean and
maximum errors change. (2) Measure the error of the gripper (binary) dimension separately and
decide whether that dimension needs 256 bins.

## Self-check questions

1. Give one thing a VLA gains by reusing a VLM backbone and one thing it pays for it (size, latency).
2. Which is better suited to a control loop above 50 Hz, action tokenization or a flow matching head, and why?
3. You want to attach a language-instructed picking task to an SO-101 arm with a single 24 GB GPU. Which model would you start with, and how (inference only, LoRA, or full fine-tuning)?

## How to study this stage

1. **Survey (first):** read only the architecture taxonomy section of the VLA survey and tabulate
   the tokenization family against the continuous head family.
2. **This lesson plus the example:** get a feel for the quantization error and the token count
   from the example.
3. **Problems:** take the quiz in the Korean original (`rc quiz m9-vla-foundation-models`).
4. **One model in depth:** read the SmolVLA blog post, and check the differences and memory
   requirements of π0, π0-FAST, and π0.5 in the openpi README.
5. **Optional:** skim the SO-100 example configuration of Isaac-GR00T and note what you would
   change (action space, cameras) to attach it to your own robot.

## References

- Hugging Face, "SmolVLA: Efficient Vision-Language-Action Model trained on LeRobot Community Data" -
  <https://huggingface.co/blog/smolvla>
- Physical Intelligence, openpi - <https://github.com/Physical-Intelligence/openpi>
- "A Survey on Vision-Language-Action Models for Embodied AI" (v7) - <https://arxiv.org/html/2405.14093v7>
- NVIDIA, Isaac-GR00T - <https://github.com/NVIDIA/Isaac-GR00T>
- Anthony Brohan et al., "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control" (2023)
- Moo Jin Kim et al., "OpenVLA: An Open-Source Vision-Language-Action Model" (2024)
- Kevin Black et al., "π0: A Vision-Language-Action Flow Model for General Robot Control" (2024)
