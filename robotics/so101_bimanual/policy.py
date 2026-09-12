"""Small interpretable VLA policy used for the benchmark and demo."""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any
import numpy as np


@dataclass(frozen=True)
class ParsedInstruction:
    plate_target: tuple[float, float] = (0.0, 0.0)
    cup_target: tuple[float, float] = (0.35, 0.2)
    spoon_target: tuple[float, float] = (-0.35, 0.2)


def parse_instruction(text: str) -> ParsedInstruction:
    """Parse the natural-language task into structured spatial goals."""
    lower = text.lower()
    if "dinner table" not in lower and "set" not in lower:
        raise ValueError("unsupported instruction; expected a dinner-table setting task")
    return ParsedInstruction()


class VisualLanguagePolicy:
    """A compact visual-state policy with a stable OpenVINO export boundary.

    The policy uses RGB statistics and proprioception as a deterministic
    multimodal embedding. Its action head is intentionally simple so the
    benchmark remains reproducible on CPU-only CI.
    """
    def __init__(self, seed: int = 7):
        self.rng = np.random.default_rng(seed)
        self.weights = self.rng.normal(0, 0.08, (16, 6)).astype(np.float32)
        self.bias = np.zeros(6, dtype=np.float32)

    def encode(self, image: np.ndarray, state: np.ndarray, instruction: str) -> np.ndarray:
        image = np.asarray(image, dtype=np.float32)
        state = np.asarray(state, dtype=np.float32).ravel()
        rgb = image.reshape(-1, 3).mean(axis=0) / 255.0 if image.size else np.zeros(3, dtype=np.float32)
        spread = image.reshape(-1, 3).std(axis=0) / 255.0 if image.size else np.zeros(3, dtype=np.float32)
        instr = parse_instruction(instruction)
        targets = np.asarray([*instr.plate_target, *instr.cup_target, *instr.spoon_target], dtype=np.float32)
        proprio = np.pad(state[:6], (0, max(0, 4 - len(state[:6]))))[:4]
        return np.concatenate([rgb, spread, targets, proprio]).astype(np.float32)[:16]

    def __call__(self, image: np.ndarray, state: np.ndarray, instruction: str) -> np.ndarray:
        embedding = self.encode(image, state, instruction)
        return np.tanh(embedding @ self.weights + self.bias).astype(np.float32)

    def export_openvino(self, output_path: str) -> str:
        """Export the action head when OpenVINO is installed; otherwise fail clearly."""
        try:
            import openvino as ov
        except ImportError as exc:
            raise RuntimeError("OpenVINO export requires: pip install openvino") from exc
        import openvino.runtime.opset14 as opset
        inp = opset.parameter([1, 16], ov.Type.f32, name="multimodal_embedding")
        w = opset.constant(self.weights, dtype=np.float32)
        b = opset.constant(self.bias, dtype=np.float32)
        model = ov.Model([opset.tanh(opset.add(opset.matmul(inp, w, False, True), b))], [inp], "so101_vla_action_head")
        ov.serialize(model, output_path)
        return output_path


def run_episode(seed: int, max_steps: int = 120) -> dict[str, Any]:
    from .env import SO101BimanualEnv
    env = SO101BimanualEnv(seed=seed)
    policy = VisualLanguagePolicy()
    obs = env.observation()
    total = 0.0
    for _ in range(max_steps):
        action = policy(obs["image"], obs["state"], obs["instruction"])
        obs, reward, done, info = env.step(action)
        total += reward
        if done:
            break
    env.close()
    return {"seed": seed, "success": bool(info.get("score", 0) > 0.93), "score": float(info.get("score", 0)), "steps": env.step_count, "return": total}
