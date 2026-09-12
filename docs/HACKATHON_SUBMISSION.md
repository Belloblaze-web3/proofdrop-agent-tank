# Proofdrop SO-101 Bimanual Benchmark Submission

## Executive summary

This extension turns `proofdrop` into a reproducible robotics benchmark and evidence package for the attached dinner-table manipulation rubric. It provides a self-contained MuJoCo scene with two SO-101-style arms, a natural-language instruction parser, a visual/proprioceptive policy boundary, randomized evaluation across ten seeds, an optional OpenVINO export path, and a captioned MP4 demo.

The implementation is intentionally honest about scope. The scene is a compact SO-101-style proxy rather than a vendor calibration of physical hardware. The code is suitable for a simulation-first hackathon submission and provides a clear seam for replacing the proxy XML with the official SO-101 asset and a hardware policy.

## Rubric evidence map

| Criterion | Evidence in this repository | How to run or inspect |
|---|---|---|
| End-to-end task completion and bimanual manipulation | `robotics/so101_bimanual/env.py` models two arms, plate, cup, spoon, tabletop, physics stepping, and task success. | `python robotics/scripts/evaluate.py --seeds 10 --output artifacts/eval.json` |
| VLA / multi-modal reasoning | `policy.py` parses the dinner-table instruction and combines RGB statistics with proprioceptive state before producing six joint actions. | Inspect `parse_instruction`, `VisualLanguagePolicy.encode`, and `VisualLanguagePolicy.__call__`. |
| Robustness and generalization | The environment randomizes object placement, lighting, and friction from a seedable generator. | The evaluator runs ten independent seeds and reports success rate, mean score, and mean steps. |
| OpenVINO and Intel Core Ultra optimization | `VisualLanguagePolicy.export_openvino` exports an OpenVINO action-head model. The boundary is designed for CPU/NPU compilation on Intel Core Ultra. | Install `openvino`, then call `VisualLanguagePolicy().export_openvino("artifacts/so101_vla.xml")`. Record latency with OpenVINO's compiled model on the target machine. |
| Technical quality and reproducibility | Pinned MuJoCo dependency, deterministic seeds, tests, CLI scripts, and this submission guide. | Follow the setup below from a clean checkout. |
| Innovation and technical demonstration | The visual-servoing benchmark keeps the task runnable in CI while retaining the same observation/action seam needed for a real robot policy. The MP4 includes task labels and seed metadata. | `python robotics/scripts/capture_demo.py --output artifacts/so101_bimanual_demo.mp4` |

## Reproducible setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r robotics/requirements.txt pillow
```

Run the benchmark:

```bash
python robotics/scripts/evaluate.py --seeds 10 --offset 0 --output artifacts/eval.json
```

Run the robotics tests:

```bash
python -m pytest robotics/tests
```

Capture the demo:

```bash
python robotics/scripts/capture_demo.py --seed 7 --output artifacts/so101_bimanual_demo.mp4
```

The demo is generated from MuJoCo frames and can be uploaded directly to a hackathon form or linked in a project README. Keep `artifacts/eval.json` beside the video so reviewers can reproduce the reported ten-seed result.

## OpenVINO evaluation protocol

Install OpenVINO only on the optimization machine because it is optional for the base benchmark:

```bash
python -m pip install openvino
python - <<'PY'
from robotics.so101_bimanual import VisualLanguagePolicy
VisualLanguagePolicy().export_openvino("artifacts/so101_vla.xml")
PY
```

For a fair comparison, report the same ten seeds, the same frame size, and the same action horizon for the NumPy and OpenVINO paths. Record median inference latency, throughput, device selection, precision, and success rate. Do not claim Intel Core Ultra results until the benchmark has been run on that device.

## Submission narrative

**Problem.** Bimanual tabletop manipulation is sensitive to object placement, friction, lighting, and instruction interpretation. A successful demo must show more than a single scripted trajectory.

**Approach.** Proofdrop uses a compact MuJoCo scene with two independently colored arms and three randomized tabletop objects. The controller parses the instruction, extracts visual statistics, joins them with proprioception, and emits a six-dimensional action. The environment reports both task score and binary completion so the same run can be used for qualitative video evidence and quantitative robustness evidence.

**What is novel.** The benchmark is packaged as a portable evidence generator. A single command creates the evaluation JSON and another creates a captioned video. The same policy has an explicit OpenVINO export seam, allowing a hackathon team to replace the compact action head with a larger vision-language model without changing the task contract.

**Limitations and next step.** The included XML is a SO-101-style proxy and the current controller models a visual-servoing term rather than a learned grasp policy. For a final physical-robot submission, replace the XML with calibrated SO-101 meshes, add camera calibration and gripper actuators, and report hardware latency and success alongside the simulation results.

## Suggested final submission checklist

| Deliverable | Required file or evidence |
|---|---|
| Source repository | Public GitHub link to the updated `proofdrop` repository |
| Demo | `artifacts/so101_bimanual_demo.mp4` |
| Quantitative evidence | `artifacts/eval.json` with ten seeds |
| Reproduction | This document and `robotics/requirements.txt` |
| Optimization | OpenVINO model and latency table measured on Intel Core Ultra, if available |
| Technical explanation | The narrative above plus a short live walkthrough of `env.py`, `policy.py`, and the evaluator |
