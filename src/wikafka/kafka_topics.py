from enum import Enum
from dataclasses import dataclass


@dataclass
class TopicConfig:
    name: str
    num_partitions: int = 1
    replication_factor: int = 1


class McpKafkaTopics(Enum):
    CONSUMER_OFFSETS = TopicConfig(name="__consumer_offsets", num_partitions=50)
    WORKORDER = TopicConfig(name="workorder")
    # DEFECT_REPORT = TopicConfig(name="defect_report")
    # FANUC_MACHINE_STATUS = TopicConfig(name="fanuc_machine_status")
    # IMS_TPM_STATUS = TopicConfig(name="ims_tpm_status")
    MACHINES = TopicConfig(name="machines")
    # MCP = TopicConfig(name="mcp")
