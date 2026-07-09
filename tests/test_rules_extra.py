from __future__ import annotations

from pathlib import Path

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def _scan(root: Path, rule_id: str):
    return Scanner(DEFAULT_CONFIG, include={rule_id}).scan(root)


def test_agents_guide_rule(tmp_path) -> None:
    missing = _scan(tmp_path, "RRD014")
    assert missing.findings and missing.findings[0].rule_id == "RRD014"

    (tmp_path / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
    present = _scan(tmp_path, "RRD014")
    assert not present.findings


def test_unpinned_dependencies_rule(tmp_path) -> None:
    (tmp_path / "requirements.txt").write_text(
        "numpy\npandas==2.0.0\n# comment\n-r other.txt\nscipy ; python_version > '3.9'\n",
        encoding="utf-8",
    )
    report = _scan(tmp_path, "RRD033")
    assert report.findings
    evidence = report.findings[0].evidence[0].message
    assert "numpy" in evidence
    assert "scipy" in evidence
    assert "pandas" not in evidence


def test_unpinned_dependencies_rule_all_pinned(tmp_path) -> None:
    (tmp_path / "requirements.txt").write_text("numpy==1.26.0\npandas>=2.0\n", encoding="utf-8")
    report = _scan(tmp_path, "RRD033")
    assert not report.findings


def test_readme_dataset_section_satisfies_data_docs_rule(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Datasets\n\n"
        "Download the Shakespeare data with "
        "`python data/shakespeare/prepare.py` before training.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD040")

    assert not report.findings


def test_readme_data_prepare_command_satisfies_data_docs_rule(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "## Quick start\n\n"
        "First download and tokenize the data:\n\n"
        "```sh\n"
        "python data/openwebtext/prepare.py\n"
        "```\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD040")

    assert not report.findings


def test_local_absolute_path_rule_flags_real_user_path(tmp_path) -> None:
    local_path = "/home/" + "alice/private-datasets/demo"
    (tmp_path / "README.md").write_text(
        f"# Demo\n\nSet `DATA_DIR={local_path}` before training.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert report.findings
    assert report.findings[0].rule_id == "RRD043"


def test_local_absolute_path_rule_ignores_placeholder_path(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nWrite outputs to `/home/user/absolute_path_to_the_output_dir`.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_url_path_segments(tmp_path) -> None:
    (tmp_path / "dataset.py").write_text(
        'URL = "https://www.example.edu/bens/home/reproducible_research/data"\n',
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_common_example_users(tmp_path) -> None:
    (tmp_path / "util.py").write_text(
        ">>> split(\"/home/joe/protein.pdb.bz2\")\nhint = '/Users/Me/Desktop/bloch.png'\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_notebook_outputs(tmp_path) -> None:
    (tmp_path / "notebook.ipynb").write_text(
        '{"cells":[{"cell_type":"code","source":"print(1)",'
        '"outputs":[{"text":"/home/alice/project/src/file.py:1: warning"}]}]}',
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_system_install_and_user_placeholders(
    tmp_path,
) -> None:
    (tmp_path / "installation.md").write_text(
        "Copy files from C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.8.\n"
        "Mount cache with -v /home/<YOUR_USER>/.cache/:/home/user/.cache/.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings

    (tmp_path / "installation.md").write_text(
        "Windows paths may be escaped, for example C:\\\\folder1\\\\folder2.\n",
        encoding="utf-8",
    )

    escaped_report = _scan(tmp_path, "RRD043")

    assert not escaped_report.findings


def test_local_absolute_path_rule_ignores_angle_bracket_user_placeholder(tmp_path) -> None:
    path_hint = "C:" + "\\Users\\<user>\\AppData\\Local\\<AppAuthor>\\scipy-data\\Cache"
    (tmp_path / "README.md").write_text(
        f"# Demo\n\nThe default cache path is `{path_hint}`.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_ellipsis_user_placeholder(tmp_path) -> None:
    (tmp_path / "example.py").write_text(
        "lib = ctypes.CDLL('/home/.../testlib.*')  # use absolute path\ndocs = '/home/...'\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_flags_real_windows_path(tmp_path) -> None:
    path_hint = "C:" + "\\Users\\alice\\private-datasets\\demo"
    (tmp_path / "README.md").write_text(
        f"# Demo\n\nSet `DATA_DIR={path_hint}` before training.\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert report.findings
    assert report.findings[0].rule_id == "RRD043"


def test_local_absolute_path_rule_ignores_regex_escapes(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\nfilterwarnings = ["ignore:\\\\n*.*scipy\\\\.sparse"]\n',
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_ci_config_paths(tmp_path) -> None:
    circleci_dir = tmp_path / ".circleci"
    circleci_dir.mkdir()
    (circleci_dir / "config.yml").write_text(
        "jobs:\n"
        "  docs:\n"
        "    environment:\n"
        "      CCACHE_DIR: /home/circleci/.ccache\n"
        "    steps:\n"
        "      - run: cp -R /tmp/build/html/. .\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_devcontainer_paths(tmp_path) -> None:
    devcontainer_dir = tmp_path / ".devcontainer"
    devcontainer_dir.mkdir()
    (devcontainer_dir / "setup.sh").write_text(
        "echo 'envs_dirs:\n  - /home/codespace/micromamba/envs' > /opt/conda/.condarc\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_test_fixtures(tmp_path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_paths.py").write_text(
        "BAD_PATH = '/home/alice/private-datasets/demo'\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_local_absolute_path_rule_ignores_vendored_dependency_paths(tmp_path) -> None:
    vendor_dir = tmp_path / "dependencies" / "tinyexr"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "build-notes.txt").write_text(
        "fixture path: C:\\projects\\tinyexr\\test\\build\\tinyexr.sln\n",
        encoding="utf-8",
    )

    report = _scan(tmp_path, "RRD043")

    assert not report.findings


def test_notebook_checkpoints_rule(tmp_path) -> None:
    checkpoint_dir = tmp_path / "notebooks" / ".ipynb_checkpoints"
    checkpoint_dir.mkdir(parents=True)
    (checkpoint_dir / "demo-checkpoint.ipynb").write_text("{}", encoding="utf-8")

    report = _scan(tmp_path, "RRD065")
    assert report.findings and report.findings[0].rule_id == "RRD065"


def test_precommit_rule(tmp_path) -> None:
    missing = _scan(tmp_path, "RRD082")
    assert missing.findings and missing.findings[0].rule_id == "RRD082"

    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
    present = _scan(tmp_path, "RRD082")
    assert not present.findings


def test_julia_test_directory_and_runner_are_detected(tmp_path) -> None:
    test_dir = tmp_path / "test"
    workflow_dir = tmp_path / ".github" / "workflows"
    test_dir.mkdir()
    workflow_dir.mkdir(parents=True)
    (test_dir / "runtests.jl").write_text("using Test\n@test true\n", encoding="utf-8")
    (tmp_path / "Project.toml").write_text(
        '[extras]\nTest = "8dfed614-e22c-5e08-85e1-65c5234f0b40"\n\n[targets]\ntest = ["Test"]\n',
        encoding="utf-8",
    )
    (workflow_dir / "ci.yml").write_text(
        "name: CI\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: julia-actions/setup-julia@v2\n"
        "      - uses: julia-actions/julia-runtest@v1\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD070", "RRD071", "RRD081"}).scan(tmp_path)

    assert not report.findings


def test_bazel_test_targets_and_ci_script_are_detected(tmp_path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    package = tmp_path / "pkg"
    workflow_dir.mkdir(parents=True)
    package.mkdir()
    (tmp_path / "WORKSPACE").write_text("# bazel workspace\n", encoding="utf-8")
    (package / "BUILD").write_text(
        'py_test(name = "model_test", srcs = ["model_test.py"])\n',
        encoding="utf-8",
    )
    (package / "model_test.py").write_text("def test_model():\n    assert True\n", encoding="utf-8")
    (workflow_dir / "ci.yml").write_text(
        "name: CI\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - run: ./testing/run_github_tests.sh\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD070", "RRD071", "RRD081"}).scan(tmp_path)

    assert not report.findings
