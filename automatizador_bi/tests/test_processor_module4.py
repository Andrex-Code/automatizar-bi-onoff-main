from pathlib import Path

import pandas as pd
import pytest

from processor import MissingColumnError, ProcessingError, process_file_plataformas_error_fe


def test_process_file_plataformas_error_fe_generates_expected_sheet(tmp_path: Path) -> None:
    cuenta_input = tmp_path / "cuenta_fe.csv"
    total_input = tmp_path / "total_plataformas.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    cuenta_df = pd.DataFrame(
        {
            "Plataforma": [" c70355 ", "80120", "70355.0", "C009901", "", None],
            "Unidad": ["U1", "U2", "U3", "U4", "U5", "U6"],
        }
    )
    total_df = pd.DataFrame(
        {
            "TC": ["70355", " 80120 ", "009901", "70000", "C70355"],
        }
    )
    cuenta_df.to_csv(cuenta_input, sep=";", index=False)
    total_df.to_csv(total_input, sep=";", index=False)

    summary = process_file_plataformas_error_fe(
        cuenta_input_path=cuenta_input,
        total_input_path=total_input,
        output_dir=output_dir,
        logs_dir=logs_dir,
        source_origin="Tomado automaticamente del modulo 2",
    )

    assert summary.output_path.exists()
    assert summary.log_path.exists()
    assert summary.secondary_input_path == total_input
    assert summary.extra_metrics is not None
    assert summary.extra_metrics["matched_unique"] == 3

    result_df = pd.read_excel(summary.output_path, sheet_name="PLATAFORMAS ERROR F.E", dtype=str)
    assert list(result_df.columns) == ["PLATAFORMAS QUE PRESENTAN ERROR F.E"]
    assert result_df["PLATAFORMAS QUE PRESENTAN ERROR F.E"].tolist() == ["009901", "70355", "80120"]


def test_process_file_plataformas_error_fe_raises_when_cuenta_column_missing(tmp_path: Path) -> None:
    cuenta_input = tmp_path / "cuenta_missing.csv"
    total_input = tmp_path / "total.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    pd.DataFrame({"Unidad": ["U1"]}).to_csv(cuenta_input, sep=";", index=False)
    pd.DataFrame({"TC": ["70355"]}).to_csv(total_input, sep=";", index=False)

    with pytest.raises(MissingColumnError) as exc:
        process_file_plataformas_error_fe(cuenta_input, total_input, output_dir, logs_dir)

    assert "CUENTA F.E SIN EMITIR" in str(exc.value)


def test_process_file_plataformas_error_fe_raises_when_total_column_missing(tmp_path: Path) -> None:
    cuenta_input = tmp_path / "cuenta.csv"
    total_input = tmp_path / "total_missing.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    pd.DataFrame({"Plataforma": ["70355"]}).to_csv(cuenta_input, sep=";", index=False)
    pd.DataFrame({"Unidad": ["U1"]}).to_csv(total_input, sep=";", index=False)

    with pytest.raises(MissingColumnError) as exc:
        process_file_plataformas_error_fe(cuenta_input, total_input, output_dir, logs_dir)

    assert "TOTAL PLATAFORMAS F.E" in str(exc.value)


def test_process_file_plataformas_error_fe_raises_when_no_matches(tmp_path: Path) -> None:
    cuenta_input = tmp_path / "cuenta.csv"
    total_input = tmp_path / "total.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    pd.DataFrame({"Plataforma": ["70355"]}).to_csv(cuenta_input, sep=";", index=False)
    pd.DataFrame({"TC": ["90000"]}).to_csv(total_input, sep=";", index=False)

    with pytest.raises(ProcessingError) as exc:
        process_file_plataformas_error_fe(cuenta_input, total_input, output_dir, logs_dir)

    assert "No se encontraron plataformas con error" in str(exc.value)
