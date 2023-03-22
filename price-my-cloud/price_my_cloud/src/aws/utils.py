from datetime import datetime, timedelta
from itertools import chain
from decimal import Decimal
from operator import itemgetter

import aws.models
import ipaddress
from aws import models as aws_models
from node import models as node_models
from django.db.models import Sum, Count, Min, Max
import boto3

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
    component_type = node_models.ComponentType.objects.get(name="EC2")
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
            "flowlogdata__destination",
            "flowlogdata__action",
        )
        .annotate(
            amount=Count("id"),
            packets=Sum("flowlogdata__packets"),
            bytes=Sum("flowlogdata__bytes"),
            # avg_request_time=Avg(
            #     F("flowlogdata__end") - F("flowlogdata__start"),
            #     output_field=DurationField(),
            # ),
            start=Min("flowlogdata__start"),
            end=Max(
                "flowlogdata__start"
            ),  # yes we want to check start, as end can be finished 60 seconds later
        )
        .values(
            "flowlogdata__source",
            "flowlogdata__destination",
            "flowlogdata__action",
            "amount",
            "packets",
            "bytes",
            "start",
            "end",
        )
    )

    connections = []
    for connection in data:
        connections.append(
            node_models.Connection(
                from_component=components_map[connection["flowlogdata__source"]],
                to_component=components_map[connection["flowlogdata__destination"]],
                number_of_requests=connection["amount"],
                # avg_time_of_request=timedelta(connection["avg_request_time"]),
                packets=connection["packets"],
                bytes=connection["bytes"],
                action=connection["flowlogdata__action"],
                start=datetime.fromtimestamp(connection["start"]),
                end=datetime.fromtimestamp(connection["end"]),
            )
        )
    node_models.Connection.objects.bulk_create(connections)

    # Prefilter components to figure out which were created by user (shown)
    # and which components are just from AWS (should be hidden)
    # node_models.Component.objects.filter(node=node).exclude(
    #     from_components__number_of_requests__gte=2
    # ).update(hidden=True)

    client_cw = boto3.client("cloudwatch")
    aws_map_ip_with_instance_id = map_ec2_with_components()
    for component in node.component_set.all():
        if component.name in aws_map_ip_with_instance_id:
            component.hidden = False
            component.instance_type = aws_map_ip_with_instance_id[component.name][
                "instance_type"
            ]
            component.save(update_fields=["hidden", "instance_type"])
            if not (
                start_connection := node_models.Connection.objects.filter(
                    from_component__name=component.name,
                    from_component__node=node,
                )
                .order_by("start")
                .first()
            ):
                continue
            if not (
                end_connection := node_models.Connection.objects.filter(
                    from_component__name=component.name,
                    from_component__node=node,
                )
                .order_by("end")
                .last()
            ):
                continue
            cpu_utilization = get_cpu_utilization(
                client_cw,
                aws_map_ip_with_instance_id[component.name]["instance_id"],
                start_connection.start,
                end_connection.end,
            )
            component.cpu_utilization = cpu_utilization
            component.save(update_fields=["cpu_utilization"])


def get_cpu_utilization(client_cw, instance_id, start_time, end_time):
    cpu_utilization = client_cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Average"],
    )

    if datapoints := cpu_utilization["Datapoints"]:
        highest_cpu_datapoint = sorted(datapoints, key=itemgetter("Average"))[-1]
        utilization = highest_cpu_datapoint["Average"]
        load = round(utilization, 3)
        return Decimal(str(load))
    return Decimal("0.000")


def map_ec2_with_components():
    ec2 = boto3.resource("ec2")
    aws_map_ip_with_instance_id = {}
    for instance in ec2.instances.all():
        ip = None
        try:
            ip = instance.public_ip_address
        except AttributeError:
            pass
        try:
            ip = instance.private_ip_address
        except AttributeError:
            pass

        if ip:
            aws_map_ip_with_instance_id[ip] = {
                "instance_id": instance.id,
                "instance_type": instance.instance_type,
            }
    return aws_map_ip_with_instance_id
