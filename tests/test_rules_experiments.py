from __future__ import annotations

import nbformat

from rrdoctor.config import DEFAULT_CONFIG
from rrdoctor.scanner import Scanner


def test_root_train_py_counts_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_root_main_variant_counts_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "main_finetune.py").write_text("print('fine-tune')\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_readme_train_command_counts_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRun `python train.py config/default.py` to reproduce the main run.\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_readme_main_variant_command_counts_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRun `python main_finetune.py --eval --data_path ${IMAGENET_DIR}`.\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_workflow_files_count_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "Snakefile").write_text(
        "rule all:\n    input: 'results/out.txt'\n", encoding="utf-8"
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_demo_notebook_counts_as_experiment_entrypoint(tmp_path) -> None:
    notebook_path = tmp_path / "graphcast_demo.ipynb"
    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("print('run demo')")])
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_tools_train_py_counts_as_experiment_entrypoint(tmp_path) -> None:
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "train.py").write_text("print('train')\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_package_train_py_counts_as_experiment_entrypoint(tmp_path) -> None:
    package = tmp_path / "demo_pkg"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "train.py").write_text("print('train')\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_readme_tools_train_command_counts_as_experiment_entrypoint(tmp_path) -> None:
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "train.py").write_text("print('train')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRun `python tools/train.py configs/default.py` to train the model.\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_documented_scripts_python_command_counts_as_experiment_entrypoint(tmp_path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "amg.py").write_text("print('generate masks')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\n```bash\npython scripts/amg.py --input image.jpg --output masks/\n```\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_documented_pyproject_console_script_counts_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\n\n[project.scripts]\ndemo-transcribe = 'demo.cli:main'\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n\n```bash\ndemo-transcribe audio.wav --model tiny\n```\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_documented_python_module_command_counts_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRun `python -m demo.train --config configs/default.yaml` to reproduce.\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_documented_python3_package_script_counts_as_experiment_entrypoint(tmp_path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n\n"
        "```bash\n"
        "python3 ${PROJECT_DIR}/demo_pkg/train.py --config=configs/default.gin\n"
        "```\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert not report.findings


def test_pyproject_console_script_prose_only_does_not_count(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\n\n[project.scripts]\ndemo-transcribe = 'demo.cli:main'\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n\nThe demo-transcribe command exists after installation.\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert len(report.findings) == 1


def test_pyproject_console_script_name_only_inline_code_does_not_count(tmp_path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'demo'\n\n[project.scripts]\ndemo-transcribe = 'demo.cli:main'\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n\nIf you use `demo-transcribe` in your work, please cite us.\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD050"}).scan(tmp_path)

    assert len(report.findings) == 1


def test_unseeded_numpy_randomness_flagged(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "import numpy as np\n\ndef train():\n    return np.random.randn(10)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.rule_id == "RRD052"
    assert finding.file == "train.py"
    assert "no deterministic seed" in finding.message


def test_seeded_numpy_randomness_passes(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "import random\n"
        "import numpy as np\n"
        "\n"
        "random.seed(7)\n"
        "np.random.seed(7)\n"
        "sample = np.random.randn(10)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert not report.findings


def test_random_seed_keyword_application_passes(tmp_path) -> None:
    (tmp_path / "run_model.py").write_text(
        "import random\n"
        "\n"
        "random_seed = FLAGS.random_seed\n"
        "if random_seed is None:\n"
        "    random_seed = random.randrange(1000)\n"
        "model_runner.predict(features, random_seed=random_seed)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert not report.findings


def test_local_random_generator_with_seed_passes(tmp_path) -> None:
    (tmp_path / "preprocess.py").write_text(
        "import random\n\nrng = random.Random(FLAGS.random_seed)\nrng.shuffle(rows)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert not report.findings


def test_torch_parameter_initialization_does_not_count_as_unseeded_experiment(
    tmp_path,
) -> None:
    (tmp_path / "model.py").write_text(
        "import torch\n"
        "from torch import nn\n"
        "\n"
        "class Model(nn.Module):\n"
        "    def __init__(self):\n"
        "        super().__init__()\n"
        "        self.positional_embedding = nn.Parameter(torch.randn(10, 32))\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert not report.findings


def test_torch_randomness_in_training_code_still_flagged(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "import torch\n\nbatch = torch.randn(10, 32)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert len(report.findings) == 1


def test_randomness_in_test_file_does_not_flag_unseeded_experiment(tmp_path) -> None:
    package = tmp_path / "demo"
    package.mkdir()
    (package / "protein_test.py").write_text(
        "import numpy as np\n\nsample = np.random.random([10, 3])\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert not report.findings


def test_sklearn_randomness_without_random_state_flagged(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "from sklearn.model_selection import train_test_split\n"
        "\n"
        "train_test_split(X, y, test_size=0.2)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert len(report.findings) == 1
    assert "train_test_split" in report.findings[0].evidence[0].value


def test_declared_seed_option_without_application_flagged(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "import argparse\n"
        "import random\n"
        "\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--seed', type=int, default=13)\n"
        "random.shuffle(rows)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert "declared" in finding.message
    assert len(finding.evidence) == 2


def test_notebook_randomness_without_seed_flagged(tmp_path) -> None:
    notebook_path = tmp_path / "analysis.ipynb"
    notebook = nbformat.v4.new_notebook(
        cells=[nbformat.v4.new_code_cell("import random\nrandom.random()")]
    )
    nbformat.write(notebook, notebook_path)

    report = Scanner(DEFAULT_CONFIG, include={"RRD052"}).scan(tmp_path)

    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.file == "analysis.ipynb"
    assert finding.line == 1


def test_cuda_without_fallback_flagged(tmp_path) -> None:
    (tmp_path / "train.py").write_text("model = model.cuda()\n", encoding="utf-8")

    report = Scanner(DEFAULT_CONFIG, include={"RRD054"}).scan(tmp_path)

    assert len(report.findings) == 1
    assert report.findings[0].rule_id == "RRD054"


def test_cuda_with_is_available_guard_passes(tmp_path) -> None:
    (tmp_path / "train.py").write_text(
        "import torch\n"
        "device = 'cuda' if torch.cuda.is_available() else 'cpu'\n"
        "model = model.to(device)\n",
        encoding="utf-8",
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD054"}).scan(tmp_path)

    assert not report.findings


def test_cuda_with_documented_requirement_passes(tmp_path) -> None:
    (tmp_path / "train.py").write_text("model = model.cuda()\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Demo\n\nRequires an NVIDIA GPU with CUDA 12.\n", encoding="utf-8"
    )

    report = Scanner(DEFAULT_CONFIG, include={"RRD054"}).scan(tmp_path)

    assert not report.findings
