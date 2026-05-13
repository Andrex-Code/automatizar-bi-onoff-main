from pathlib import Path

import pandas as pd
import pytest

from processor import MissingColumnError, ProcessingError, process_file_cartera


def _build_facturacion_dataframe(
    platform_col: str = "PLATAFORMA",
    payment_col: str = "ESTADO_DE_PAGO",
    platform_values: list[str] | None = None,
    payment_values: list[str] | None = None,
) -> pd.DataFrame:
    columns = [f"COL_{index:02d}" for index in range(1, 32)]
    columns[1] = platform_col
    columns[2] = payment_col
    columns[24] = "COLUMN_Y_REMOVE"
    columns[29] = "COLUMN_AD_REMOVE"

    rows_count = 4
    data = {column: [f"{column}_{row}" for row in range(rows_count)] for column in columns}

    default_platforms = ["70355.0", " 80120 ", "009901", "C70500"]
    default_payments = ["PENDIENTE", "pendiente ", "PENDIENTE-EXCEPCION", "PAGADO"]
    data[platform_col] = platform_values if platform_values is not None else default_platforms
    data[payment_col] = payment_values if payment_values is not None else default_payments

    return pd.DataFrame(data)


def test_process_file_cartera_generates_expected_sheets_and_filters_pending(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera.xlsx"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = _build_facturacion_dataframe(platform_col="TC", payment_col="ESTADO PAGO")
    with pd.ExcelWriter(input_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="FACTURACION", index=False)

    summary = process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert summary.output_path.exists()
    assert summary.log_path.exists()
    assert summary.extra_metrics is not None
    assert summary.extra_metrics["cartera_rows"] == 4
    assert summary.extra_metrics["pending_rows"] == 2

    cartera_df = pd.read_excel(summary.output_path, sheet_name="CARTERA", dtype=str)
    pending_df = pd.read_excel(summary.output_path, sheet_name="PAGO PENDIENTE", dtype=str)

    assert "COLUMN_Y_REMOVE" not in cartera_df.columns
    assert "COLUMN_AD_REMOVE" not in cartera_df.columns
    assert pending_df.columns.tolist() == ["PLATAFORMA", "ESTADO_DE_PAGO"]
    assert pending_df["PLATAFORMA"].tolist() == ["70355", "80120"]
    assert pending_df["ESTADO_DE_PAGO"].tolist() == ["PENDIENTE", "PENDIENTE"]


def test_process_file_cartera_supports_facturacion_sheet_equivalent_name(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera_facturacion.xlsx"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = _build_facturacion_dataframe()
    with pd.ExcelWriter(input_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Facturacion", index=False)

    summary = process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)
    assert summary.output_path.exists()


def test_process_file_cartera_supports_csv_input(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = _build_facturacion_dataframe()
    df.to_csv(input_path, sep=";", index=False)

    summary = process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)
    assert summary.output_path.exists()
    pending_df = pd.read_excel(summary.output_path, sheet_name="PAGO PENDIENTE", dtype=str)
    assert len(pending_df) == 2


def test_process_file_cartera_works_with_less_than_31_columns(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera_short.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "PLATAFORMA": ["70355", "80120"],
            "ESTADO_DE_PAGO": ["PENDIENTE", "PAGADO"],
            "OTRA": ["x", "y"],
        }
    )
    df.to_csv(input_path, sep=",", index=False)

    summary = process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)
    assert summary.output_path.exists()
    assert summary.extra_metrics is not None
    assert summary.extra_metrics["pending_rows"] == 1


def test_process_file_cartera_raises_when_facturacion_sheet_missing(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera_no_sheet.xlsx"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = _build_facturacion_dataframe()
    with pd.ExcelWriter(input_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="OTRA_HOJA", index=False)

    with pytest.raises(ProcessingError) as exc:
        process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert "No se encontro la hoja FACTURACION" in str(exc.value)


def test_process_file_cartera_raises_when_platform_column_missing(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera_no_platform.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = _build_facturacion_dataframe(platform_col="OTRA_COLUMNA")
    df.to_csv(input_path, sep=";", index=False)

    with pytest.raises(MissingColumnError) as exc:
        process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert "PLATAFORMA" in str(exc.value)


def test_process_file_cartera_raises_when_estado_column_missing(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera_no_estado.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = _build_facturacion_dataframe(payment_col="ESTADO_X")
    df.to_csv(input_path, sep=";", index=False)

    with pytest.raises(MissingColumnError) as exc:
        process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert "ESTADO_DE_PAGO" in str(exc.value)


def test_process_file_cartera_generates_empty_pending_when_no_pending(tmp_path: Path) -> None:
    input_path = tmp_path / "cartera_no_pending.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = _build_facturacion_dataframe(payment_values=["PAGADO", "VENCIDO", "EN COBRO", "ANULADO"])
    df.to_csv(input_path, sep=";", index=False)

    summary = process_file_cartera(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)
    assert summary.extra_metrics is not None
    assert summary.extra_metrics["pending_rows"] == 0

    pending_df = pd.read_excel(summary.output_path, sheet_name="PAGO PENDIENTE", dtype=str)
    assert pending_df.columns.tolist() == ["PLATAFORMA", "ESTADO_DE_PAGO"]
    assert len(pending_df) == 0
