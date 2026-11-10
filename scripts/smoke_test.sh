#!/bin/bash
# Checks that the workerd installed in the active Python environment can serve a request.
set -euo pipefail

workerd --version
python -m workerd_bin --version

dir=$(mktemp -d)
cat > "$dir/config.capnp" <<'EOF'
using Workerd = import "/workerd/workerd.capnp";
const config :Workerd.Config = (
  services = [(name = "main", worker = .worker)],
  sockets = [(name = "http", address = "127.0.0.1:8080", http = (), service = "main")],
);
const worker :Workerd.Worker = (
  modules = [(name = "worker", esModule = embed "worker.js")],
  compatibilityDate = "2025-01-01",
);
EOF
echo 'export default { fetch() { return new Response("ok\n"); } };' > "$dir/worker.js"

workerd serve "$dir/config.capnp" &
pid=$!
trap 'kill $pid' EXIT

for _ in $(seq 30); do
    curl -sf http://127.0.0.1:8080 && exit 0
    sleep 1
done
echo "workerd did not respond" >&2
exit 1
