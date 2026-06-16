# Pre-commit

[pre-commit](https://pre-commit.com/) is a framework for managing Git hooks that are run before committing a new version of the software. [Git hooks](https://git-scm.com/book/ms/v2/Customizing-Git-Git-Hooks) are a way of integrating into Git by letting Git call a program on specific events like on commits. These hooks can either fix small issues such as formatting or stop the commit when errors are detected that cannot be fixed.

## Installation

Pre-commit can be installed with `pipx` system-wide:

```shell
pipx install pre-commit
```

Then git integration to run it before committing is set up using the following command (in the repository):

```shell
pre-commit install
```

## Configuration

Hooks are configured in [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml). All hooks used are documented below:

### `check-added-large-files`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-added-large-files) checks that no large files (>500kB) are added to the repository. If files of that size are to be added, [git-lfs](https://git-lfs.com/) is to be set up and used.

### `check-json`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-json) checks syntax of json files in the repository.

### `check-symlinks`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-symlinks) checks that all [symlinks](https://en.wikipedia.org/wiki/Symbolic_link) in the repository point to valid files.

### `check-toml`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-toml) checks syntax of all toml files in the repository.

### `check-xml`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#check-xml) checks syntax of all xml files in the repository.

### `detect-private-key`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#detect-private-key) checks that the repository does not contain private keys.

### `end-of-file-fixer`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#end-of-file-fixer) ensures that files end in a newline and only in a newline.

### `fix-byte-order-marker`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#fix-byte-order-marker) removes any UTF-8 [byte order markers](https://en.wikipedia.org/wiki/Byte_order_mark).

### `trailing-whitespace`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#trailing-whitespace) trims trailing whitespace.

### `mixed-line-ending`

[This hook](https://github.com/pre-commit/pre-commit-hooks?tab=readme-ov-file#mixed-line-ending) replaces mixed line endings with the most frequently occurring line ending in the repository.

### `ruff`

[This hook](https://github.com/astral-sh/ruff-pre-commit) runs ruff linting.

### `ruff-format`

[This hook](https://github.com/astral-sh/ruff-pre-commit) runs ruff formatting.

### `mypy`

[This hook](https://pre-commit.com/#new-hooks:~:text=changed%2C%201%20insertion(%2B)-,Creating%20new%20hooks,-%C2%B6) runs mypy through poetry type checking.

### `poetry-check`

[This hook](https://python-poetry.org/docs/pre-commit-hooks/#poetry-check) runs `poetry check` to ensure that the poetry files are not in a broken state.

### `poetry-lock`

[This hook](poetry-lock) runs `poetry lock` to ensure that the poetry lockfile is up to date.
