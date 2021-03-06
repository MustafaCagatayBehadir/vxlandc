import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json
from pprint import pprint


class PortConfigsTests:
    """
    A Test Class for NSO package Port Configs
    """

    payload_path = Path.cwd() / "tests" / "test_01_port_configs" / "payload"
    expected_path = Path.cwd() / "tests" / "test_01_port_configs" / "expected"
    nso = NsoRestconfCall()

    @classmethod
    def setup_class(cls):
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
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1'),
        (expected_path / 'ref_001_port_ETH100002_sw_2_e_1_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1'),
        (expected_path / 'ref_001_port_ETH100002_sw_2_e_1_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F2')
    ], indirect=['expected'])
    def test_001_ethernet_port(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_002_port_PC100001_sw_3_po_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=1'),
        (expected_path / 'ref_002_port_PC100002_sw_4_po_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=2'),
        (expected_path / 'ref_002_port_PC100001_member_sw_3_e_1_10.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F10'),
        (expected_path / 'ref_002_port_PC100001_member_sw_3_e_1_11.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F11'),
        (expected_path / 'ref_002_port_PC100002_member_sw_4_e_1_10.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F10'),
        (expected_path / 'ref_002_port_PC100002_member_sw_4_e_1_11.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F11'),
    ], indirect=['expected'])
    def test_002_portchannel_port(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_003_port_VPC100001_sw_1_2_po_10.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=10'),
        (expected_path / 'ref_003_port_VPC100001_sw_1_2_po_10.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=10'),
        (expected_path / 'ref_003_port_VPC100002_sw_1_2_po_20.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=20'),
        (expected_path / 'ref_003_port_VPC100002_sw_1_2_po_20.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=20'),
        (expected_path / 'ref_003_port_VPC100001_member_sw_1_2_e_10.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F10'),
        (expected_path / 'ref_003_port_VPC100001_member_sw_1_2_e_11.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F11'),
        (expected_path / 'ref_003_port_VPC100001_member_sw_1_2_e_10.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F10'),
        (expected_path / 'ref_003_port_VPC100001_member_sw_1_2_e_11.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F11'),
        (expected_path / 'ref_003_port_VPC100002_member_sw_1_2_e_12.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F12'),
        (expected_path / 'ref_003_port_VPC100002_member_sw_1_2_e_13.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F13'),
        (expected_path / 'ref_003_port_VPC100002_member_sw_1_2_e_12.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F12'),
        (expected_path / 'ref_003_port_VPC100002_member_sw_1_2_e_13.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F13'),
    ], indirect=['expected'])
    def test_003_vpc_portchannel_port(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_004_port_ETH100001_sw_1_e_1_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS/port-config=ETH100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1'),
        (expected_path / 'ref_004_port_PC100001_sw_3_po_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=PC_PG_1_TRUNK/port-config=PC100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=1'),
        (expected_path / 'ref_004_port_VPC100001_sw_1_2_po_10.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS/port-config=VPC100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=10'),
    ], indirect=['expected'])
    def test_004_port_shutdown(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_004_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected
        pprint(get_resp.json())

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_005_port_ETH100001_sw_1_e_1_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS/port-config=ETH100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1'),
        (expected_path / 'ref_005_port_VPC100001_sw_1_2_po_10.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS/port-config=VPC100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=10'),
    ], indirect=['expected'])
    def test_005_port_storm_control_action_trap(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_005_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected
        pprint(get_resp.json())

    @mark.parametrize('expected, post_payload, post_path', [
        (expected_path / 'ref_006_port_ETH100003_error.json',
         payload_path / 'test_006_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS'),
        (expected_path / 'ref_006_port_PC100003_error.json',
         payload_path / 'test_006_config_02.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=PC_PG_1_TRUNK'),
        (expected_path / 'ref_006_port_VPC100003_error.json',
         payload_path / 'test_006_config_03.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS')
    ], indirect=['expected'])
    def test_006_interface_already_used(self, expected, post_payload, post_path):
        resp = self.nso.post(payload=post_payload,
                             path=post_path, params='', action=False)
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, patch_payload, patch_path', [
        (expected_path / 'ref_007_port_ETH100001_error.json',
         payload_path / 'test_007_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS/port-config=ETH100001'),
        (expected_path / 'ref_007_port_PC100001_error.json',
         payload_path / 'test_007_config_02.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=PC_PG_1_TRUNK/port-config=PC100001'),
        (expected_path / 'ref_007_port_VPC100001_error.json',
         payload_path / 'test_007_config_03.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS/port-config=VPC100001')
    ], indirect=['expected'])
    def test_007_node_change(self, expected, patch_payload, patch_path):
        resp = self.nso.patch(payload=patch_payload,
                              path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_008_port_ETH100001_sw_1_e_1_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS/port-config=ETH100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1'),
        (expected_path / 'ref_008_port_PC100001_sw_3_po_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=PC_PG_1_TRUNK//port-config=PC100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=1'),
        (expected_path / 'ref_008_port_VPC100001_sw_1_2_po_10.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS/port-config=VPC100001/',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=10')
    ], indirect=['expected'])
    def test_008_bum(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_008_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected
        pprint(get_resp.json())

    @mark.parametrize('expected, delete_path', [
        (expected_path / 'ref_009_port_ETH100002_error.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_TRUNK/port-config=ETH100002')
    ], indirect=['expected'])
    def test_009_port_delete(self, expected, delete_path):
        resp = self.nso.delete(path=delete_path)
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, patch_payload, patch_path', [
        (expected_path / 'ref_010_port_ETH100003_error.json',
         payload_path / 'test_010_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS/port-config'),
        (expected_path / 'ref_010_port_PC100003_error.json',
         payload_path / 'test_010_config_02.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=PC_PG_1_TRUNK/port-config'),
        (expected_path / 'ref_010_port_VPC100003_error.json',
         payload_path / 'test_010_config_03.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS/port-config')
    ], indirect=['expected'])
    def test_010_routed_interface(self, expected, patch_payload, patch_path):
        resp = self.nso.patch(payload=patch_payload,
                              path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, patch_payload, patch_path', [
        (expected_path / 'ref_011_port_ETH100003_error.json',
         payload_path / 'test_011_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS/port-config'),
        (expected_path / 'ref_011_port_PC100003_error.json',
         payload_path / 'test_011_config_02.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=PC_PG_1_TRUNK/port-config'),
        (expected_path / 'ref_011_port_VPC100003_error.json',
         payload_path / 'test_011_config_03.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS/port-config')
    ], indirect=['expected'])
    def test_011_used_interface(self, expected, patch_payload, patch_path):
        resp = self.nso.patch(payload=patch_payload,
                              path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, patch_payload, patch_path', [
        (expected_path / 'ref_012_port_group_ETH_PG_1_ACCESS_error.json',
         payload_path / 'test_012_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=ETH_PG_1_ACCESS'),
        (expected_path / 'ref_012_port_group_PC_PG_1_TRUNK_error.json',
         payload_path / 'test_012_config_02.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=PC_PG_1_TRUNK'),
        (expected_path / 'ref_012_port_group_VPC_PG_1_ACCESS_error.json',
         payload_path / 'test_012_config_03.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/port-configs=VPC_PG_1_ACCESS')
    ], indirect=['expected'])
    def test_012_port_group_mode_change(self, expected, patch_payload, patch_path):
        resp = self.nso.patch(payload=patch_payload,
                              path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())
