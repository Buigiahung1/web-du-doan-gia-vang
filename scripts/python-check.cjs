const { spawnSync } = require("node:child_process");
const { existsSync, mkdirSync } = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const python = path.join(
  root,
  ".venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python"
);
if (!existsSync(python))
  throw new Error(
    "Create the root .venv and install backend/requirements-dev.txt first."
  );
const mode = process.argv[2];
let args;
if (mode === "typecheck") {
  args = ["-m", "mypy", "app", "--ignore-missing-imports"];
} else if (mode === "test") {
  if (!existsSync(path.join(root, "backend/tests")))
    throw new Error(
      "Local backend/tests must be provisioned; this hook does not silently skip tests."
    );
  const base = path.join(
    root,
    ".local-artifacts",
    "checks",
    `pytest-${Date.now()}`
  );
  mkdirSync(path.dirname(base), { recursive: true });
  args = ["-m", "pytest", "-q", "--basetemp", base];
} else throw new Error("Expected typecheck or test");
const result = spawnSync(python, args, {
  cwd: path.join(root, "backend"),
  stdio: "inherit",
  env: {
    ...process.env,
    DATABASE_URL: "sqlite://",
    USE_STUB_MODEL: "false",
    PYTHONPATH: root,
    PYTHONIOENCODING: "utf-8",
  },
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
