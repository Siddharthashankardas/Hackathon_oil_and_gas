"""CSV-backed synthetic POC network loader. Structural checks only; not a hydraulic solver."""
from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class NetworkNode:
    node_id: str
    node_type: str
    distance_km: float
    nominal_pressure_bar: float
    elevation_m: float
    elevation_datum: str

@dataclass(frozen=True)
class PipeSegment:
    segment_id: str
    from_node: str
    to_node: str
    length_km: float
    diameter_m: float
    roughness_mm: float
    roughness_m: float

@dataclass(frozen=True)
class PipelineNetwork:
    network_version: str
    nodes: tuple[NetworkNode, ...]
    segments: tuple[PipeSegment, ...]
    equipment: tuple[dict[str, Any], ...]

def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required CSV not found: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def _number(row: dict[str, str], field: str, file_name: str) -> float:
    value = row.get(field, "")
    if value is None or value.strip() == "":
        raise ValueError(f"{file_name}: {field} is required")
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{file_name}: {field} must be numeric, got {value!r}") from exc

def load_network(data_dir: str | Path, network_version: str = "SYNTHETIC-POC-v2") -> PipelineNetwork:
    """Load CSVs, check IDs/endpoints/geometry, and return an immutable network."""
    folder = Path(data_dir)
    node_rows = _read_csv(folder / "network_nodes.csv")
    segment_rows = _read_csv(folder / "network_segments.csv")
    equipment_path = folder / "network_equipment.csv"
    equipment_rows = _read_csv(equipment_path) if equipment_path.exists() else []

    nodes, node_ids = [], set()
    allowed_types = {"RECEIPT", "JUNCTION", "COMPRESSOR", "DELIVERY", "STORAGE", "VALVE"}
    for row in node_rows:
        node_id = row.get("node_id", "").strip()
        if not node_id or node_id in node_ids:
            raise ValueError(f"Blank or duplicate node_id: {node_id!r}")
        node_ids.add(node_id)
        node_type = row.get("node_type", "").strip().upper()
        if node_type not in allowed_types:
            raise ValueError(f"Unsupported node_type {node_type!r} for {node_id}")
        nodes.append(NetworkNode(node_id, node_type,
            _number(row, "distance_km", "network_nodes.csv"),
            _number(row, "nominal_pressure_bar", "network_nodes.csv"),
            _number(row, "elevation_m", "network_nodes.csv"),
            row.get("elevation_datum", "UNSPECIFIED").strip() or "UNSPECIFIED"))

    segments, segment_ids = [], set()
    for row in segment_rows:
        sid = row.get("segment_id", "").strip()
        if not sid or sid in segment_ids:
            raise ValueError(f"Blank or duplicate segment_id: {sid!r}")
        segment_ids.add(sid)
        start, end = row.get("from_node", "").strip(), row.get("to_node", "").strip()
        if start not in node_ids or end not in node_ids:
            raise ValueError(f"{sid}: from_node/to_node must reference known nodes")
        if start == end:
            raise ValueError(f"{sid}: pipe cannot connect a node to itself")
        length = _number(row, "length_km", "network_segments.csv")
        diameter = _number(row, "diameter_m", "network_segments.csv")
        rough_mm = _number(row, "roughness_mm", "network_segments.csv")
        if length <= 0 or diameter <= 0 or rough_mm < 0:
            raise ValueError(f"{sid}: invalid length, diameter or roughness")
        segments.append(PipeSegment(sid, start, end, length, diameter, rough_mm, rough_mm / 1000.0))

    if not nodes or not segments:
        raise ValueError("Network must contain at least one node and one pipe segment")
    return PipelineNetwork(network_version, tuple(nodes), tuple(segments), tuple(equipment_rows))

if __name__ == "__main__":
    # Run from backend/: python -m app.services.network_builder
    data_folder = Path(__file__).resolve().parents[3] / "data" / "raw"

    network = load_network(data_folder)

    print(f"Loaded {len(network.nodes)} nodes and {len(network.segments)} segments")
