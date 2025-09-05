from pathlib import Path

from antares.study.version.model.study_version import StudyVersion

from .upgrade_method import UpgradeMethod
from ..model.general_data import GeneralData, GENERAL_DATA_PATH

import numpy as np

def upgrade_thematic_trimming(data: GeneralData) -> None:
    def _get_thermal_variables_to_remove() -> set[str]:
        groups = {
            "nuclear",
            "lignite",
            "coal",
            "battery",
            "gas",
            "oil",
            "mix. fuel",
            "misc. dtg",
            "misc. dtg 2",
            "misc. dtg 3",
            "misc. dtg 4",
        }
        return groups

    def _get_renewable_variables_to_remove() -> set[str]:
        groups = {
            "wind offshore",
            "wind onshore",
            "solar concrt.",
            "solar pv",
            "solar rooft",
            "renw. 1",
            "renw. 2",
            "renw. 3",
            "renw. 4",
        }
        return groups

    variables_selection = data["variables selection"]
    var_thermal_to_remove = _get_thermal_variables_to_remove()
    var_renewable_to_remove = _get_renewable_variables_to_remove()
    var_to_remove = var_thermal_to_remove.union(var_renewable_to_remove)

    d: dict[str, list[str]] = {}
    for sign in ["+", "-"]:
        select_var_key = f"select_var {sign}"
        original_vars = variables_selection.get(select_var_key, [])
        filtered_vars = [var for var in original_vars if var.lower() not in var_to_remove]
        d[select_var_key] = filtered_vars

    # Update "select_var -"
    select_var_minus = "select_var -"
    variables_selection[select_var_minus] = d[select_var_minus]

    # Process "+" further
    select_var_plus = "select_var +"
    original_plus_vars = variables_selection.get(select_var_plus, [])

    append_thermal = any(var.lower() in var_thermal_to_remove for var in original_plus_vars)
    append_renewable = any(var.lower() in var_renewable_to_remove for var in original_plus_vars)

    if append_thermal:
        d[select_var_plus].append("DISPATCH. GEN.")
    if append_renewable:
        d[select_var_plus].append("RENEWABLE GEN.")

    variables_selection[select_var_plus] = d[select_var_plus]


class UpgradeTo0903(UpgradeMethod):
    """
    This class upgrades the study from version 9.2 to version 9.3.
    """

    old = StudyVersion(9, 2)
    new = StudyVersion(9, 3)
    files = [GENERAL_DATA_PATH]

    @staticmethod
    def _upgrade_general_data(study_dir: Path) -> None:
        data = GeneralData.from_ini_file(study_dir)
        general = data["general"]
        general.pop("refreshtimeseries", None)
        general.pop("refreshintervalload", None)
        general.pop("refreshintervalhydro", None)
        general.pop("refreshintervalwind", None)
        general.pop("refreshintervalthermal", None)
        general.pop("refreshintervalsolar", None)

        data["other preferences"]["accurate-shave-peaks-include-short-term-storage"] = False
        data["adequacy patch"]["redispatch"] = False

        data["compatibility"]["hydro-rule-curves"] = "single"

        if "variables selection" in data:
            upgrade_thematic_trimming(data)

        data.to_ini_file(study_dir)

    @staticmethod

    def _upgrade_hydro(study_dir: Path) -> None:
        hydro_dir = study_dir / "input" / "hydro"

        matrices_to_create = [
            "maxDailyReservoirLevels.txt",
            "minDailyReservoirLevels.txt",
            "avgDailyReservoirLevels.txt",
        ]

        series_path = hydro_dir / "series"

        if not Path(series_path).is_dir():
            return
        
        for area in series_path.iterdir():
            area_dir = hydro_dir / area
            for matrix in matrices_to_create:
                match matrix:
                    case "maxDailyReservoirLevels.txt":
                        (area_dir / matrix).touch()
                        np.savetxt(
                        area_dir / matrix, 
                        np.full((365, 1), 1), 
                        fmt="%.1f"
                        )
                    case "minDailyReservoirLevels.txt":
                        (area_dir / matrix).touch()
                        np.savetxt(
                        area_dir / matrix, 
                        np.full((365, 1), 0), 
                        fmt="%.1f"
                        )
                    case "avgDailyReservoirLevels.txt":
                        (area_dir / matrix).touch()    
                        np.savetxt(
                            area_dir / matrix,
                            np.full((365, 1), 0.5),
                            fmt="%.1f"
                        )
                    case _:
                        (area_dir / matrix).touch()
                
        


    @classmethod
    def upgrade(cls, study_dir: Path) -> None:
        """
        Upgrades the study to version 9.3.

        Args:
            study_dir: The study directory.
        """
        
        cls._upgrade_general_data(study_dir)
        cls._upgrade_hydro(study_dir)