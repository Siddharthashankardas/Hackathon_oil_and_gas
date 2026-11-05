
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class NodeType(str, Enum):
    RECEIPT = "receipt"
    JUNCTION = "junction"
    DELIVERY = "delivery"


class NetworkNode(BaseModel):
    node_id: str
    node_type: NodeType
    elevation_m: float


class PipeSegment(BaseModel):
    segment_id: str

    # The two nodes connected by this pipe
    from_node: str
    to_node: str

    # All physical dimensions use metres internally
    length_m: float = Field(gt=0)
    internal_diameter_m: float = Field(gt=0)
    roughness_m: float = Field(ge=0)


class PipelineNetwork(BaseModel):
    network_version: str

    nodes: list[NetworkNode]
    segments: list[PipeSegment]

    @model_validator(mode="after")
    def validate_connections(self):
        node_ids = {node.node_id for node in self.nodes}

        for segment in self.segments:
            if segment.from_node not in node_ids:
                raise ValueError(
                    f"Unknown start node: {segment.from_node}"
                )

            if segment.to_node not in node_ids:
                raise ValueError(
                    f"Unknown end node: {segment.to_node}"
                )

        return self
