from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cpu_and_gpu_images_drop_root_without_world_writable_workdir():
    for name in ("Dockerfile", "Dockerfile.gpu"):
        dockerfile = (ROOT / name).read_text(encoding="utf-8")

        assert "USER moneyprint" in dockerfile
        assert "RUNTIME_UID=1000" in dockerfile
        assert "RUNTIME_GID=1000" in dockerfile
        assert "chmod 777" not in dockerfile
        assert "chown moneyprint:moneyprint /MoneyPrinterTurbo" in dockerfile


def test_compose_services_map_runtime_identity_to_bind_mount_owner():
    for name in ("docker-compose.yml", "docker-compose.release.yml"):
        compose = (ROOT / name).read_text(encoding="utf-8")

        assert compose.count(
            'user: "${MONEYPRINT_UID:-1000}:${MONEYPRINT_GID:-1000}"'
        ) == 2
