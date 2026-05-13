from __future__ import annotations

import csv
import logging
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd

MONTH_NAMES_ES = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)


OUTPUT_COLUMNS = [
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

ALERT_COLUMNS = [
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

MODULE2_OUTPUT_COLUMNS = [
    "PLATAFORMA",
    "UNIDAD",
    "ID_VENTA",
    "CONSECUTIVO_FE",
    "FECHA_VENTA",
    "COD_ERROR",
    "DETALLE DEL ERROR",
    "COD_ERROR_TEXTO",
]

MODULE3_OUTPUT_COLUMNS = [
    "PLATAFORMA",
    "UNIDAD",
    "ID_VENTA",
    "CONSECUTIVO",
    "FECHA DE VENTA",
    "COD_ERROR",
    "DETALLE DEL ERROR",
]

MODULE4_SHEET_NAME = "PLATAFORMAS ERROR F.E"
MODULE4_OUTPUT_COLUMN = "PLATAFORMAS QUE PRESENTAN ERROR F.E"
MODULE5_CARTERA_SHEET_NAME = "CARTERA"
MODULE5_PENDING_SHEET_NAME = "PAGO PENDIENTE"
MODULE5_PENDING_COLUMNS = ["PLATAFORMA", "ESTADO_DE_PAGO"]

FIELD_LABELS = {
    "platform": "PLATAFORMA",
    "authorization": "AUTORIZACION",
    "prefix": "PREFIJO",
    "unit": "UNIDAD",
    "total": "TOTAL",
    "consumption": "CONSUMO",
    "available": "DISPONIBLE",
    "type_source": "TIPO DOC",
    "notification": "NOTIFICACION",
}

COLUMN_ALIASES = {
    "platform": ["idPartner", "plataforma", "partner", "id partner", "ID_PARTNER", "TC"],
    "authorization": [
        "idDpnDianAuthorization",
        "idppDianAuthorization",
        "DianAuthorization",
        "autorizacion",
        "resolucion",
        "authorization",
    ],
    "prefix": ["idDpnPrefix", "idppPrefix", "prefijo", "prefix", "id Dpn Prefix"],
    "unit": ["idroute", "unidad", "route", "id route", "ruta"],
    "total": [
        "idDpnEndConsecutive",
        "idppEndConsecutive",
        "total",
        "end consecutive",
        "EndConsecutive",
        "Consecutivo Final",
    ],
    "consumption": [
        "idDpnCurrentConsecutive",
        "idppCurrentConsecutive",
        "consumo",
        "current consecutive",
        "CurrentConsecutive",
        "Consecutivo Actual",
    ],
    "available": ["Diferencia", "disponible", "available", "difference"],
    "type_source": [
        "TypeRes",
        "Type Res",
        "TipoRes",
        "tipo",
        "tipo de registro",
        "tipo documento",
        "documento",
        "type",
    ],
    "notification": ["result", "notificacion", "resultado", "notification", "ALERTA"],
}

MODULE2_FIELD_LABELS = {
    "platform": "PLATAFORMA",
    "unit": "UNIDAD",
    "sale_id": "ID_VENTA",
    "fe_consecutive": "CONSECUTIVO_FE",
    "sale_date": "FECHA_VENTA",
    "error_code": "COD_ERROR",
    "error_details": "DETALLE DEL ERROR",
}

MODULE3_FIELD_LABELS = {
    "platform": "PLATAFORMA",
    "unit": "UNIDAD",
    "sale_id": "ID_VENTA",
    "consecutive": "CONSECUTIVO_FE",
    "sale_date": "FECHA_VENTA",
    "error_code": "COD_ERROR",
    "error_details": "DETALLE DEL ERROR",
}

MODULE4_FIELD_LABELS = {
    "platform": "PLATAFORMA",
}

MODULE2_COLUMN_ALIASES = {
    "platform": ["Plataforma", "idPartner", "partner", "id partner"],
    "unit": ["Unidad", "idroute", "route", "id route"],
    "sale_id": ["id_Venta", "id venta", "idventa", "sale id"],
    "fe_consecutive": ["Consecutivo_FE", "consecutivo fe", "consecutivo", "fe consecutivo"],
    "sale_date": ["Fecha_Venta", "fecha venta", "sale date", "fecha"],
    "error_code": ["Cod_error", "cod error", "coderror", "codigo error", "error code"],
    "error_details": [
        "Error_details",
        "error details",
        "errordetails",
        "detalle error",
        "detalle del error",
    ],
}

MODULE3_COLUMN_ALIASES = {
    "platform": ["Plataforma", "idPartner", "partner", "id partner"],
    "unit": ["Unidad", "idroute", "route", "id route"],
    "sale_id": ["ID_VENTA", "id_Venta", "id venta", "idventa", "sale id"],
    "consecutive": ["CONSECUTIVO_FE", "Consecutivo_FE", "consecutivo fe", "consecutivo"],
    "sale_date": ["FECHA_VENTA", "Fecha_Venta", "fecha venta", "fecha de venta", "sale date"],
    "error_code": ["COD_ERROR", "Cod_error", "cod error", "coderror", "codigo error", "error code"],
    "error_details": [
        "DETALLE DEL ERROR",
        "Error_details",
        "error details",
        "errordetails",
        "detalle error",
        "detalle del error",
    ],
}

MODULE4_CUENTA_COLUMN_ALIASES = {
    "platform": ["PLATAFORMA", "Plataforma", "idPartner", "ID_PARTNER", "id partner"],
}

MODULE4_TOTAL_COLUMN_ALIASES = {
    "platform": ["PLATAFORMA", "Plataforma", "TC", "Tienda", "ID_PARTNER", "idPartner", "id partner"],
}

MODULE5_PLATFORM_ALIASES = [
    "PLATAFORMA",
    "Plataforma",
    "TC",
    "Tienda",
    "idPartner",
    "ID_PARTNER",
    "ID PARTNER",
    "NUMERO PLATAFORMA",
    "NUMERO_DE_PLATAFORMA",
]

MODULE5_PAYMENT_STATUS_ALIASES = [
    "ESTADO_DE_PAGO",
    "ESTADO DE PAGO",
    "Estado de pago",
    "estado_pago",
    "Estado_Pago",
    "ESTADO PAGO",
]


class ProcessingError(Exception):
    """Base exception for user-facing processing errors."""


class MissingColumnError(ProcessingError):
    """Raised when a required column was not found in source data."""


@dataclass
class ProcessSummary:
    input_path: Path
    output_path: Path
    log_path: Path
    rows_read: int
    rows_output: int
    alerts_count: int
    secondary_input_path: Path | None = None
    source_origin: str | None = None
    extra_metrics: dict[str, int] | None = None


StatusCallback = Callable[[str], None]


def process_file(
    input_path: str | Path,
    output_dir: str | Path,
    logs_dir: str | Path,
    status_callback: StatusCallback | None = None,
    source_origin: str | None = None,
) -> ProcessSummary:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    logs_dir = Path(logs_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    dated_output_dir = _build_dated_output_dir(output_dir, now)
    output_path = dated_output_dir / f"1-RESULTADO_BASE_RESOLUCIONES_FE_{timestamp}.xlsx"
    log_path = logs_dir / f"procesamiento_{timestamp}.log"

    logger = _build_logger(log_path)

    try:
        _set_status(status_callback, "Leyendo archivo...")
        logger.info("Inicio de procesamiento")
        if source_origin:
            logger.info("Origen del archivo: %s", source_origin)
        logger.info("Archivo de entrada: %s", input_path)

        source_df = read_input_file(input_path)
        rows_read = len(source_df)
        logger.info("Filas leidas: %s", rows_read)

        _set_status(status_callback, "Transformando datos...")
        transformed_df = transform_dataframe(source_df)

        _set_status(status_callback, "Generando hoja ALERTA...")
        alert_df = build_alert_sheet(transformed_df)

        _set_status(status_callback, "Guardando archivo Excel...")
        write_output_excel(transformed_df, alert_df, output_path)

        logger.info("Filas resultantes: %s", len(transformed_df))
        logger.info("Total alertas: %s", len(alert_df))
        logger.info("Archivo generado: %s", output_path)

        _set_status(status_callback, "Proceso completado")
        return ProcessSummary(
            input_path=input_path,
            output_path=output_path,
            log_path=log_path,
            rows_read=rows_read,
            rows_output=len(transformed_df),
            alerts_count=len(alert_df),
        )
    except ProcessingError as exc:
        logger.exception("Error de validacion: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Error inesperado")
        raise ProcessingError("Ocurrio un error inesperado al procesar el archivo.") from exc
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def process_file_cuenta_fe_sin_emitir(
    input_path: str | Path,
    output_dir: str | Path,
    logs_dir: str | Path,
    status_callback: StatusCallback | None = None,
    source_origin: str | None = None,
) -> ProcessSummary:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    logs_dir = Path(logs_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    dated_output_dir = _build_dated_output_dir(output_dir, now)
    output_path = dated_output_dir / f"2-RESULTADO_CUENTA_FE_SIN_EMITIR_{timestamp}.xlsx"
    log_path = logs_dir / f"procesamiento_cuenta_fe_sin_emitir_{timestamp}.log"

    logger = _build_logger(log_path)

    try:
        _set_status(status_callback, "Leyendo archivo...")
        logger.info("Inicio de procesamiento")
        logger.info("Modulo ejecutado: CUENTA F.E SIN EMITIR")
        if source_origin:
            logger.info("Origen del archivo: %s", source_origin)
        logger.info("Archivo de entrada: %s", input_path)

        source_df = read_input_file(input_path)
        rows_read = len(source_df)
        logger.info("Filas leidas: %s", rows_read)

        _set_status(status_callback, "Transformando datos...")
        transformed_df = transform_cuenta_fe_dataframe(source_df)

        _set_status(status_callback, "Guardando archivo Excel...")
        write_cuenta_fe_output_excel(transformed_df, output_path)

        logger.info("Filas resultantes: %s", len(transformed_df))
        logger.info("Archivo generado: %s", output_path)

        _set_status(status_callback, "Proceso completado")
        return ProcessSummary(
            input_path=input_path,
            output_path=output_path,
            log_path=log_path,
            rows_read=rows_read,
            rows_output=len(transformed_df),
            alerts_count=0,
        )
    except ProcessingError as exc:
        logger.exception("Error de validacion: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Error inesperado")
        raise ProcessingError("Ocurrio un error inesperado al procesar el archivo.") from exc
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def process_file_error_fe(
    input_path: str | Path,
    output_dir: str | Path,
    logs_dir: str | Path,
    status_callback: StatusCallback | None = None,
    source_origin: str | None = None,
) -> ProcessSummary:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    logs_dir = Path(logs_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    dated_output_dir = _build_dated_output_dir(output_dir, now)
    output_path = dated_output_dir / f"3-RESULTADO_ERROR_FE_{timestamp}.xlsx"
    log_path = logs_dir / f"procesamiento_error_fe_{timestamp}.log"

    logger = _build_logger(log_path)

    try:
        _set_status(status_callback, "Leyendo archivo...")
        logger.info("Inicio de procesamiento")
        logger.info("Modulo ejecutado: ERROR F.E")
        if source_origin:
            logger.info("Origen del archivo: %s", source_origin)
        logger.info("Archivo de entrada: %s", input_path)

        source_df = read_input_file(input_path)
        rows_read = len(source_df)
        logger.info("Filas leidas: %s", rows_read)

        _set_status(status_callback, "Transformando datos...")
        column_map = _resolve_module3_required_columns(source_df.columns)
        logger.info("Columnas detectadas: %s", column_map)
        transformed_df = transform_error_fe_dataframe(source_df, column_map=column_map)

        _set_status(status_callback, "Guardando archivo Excel...")
        write_error_fe_output_excel(transformed_df, output_path)

        logger.info("Filas resultantes: %s", len(transformed_df))
        logger.info("Archivo generado: %s", output_path)

        _set_status(status_callback, "Proceso completado")
        return ProcessSummary(
            input_path=input_path,
            output_path=output_path,
            log_path=log_path,
            rows_read=rows_read,
            rows_output=len(transformed_df),
            alerts_count=0,
            source_origin=source_origin,
        )
    except ProcessingError as exc:
        logger.exception("Error de validacion: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Error inesperado")
        raise ProcessingError("Ocurrio un error inesperado al procesar el archivo.") from exc
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def process_file_plataformas_error_fe(
    cuenta_input_path: str | Path,
    total_input_path: str | Path,
    output_dir: str | Path,
    logs_dir: str | Path,
    status_callback: StatusCallback | None = None,
    source_origin: str | None = None,
) -> ProcessSummary:
    cuenta_input_path = Path(cuenta_input_path)
    total_input_path = Path(total_input_path)
    output_dir = Path(output_dir)
    logs_dir = Path(logs_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    dated_output_dir = _build_dated_output_dir(output_dir, now)
    output_path = dated_output_dir / f"4-RESULTADO_PLATAFORMAS_ERROR_FE_{timestamp}.xlsx"
    log_path = logs_dir / f"procesamiento_plataformas_error_fe_{timestamp}.log"

    logger = _build_logger(log_path)

    try:
        _set_status(status_callback, "Leyendo archivo Cuenta F.E sin emitir...")
        logger.info("Inicio de procesamiento")
        logger.info("Modulo ejecutado: PLATAFORMAS QUE PRESENTAN ERROR F.E")
        logger.info("Archivo CUENTA F.E SIN EMITIR: %s", cuenta_input_path)
        if source_origin:
            logger.info("Origen del archivo CUENTA F.E: %s", source_origin)

        cuenta_df = read_input_file(cuenta_input_path)
        rows_cuenta = len(cuenta_df)
        logger.info("Total filas leidas CUENTA F.E SIN EMITIR: %s", rows_cuenta)

        _set_status(status_callback, "Leyendo archivo Total Plataformas F.E...")
        logger.info("Archivo TOTAL PLATAFORMAS F.E: %s", total_input_path)
        total_df = read_input_file(total_input_path)
        rows_total = len(total_df)
        logger.info("Total filas leidas TOTAL PLATAFORMAS F.E: %s", rows_total)

        _set_status(status_callback, "Cruzando plataformas...")
        result_df, metrics = transform_plataformas_error_fe(cuenta_df, total_df)
        logger.info("Columnas detectadas CUENTA F.E: %s", metrics["cuenta_column"])
        logger.info("Columnas detectadas TOTAL PLATAFORMAS F.E: %s", metrics["total_column"])
        logger.info("Total plataformas unicas CUENTA F.E SIN EMITIR: %s", metrics["cuenta_unique"])
        logger.info("Total plataformas unicas TOTAL PLATAFORMAS F.E: %s", metrics["total_unique"])
        logger.info("Total plataformas con error encontradas: %s", metrics["matched_unique"])

        _set_status(status_callback, "Guardando archivo Excel...")
        write_plataformas_error_fe_output_excel(result_df, output_path)
        logger.info("Archivo generado: %s", output_path)

        _set_status(status_callback, "Proceso completado")
        return ProcessSummary(
            input_path=cuenta_input_path,
            secondary_input_path=total_input_path,
            output_path=output_path,
            log_path=log_path,
            rows_read=rows_cuenta + rows_total,
            rows_output=len(result_df),
            alerts_count=0,
            source_origin=source_origin,
            extra_metrics={
                "cuenta_rows": rows_cuenta,
                "cuenta_unique": metrics["cuenta_unique"],
                "total_rows": rows_total,
                "total_unique": metrics["total_unique"],
                "matched_unique": metrics["matched_unique"],
            },
        )
    except ProcessingError as exc:
        logger.exception("Error de validacion: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Error inesperado")
        raise ProcessingError("Ocurrio un error inesperado al procesar el archivo.") from exc
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def process_file_cartera(
    input_path: str | Path,
    output_dir: str | Path,
    logs_dir: str | Path,
    status_callback: StatusCallback | None = None,
    source_origin: str | None = None,
) -> ProcessSummary:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    logs_dir = Path(logs_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    dated_output_dir = _build_dated_output_dir(output_dir, now)
    output_path = dated_output_dir / f"5-RESULTADO_CARTERA_{timestamp}.xlsx"
    log_path = logs_dir / f"procesamiento_cartera_{timestamp}.log"

    logger = _build_logger(log_path)

    try:
        _set_status(status_callback, "Leyendo archivo de Cartera...")
        logger.info("Inicio de procesamiento")
        logger.info("Modulo ejecutado: CARTERA")
        logger.info("Archivo de entrada: %s", input_path)

        source_df, source_sheet = read_cartera_input(input_path)
        rows_read = len(source_df)
        logger.info("Hoja leida: %s", source_sheet)
        logger.info("Total filas leidas: %s", rows_read)

        _set_status(status_callback, "Preparando hoja CARTERA...")
        cartera_df, cartera_meta = transform_cartera_dataframe(source_df)
        logger.info("Columnas originales detectadas: %s", cartera_meta["original_columns"])
        logger.info("Columnas eliminadas: %s", cartera_meta["removed_columns"])
        logger.info("Total registros en CARTERA: %s", len(cartera_df))
        if cartera_meta["warning_less_than_31_columns"]:
            logger.warning("El archivo tiene menos de 31 columnas. Se usaron columnas disponibles.")

        _set_status(status_callback, "Generando hoja PAGO PENDIENTE...")
        pago_pendiente_df, pending_meta = build_pago_pendiente_sheet(cartera_df)
        logger.info("Columna detectada como PLATAFORMA: %s", pending_meta["platform_column"])
        logger.info("Columna detectada como ESTADO_DE_PAGO: %s", pending_meta["payment_status_column"])
        logger.info("Total registros en PAGO PENDIENTE: %s", len(pago_pendiente_df))
        if pending_meta["pending_warning_message"]:
            logger.warning("%s", pending_meta["pending_warning_message"])

        _set_status(status_callback, "Guardando archivo Excel...")
        write_cartera_output_excel(cartera_df, pago_pendiente_df, output_path)
        logger.info("Archivo generado: %s", output_path)

        _set_status(status_callback, "Proceso completado")
        return ProcessSummary(
            input_path=input_path,
            output_path=output_path,
            log_path=log_path,
            rows_read=rows_read,
            rows_output=len(cartera_df),
            alerts_count=len(pago_pendiente_df),
            source_origin=source_origin,
            extra_metrics={
                "cartera_rows": len(cartera_df),
                "pending_rows": len(pago_pendiente_df),
            },
        )
    except ProcessingError as exc:
        logger.exception("Error de validacion: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Error inesperado")
        raise ProcessingError("Ocurrio un error inesperado al procesar el archivo.") from exc
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def read_input_file(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise ProcessingError("No se encontro el archivo seleccionado.")

    suffix = input_path.suffix.lower()

    if suffix in {".csv", ".txt"}:
        df = _read_delimited_file(input_path)
    elif suffix in {".xlsx", ".xlsm"}:
        try:
            excel_file = pd.ExcelFile(input_path, engine="openpyxl")
        except Exception as exc:
            raise ProcessingError("No se pudo leer el archivo Excel seleccionado.") from exc

        df = pd.DataFrame()
        for sheet_name in excel_file.sheet_names:
            candidate = pd.read_excel(input_path, sheet_name=sheet_name, dtype=str, engine="openpyxl")
            if not candidate.empty:
                df = candidate
                break
    else:
        raise ProcessingError("Formato no soportado. Usa CSV, TXT, XLSX o XLSM.")

    if df.empty:
        raise ProcessingError("El archivo no tiene datos para procesar.")

    return df.fillna("")


def transform_dataframe(source_df: pd.DataFrame) -> pd.DataFrame:
    column_map = _resolve_required_columns(source_df.columns)

    result_df = pd.DataFrame(
        {
            "PLATAFORMA": _clean_platform(source_df[column_map["platform"]]),
            "AUTORIZACION": _clean_identifier_column(source_df[column_map["authorization"]], strip_decimal=True),
            "PREFIJO": _clean_prefix_column(source_df[column_map["prefix"]]),
            "UNIDAD": _clean_identifier_column(source_df[column_map["unit"]], strip_decimal=True),
            "TOTAL": _clean_numeric_column(source_df[column_map["total"]]),
            "CONSUMO": _clean_numeric_column(source_df[column_map["consumption"]]),
            "DISPONIBLE": _clean_numeric_column(source_df[column_map["available"]]),
            "TIPO DOC": _map_tipo_doc(source_df[column_map["type_source"]]),
            "NOTIFICACION": _clean_text_column(source_df[column_map["notification"]]),
        }
    )

    result_df = _remove_leading_export_artifact(result_df)
    result_df = _normalize_available_precision_legacy(result_df)

    return result_df[OUTPUT_COLUMNS]


def transform_cuenta_fe_dataframe(source_df: pd.DataFrame) -> pd.DataFrame:
    column_map = _resolve_module2_required_columns(source_df.columns)

    cod_error = _clean_text_column(source_df[column_map["error_code"]])
    result_df = pd.DataFrame(
        {
            "PLATAFORMA": _clean_identifier_column(source_df[column_map["platform"]], strip_decimal=True),
            "UNIDAD": _clean_text_column(source_df[column_map["unit"]]),
            "ID_VENTA": _clean_identifier_column(source_df[column_map["sale_id"]]),
            "CONSECUTIVO_FE": _clean_identifier_column(source_df[column_map["fe_consecutive"]]),
            "FECHA_VENTA": _clean_text_column(source_df[column_map["sale_date"]]),
            "COD_ERROR": cod_error,
            "DETALLE DEL ERROR": _clean_module2_error_details(source_df[column_map["error_details"]]),
            "COD_ERROR_TEXTO": cod_error,
        }
    )
    return result_df[MODULE2_OUTPUT_COLUMNS]


def transform_error_fe_dataframe(
    source_df: pd.DataFrame,
    column_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    resolved_columns = column_map or _resolve_module3_required_columns(source_df.columns)

    result_df = pd.DataFrame(
        {
            "PLATAFORMA": _clean_identifier_column(source_df[resolved_columns["platform"]], strip_decimal=True),
            "UNIDAD": _clean_text_column(source_df[resolved_columns["unit"]]),
            "ID_VENTA": _clean_identifier_column(source_df[resolved_columns["sale_id"]]),
            "CONSECUTIVO": _clean_identifier_column(source_df[resolved_columns["consecutive"]]),
            "FECHA DE VENTA": _clean_text_column(source_df[resolved_columns["sale_date"]]),
            "COD_ERROR": _clean_text_column(source_df[resolved_columns["error_code"]]),
            "DETALLE DEL ERROR": _clean_text_column(source_df[resolved_columns["error_details"]]),
        }
    )
    return result_df[MODULE3_OUTPUT_COLUMNS]


def transform_plataformas_error_fe(
    cuenta_df: pd.DataFrame,
    total_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, str | int]]:
    cuenta_column = _resolve_module4_platform_column(
        cuenta_df.columns,
        aliases=MODULE4_CUENTA_COLUMN_ALIASES["platform"],
        missing_message="No se pudo encontrar la columna PLATAFORMA en CUENTA F.E SIN EMITIR.",
    )
    total_column = _resolve_module4_platform_column(
        total_df.columns,
        aliases=MODULE4_TOTAL_COLUMN_ALIASES["platform"],
        missing_message="No se pudo encontrar la columna PLATAFORMA en TOTAL PLATAFORMAS F.E.",
    )

    cuenta_platforms = _clean_platform_for_match(cuenta_df[cuenta_column]).drop_duplicates()
    total_platforms = _clean_platform_for_match(total_df[total_column]).drop_duplicates()

    if cuenta_platforms.empty:
        raise ProcessingError(
            "No se encontraron plataformas validas en CUENTA F.E SIN EMITIR despues de la limpieza."
        )
    if total_platforms.empty:
        raise ProcessingError(
            "No se encontraron plataformas validas en TOTAL PLATAFORMAS F.E despues de la limpieza."
        )

    matched = total_platforms[total_platforms.isin(set(cuenta_platforms))].drop_duplicates()

    if matched.empty:
        raise ProcessingError(
            "No se encontraron plataformas con error que coincidan entre CUENTA F.E SIN EMITIR y "
            "TOTAL PLATAFORMAS F.E. Revisa que los archivos correspondan al dia correcto."
        )

    sorted_matched = _sort_platform_series(matched)
    result_df = pd.DataFrame({MODULE4_OUTPUT_COLUMN: sorted_matched})
    metrics: dict[str, str | int] = {
        "cuenta_column": cuenta_column,
        "total_column": total_column,
        "cuenta_unique": int(cuenta_platforms.nunique()),
        "total_unique": int(total_platforms.nunique()),
        "matched_unique": int(sorted_matched.nunique()),
    }
    return result_df, metrics


def read_cartera_input(input_path: Path) -> tuple[pd.DataFrame, str]:
    if not input_path.exists():
        raise ProcessingError("No se encontro el archivo seleccionado.")

    suffix = input_path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        source_df = _read_delimited_file(input_path).fillna("")
        if source_df.empty:
            raise ProcessingError("El archivo no tiene datos para procesar.")
        return source_df, "FACTURACION (CSV/TXT)"

    if suffix in {".xlsx", ".xlsm"}:
        try:
            excel_file = pd.ExcelFile(input_path, engine="openpyxl")
        except Exception as exc:
            raise ProcessingError("No se pudo leer el archivo Excel seleccionado.") from exc

        target_sheet = _find_facturacion_sheet(excel_file.sheet_names)
        if not target_sheet:
            raise ProcessingError(
                "No se encontro la hoja FACTURACION. Revisa que el archivo seleccionado sea el archivo de Cartera correcto."
            )

        try:
            source_df = pd.read_excel(input_path, sheet_name=target_sheet, dtype=str, engine="openpyxl")
        except Exception as exc:
            raise ProcessingError("No se pudo leer la hoja FACTURACION del archivo seleccionado.") from exc

        source_df = source_df.fillna("")
        if source_df.empty:
            raise ProcessingError("El archivo no tiene datos para procesar.")
        return source_df, target_sheet

    raise ProcessingError("Formato no soportado. Usa CSV, TXT, XLSX o XLSM.")


def transform_cartera_dataframe(
    source_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, list[str] | bool]]:
    prepared_df = source_df.fillna("").copy()
    non_empty_mask = prepared_df.astype(str).replace(r"^\s*$", "", regex=True).ne("").any(axis=1)
    prepared_df = prepared_df.loc[non_empty_mask].reset_index(drop=True)

    max_columns = min(31, prepared_df.shape[1])
    limited_df = prepared_df.iloc[:, :max_columns].copy()
    original_columns = [str(column) for column in limited_df.columns]

    columns_to_remove = {24, 29}
    keep_indices = [index for index in range(max_columns) if index not in columns_to_remove]
    removed_columns = [original_columns[index] for index in range(max_columns) if index in columns_to_remove]
    cartera_df = limited_df.iloc[:, keep_indices].copy()

    meta: dict[str, list[str] | bool] = {
        "original_columns": original_columns,
        "removed_columns": removed_columns,
        "warning_less_than_31_columns": prepared_df.shape[1] < 31,
    }
    return cartera_df, meta


def build_pago_pendiente_sheet(
    cartera_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, str]]:
    platform_column = _resolve_module5_column(
        cartera_df.columns,
        aliases=MODULE5_PLATFORM_ALIASES,
        missing_message="No se pudo encontrar la columna PLATAFORMA. Revisa que el archivo tenga los encabezados correctos.",
    )
    payment_status_column = _resolve_module5_column(
        cartera_df.columns,
        aliases=MODULE5_PAYMENT_STATUS_ALIASES,
        missing_message=(
            "No se pudo encontrar la columna ESTADO_DE_PAGO. Revisa que el archivo tenga los encabezados correctos."
        ),
    )

    payment_status_normalized = cartera_df[payment_status_column].fillna("").astype(str).map(_normalize_text)
    pending_mask = payment_status_normalized == "PENDIENTE"

    pending_platforms = _clean_platform_for_pending(cartera_df.loc[pending_mask, platform_column])
    pending_platforms = pending_platforms[pending_platforms.str.strip().ne("")]
    pending_df = pd.DataFrame(
        {
            "PLATAFORMA": pending_platforms.values,
            "ESTADO_DE_PAGO": "PENDIENTE",
        }
    )
    pending_df = pending_df[MODULE5_PENDING_COLUMNS]

    warning_message = ""
    if pending_df.empty:
        warning_message = (
            "No se encontraron registros con ESTADO_DE_PAGO igual a PENDIENTE. "
            "Se generara la hoja PAGO PENDIENTE solo con encabezados."
        )

    meta = {
        "platform_column": platform_column,
        "payment_status_column": payment_status_column,
        "pending_warning_message": warning_message,
    }
    return pending_df, meta


def build_alert_sheet(result_df: pd.DataFrame) -> pd.DataFrame:
    mask = result_df["NOTIFICACION"].str.contains("VENCIMIENTO", case=False, na=False)
    alert_df = result_df.loc[mask, OUTPUT_COLUMNS].copy()
    alert_df.rename(columns={"NOTIFICACION": "ALERTA"}, inplace=True)
    return alert_df[ALERT_COLUMNS]


def write_output_excel(result_df: pd.DataFrame, alert_df: pd.DataFrame, output_path: Path) -> None:
    try:
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            result_df.to_excel(writer, sheet_name="RESOLUCIONES FE", index=False)
            alert_df.to_excel(writer, sheet_name="ALERTA", index=False)

            workbook = writer.book
            text_format = workbook.add_format({"num_format": "@"})

            ws_result = writer.sheets["RESOLUCIONES FE"]
            ws_alert = writer.sheets["ALERTA"]

            # Keep key identifiers as text to avoid scientific notation in Excel.
            ws_result.set_column("A:D", 18, text_format)
            ws_result.set_column("H:I", 25, text_format)
            ws_alert.set_column("A:D", 18, text_format)
            ws_alert.set_column("H:I", 25, text_format)
            ws_result.ignore_errors({"number_stored_as_text": "A1:I1048576"})
            ws_alert.ignore_errors({"number_stored_as_text": "A1:I1048576"})
            ws_result.autofilter(0, 0, len(result_df), len(OUTPUT_COLUMNS) - 1)
            ws_alert.autofilter(0, 0, len(alert_df), len(ALERT_COLUMNS) - 1)
    except Exception as exc:
        raise ProcessingError("No se pudo generar el archivo de salida.") from exc


def write_cuenta_fe_output_excel(result_df: pd.DataFrame, output_path: Path) -> None:
    try:
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            result_df.to_excel(writer, sheet_name="CUENTA F.E SIN EMITIR", index=False)

            workbook = writer.book
            text_format = workbook.add_format({"num_format": "@"})
            ws_result = writer.sheets["CUENTA F.E SIN EMITIR"]

            ws_result.set_column("A:H", 24, text_format)
            ws_result.ignore_errors({"number_stored_as_text": "A1:H1048576"})
            ws_result.freeze_panes(1, 0)
            ws_result.autofilter(0, 0, len(result_df), len(MODULE2_OUTPUT_COLUMNS) - 1)
    except Exception as exc:
        raise ProcessingError("No se pudo generar el archivo de salida.") from exc


def write_error_fe_output_excel(result_df: pd.DataFrame, output_path: Path) -> None:
    try:
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            result_df.to_excel(writer, sheet_name="ERROR F.E", index=False)

            workbook = writer.book
            text_format = workbook.add_format({"num_format": "@"})
            ws_result = writer.sheets["ERROR F.E"]

            ws_result.set_column("A:G", 24, text_format)
            ws_result.freeze_panes(1, 0)
            ws_result.autofilter(0, 0, len(result_df), len(MODULE3_OUTPUT_COLUMNS) - 1)
    except Exception as exc:
        raise ProcessingError("No se pudo generar el archivo de salida.") from exc


def write_plataformas_error_fe_output_excel(result_df: pd.DataFrame, output_path: Path) -> None:
    try:
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            result_df.to_excel(writer, sheet_name=MODULE4_SHEET_NAME, index=False)

            workbook = writer.book
            text_format = workbook.add_format({"num_format": "@"})
            ws_result = writer.sheets[MODULE4_SHEET_NAME]

            ws_result.set_column("A:A", 42, text_format)
            ws_result.freeze_panes(1, 0)
            ws_result.autofilter(0, 0, len(result_df), 0)
    except Exception as exc:
        raise ProcessingError("No se pudo generar el archivo de salida.") from exc


def write_cartera_output_excel(cartera_df: pd.DataFrame, pending_df: pd.DataFrame, output_path: Path) -> None:
    try:
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            cartera_df.to_excel(writer, sheet_name=MODULE5_CARTERA_SHEET_NAME, index=False)
            pending_df.to_excel(writer, sheet_name=MODULE5_PENDING_SHEET_NAME, index=False)

            workbook = writer.book
            text_format = workbook.add_format({"num_format": "@"})

            ws_cartera = writer.sheets[MODULE5_CARTERA_SHEET_NAME]
            ws_pending = writer.sheets[MODULE5_PENDING_SHEET_NAME]

            if cartera_df.shape[1] > 0:
                ws_cartera.set_column(0, cartera_df.shape[1] - 1, 22, text_format)
                ws_cartera.autofilter(0, 0, len(cartera_df), cartera_df.shape[1] - 1)
            ws_cartera.freeze_panes(1, 0)

            ws_pending.set_column(0, len(MODULE5_PENDING_COLUMNS) - 1, 24, text_format)
            ws_pending.freeze_panes(1, 0)
            ws_pending.autofilter(0, 0, len(pending_df), len(MODULE5_PENDING_COLUMNS) - 1)
    except Exception as exc:
        raise ProcessingError("No se pudo generar el archivo de salida.") from exc


def _resolve_required_columns(columns: pd.Index) -> dict[str, str]:
    resolved: dict[str, str] = {}
    normalized = {column: _normalize_column_name(column) for column in columns}

    for field, aliases in COLUMN_ALIASES.items():
        match = _find_matching_column(normalized, aliases)
        if not match:
            label = FIELD_LABELS[field]
            raise MissingColumnError(
                f"No se pudo encontrar la columna {label}. "
                "Revisa que el archivo corresponda al reporte de seguimiento FE TryTiendas."
            )
        resolved[field] = match

    return resolved


def _resolve_module2_required_columns(columns: pd.Index) -> dict[str, str]:
    resolved: dict[str, str] = {}
    normalized = {column: _normalize_column_name(column) for column in columns}

    for field, aliases in MODULE2_COLUMN_ALIASES.items():
        match = _find_matching_column(normalized, aliases)
        if not match:
            label = MODULE2_FIELD_LABELS[field]
            raise MissingColumnError(
                f"No se pudo encontrar la columna {label}. "
                "Revisa que el archivo corresponda al reporte CUENTA F.E SIN EMITIR."
            )
        resolved[field] = match

    return resolved


def _resolve_module3_required_columns(columns: pd.Index) -> dict[str, str]:
    resolved: dict[str, str] = {}
    normalized = {column: _normalize_column_name(column) for column in columns}

    for field, aliases in MODULE3_COLUMN_ALIASES.items():
        match = _find_matching_column(normalized, aliases)
        if not match:
            label = MODULE3_FIELD_LABELS[field]
            raise MissingColumnError(
                f"No se pudo encontrar la columna {label}. "
                "Revisa que el archivo corresponda al reporte CUENTA F.E SIN EMITIR."
            )
        resolved[field] = match

    return resolved


def _resolve_module4_platform_column(
    columns: pd.Index,
    aliases: list[str],
    missing_message: str,
) -> str:
    normalized = {column: _normalize_column_name(column) for column in columns}
    match = _find_matching_column(normalized, aliases)
    if not match:
        raise MissingColumnError(missing_message)
    return match


def _resolve_module5_column(
    columns: pd.Index,
    aliases: list[str],
    missing_message: str,
) -> str:
    normalized = {column: _normalize_column_name(column) for column in columns}
    match = _find_matching_column(normalized, aliases)
    if not match:
        raise MissingColumnError(missing_message)
    return match


def _find_matching_column(normalized_map: dict[str, str], aliases: list[str]) -> str | None:
    alias_norm = [_normalize_column_name(alias) for alias in aliases]

    for alias in alias_norm:
        for column, normalized in normalized_map.items():
            if normalized == alias:
                return column

    for alias in alias_norm:
        for column, normalized in normalized_map.items():
            if alias and alias in normalized:
                return column

    return None


def _read_delimited_file(input_path: Path) -> pd.DataFrame:
    detected = _detect_delimiter(input_path)
    candidates = [detected, ";", ",", "\t"]

    best_df: pd.DataFrame | None = None
    best_cols = 0

    for encoding in ("utf-8-sig", "latin-1"):
        for separator in dict.fromkeys(candidates):
            try:
                df = pd.read_csv(
                    input_path,
                    sep=separator,
                    dtype=str,
                    encoding=encoding,
                    low_memory=False,
                )
            except Exception:
                continue

            if df.shape[1] > best_cols:
                best_df = df
                best_cols = df.shape[1]

    if best_df is None:
        raise ProcessingError("No se pudo leer el archivo CSV/TXT seleccionado.")

    if best_df.shape[1] == 1:
        best_df = _split_single_column(best_df)

    return best_df


def _split_single_column(df: pd.DataFrame) -> pd.DataFrame:
    series = df.iloc[:, 0].astype(str)

    for separator in (";", "\t", ","):
        if not series.str.contains(re.escape(separator)).any():
            continue

        split_df = series.str.split(separator, expand=True)
        if split_df.shape[1] > 1:
            header = split_df.iloc[0].fillna("").astype(str).tolist()
            data = split_df.iloc[1:].copy()
            data.columns = header
            return data

    return df


def _detect_delimiter(input_path: Path) -> str:
    sample = ""
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            with input_path.open("r", encoding=encoding, errors="ignore") as handle:
                sample = handle.read(64000)
            break
        except Exception:
            continue

    if not sample:
        return ";"

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[";", ",", "\t"])
        return dialect.delimiter
    except Exception:
        first_line = sample.splitlines()[0] if sample.splitlines() else sample
        delimiter_counts = {
            ";": first_line.count(";"),
            ",": first_line.count(","),
            "\t": first_line.count("\t"),
        }
        return max(delimiter_counts, key=delimiter_counts.get)


def _clean_platform(series: pd.Series) -> pd.Series:
    cleaned = _clean_text_column(series)
    cleaned = cleaned.str.replace(r"^[cC]", "", regex=True)
    cleaned = cleaned.str.replace(r"\.0$", "", regex=True)
    cleaned = cleaned.str.strip()
    return cleaned


def _clean_platform_for_match(series: pd.Series) -> pd.Series:
    cleaned = _clean_text_column(series)
    cleaned = cleaned.str.replace(r"^[cC]", "", regex=True)
    cleaned = cleaned.str.replace(r"^(\d+)\.0+$", r"\1", regex=True)
    cleaned = cleaned.str.strip()
    invalid_values = {"", "NAN", "NONE", "NULL"}
    cleaned = cleaned[~cleaned.str.upper().isin(invalid_values)]
    return cleaned


def _clean_platform_for_pending(series: pd.Series) -> pd.Series:
    cleaned = _clean_text_column(series)
    cleaned = cleaned.str.replace(r"^[cC]", "", regex=True)

    scientific_mask = cleaned.str.contains(r"^[+-]?\d+(?:\.\d+)?[eE][+-]?\d+$", regex=True, na=False)
    if scientific_mask.any():
        numeric = pd.to_numeric(cleaned.where(scientific_mask), errors="coerce")
        converted = numeric.map(lambda value: _format_decimal_string(value) if pd.notna(value) else "")
        cleaned.loc[scientific_mask] = converted.loc[scientific_mask]

    cleaned = cleaned.str.replace(r"^(\d+)\.0+$", r"\1", regex=True)
    cleaned = cleaned.str.strip()
    return cleaned


def _clean_identifier_column(series: pd.Series, strip_decimal: bool = False) -> pd.Series:
    cleaned = _clean_text_column(series)
    cleaned = cleaned.str.replace(",", ".", regex=False)

    scientific_mask = cleaned.str.contains(r"^[+-]?\d+(?:\.\d+)?[eE][+-]?\d+$", regex=True, na=False)
    if scientific_mask.any():
        numeric = pd.to_numeric(cleaned.where(scientific_mask), errors="coerce")
        converted = numeric.map(lambda value: _format_decimal_string(value) if pd.notna(value) else "")
        cleaned.loc[scientific_mask] = converted.loc[scientific_mask]

    if strip_decimal:
        cleaned = cleaned.str.replace(r"\.0+$", "", regex=True)

    return cleaned.str.strip()


def _format_decimal_string(value: float) -> str:
    text = f"{value:.15f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _map_tipo_doc(series: pd.Series) -> pd.Series:
    normalized = series.fillna("").astype(str).map(_normalize_text)

    mapped = pd.Series("", index=series.index, dtype="object")
    mapped.loc[normalized == "DOCUMENTO POS"] = "RESOLUCION DIAN"
    mapped.loc[normalized.str.contains("RESOLUCION FE", na=False)] = "RESOLUCION POS"

    return mapped


def _clean_numeric_column(series: pd.Series) -> pd.Series:
    cleaned = _clean_text_column(series).str.replace(",", ".", regex=False)

    def _normalize_numeric_token(token: str) -> str:
        if not token:
            return ""

        try:
            number = Decimal(token)
        except InvalidOperation:
            return token

        if not number.is_finite():
            return token

        normalized = format(number, "f")
        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".")
        if normalized in {"-0", "+0", ""}:
            return "0"
        return normalized

    return cleaned.map(_normalize_numeric_token)


def _clean_prefix_column(series: pd.Series) -> pd.Series:
    cleaned = _clean_text_column(series)

    # Normalize prefixes like "5370-" to "-5370" to keep a consistent sign location.
    trailing_minus_mask = cleaned.str.endswith("-") & ~cleaned.str.startswith("-")
    if trailing_minus_mask.any():
        cleaned.loc[trailing_minus_mask] = "-" + cleaned.loc[trailing_minus_mask].str[:-1]

    # Collapse pure zero prefixes (e.g. "00", "000") to a canonical "0".
    zeros_mask = cleaned.str.fullmatch(r"0+")
    if zeros_mask.any():
        cleaned.loc[zeros_mask] = "0"

    return cleaned


def _remove_leading_export_artifact(result_df: pd.DataFrame) -> pd.DataFrame:
    if result_df.empty:
        return result_df

    first = result_df.iloc[0]
    first_tipo = str(first.get("TIPO DOC", "")).strip().upper()
    first_prefijo = str(first.get("PREFIJO", "")).strip().upper()
    first_platform = str(first.get("PLATAFORMA", "")).strip()
    first_unit = str(first.get("UNIDAD", "")).strip()

    # Some exports arrive with a leading DIAN-FE row that does not belong to the
    # final manual consolidation. Drop it only when the paired POS row exists.
    if first_tipo != "RESOLUCION DIAN" or first_prefijo != "FE":
        return result_df

    paired_pos_mask = (
        result_df["PLATAFORMA"].astype(str).str.strip().eq(first_platform)
        & result_df["UNIDAD"].astype(str).str.strip().eq(first_unit)
        & result_df["TIPO DOC"].astype(str).str.strip().str.upper().eq("RESOLUCION POS")
        & result_df["AUTORIZACION"].astype(str).str.strip().eq("0")
    )
    if not paired_pos_mask.any():
        return result_df

    return result_df.iloc[1:].reset_index(drop=True)


def _normalize_available_precision_legacy(result_df: pd.DataFrame) -> pd.DataFrame:
    if result_df.empty:
        return result_df

    normalized = result_df.copy()
    total = normalized["TOTAL"].astype(str).str.strip()
    available = normalized["DISPONIBLE"].astype(str).str.strip()

    # Keep compatibility with legacy manual workbooks where very large "DISPONIBLE"
    # values close to powers of ten are represented as the same scientific-magnitude
    # total (for example 9999999999981929 -> 1E+16).
    near_power_of_ten_mask = (
        total.str.fullmatch(r"1[0]{15,}")
        & available.str.fullmatch(r"9{5,}\d{5,}")
    )
    if near_power_of_ten_mask.any():
        normalized.loc[near_power_of_ten_mask, "DISPONIBLE"] = normalized.loc[near_power_of_ten_mask, "TOTAL"]

    return normalized


def _clean_text_column(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def _clean_module2_error_details(series: pd.Series) -> pd.Series:
    cleaned = _clean_text_column(series)
    return cleaned.str.split(";", n=1).str[0].str.strip()


def _normalize_text(value: str) -> str:
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text)
    return text.upper()


def _normalize_column_name(value: str) -> str:
    text = _normalize_text(value)
    return re.sub(r"[^A-Z0-9]", "", text)


def _find_facturacion_sheet(sheet_names: list[str]) -> str | None:
    normalized_target = _normalize_column_name("FACTURACION")
    for sheet_name in sheet_names:
        if _normalize_column_name(sheet_name) == normalized_target:
            return sheet_name
    return None


def _sort_platform_series(series: pd.Series) -> pd.Series:
    helper_df = pd.DataFrame({"platform": series.astype(str)})
    helper_df["numeric_order"] = pd.to_numeric(helper_df["platform"], errors="coerce")
    helper_df.sort_values(by=["numeric_order", "platform"], inplace=True, na_position="last")
    return helper_df["platform"].reset_index(drop=True)


def _build_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger(f"automatizador_bi_{log_path.stem}")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def _build_dated_output_dir(base_output_dir: Path, now: datetime) -> Path:
    year_folder = str(now.year)
    month_folder = MONTH_NAMES_ES[now.month - 1]
    day_folder = f"Dia {now.day:02d}"
    target_dir = base_output_dir / year_folder / month_folder / day_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def _set_status(status_callback: StatusCallback | None, message: str) -> None:
    if status_callback:
        status_callback(message)
