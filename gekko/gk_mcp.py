from __future__ import annotations

import argparse
import gc
import io
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import traceback
import uuid
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, Iterable, Optional

from .gekko import GEKKO

RUNS_DIRNAME = ".mcp/runs"
MODEL_SECTION_HEADERS = {
    "Constants",
    "Parameters",
    "Variables",
    "Intermediates",
    "Equations",
    "Connections",
    "Objects",
    "Compounds",
}

__all__ = [
    "AnalysisTarget",
    "ModelMCP",
    "attach_model",
    "bundle_model",
    "check_python_syntax",
    "create_model",
    "diagnose_model",
    "execute_script",
    "get_degrees_of_freedom",
    "get_options",
    "list_runs",
    "materialize_model",
    "parse_dbs_text",
    "parse_info_text",
    "resolve_analysis_target",
    "run_python_script",
    "save_model_script",
    "scaffold_model_script",
    "suggest_tuning_changes",
    "summarize_results",
]


@dataclass
class AnalysisTarget:
    workspace_root: Path
    bundle_dir: Optional[Path]
    model_dir: Path
    metadata: Dict[str, Any]
    model_metadata: Dict[str, Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def runs_root(workspace_root: Path) -> Path:
    root = Path(workspace_root).resolve() / RUNS_DIRNAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def new_run_id(prefix: str = "run") -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{timestamp}-{uuid.uuid4().hex[:8]}"


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_text_if_exists(path: Optional[Path]) -> Optional[str]:
    if path is None or not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def load_json_if_exists(path: Optional[Path]) -> Optional[Dict[str, Any]]:
    text = read_text_if_exists(path)
    if text is None:
        return None
    return json.loads(text)


def resolve_workspace_path(
    workspace_root: Path,
    candidate: str,
    *,
    must_exist: bool = False,
    allow_outside_workspace: bool = False,
) -> Path:
    root = Path(workspace_root).resolve()
    path = Path(candidate).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not allow_outside_workspace:
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Path must stay inside the workspace root: {root}") from exc
    if must_exist and not path.exists():
        raise FileNotFoundError(path)
    return path


def copy_directory_contents(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def _parse_scalar(value: str) -> Any:
    stripped = value.strip()
    if stripped.startswith(("'", '"')) and stripped.endswith(("'", '"')) and len(stripped) >= 2:
        return stripped[1:-1]
    if stripped.upper() == "TRUE":
        return True
    if stripped.upper() == "FALSE":
        return False
    if re.fullmatch(r"[+-]?\d+", stripped):
        try:
            return int(stripped)
        except ValueError:
            return stripped
    try:
        return float(stripped)
    except ValueError:
        return stripped


def parse_dbs_text(text: str) -> Dict[str, Any]:
    global_options: Dict[str, Any] = {}
    local_options: Dict[str, Dict[str, Any]] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("!", "#")) or "=" not in line:
            continue
        lhs, rhs = line.split("=", 1)
        lhs = lhs.strip()
        rhs_value = _parse_scalar(rhs)
        if "." not in lhs:
            continue
        owner, option = lhs.split(".", 1)
        owner = owner.strip()
        option = option.strip().upper()
        if owner.upper() == "APM":
            global_options[option] = rhs_value
        else:
            local_options.setdefault(owner, {})[option] = rhs_value

    return {"global": global_options, "local": local_options}


def parse_info_text(text: str) -> Dict[str, Any]:
    by_name: Dict[str, str] = {}
    by_type: Dict[str, list[str]] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or "," not in line:
            continue
        var_type, name = [part.strip() for part in line.split(",", 1)]
        if not var_type or not name:
            continue
        by_name[name] = var_type
        by_type.setdefault(var_type, []).append(name)

    for names in by_type.values():
        names.sort()

    return {"by_name": by_name, "by_type": by_type}


def extract_model_sections(text: str) -> Dict[str, list[str]]:
    sections = {header: [] for header in MODEL_SECTION_HEADERS}
    current: Optional[str] = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("!"):
            continue
        if line in ("Model", "End Model"):
            continue
        if line in MODEL_SECTION_HEADERS:
            current = line
            continue
        if line.startswith("End "):
            current = None
            continue
        if current is not None:
            sections[current].append(line)

    return sections


def find_artifact_file(model_dir: Path, kind: str) -> Optional[Path]:
    model_dir = Path(model_dir)
    if not model_dir.exists():
        return None

    if kind == "model":
        matches = sorted(model_dir.glob("*.apm"))
        return matches[0] if matches else None
    if kind == "info":
        matches = sorted(model_dir.glob("*.info"))
        return matches[0] if matches else None
    if kind == "measurements":
        path = model_dir / "measurements.dbs"
        return path if path.exists() else None
    if kind == "options":
        path = model_dir / "options.json"
        return path if path.exists() else None
    if kind == "results":
        path = model_dir / "results.json"
        return path if path.exists() else None
    return None


def artifact_paths(model_dir: Path) -> Dict[str, Optional[Path]]:
    return {
        "model": find_artifact_file(model_dir, "model"),
        "info": find_artifact_file(model_dir, "info"),
        "measurements": find_artifact_file(model_dir, "measurements"),
        "options": find_artifact_file(model_dir, "options"),
        "results": find_artifact_file(model_dir, "results"),
    }


def bundle_io_paths(bundle_dir: Path) -> Dict[str, Path]:
    bundle_dir = Path(bundle_dir)
    return {
        "metadata": bundle_dir / "metadata.json",
        "stdout": bundle_dir / "stdout.txt",
        "stderr": bundle_dir / "stderr.txt",
        "script": bundle_dir / "script.py",
    }


def _resolve_bundle_model(
    bundle_dir: Path,
    metadata: Dict[str, Any],
    model_index: int,
) -> tuple[Path, Dict[str, Any]]:
    models = metadata.get("models") or []
    if models:
        if model_index < 0 or model_index >= len(models):
            raise IndexError(f"Model index {model_index} is out of range for run {bundle_dir.name}")
        model_metadata = models[model_index]
        bundle_subdir = model_metadata.get("bundle_subdir")
        if bundle_subdir:
            return bundle_dir / bundle_subdir, model_metadata

    fallback = bundle_dir / "models" / str(model_index)
    if fallback.exists():
        return fallback, {"index": model_index, "bundle_subdir": str(fallback.relative_to(bundle_dir))}

    return bundle_dir, {"index": model_index}


def resolve_analysis_target(
    workspace_root: Path,
    *,
    run_id: Optional[str] = None,
    path: Optional[str] = None,
    model_index: int = 0,
) -> AnalysisTarget:
    if not run_id and not path:
        raise ValueError("Either run_id or path is required")

    if run_id:
        bundle_dir = runs_root(workspace_root) / run_id
        if not bundle_dir.exists():
            raise FileNotFoundError(bundle_dir)
        metadata = load_json_if_exists(bundle_dir / "metadata.json") or {}
        model_dir, model_metadata = _resolve_bundle_model(bundle_dir, metadata, model_index)
        return AnalysisTarget(
            workspace_root=Path(workspace_root).resolve(),
            bundle_dir=bundle_dir,
            model_dir=model_dir,
            metadata=metadata,
            model_metadata=model_metadata,
        )

    resolved_path = Path(path).expanduser()
    if not resolved_path.is_absolute():
        resolved_path = Path(workspace_root).resolve() / resolved_path
    resolved_path = resolved_path.resolve()
    if resolved_path.is_file():
        resolved_path = resolved_path.parent

    metadata_path = resolved_path / "metadata.json"
    if metadata_path.exists() or (resolved_path / "models").exists():
        metadata = load_json_if_exists(metadata_path) or {}
        model_dir, model_metadata = _resolve_bundle_model(resolved_path, metadata, model_index)
        return AnalysisTarget(
            workspace_root=Path(workspace_root).resolve(),
            bundle_dir=resolved_path,
            model_dir=model_dir,
            metadata=metadata,
            model_metadata=model_metadata,
        )

    return AnalysisTarget(
        workspace_root=Path(workspace_root).resolve(),
        bundle_dir=None,
        model_dir=resolved_path,
        metadata={},
        model_metadata={"index": model_index},
    )


def iter_log_texts(target: AnalysisTarget) -> Iterable[str]:
    for text in target.metadata.get("_inline_logs", []) or []:
        if text:
            yield text

    bundle_dir = target.bundle_dir
    if bundle_dir is not None:
        for name in ("stdout.txt", "stderr.txt"):
            text = read_text_if_exists(bundle_dir / name)
            if text:
                yield text

    if target.model_dir.exists():
        for pattern in ("*.lst", "*.out", "*.log", "*.txt"):
            for path in sorted(target.model_dir.glob(pattern)):
                if bundle_dir is not None and path.parent == bundle_dir and path.name in ("stdout.txt", "stderr.txt"):
                    continue
                text = read_text_if_exists(path)
                if text:
                    yield text


def list_run_summaries(workspace_root: Path, limit: Optional[int] = None) -> list[Dict[str, Any]]:
    root = runs_root(workspace_root)
    bundle_dirs = sorted(
        [path for path in root.iterdir() if path.is_dir()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if limit is not None:
        bundle_dirs = bundle_dirs[:limit]

    summaries: list[Dict[str, Any]] = []
    for bundle_dir in bundle_dirs:
        metadata = load_json_if_exists(bundle_dir / "metadata.json") or {}
        summaries.append(
            {
                "run_id": bundle_dir.name,
                "status": metadata.get("status"),
                "script_path": metadata.get("script_path"),
                "duration_seconds": metadata.get("duration_seconds"),
                "started_at": metadata.get("started_at"),
                "bundle_dir": str(bundle_dir),
                "model_count": len(metadata.get("models") or []),
                "models": metadata.get("models") or [],
            }
        )
    return summaries


def save_model_script(
    workspace_root: Path,
    path: str,
    source: str,
    *,
    overwrite: bool = False,
) -> Dict[str, Any]:
    target = resolve_workspace_path(workspace_root, path)
    existed_before = target.exists()
    if existed_before and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    return {
        "path": str(target),
        "line_count": len(source.splitlines()),
        "overwrote_existing": existed_before and overwrite,
    }


def check_python_syntax(
    *,
    source: Optional[str] = None,
    path: Optional[str] = None,
    workspace_root: Optional[Path] = None,
) -> Dict[str, Any]:
    if source is None and path is None:
        raise ValueError("Either source or path is required")

    if source is None:
        if workspace_root is None:
            raise ValueError("workspace_root is required when checking a file path")
        source_path = resolve_workspace_path(workspace_root, path, must_exist=True, allow_outside_workspace=True)
        source = source_path.read_text(encoding="utf-8")
        filename = str(source_path)
    else:
        filename = path or "<memory>"

    try:
        compile(source, filename, "exec")
    except SyntaxError as exc:
        return {
            "valid": False,
            "filename": filename,
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.msg,
                "line": exc.lineno,
                "column": exc.offset,
                "text": exc.text.rstrip("\n") if exc.text else None,
            },
            "formatted": f"{exc.__class__.__name__}: {exc.msg} (line {exc.lineno}, column {exc.offset})",
        }

    return {
        "valid": True,
        "filename": filename,
        "line_count": len(source.splitlines()),
    }


def _template_for(problem_type: str, model_name: str) -> str:
    key = problem_type.lower().replace("-", "_")
    templates = {
        "steady_state": f"""
        from gekko import GEKKO

        m = GEKKO(remote=False, name="{model_name}")

        x = m.Var(value=1, lb=0)
        y = m.Var(value=2, lb=0)

        m.Equations([
            x + y == 5,
            x - y == 1,
        ])
        m.Minimize((x - 3) ** 2 + (y - 2) ** 2)

        m.solve(disp=True)

        print("x =", x.value[0])
        print("y =", y.value[0])
        print("run_directory =", m.path)
        """,
        "dynamic_optimization": f"""
        from gekko import GEKKO

        m = GEKKO(remote=False, name="{model_name}")
        m.time = [0, 1, 2, 3, 4, 5]

        u = m.MV(value=0, lb=-2, ub=2)
        u.STATUS = 1
        x = m.Var(value=0)

        m.Equation(x.dt() == -x + u)
        m.Minimize((x - 1) ** 2)

        m.options.IMODE = 6
        m.solve(disp=True)

        print("final_x =", x.value[-1])
        print("run_directory =", m.path)
        """,
        "mhe": f"""
        from gekko import GEKKO

        m = GEKKO(remote=False, name="{model_name}")
        m.time = [0, 1, 2, 3, 4]

        k = m.FV(value=0.8, lb=0.1, ub=2.0)
        k.STATUS = 1
        y = m.CV(value=[0.0, 0.2, 0.35, 0.5, 0.62])
        y.FSTATUS = 1
        y.STATUS = 1
        y.MEAS_GAP = 0.01
        u = m.Param(value=[1, 1, 1, 1, 1])

        m.Equation(y.dt() == -k * y + u)

        m.options.IMODE = 5
        m.options.EV_TYPE = 1
        m.solve(disp=True)

        print("estimated_k =", k.value[0])
        print("run_directory =", m.path)
        """,
        "mpc": f"""
        from gekko import GEKKO

        m = GEKKO(remote=False, name="{model_name}")
        m.time = [0, 1, 2, 3, 4, 5]

        mv = m.MV(value=0, lb=-2, ub=2)
        mv.STATUS = 1
        mv.DCOST = 0.1
        mv.DMAX = 0.5

        cv = m.CV(value=0)
        cv.STATUS = 1
        cv.FSTATUS = 1
        cv.TAU = 2
        cv.TR_INIT = 1
        cv.SP = 1

        m.Equation(cv.dt() == -cv + mv)

        m.options.IMODE = 6
        m.options.CV_TYPE = 2
        m.solve(disp=True)

        print("predicted_cv =", cv.value)
        print("planned_mv =", mv.value)
        print("run_directory =", m.path)
        """,
    }

    if key not in templates:
        supported = ", ".join(sorted(templates))
        raise ValueError(f"Unsupported problem_type '{problem_type}'. Supported values: {supported}")

    return textwrap.dedent(templates[key]).strip() + "\n"


def scaffold_model_script(
    workspace_root: Path,
    *,
    problem_type: str,
    model_name: str = "gekko_model",
    path: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    template = _template_for(problem_type, model_name)
    response: Dict[str, Any] = {
        "problem_type": problem_type,
        "model_name": model_name,
        "source": template,
    }
    if path:
        response["file"] = save_model_script(workspace_root, path, template, overwrite=overwrite)
    return response


@contextmanager
def pushd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


@contextmanager
def prepend_sys_path(path: Path):
    value = str(path)
    sys.path.insert(0, value)
    try:
        yield
    finally:
        try:
            sys.path.remove(value)
        except ValueError:
            pass


def _baseline_model_ids() -> set[int]:
    return {id(obj) for obj in gc.get_objects() if isinstance(obj, GEKKO)}


def _discover_models(namespace: Dict[str, Any], baseline_ids: set[int]) -> list[Any]:
    discovered = []
    seen_ids = set()

    for value in namespace.values():
        if isinstance(value, GEKKO) and id(value) not in seen_ids:
            discovered.append(value)
            seen_ids.add(id(value))

    for obj in gc.get_objects():
        if isinstance(obj, GEKKO) and id(obj) not in baseline_ids and id(obj) not in seen_ids:
            discovered.append(obj)
            seen_ids.add(id(obj))

    return discovered


def _materialize_artifacts(model: GEKKO) -> Dict[str, Any]:
    notes: list[str] = []
    success = True
    try:
        if getattr(model, "_model", None) != "provided":
            model._build_model()
        if getattr(model, "_csv_status", None) != "provided":
            model._write_csv()
        model._generate_dbs_file()
        model._write_solver_options()
        model._write_info()
    except Exception as exc:
        success = False
        notes.append(f"Artifact materialization failed: {exc}")
    return {"success": success, "notes": notes}


def _snapshot_model(model: GEKKO, destination: Path, index: int) -> Dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    materialization = _materialize_artifacts(model)
    source_path = Path(getattr(model, "_path", "") or "")
    if source_path.exists():
        copy_directory_contents(source_path, destination)

    files = sorted(path.name for path in destination.iterdir()) if destination.exists() else []
    return {
        "index": index,
        "model_name": getattr(model, "_model_name", f"model_{index}"),
        "remote": bool(getattr(model, "_remote", False)),
        "original_path": str(source_path) if source_path else None,
        "bundle_subdir": str(destination.relative_to(destination.parent.parent)),
        "materialization": materialization,
        "files": files,
    }


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def execute_script(script_path: Path, run_dir: Path, run_id: str) -> Dict[str, Any]:
    io_paths = bundle_io_paths(run_dir)
    syntax = check_python_syntax(path=str(script_path), workspace_root=script_path.parent)
    started_at = utc_now_iso()
    start = perf_counter()

    if not syntax["valid"]:
        _write_text(io_paths["stdout"], "")
        _write_text(io_paths["stderr"], syntax["formatted"] + "\n")
        metadata = {
            "run_id": run_id,
            "status": "syntax_error",
            "script_path": str(script_path),
            "started_at": started_at,
            "completed_at": utc_now_iso(),
            "duration_seconds": round(perf_counter() - start, 6),
            "models": [],
            "exception": syntax["error"],
        }
        write_json(io_paths["metadata"], metadata)
        return metadata

    baseline_ids = _baseline_model_ids()
    namespace: Dict[str, Any] = {"__name__": "__main__", "__file__": str(script_path), "__package__": None}
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    status = "success"
    exception_payload = None

    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        with pushd(script_path.parent), prepend_sys_path(script_path.parent):
            try:
                code = compile(script_path.read_text(encoding="utf-8"), str(script_path), "exec")
                exec(code, namespace)
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
                if code not in (None, 0):
                    status = "runtime_error"
                    exception_payload = {
                        "type": exc.__class__.__name__,
                        "message": str(exc),
                        "exit_code": code,
                    }
                    traceback.print_exc()
            except BaseException as exc:
                status = "runtime_error"
                exception_payload = {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                }
                traceback.print_exc()

    stdout_text = stdout_buffer.getvalue()
    stderr_text = stderr_buffer.getvalue()
    _write_text(io_paths["stdout"], stdout_text)
    _write_text(io_paths["stderr"], stderr_text)

    models = _discover_models(namespace, baseline_ids)
    model_records = []
    for index, model in enumerate(models):
        model_destination = run_dir / "models" / str(index)
        model_records.append(_snapshot_model(model, model_destination, index))

    metadata = {
        "run_id": run_id,
        "status": status,
        "script_path": str(script_path),
        "started_at": started_at,
        "completed_at": utc_now_iso(),
        "duration_seconds": round(perf_counter() - start, 6),
        "models": model_records,
    }
    if exception_payload is not None:
        metadata["exception"] = exception_payload

    write_json(io_paths["metadata"], metadata)
    return metadata


def run_python_script(
    workspace_root: Path,
    *,
    path: str,
    timeout_seconds: int = 60,
) -> Dict[str, Any]:
    script_path = resolve_workspace_path(
        workspace_root,
        path,
        must_exist=True,
        allow_outside_workspace=True,
    )

    run_id = new_run_id()
    bundle_dir = runs_root(workspace_root) / run_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    io_paths = bundle_io_paths(bundle_dir)
    shutil.copy2(script_path, io_paths["script"])

    env = os.environ.copy()
    package_root = str(Path(__file__).resolve().parent.parent)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = package_root if not existing_pythonpath else package_root + os.pathsep + existing_pythonpath

    command = [
        sys.executable,
        "-m",
        "gekko.gk_mcp",
        "--script",
        str(script_path),
        "--run-dir",
        str(bundle_dir),
        "--run-id",
        run_id,
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(script_path.parent),
            env=env,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        io_paths["stdout"].write_text(stdout, encoding="utf-8")
        io_paths["stderr"].write_text(stderr, encoding="utf-8")
        metadata = {
            "run_id": run_id,
            "status": "timeout",
            "script_path": str(script_path),
            "started_at": None,
            "completed_at": None,
            "duration_seconds": timeout_seconds,
            "models": [],
            "runner_stdout": stdout,
            "runner_stderr": stderr,
        }
        write_json(io_paths["metadata"], metadata)
        return metadata

    metadata = load_json_if_exists(io_paths["metadata"])
    if metadata is None:
        metadata = {
            "run_id": run_id,
            "status": "runner_error" if completed.returncode else "unknown",
            "script_path": str(script_path),
            "models": [],
            "runner_stdout": completed.stdout,
            "runner_stderr": completed.stderr,
        }
        write_json(io_paths["metadata"], metadata)

    metadata["bundle_dir"] = str(bundle_dir)
    metadata["runner_exit_code"] = completed.returncode
    metadata["runner_stdout"] = completed.stdout
    metadata["runner_stderr"] = completed.stderr
    write_json(io_paths["metadata"], metadata)
    return metadata


def list_runs(workspace_root: Path, limit: Optional[int] = None) -> Dict[str, Any]:
    return {"runs": list_run_summaries(workspace_root, limit=limit)}


def create_model(*, remote: bool = False, server: str = "http://byu.apmonitor.com", name: Optional[str] = None) -> GEKKO:
    return GEKKO(remote=remote, server=server, name=name)


def _materialize(model: GEKKO) -> Dict[str, Any]:
    notes: list[str] = []
    success = True
    try:
        if getattr(model, "_model", None) != "provided":
            model._build_model()
        if getattr(model, "_csv_status", None) != "provided":
            model._write_csv()
        model._generate_dbs_file()
        model._write_solver_options()
        model._write_info()
    except Exception as exc:
        success = False
        notes.append(str(exc))

    model_dir = Path(getattr(model, "_path", "") or "").resolve()
    files = sorted(path.name for path in model_dir.iterdir()) if model_dir.exists() else []
    return {
        "success": success,
        "notes": notes,
        "model_dir": str(model_dir),
        "model_name": getattr(model, "_model_name", "gekko_model"),
        "files": files,
    }


def materialize_model(model: GEKKO) -> Dict[str, Any]:
    return _materialize(model)


def _target_from_model(
    model: GEKKO,
    *,
    workspace_root: Path,
    stdout_text: Optional[str] = None,
    stderr_text: Optional[str] = None,
) -> AnalysisTarget:
    materialized = _materialize(model)
    inline_logs = [text for text in (stdout_text, stderr_text) if text]
    metadata = {
        "source": "model_instance",
        "model_name": materialized["model_name"],
        "_inline_logs": inline_logs,
    }
    model_metadata = {
        "index": 0,
        "model_name": materialized["model_name"],
        "files": materialized["files"],
    }
    return AnalysisTarget(
        workspace_root=Path(workspace_root).resolve(),
        bundle_dir=None,
        model_dir=Path(materialized["model_dir"]),
        metadata=metadata,
        model_metadata=model_metadata,
    )


def bundle_model(
    model: GEKKO,
    *,
    workspace_root: Optional[Path] = None,
    run_id: Optional[str] = None,
    stdout_text: Optional[str] = None,
    stderr_text: Optional[str] = None,
) -> Dict[str, Any]:
    root = Path(workspace_root or Path.cwd()).resolve()
    materialized = _materialize(model)
    resolved_run_id = run_id or new_run_id("model")
    bundle_dir = runs_root(root) / resolved_run_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    io_paths = bundle_io_paths(bundle_dir)
    io_paths["stdout"].write_text(stdout_text or "", encoding="utf-8")
    io_paths["stderr"].write_text(stderr_text or "", encoding="utf-8")

    model_destination = bundle_dir / "models" / "0"
    model_destination.mkdir(parents=True, exist_ok=True)
    source_model_dir = Path(materialized["model_dir"])
    if source_model_dir.exists():
        copy_directory_contents(source_model_dir, model_destination)

    files = sorted(path.name for path in model_destination.iterdir()) if model_destination.exists() else []
    metadata = {
        "run_id": resolved_run_id,
        "status": "bundled_model",
        "created_at": utc_now_iso(),
        "model_name": materialized["model_name"],
        "models": [
            {
                "index": 0,
                "model_name": materialized["model_name"],
                "original_path": materialized["model_dir"],
                "bundle_subdir": "models/0",
                "materialization": {
                    "success": materialized["success"],
                    "notes": materialized["notes"],
                },
                "files": files,
            }
        ],
    }
    write_json(io_paths["metadata"], metadata)
    metadata["bundle_dir"] = str(bundle_dir)
    return metadata


def _resolve_target(
    *,
    model: Optional[GEKKO] = None,
    workspace_root: Optional[Path] = None,
    run_id: Optional[str] = None,
    path: Optional[str] = None,
    model_index: int = 0,
    stdout_text: Optional[str] = None,
    stderr_text: Optional[str] = None,
) -> AnalysisTarget:
    root = Path(workspace_root or Path.cwd()).resolve()
    if model is not None:
        return _target_from_model(
            model,
            workspace_root=root,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
        )
    return resolve_analysis_target(root, run_id=run_id, path=path, model_index=model_index)


def get_options(
    model: Optional[GEKKO] = None,
    *,
    workspace_root: Optional[Path] = None,
    run_id: Optional[str] = None,
    path: Optional[str] = None,
    model_index: int = 0,
) -> Dict[str, Any]:
    target = _resolve_target(
        model=model,
        workspace_root=workspace_root,
        run_id=run_id,
        path=path,
        model_index=model_index,
    )
    paths = artifact_paths(target.model_dir)
    dbs = parse_dbs_text(read_text_if_exists(paths["measurements"]) or "")
    info = parse_info_text(read_text_if_exists(paths["info"]) or "")
    options_json = load_json_if_exists(paths["options"]) or {}

    grouped_variables: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for name, options in sorted(dbs["local"].items()):
        var_type = info["by_name"].get(name, "UNKNOWN")
        grouped_variables.setdefault(var_type, {})[name] = options

    return {
        "model_dir": str(target.model_dir),
        "global": dbs["global"],
        "variables": grouped_variables,
        "variable_types": info["by_type"],
        "options_json": options_json,
    }


def summarize_results(
    model: Optional[GEKKO] = None,
    *,
    workspace_root: Optional[Path] = None,
    run_id: Optional[str] = None,
    path: Optional[str] = None,
    model_index: int = 0,
) -> Dict[str, Any]:
    target = _resolve_target(
        model=model,
        workspace_root=workspace_root,
        run_id=run_id,
        path=path,
        model_index=model_index,
    )
    paths = artifact_paths(target.model_dir)
    results = load_json_if_exists(paths["results"])
    options = load_json_if_exists(paths["options"]) or {}

    if results is None:
        return {
            "available": False,
            "message": "results.json was not found for this run",
            "model_dir": str(target.model_dir),
        }

    scalars: Dict[str, Any] = {}
    series_preview: Dict[str, Dict[str, Any]] = {}
    for key, value in results.items():
        if isinstance(value, list):
            series_preview[key] = {
                "length": len(value),
                "first": value[0] if value else None,
                "last": value[-1] if value else None,
            }
        else:
            scalars[key] = value

    solver_summary: Dict[str, Any] = {}
    apm_options = options.get("APM") if isinstance(options, dict) else None
    if isinstance(apm_options, dict):
        for key in (
            "APPINFO",
            "APPSTATUS",
            "ITERATIONS",
            "IMODE",
            "OBJFCNVAL",
            "SOLVER",
            "SOLVESTATUS",
            "SOLVETIME",
        ):
            if key in apm_options:
                solver_summary[key] = apm_options[key]

    return {
        "available": True,
        "model_dir": str(target.model_dir),
        "solver_summary": solver_summary,
        "scalars": scalars,
        "series_preview": series_preview,
    }


def get_degrees_of_freedom(
    model: Optional[GEKKO] = None,
    *,
    workspace_root: Optional[Path] = None,
    run_id: Optional[str] = None,
    path: Optional[str] = None,
    model_index: int = 0,
    stdout_text: Optional[str] = None,
    stderr_text: Optional[str] = None,
) -> Dict[str, Any]:
    target = _resolve_target(
        model=model,
        workspace_root=workspace_root,
        run_id=run_id,
        path=path,
        model_index=model_index,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
    )

    return _get_degrees_of_freedom_from_target(target)


def _get_degrees_of_freedom_from_target(target: AnalysisTarget) -> Dict[str, Any]:
    exact_match = None
    for text in iter_log_texts(target):
        match = re.search(r"degrees of freedom[^-\d]*(-?\d+)", text, flags=re.IGNORECASE)
        if match:
            exact_match = int(match.group(1))
            break

    paths = artifact_paths(target.model_dir)
    model_text = read_text_if_exists(paths["model"]) or ""
    sections = extract_model_sections(model_text)
    dbs = parse_dbs_text(read_text_if_exists(paths["measurements"]) or "")
    info = parse_info_text(read_text_if_exists(paths["info"]) or "")

    active_fv = 0
    active_mv = 0
    for name, options in dbs["local"].items():
        var_type = info["by_name"].get(name)
        status = options.get("STATUS", 0)
        if var_type == "FV" and status == 1:
            active_fv += 1
        if var_type == "MV" and status == 1:
            active_mv += 1

    variable_count = len(sections["Variables"])
    equation_count = len(sections["Equations"])
    parameter_count = len(sections["Parameters"])
    estimated = variable_count + active_fv + active_mv - equation_count

    response = {
        "model_dir": str(target.model_dir),
        "counts": {
            "parameters": parameter_count,
            "variables": variable_count,
            "intermediates": len(sections["Intermediates"]),
            "equations": equation_count,
            "objects": len(sections["Objects"]),
            "connections": len(sections["Connections"]),
        },
        "active_decision_variables": {
            "fv_status_on": active_fv,
            "mv_status_on": active_mv,
        },
        "estimated_degrees_of_freedom": estimated,
        "estimate_note": (
            "Estimated from the compiled .apm model plus FV/MV STATUS flags in measurements.dbs. "
            "Use the solver-reported DOF when it is available."
        ),
    }
    if exact_match is not None:
        response["solver_reported_degrees_of_freedom"] = exact_match
    return response


def _extract_relevant_snippet(text: str, needle: str, window: int = 6) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if needle.lower() in line.lower():
            start = max(0, index - window)
            end = min(len(lines), index + window + 1)
            return "\n".join(lines[start:end])
    return "\n".join(lines[: min(len(lines), window * 2)])


def diagnose_model(
    model: Optional[GEKKO] = None,
    *,
    workspace_root: Optional[Path] = None,
    run_id: Optional[str] = None,
    path: Optional[str] = None,
    model_index: int = 0,
    stdout_text: Optional[str] = None,
    stderr_text: Optional[str] = None,
) -> Dict[str, Any]:
    target = _resolve_target(
        model=model,
        workspace_root=workspace_root,
        run_id=run_id,
        path=path,
        model_index=model_index,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
    )
    logs = list(iter_log_texts(target))
    combined = "\n".join(logs)
    lower = combined.lower()
    dof = _get_degrees_of_freedom_from_target(target)

    category = "unknown"
    findings: list[str] = []
    suggestions: list[str] = []
    snippet = ""

    if "syntaxerror" in lower or "indentationerror" in lower:
        category = "python_syntax_error"
        snippet = _extract_relevant_snippet(combined, "error")
        findings.append("Python failed before GEKKO could solve the model.")
        suggestions.append("Fix the reported file and line first, then rerun the script.")
        suggestions.append("Use `check_python_syntax` before execution to catch parser errors early.")
    elif "@error" in lower:
        category = "apmonitor_error"
        snippet = _extract_relevant_snippet(combined, "@error")
        findings.append("APMonitor reported an @error block while processing the model.")
        suggestions.append("Inspect the compiled model file to see how Python expressions were translated.")
        suggestions.append("Check array indexing, intermediate definitions, and equation syntax near the error block.")
    elif "infeasible" in lower or "no feasible solution" in lower:
        category = "infeasible_model"
        snippet = _extract_relevant_snippet(combined, "infeasible")
        findings.append("The solver reported that the model is infeasible.")
        suggestions.append("Relax bounds or conflicting equations and provide better initial guesses.")
        suggestions.append("Inspect the compiled model and local tuning options for contradictory constraints.")
    elif "time limit exceeded" in lower or "maximum iterations" in lower:
        category = "convergence_or_timeout"
        snippet = _extract_relevant_snippet(combined, "time limit")
        findings.append("The solve ended before convergence.")
        suggestions.append("Reduce horizon complexity or collocation density, then rerun.")
        suggestions.append("Improve scaling and initial guesses before increasing iteration limits.")
    elif dof.get("solver_reported_degrees_of_freedom", dof["estimated_degrees_of_freedom"]) < 0:
        category = "overspecified_model"
        findings.append("The model appears to be overspecified with negative degrees of freedom.")
        suggestions.append("Remove duplicate equations or disable extra FV/MV STATUS flags.")
        suggestions.append("Check whether variables were fixed twice through equations and bounds.")
    else:
        category = "missing_results"
        findings.append("No definitive solve failure pattern was found, but the expected result artifacts are missing.")
        suggestions.append("Run with `disp=True` so the solver log is captured in stdout.")
        suggestions.append("Inspect the available stdout, stderr, and compiled model files together.")

    paths = artifact_paths(target.model_dir)
    support = {name: str(path) for name, path in paths.items() if path is not None}
    if target.bundle_dir is not None:
        stdout_path = target.bundle_dir / "stdout.txt"
        stderr_path = target.bundle_dir / "stderr.txt"
        if stdout_path.exists():
            support["stdout"] = str(stdout_path)
        if stderr_path.exists():
            support["stderr"] = str(stderr_path)

    return {
        "category": category,
        "model_dir": str(target.model_dir),
        "findings": findings,
        "suggestions": suggestions,
        "degrees_of_freedom": dof,
        "snippet": snippet,
        "supporting_files": support,
    }


def suggest_tuning_changes(
    model: Optional[GEKKO] = None,
    *,
    goal: str = "improve performance",
    workspace_root: Optional[Path] = None,
    run_id: Optional[str] = None,
    path: Optional[str] = None,
    model_index: int = 0,
) -> Dict[str, Any]:
    options = get_options(
        model=model,
        workspace_root=workspace_root,
        run_id=run_id,
        path=path,
        model_index=model_index,
    )
    global_options = options["global"]
    variable_groups = options["variables"]
    normalized_goal = goal.lower()
    suggestions: list[Dict[str, Any]] = []

    nodes = global_options.get("NODES")
    if any(token in normalized_goal for token in ("faster", "speed", "performance", "converge")):
        if isinstance(nodes, (int, float)) and nodes > 2:
            suggestions.append(
                {
                    "parameter": "NODES",
                    "current": nodes,
                    "direction": "decrease",
                    "reason": "Lower collocation density reduces solve size and often improves iteration time.",
                }
            )
        if global_options.get("SCALING") == 0:
            suggestions.append(
                {
                    "parameter": "SCALING",
                    "current": 0,
                    "direction": "set to 1",
                    "reason": "Automatic scaling usually improves solver robustness on poorly scaled models.",
                }
            )

    if any(token in normalized_goal for token in ("smooth", "oscillation", "aggressive")):
        for name, settings in variable_groups.get("MV", {}).items():
            if settings.get("DCOST") in (None, 0, 0.0):
                suggestions.append(
                    {
                        "parameter": f"{name}.DCOST",
                        "current": settings.get("DCOST"),
                        "direction": "increase",
                        "reason": "Adding MV movement penalty typically reduces aggressive control moves.",
                    }
                )
            if settings.get("DMAX") in (None, 1.0e20):
                suggestions.append(
                    {
                        "parameter": f"{name}.DMAX",
                        "current": settings.get("DMAX"),
                        "direction": "set a finite bound",
                        "reason": "A finite DMAX limits one-step MV movement and smooths actuator behavior.",
                    }
                )

    if any(token in normalized_goal for token in ("track", "tracking", "response", "sluggish")):
        for name, settings in variable_groups.get("CV", {}).items():
            tau = settings.get("TAU")
            if isinstance(tau, (int, float)) and tau > 1:
                suggestions.append(
                    {
                        "parameter": f"{name}.TAU",
                        "current": tau,
                        "direction": "decrease",
                        "reason": "Smaller TAU makes the desired CV trajectory more responsive.",
                    }
                )
            if settings.get("TR_INIT") == 0:
                suggestions.append(
                    {
                        "parameter": f"{name}.TR_INIT",
                        "current": 0,
                        "direction": "consider enabling",
                        "reason": "Trajectory initialization can improve CV tracking on setpoint changes.",
                    }
                )

    if any(token in normalized_goal for token in ("estimate", "mhe", "measurement")):
        for group_name in ("CV", "FV"):
            for name, settings in variable_groups.get(group_name, {}).items():
                if settings.get("FSTATUS") == 0:
                    suggestions.append(
                        {
                            "parameter": f"{name}.FSTATUS",
                            "current": 0,
                            "direction": "increase toward 1",
                            "reason": "Measurements are ignored when FSTATUS is 0.",
                        }
                    )
                if settings.get("WMEAS") in (None, 0, 0.0):
                    suggestions.append(
                        {
                            "parameter": f"{name}.WMEAS",
                            "current": settings.get("WMEAS"),
                            "direction": "increase",
                            "reason": "Higher WMEAS emphasizes measurement tracking in estimation mode.",
                        }
                    )

    return {
        "goal": goal,
        "model_dir": options["model_dir"],
        "global_options": global_options,
        "suggestions": suggestions,
        "note": (
            "These are rule-based tuning suggestions derived from measurements.dbs and the GEKKO tuning "
            "parameter reference. They should be validated with another run."
        ),
    }


class ModelMCP:
    def __init__(self, model: GEKKO, *, workspace_root: Optional[Path] = None) -> None:
        self.model = model
        self.workspace_root = Path(workspace_root or Path.cwd()).resolve()

    def materialize(self) -> Dict[str, Any]:
        return materialize_model(self.model)

    def bundle(
        self,
        *,
        run_id: Optional[str] = None,
        stdout_text: Optional[str] = None,
        stderr_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        return bundle_model(
            self.model,
            workspace_root=self.workspace_root,
            run_id=run_id,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
        )

    def get_degrees_of_freedom(
        self,
        *,
        stdout_text: Optional[str] = None,
        stderr_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        return get_degrees_of_freedom(
            self.model,
            workspace_root=self.workspace_root,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
        )

    def get_options(self) -> Dict[str, Any]:
        return get_options(self.model, workspace_root=self.workspace_root)

    def summarize_results(self) -> Dict[str, Any]:
        return summarize_results(self.model, workspace_root=self.workspace_root)

    def diagnose(
        self,
        *,
        stdout_text: Optional[str] = None,
        stderr_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        return diagnose_model(
            self.model,
            workspace_root=self.workspace_root,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
        )

    def suggest_tuning_changes(self, *, goal: str = "improve performance") -> Dict[str, Any]:
        return suggest_tuning_changes(self.model, workspace_root=self.workspace_root, goal=goal)


def attach_model(model: GEKKO, *, workspace_root: Optional[Path] = None) -> ModelMCP:
    return ModelMCP(model, workspace_root=workspace_root)


def _parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a GEKKO Python script and bundle its artifacts.")
    parser.add_argument("--script", required=True, help="Python script to execute")
    parser.add_argument("--run-dir", required=True, help="Directory where the bundled run artifacts should be written")
    parser.add_argument("--run-id", required=True, help="Stable run identifier")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    script_path = Path(args.script).resolve()
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    metadata = execute_script(script_path, run_dir, args.run_id)
    sys.stdout.write(str({"run_id": metadata["run_id"], "status": metadata["status"]}))
    sys.stdout.flush()
    return 0 if metadata["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
