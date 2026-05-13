from pathlib import Path

import pandas as pd
import pytest

from processor import MissingColumnError, process_file_cuenta_fe_sin_emitir


def test_process_file_cuenta_fe_generates_expected_sheet(tmp_path: Path) -> None:
    input_path = tmp_path / "cuenta_fe.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "Plataforma": ["70355.0", "80120"],
            "Unidad": ["U1", "U2"],
            "id_Venta": ["1.23E+10", "990001"],
            "Consecutivo_FE": ["45001", "3.456E+06"],
            "Fecha_Venta": ["2026-05-12 15:00:00.123", "2026-05-12 16:00:00.456"],
            "Fecha_Fin": ["", ""],
            "Cod_error": ["-1", "500"],
            "Error_details": ["Sin emitir; texto adicional", "Pendiente validacion"],
        }
    )
    df.to_csv(input_path, sep=";", index=False)

    summary = process_file_cuenta_fe_sin_emitir(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert summary.output_path.exists()
    assert summary.log_path.exists()
    assert summary.rows_read == 2
    assert summary.rows_output == 2

    result_df = pd.read_excel(summary.output_path, sheet_name="CUENTA F.E SIN EMITIR", dtype=str)

    assert list(result_df.columns) == [
        "PLATAFORMA",
        "UNIDAD",
        "ID_VENTA",
        "CONSECUTIVO_FE",
        "FECHA_VENTA",
        "COD_ERROR",
        "DETALLE DEL ERROR",
        "COD_ERROR_TEXTO",
    ]
    assert result_df.loc[0, "PLATAFORMA"] == "70355"
    assert result_df.loc[0, "ID_VENTA"] == "12300000000"
    assert result_df.loc[1, "CONSECUTIVO_FE"] == "3456000"
    assert result_df.loc[0, "DETALLE DEL ERROR"] == "Sin emitir"
    assert result_df["COD_ERROR"].tolist() == result_df["COD_ERROR_TEXTO"].tolist()


def test_process_file_cuenta_fe_raises_when_required_column_missing(tmp_path: Path) -> None:
    input_path = tmp_path / "cuenta_fe_faltante.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "Plataforma": ["70355"],
            "Unidad": ["U1"],
            "id_Venta": ["1000"],
            "Consecutivo_FE": ["2000"],
            "Fecha_Venta": ["2026-05-12"],
            "Error_details": ["Sin emitir"],
        }
    )
    df.to_csv(input_path, sep=",", index=False)

    with pytest.raises(MissingColumnError) as exc:
        process_file_cuenta_fe_sin_emitir(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert "COD_ERROR" in str(exc.value)
