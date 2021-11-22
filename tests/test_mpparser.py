#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD.
# See https://nomad-lab.eu for further info.
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
#

import pytest

from nomad.datamodel import EntryArchive
from mpparser.mp_parser import MPParser


def approx(value, abs=0, rel=1e-6):
    return pytest.approx(value, abs=abs, rel=rel)


@pytest.fixture(scope='module')
def parser():
    return MPParser()


def test_all(parser):
    archive = EntryArchive()
    parser.parse('tests/data/mp-149/mp-149_materials.json', archive, None)

    run = archive.run[0]
    assert run.program.name == 'MaterialsProject'

    sec_system = run.system[0]
    assert sec_system.atoms.labels == ['Si', 'Si']
    assert sec_system.atoms.lattice_vectors[1][2].magnitude == approx(2.734364e-10)
    assert sec_system.atoms.positions[0][0].magnitude == approx(1.367182e-10)
    assert sec_system.x_mp_composition_reduced[0].x_mp_value == approx(1.0)
    assert sec_system.x_mp_symmetry[0].x_mp_symprec == approx(0.1)
    assert sec_system.x_mp_elements[0] == 'Si'
    assert sec_system.x_mp_volume == approx(40.88829284866483)
    assert sec_system.x_mp_formula_anonymous == 'A'

    sec_method = run.method[0]
    assert sec_method.dft.xc_functional.exchange[0].name == 'GGA_X_PBE'
    assert sec_method.basis_set[0].type == 'plane waves'
    assert sec_method.basis_set[0].cell_dependent[0].planewave_cutoff.magnitude == approx(1.0830714e-16)

    assert len(archive.workflow) == 4
    for workflow in archive.workflow:
        if workflow.type == 'elastic':
            elastic = workflow.elastic
            assert elastic.energy_stress_calculator == 'VASP'
            assert elastic.elastic_constants_matrix_second_order[2][1].magnitude == approx(5.3e+10)
            assert elastic.compliance_matrix_second_order[1][0].magnitude == approx(-2.3e-09)
            assert elastic.poisson_ratio_hill == approx(0.20424545172250694)
            assert elastic.bulk_modulus_voigt.magnitude == approx(8.30112837e+10)
        elif workflow.type == 'equation_of_state':
            eos = workflow.equation_of_state
            assert eos.energies[5].magnitude == approx(-8.33261753e-19)
            assert eos.volumes[-4].magnitude == approx(2.43493103e-29)
            assert len(eos.eos_fit) == 8
            for fit in eos.eos_fit:
                if fit.function_name == 'mie_gruneisen':
                    assert fit.fitted_energies[10].magnitude == approx(-8.62595192e-19)
                elif fit.function_name == 'vinet':
                    assert fit.bulk_modulus_derivative == approx(4.986513157963165)
                elif fit.function_name == 'birch_euler':
                    assert fit.equilibrium_energy.magnitude == approx(-8.69065241e-19)
                elif fit.function_name == 'murnaghan':
                    assert fit.equilibrium_volume.magnitude == approx(2.04781109e-29)
                elif fit.function_name == 'pack_evans_james':
                    assert fit.bulk_modulus.magnitude == approx(8.67365485e+10)
        elif workflow.type == 'phonon':
            segment = run.calculation[-1].band_structure_phonon[0].segment
            assert len(segment) == 10
            assert segment[2].energies[0][7][3].magnitude == approx(7.33184304e-21)
            assert segment[5].kpoints[9][1] == approx(0.32692307692)
            assert segment[9].endpoints_labels == ['U', 'X']
            dos = run.calculation[-1].dos_phonon[0]
            assert dos.energies[20].magnitude == approx(3.49331979e-22)
            assert dos.total[0].value[35].magnitude == approx(1.27718386e+19)
            phonon = workflow.phonon
            assert phonon.with_non_analytic_correction
        elif workflow.type == 'thermodynamics':
            thermo = workflow.thermodynamics
            assert thermo.stability.formation_energy.magnitude == approx(0)
            assert thermo.stability.is_stable
