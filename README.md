# workerd-bin

An unofficial redistribution of [Cloudflare workerd](https://github.com/cloudflare/workerd) binaries as Python wheels, so workerd can be installed anywhere `pip` can reach PyPI.

The package version matches the upstream workerd release it contains.

## Usage

```sh
pip install workerd-bin
workerd serve config.capnp
```

Or run it as a module (`python -m workerd_bin`), or locate the binary from Python:

```python
from workerd_bin import find_workerd_bin
```

## Supported platforms

- Linux x86_64 and aarch64 (glibc 2.35 or later)
- macOS 13.5 or later, x86_64 and arm64

## Building

```sh
./scripts/build.sh
```

This builds one wheel per platform into `dist/`. There is deliberately no sdist: building one on an unsupported platform would install a binary that can't run there. Each wheel downloads the matching binary from the GitHub release named by `version` in `pyproject.toml` and checks it against the SHA-256 digest GitHub publishes for that asset. Set `GITHUB_TOKEN` if you hit API rate limits.

## Releasing

Change `version` in `pyproject.toml`, commit, then push a matching tag (e.g. `v1.20261023.1`). GitHub Actions builds the wheels, smoke-tests them, and publishes to TestPyPI then PyPI using trusted publishing.

To release a packaging fix without changing workerd, append a post-release suffix (e.g. `1.20261023.1.post1`).
