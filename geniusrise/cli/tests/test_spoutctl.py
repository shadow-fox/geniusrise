# 🧠 Geniusrise
# Copyright (C) 2023  geniusrise.ai
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os

import pytest

from geniusrise.cli.discover import Discover
from geniusrise.cli.spoutctl import SpoutCtl
from geniusrise.core import Spout


@pytest.fixture
def discovered_spout():
    discover = Discover(directory=".")
    print(os.path.dirname(os.path.abspath(__file__)) + "/test_spout")
    classes = discover.scan_directory()
    return classes.get("TestSpoutCtlSpout")


@pytest.fixture
def spoutctl(discovered_spout):
    return SpoutCtl(discovered_spout)


def test_spoutctl_init(discovered_spout):
    spoutctl = SpoutCtl(discovered_spout)
    assert spoutctl.discovered_spout == discovered_spout
    assert discovered_spout


# fmt: off
@pytest.mark.parametrize(
    "output_type,state_type",
    [
        ("batch", "none"),
        ("batch", "redis"),
        ("batch", "postgres"),
        ("batch", "dynamodb"),
        ("batch", "prometheus"),
        ("streaming", "none"),
        ("streaming", "redis"),
        ("streaming", "postgres"),
        ("streaming", "dynamodb"),
        ("streaming", "prometheus"),
        ("stream_to_batch", "none"),
        ("stream_to_batch", "redis"),
        ("stream_to_batch", "postgres"),
        ("stream_to_batch", "dynamodb"),
        ("stream_to_batch", "prometheus"),
    ],
)
def test_spoutctl_run(spoutctl, output_type, state_type, tmpdir):
    parser = argparse.ArgumentParser()
    spoutctl.create_parser(parser)
    args = parser.parse_args([
        "rise",
        output_type,
        state_type,
        "test_method",
        "--output_kafka_topic", "test_topic",
        "--output_kafka_cluster_connection_string", "localhost:9094",
        "--redis_host", "localhost",
        "--redis_port", "6379",
        "--redis_db", "0",
        "--postgres_host", "localhost",
        "--postgres_port", "5432",
        "--postgres_user", "postgres",
        "--postgres_password", "postgres",
        "--postgres_database", "geniusrise",
        "--postgres_table", "geniusrise_state",
        "--dynamodb_table_name", "test_table",
        "--dynamodb_region_name", "ap-south-1",
        "--prometheus_gateway", "localhost:9091",
        "--output_folder", str(tmpdir),
        "--output_s3_bucket", "geniusrise-test-bucket",
        "--output_s3_folder", "whatever",
        "--buffer_size", "1",
        "--args", "1", "2", "3", "a=4", "b=5", "c=6"
    ])
    result = spoutctl.run(args)
    assert result == 90
    assert isinstance(spoutctl.spout, Spout)
# fmt: on


@pytest.mark.parametrize(
    "output_type,state_type",
    [
        ("batch", "none"),
        ("batch", "redis"),
        ("batch", "postgres"),
        ("batch", "dynamodb"),
        ("batch", "prometheus"),
        ("streaming", "none"),
        ("streaming", "redis"),
        ("streaming", "postgres"),
        ("streaming", "dynamodb"),
        ("streaming", "prometheus"),
        ("stream_to_batch", "none"),
        ("stream_to_batch", "redis"),
        ("stream_to_batch", "postgres"),
        ("stream_to_batch", "dynamodb"),
        ("stream_to_batch", "prometheus"),
    ],
)
def test_spoutctl_create_spout(spoutctl, output_type, state_type, tmpdir):
    kwargs = {
        "output_folder": tmpdir,
        "output_kafka_topic": "test_topic",
        "output_kafka_cluster_connection_string": "localhost:9094",
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "postgres_host": "localhost",
        "postgres_port": 5432,
        "postgres_user": "postgres",
        "postgres_password": "postgres",
        "postgres_database": "geniusrise",
        "postgres_table": "geniusrise_state",
        "dynamodb_table_name": "test_table",
        "dynamodb_region_name": "ap-south-1",
        "prometheus_gateway": "localhost:9091",
        "output_s3_bucket": "geniusrise-test-bucket",
        "output_s3_folder": "whatever",
        "buffer_size": 1,
    }

    spout = spoutctl.create_spout(output_type, state_type, **kwargs)
    assert isinstance(spout, Spout)


def test_spoutctl_execute_spout(spoutctl, tmpdir):
    spout = spoutctl.create_spout(
        "batch",
        "none",
        output_folder=tmpdir,
        output_s3_bucket="geniusrise-test-bucket",
        output_s3_folder="whatever",
    )
    result = spoutctl.execute_spout(spout, "test_method", 1, 2, 3, a=4, b=5, c=6)
    assert result == 6 * (4 + 5 + 6)
