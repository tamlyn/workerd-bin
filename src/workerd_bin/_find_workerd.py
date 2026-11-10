import os
import sysconfig


def find_workerd_bin() -> str:
    """Return the path of the bundled workerd binary."""
    exe = "workerd"

    candidates = [
        os.path.join(sysconfig.get_path("scripts"), exe),
        os.path.join(sysconfig.get_path("scripts", sysconfig.get_preferred_scheme("user")), exe),
        # `pip install --target` puts scripts in `bin` next to the package.
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", exe),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(f"workerd binary not found in any of: {candidates}")
