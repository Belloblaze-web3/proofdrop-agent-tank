import numpy as np
from robotics.so101_bimanual import SO101BimanualEnv, parse_instruction, run_episode


def test_instruction_parser_returns_spatial_goals():
    parsed = parse_instruction("Set the dinner table with the plate, cup, and spoon")
    assert parsed.plate_target == (0.0, 0.0)
    assert parsed.cup_target == (0.35, 0.2)


def test_environment_reset_is_seed_deterministic():
    a = SO101BimanualEnv(seed=4)
    b = SO101BimanualEnv(seed=4)
    assert np.allclose(a.state.plate_xy, b.state.plate_xy)
    assert np.allclose(a.reset()["state"], b.reset()["state"])
    a.close(); b.close()


def test_episode_completes_end_to_end():
    result = run_episode(3, max_steps=120)
    assert result["success"]
    assert result["score"] > 0.93
    assert result["steps"] <= 120
