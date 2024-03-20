import re

import antares.study.version.__about__ as about


def test_about() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", about.__version__)
    assert about.__author__ == "RTE, Antares Web Team"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}|unreleased", about.__date__)
    assert about.__credits__ == "© Réseau de Transport de l’Électricité (RTE)"
