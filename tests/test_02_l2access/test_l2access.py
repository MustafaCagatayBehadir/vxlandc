import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


class L1AccessTests:
    """
    A Test Class for NSO package l1access
    """

    payload_path = Path.cwd() / "tests" / "test_02_l2access" / "payload"
    expected_path = Path.cwd() / "tests" / "test_02_l2access" / "expected"
    nso = NsoRestconfCall()

    @classmethod
    def setup_class(cls):
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_external_ports_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_external_ports_approved.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_external_port_groups_config.json",
            path="",
            params="",
        )

    def test_001(self):
        assert True

    # @classmethod
    # def teardown_class(cls):
    #     cls.nso.delete(path="vxlandc-core:vxlandc")
    #     cls.nso.delete(path="resource-allocator:resource-pools")
