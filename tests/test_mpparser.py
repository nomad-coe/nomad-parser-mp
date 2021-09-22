#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for
#
# Licensed under the Apache License, Version 2.0 (the "Lice
# you may not use this file except in compliance with the L
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing
# distributed under the License is distributed on an "AS IS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expr
# See the License for the specific language governing permi
# limitations under the License.
#

import pytest
import numpy as np

from nomad.datamodel import EntryArchive
from ..mpparser.mp_parser import MPParser


def approx(value, abs=0, rel=1e-6):
    return pytest.approx(value, abs=abs, rel=rel)


@pytest.fixture(scope='module')
def parser():
    return MPParser()


def test_all(parser):
    archive = EntryArchive()
    parser.parse('tests/data/mp-149/mp-149_materials.json', archive, None)

    sec_system = archive.run[0].system[0]
    assert sec_system.atoms.labels == ['Si', 'Si']