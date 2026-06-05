"""Setuptools hook — provision Brain access on pip install."""
from setuptools import setup
from setuptools.command.install import install


class GhostHealerInstall(install):
    def run(self):
        install.run(self)
        try:
            from ghost_healer.core.credentials import ensure_builtin_credentials

            ensure_builtin_credentials()
            print("[GHOST] Ready — install-only Brain access (Python SDK).")
        except Exception:
            pass


setup(cmdclass={"install": GhostHealerInstall})
