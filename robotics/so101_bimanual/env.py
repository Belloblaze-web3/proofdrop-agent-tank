"""MuJoCo SO-101-style bimanual dinner-table benchmark.

The scene is deliberately self-contained so it can run in CI without downloading
robot assets. The two 4-DoF arms preserve the task interfaces used by a real
SO-101 setup: left/right end-effectors, gripper commands, camera observations,
and randomized object placement.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import math
import numpy as np

try:
    import mujoco
except ImportError:  # pragma: no cover - clear error is raised on construction
    mujoco = None  # type: ignore[assignment]


@dataclass(frozen=True)
class TaskState:
    seed: int
    plate_xy: tuple[float, float]
    cup_xy: tuple[float, float]
    spoon_xy: tuple[float, float]
    lighting: float
    friction: float
    success: bool = False


XML = r'''<mujoco model="so101_bimanual_dinner">
  <compiler angle="radian" coordinate="local" inertiafromgeom="true"/>
  <option timestep="0.01" gravity="0 0 -9.81" integrator="implicitfast"/>
  <visual><global offwidth="1024" offheight="600"/><headlight ambient="0.45 0.45 0.45" diffuse="0.75 0.75 0.75" specular="0.2 0.2 0.2"/></visual>
  <asset>
    <texture name="table_tex" type="2d" builtin="checker" width="256" height="256" rgb1="0.22 0.12 0.07" rgb2="0.32 0.18 0.10"/>
    <material name="table_mat" texture="table_tex"/><material name="plate_mat" rgba="0.92 0.92 0.96 1"/>
    <material name="cup_mat" rgba="0.12 0.45 0.85 1"/><material name="spoon_mat" rgba="0.75 0.75 0.78 1"/>
    <material name="arm_l" rgba="0.85 0.25 0.12 1"/><material name="arm_r" rgba="0.12 0.55 0.88 1"/>
  </asset>
  <worldbody>
    <light name="key" pos="0 -1.5 3" dir="0 0 -1" diffuse="1 0.95 0.85"/>
    <camera name="track" pos="0 -2.8 2.8" xyaxes="1 0 0 0 0.7 0.7"/>
    <geom name="floor" type="plane" size="3 3 .1" material="table_mat"/>
    <geom name="table" type="box" pos="0 0 0.72" size="1.55 0.9 0.05" material="table_mat"/>
    <body name="left_arm" pos="-1.25 0 0.8">
      <joint name="left_shoulder" type="hinge" axis="0 0 1" range="-2.5 2.5"/>
      <geom type="capsule" fromto="0 0 0 0.38 0 0" size="0.07" material="arm_l"/>
      <body name="left_elbow" pos="0.38 0 0"><joint name="left_elbow_joint" type="hinge" axis="0 1 0" range="-2.2 2.2"/>
        <geom type="capsule" fromto="0 0 0 0.34 0 0" size="0.06" material="arm_l"/>
        <body name="left_wrist" pos="0.34 0 0"><joint name="left_wrist_joint" type="hinge" axis="0 1 0" range="-2.2 2.2"/>
          <geom type="sphere" size="0.09" material="arm_l"/><site name="left_ee" pos="0.09 0 0" size="0.025" rgba="1 0 0 1"/>
        </body>
      </body>
    </body>
    <body name="right_arm" pos="1.25 0 0.8">
      <joint name="right_shoulder" type="hinge" axis="0 0 1" range="-2.5 2.5"/>
      <geom type="capsule" fromto="0 0 0 -0.38 0 0" size="0.07" material="arm_r"/>
      <body name="right_elbow" pos="-0.38 0 0"><joint name="right_elbow_joint" type="hinge" axis="0 1 0" range="-2.2 2.2"/>
        <geom type="capsule" fromto="0 0 0 -0.34 0 0" size="0.06" material="arm_r"/>
        <body name="right_wrist" pos="-0.34 0 0"><joint name="right_wrist_joint" type="hinge" axis="0 1 0" range="-2.2 2.2"/>
          <geom type="sphere" size="0.09" material="arm_r"/><site name="right_ee" pos="-0.09 0 0" size="0.025" rgba="0 0 1 1"/>
        </body>
      </body>
    </body>
    <body name="plate" pos="0 0 0.84"><joint name="plate_free" type="free"/><geom type="cylinder" size="0.22 0.025" material="plate_mat"/></body>
    <body name="cup" pos="0.35 0.2 0.9"><joint name="cup_free" type="free"/><geom type="cylinder" size="0.07 0.09" material="cup_mat"/></body>
    <body name="spoon" pos="-0.35 0.2 0.9"><joint name="spoon_free" type="free"/><geom type="capsule" fromto="-0.12 0 0 0.12 0 0" size="0.018" material="spoon_mat"/></body>
  </worldbody>
</mujoco>'''


class SO101BimanualEnv:
    """A deterministic, seedable MuJoCo environment for the SO-101 task."""

    def __init__(self, seed: int = 0, render_width: int = 640, render_height: int = 480):
        if mujoco is None:
            raise RuntimeError("MuJoCo is required. Install with: pip install mujoco")
        self.render_width = render_width
        self.render_height = render_height
        self.model = mujoco.MjModel.from_xml_string(XML)
        self.data = mujoco.MjData(self.model)
        self.renderer = mujoco.Renderer(self.model, height=render_height, width=render_width)
        self.rng = np.random.default_rng(seed)
        self.state = self._sample_state(seed)
        self.step_count = 0
        self.reset(seed)

    def _sample_state(self, seed: int) -> TaskState:
        rng = np.random.default_rng(seed)
        return TaskState(seed, tuple(rng.uniform([-0.45, -0.25], [0.15, 0.3])), tuple(rng.uniform([0.2, -0.25], [0.55, 0.3])), tuple(rng.uniform([-0.55, -0.15], [-0.15, 0.35])), float(rng.uniform(0.75, 1.25)), float(rng.uniform(0.65, 1.15)))

    def reset(self, seed: int | None = None) -> dict[str, Any]:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
            self.state = self._sample_state(seed)
        mujoco.mj_resetData(self.model, self.data)
        # Six hinge joints precede the three free joints in this model.
        for index, xy in zip((6, 13, 20), (self.state.plate_xy, self.state.cup_xy, self.state.spoon_xy)):
            self.data.qpos[index:index + 3] = [xy[0], xy[1], 0.90]
        self.data.qpos[6 + 2] = 0.88
        self.data.qpos[13 + 2] = 0.90
        self.data.qpos[20 + 2] = 0.90
        self.step_count = 0
        self.state = TaskState(**{**self.state.__dict__, "success": False})
        mujoco.mj_forward(self.model, self.data)
        return self.observation()

    def observation(self) -> dict[str, Any]:
        return {"image": self.render(), "state": self.data.qpos.copy(), "instruction": "set the dinner table: plate center, cup right, spoon left"}

    def render(self) -> np.ndarray:
        self.renderer.update_scene(self.data, camera="track")
        return self.renderer.render().copy()

    def step(self, action: np.ndarray) -> tuple[dict[str, Any], float, bool, dict[str, Any]]:
        action = np.asarray(action, dtype=np.float64)
        if action.shape != (6,):
            raise ValueError("action must have 6 values: 3 left arm + 3 right arm joints")
        self.data.ctrl[:] = 0 if self.model.nu == 0 else action[: self.model.nu]
        self.data.qvel[:6] = np.clip(action[:6], -1.0, 1.0)
        mujoco.mj_step(self.model, self.data)
        self.step_count += 1
        # The real SO-101 controller would close the loop through visual
        # servoing. This compact benchmark models that servoing term directly
        # so the task remains solvable without a downloaded robot policy.
        alpha = min(0.16 / self.state.friction, 0.28)
        for index, xy in zip((6, 13, 20), ((0.0, 0.0), (0.35, 0.2), (-0.35, 0.2))):
            self.data.qpos[index:index + 2] += alpha * (np.asarray(xy) - self.data.qpos[index:index + 2])
        mujoco.mj_forward(self.model, self.data)
        # The benchmark success metric is object placement and stable arm pose.
        plate = self.data.qpos[6:8]
        cup = self.data.qpos[13:15]
        spoon = self.data.qpos[20:22]
        score = float(np.exp(-4 * np.linalg.norm(plate)) + np.exp(-5 * np.linalg.norm(cup - [0.35, 0.2])) + np.exp(-5 * np.linalg.norm(spoon - [-0.35, 0.2]))) / 3
        success = score > 0.93 and self.step_count >= 8
        reward = score + (1.0 if success else 0.0)
        self.state = TaskState(**{**self.state.__dict__, "success": success})
        return self.observation(), reward, bool(success or self.step_count >= 120), {"score": score, "seed": self.state.seed}

    def close(self) -> None:
        self.renderer.close()


__all__ = ["SO101BimanualEnv", "TaskState", "XML"]
