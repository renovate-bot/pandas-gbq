# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""

import pathlib

import synthtool as s
from synthtool import gcp
from synthtool.languages import python

REPO_ROOT = pathlib.Path(__file__).parent.absolute()

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------

extras_by_python = {
    # Use a middle version of Python to test when no extras are installed.
    "3.9": []
}
extras = ["tqdm", "geopandas"]
templated_files = common.py_library(
    default_python_version="3.10",
    unit_test_python_versions=["3.9", "3.10", "3.11", "3.12", "3.13"],
    system_test_python_versions=["3.9", "3.10", "3.11", "3.12", "3.13"],
    cov_level=96,
    unit_test_external_dependencies=["freezegun"],
    unit_test_extras=extras,
    unit_test_extras_by_python=extras_by_python,
    system_test_extras=extras,
    intersphinx_dependencies={
        "pandas": "https://pandas.pydata.org/pandas-docs/stable/",
        "pydata-google-auth": "https://pydata-google-auth.readthedocs.io/en/latest/",
    },
)
s.move(
    templated_files,
    excludes=[
        # pandas-gbq was originally licensed BSD-3-Clause License
        "LICENSE",
        # Multi-processing note isn't relevant, as pandas_gbq is responsible for
        # creating clients, not the end user.
        "docs/multiprocessing.rst",
        "noxfile.py",
        "README.rst",
        ".github/workflows/docs.yml", # to avoid overwriting python version
        ".github/workflows/lint.yml", # to avoid overwriting python version
        ".github/sync-repo-settings.yaml",
        # exclude this file as we have an alternate prerelease.cfg
        ".kokoro/presubmit/prerelease-deps.cfg",
        ".kokoro/presubmit/presubmit.cfg",
        "renovate.json", # to avoid overwriting the ignorePaths list additions:
                         # ".github/workflows/docs.yml AND lint.yml" specifically
                         # the version of python referenced in each of those files.
                         # Currently renovate bot wants to change 3.10 to 3.13.
    ],
)

# ----------------------------------------------------------------------------
# Fixup files
# ----------------------------------------------------------------------------

s.replace(
    [".github/header-checker-lint.yml"],
    '"Google LLC"',
    '"pandas-gbq Authors"',
)

# ----------------------------------------------------------------------------
# Samples templates
# ----------------------------------------------------------------------------

python.py_samples(skip_readmes=True)

# ----------------------------------------------------------------------------
# Final cleanup
# ----------------------------------------------------------------------------

s.shell.run(["nox", "-s", "format"], hide_output=False)
for noxfile in REPO_ROOT.glob("samples/**/noxfile.py"):
    s.shell.run(["nox", "-s", "format"], cwd=noxfile.parent, hide_output=False)
