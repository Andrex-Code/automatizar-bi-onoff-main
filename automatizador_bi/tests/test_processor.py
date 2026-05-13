from pathlib import Path

import pandas as pd
import pytest

from processor import MissingColumnError, process_file


def test_process_file_generates_expected_sheets(tmp_path: Path) -> None:
    input_path = tmp_path / "entrada.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "TypeRes": ["Documento POS", "Resolucion FE"],
            "idPartner": ["c5011", "C5370"],
            "idDpnDianAuthorization": ["12345678901234567890", "999900001111"],
            "idDpnPrefix": ["AB", "XY"],
            "idroute": ["U1", "U2"],
            "idDpnEndConsecutive": [100, 200],
            "idDpnCurrentConsecutive": [20, 150],
            "Diferencia": [80, 50],
            "result": ["Sin novedad", "Vencimiento en 5 dias"],
        }
    )
    df.to_csv(input_path, sep=";", index=False)

    summary = process_file(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert summary.output_path.exists()
    assert summary.log_path.exists()
    assert summary.rows_read == 2
    assert summary.rows_output == 2
    assert summary.alerts_count == 1

    result_df = pd.read_excel(summary.output_path, sheet_name="RESOLUCIONES FE", dtype=str)
    alert_df = pd.read_excel(summary.output_path, sheet_name="ALERTA", dtype=str)

    assert list(result_df.columns) == [
        "PLATAFORMA",
        "AUTORIZACION",
        "PREFIJO",
        "UNIDAD",
        "TOTAL",
        "CONSUMO",
        "DISPONIBLE",
        "TIPO DOC",
        "NOTIFICACION",
    ]

    assert list(alert_df.columns) == [
        "PLATAFORMA",
        "AUTORIZACION",
        "PREFIJO",
        "UNIDAD",
        "TOTAL",
        "CONSUMO",
        "DISPONIBLE",
        "TIPO DOC",
        "ALERTA",
    ]

    assert result_df.loc[0, "PLATAFORMA"] == "5011"
    assert result_df.loc[1, "PLATAFORMA"] == "5370"
    assert result_df.loc[0, "TIPO DOC"] == "RESOLUCION DIAN"
    assert result_df.loc[1, "TIPO DOC"] == "RESOLUCION POS"
    assert len(alert_df) == 1
    assert "Vencimiento" in alert_df.loc[0, "ALERTA"]


def test_process_file_raises_when_required_column_missing(tmp_path: Path) -> None:
    input_path = tmp_path / "entrada_faltante.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "TypeRes": ["Documento POS"],
            "idPartner": ["c5011"],
            "idDpnPrefix": ["AB"],
            "idroute": ["U1"],
            "idDpnEndConsecutive": [100],
            "idDpnCurrentConsecutive": [20],
            "Diferencia": [80],
            "result": ["Sin novedad"],
        }
    )
    df.to_csv(input_path, index=False)

    with pytest.raises(MissingColumnError) as exc:
        process_file(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)

    assert "AUTORIZACION" in str(exc.value)


def test_process_file_normalizes_prefix_and_preserves_large_numbers(tmp_path: Path) -> None:
    input_path = tmp_path / "entrada_idpp.csv"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"

    df = pd.DataFrame(
        {
            "TypeRes": ["Resolucion FE", "Resolucion FE"],
            "idPartner": ["c5407", "c5228"],
            "idppDianAuthorization": ["5407", "5228"],
            "idppPrefix": ["5407-", "00"],
            "idroute": ["1.0", "1"],
            "idppEndConsecutive": ["100000", "10000000000000000"],
            "idppCurrentConsecutive": ["21870", "18071"],
            "Diferencia": ["78130", "9999999999981929"],
            "result": [
                "VIGENTE Quedan mas de 100 Consecutivos",
                "VIGENTE Quedan mas de 100 Consecutivos",
            ],
        }
    )
    df.to_csv(input_path, index=False)

    summary = process_file(input_path=input_path, output_dir=output_dir, logs_dir=logs_dir)
    result_df = pd.read_excel(summary.output_path, sheet_name="RESOLUCIONES FE", dtype=str)

    assert result_df.loc[0, "PREFIJO"] == "-5407"
    assert result_df.loc[1, "PREFIJO"] == "0"
    assert result_df.loc[0, "UNIDAD"] == "1"
    assert result_df.loc[1, "TOTAL"] == "10000000000000000"
    assert result_df.loc[1, "DISPONIBLE"] == "10000000000000000"
