from itertools import chain

import aws.models
import ipaddress
from aws import models as aws_models
from node import models as node_models
from django.db.models import Sum, Count

LOG_MODEL_MAP = {
    "source": "srcaddr",
    "destination": "dstaddr",
    "source_port": "srcport",
    "destination_port": "dstport",
    "protocol": "protocol",
    "packet": "packets",
    "bytes": "bytes",
    "start": "start",
    "end": "end",
    "action": "action",
    "log_status": "log-status",
}

HEADER_TEMPLATE = {
    "version": 0,
    "account-id": 1,
    "interface-id": 2,
    "srcaddr": 3,
    "dstaddr": 4,
    "srcport": 5,
    "dstport": 6,
    "protocol": 7,
    "packets": 8,
    "bytes": 9,
    "start": 10,
    "end": 11,
    "action": 12,
    "log-status": 13,
}


def create_flow_log(node: node_models.Node, file):
    flow_log = aws.models.FlowLog.objects.create(node=node, filename=file.name)
    return flow_log


def validate_ip_address(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def handle_uploaded_file(node: node_models.Node, file):
    flow_log = create_flow_log(node, file)

    header = HEADER_TEMPLATE
    f = file.open()
    header_items = f.readline().decode().strip("\\n").split()
    for index, item in enumerate(header_items):
        if item in header:
            header[item] = index

    flow_log_data_bulk = []
    for line in f:  # TODO probably should used chunks
        line = line.decode()
        line_items = line.strip("\\n").split()
        if all(
            map(
                lambda x: validate_ip_address(x),
                [line_items[header["srcaddr"]], line_items[header["dstaddr"]]],
            )
        ):
            flow_log_data_bulk.append(
                aws_models.FlowLogData(
                    flow_log=flow_log,
                    source=line_items[header["srcaddr"]],
                    destination=line_items[header["dstaddr"]],
                    source_port=line_items[header["srcport"]],
                    destination_port=line_items[header["dstport"]],
                    protocol=line_items[header["protocol"]],
                    packets=line_items[header["packets"]],
                    bytes=line_items[header["bytes"]],
                    start=line_items[header["start"]],
                    end=line_items[header["end"]],
                    action=line_items[header["action"]],
                    log_status=line_items[header["log-status"]],
                )
            )
    aws_models.FlowLogData.objects.bulk_create(flow_log_data_bulk)
    # batch_size = 100
    # while True:
    #     batch = list(islice(flow_log_data_bulk, batch_size))
    #     if not batch:
    #         break
    # aws_models.FlowLogData.objects.bulk_create(batch, batch_size)

    return flow_log


def convert_flow_logs_to_components(node: node_models.Node):
    source_components = node.flowlog_set.values_list(
        "flowlogdata__source", flat=True
    ).distinct()
    destination_components = node.flowlog_set.values_list(
        "flowlogdata__destination", flat=True
    ).distinct()
    components = set(chain(source_components, destination_components))
    component_type = (
        node_models.ComponentType.objects.first()
    )  # TODO should pick automatically type
    components_map = {}
    for ip in components:
        component = node_models.Component.objects.create(
            node=node,
            type=component_type,
            name=ip,
        )
        components_map[ip] = component

    data = (
        node.flowlog_set.values(
            "flowlogdata__source",
            # "flowlogdata__source_port",
            "flowlogdata__destination",
            # "flowlogdata__destination_port",
            # "flowlogdata__protocol",
        )
        .annotate(
            amount=Count("id"),
            packets=Sum("flowlogdata__packets"),
            bytes=Sum("flowlogdata__bytes"),
        )
        .values(
            "flowlogdata__source",
            # "flowlogdata__source_port",
            "flowlogdata__destination",
            # "flowlogdata__destination_port",
            # "flowlogdata__protocol",
            "amount",
            "packets",
            "bytes",
        )
    )

    connections = []
    for connection in data:
        connections.append(
            node_models.Connection(
                from_component=components_map[connection["flowlogdata__source"]],
                to_component=components_map[connection["flowlogdata__destination"]],
                number_of_requests=connection["amount"],
                description=f'{connection["packets"]}: {connection["bytes"]}',
            )
        )
    node_models.Connection.objects.bulk_create(connections)

    # Prefilter components to figure out which were created by user (shown)
    # and which components are just from AWS (should be hidden)
    node_models.Component.objects.filter(node=node).exclude(
        from_components__number_of_requests__gte=2
    ).update(hidden=True)
