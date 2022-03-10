import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


class L1AccessTests:
    """
    A Test Class for NSO package l1access
    """

    payload_path = Path.cwd() / "tests" / "l1access" / "payload"
    expected_path = Path.cwd() / "tests" / "l1access" / "expected"
    nso = NsoRestconfCall()

    @classmethod
    def setup_class(cls):
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_resource_pools_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_site_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_ports_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_ports_approved.json",
            path="",
            params="",
        )


    @mark.parametrize('expected, path', [
        (expected_path / 'ref_001_port_ETH100001_sw_1_e_1_1.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1'),
        (expected_path / 'ref_001_port_ETH100002_sw_1_e_1_2.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F2'),
        (expected_path / 'ref_001_port_ETH100002_sw_1_e_1_3.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F3'),
        (expected_path / 'ref_001_port_ETH100003_sw_3_e_1_1.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-03/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1')
    ], indirect=['expected'])
    def test_001_ethernet_port(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @classmethod
    def teardown_class(cls):
        cls.nso.delete(path="vxlandc-core:vxlandc")
        cls.nso.delete(path="resource-allocator:resource-pools")
