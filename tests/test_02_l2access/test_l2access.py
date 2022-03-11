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
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_l2fabric_service_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_l2fabric_service_approved.json",
            path="",
            params="",
        )

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_001_vlan_l2fabric_service_sw_5.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-05/config/tailf-ned-cisco-nx:vlan')
    ], indirect=['expected'])
    def test_001(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @classmethod
    def teardown_class(cls):
        cls.nso.delete(path="vxlandc-core:vxlandc")
        cls.nso.delete(path="resource-allocator:resource-pools")
