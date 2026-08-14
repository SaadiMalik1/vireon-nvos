from vireon_core.contracts.base import EnvironmentCapture

def test_environment_capture_populates_all_fields():
    ctx = EnvironmentCapture.capture()
    assert ctx.os_info is not None
    assert ctx.cpu_info is not None
    assert ctx.compiler_info is not None
    assert "numpy" in ctx.dependency_versions
    assert len(ctx.environment_fingerprint) == 64

def test_git_sha_is_hex_or_none():
    ctx = EnvironmentCapture.capture()
    if ctx.git_sha is not None:
        assert len(ctx.git_sha) == 40
        int(ctx.git_sha, 16)  # valid hex

def test_fingerprint_is_deterministic_for_same_env():
    ctx1 = EnvironmentCapture.capture()
    ctx2 = EnvironmentCapture.capture()
    # Same env -> same fingerprint (within same process)
    assert ctx1.environment_fingerprint == ctx2.environment_fingerprint

def test_no_hardcoded_fingerprint_string():
    ctx = EnvironmentCapture.capture()
    assert ctx.environment_fingerprint != "deterministic-" + "virtual-env"
