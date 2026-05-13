from pathlib import Path

import pandas as pd
import pytest

from processor import MissingColumnError, process_file_error_fe


def test_process_file_error_fe_generates_expected_sheet(tmp_path: Path) -> None:
    input_path = tmp_path / "error_fe.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "Plataforma": ["70355.0", "80120"],
            "Unidad": ["U1", "U2"],
            "id_Venta": ["1.23E+10", "00990001"],
            "Consecutivo_FE": ["45001", "3.456E+06"],
            "Fecha_Venta": ["2026-05-12 15:00:00.123", "2026-05-12 16:00:00.456"],
            "Cod_error": ["-1", "500"],
            "Error_details": ["Sin emitir", "Pendiente validacion"],
            "COD_ERROR_TEXTO": ["-1", "500"],
        }
    )
    df.to_csv(input_path, sep=";", index=False)

    summary = process_file_error_fe(
        input_path=input_path,
        output_dir=output_dir,
        logs_dir=logs_dir,
        source_origin="Tomado automaticamente del modulo 2",
    )

    assert summary.output_path.exists()
    assert summary.log_path.exists()
    assert summary.rows_read == 2
    assert summary.rows_output == 2

    result_df = pd.read_excel(summary.output_path, sheet_name="ERROR F.E", dtype=str)

    assert list(result_df.columns) == [
        "PLATAFORMA",
        "UNIDAD",
        "ID_VENTA",
        "CONSECUTIVO",
        "FECHA DE VENTA",
        "COD_ERROR",
        "DETALLE DEL ERROR",
    ]
    assert "COD_ERROR_TEXTO" not in result_df.columns
    assert result_df.loc[0, "PLATAFORMA"] == "70355"
    assert result_df.loc[0, "ID_VENTA"] == "12300000000"
    assert result_df.loc[1, "ID_VENTA"] == "00990001"
    assert result_df.loc[1, "CONSECUTIVO"] == "3456000"


def test_process_file_error_fe_raises_when_required_column_missing(tmp_path: Path) -> None:
    input_path = tmp_path / "error_fe_missing.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "Plataforma": ["70355"],
            "Unidad": ["U1"],
            "id_Venta": ["1000"],
            "Fecha_Venta": ["2026-05-12"],
            "Cod_error": ["500"],
            "Error_details": ["Sin emitir"],
        }
    )
    df.to_csv(input_path, sep=",", index=False)

    with pytest.raises(MissingColumnError) as exc:
        process_file_error_fe(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert "CONSECUTIVO_FE" in str(exc.value)
