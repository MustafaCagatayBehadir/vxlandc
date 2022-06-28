import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json
from pprint import pprint


class BDConfigsTests:
    """
    A Test Class for NSO bridge-domain service
    """

    payload_path = Path.cwd() / "tests" / "test_02_bd_configs" / "payload"
    expected_path = Path.cwd() / "tests" / "test_02_bd_configs" / "expected"
    nso = NsoRestconfCall()

    @classmethod
    def setup_class(cls):
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_vrf_service_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_vrf_service_approved.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_fabric_service_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_fabric_service_approved.json",
            path="",
            params="",
        )

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_001_vlan_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:vlan'),
        (expected_path / 'ref_001_vlan_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:vlan'),
        (expected_path / 'ref_001_vlan_bd_service_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:vlan'),
        (expected_path / 'ref_001_vlan_bd_service_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:vlan')
    ], indirect=['expected'])
    def test_001_vlan(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_002_nve_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/nve=1/member'),
        (expected_path / 'ref_002_nve_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/nve=1/member'),
        (expected_path / 'ref_002_nve_bd_service_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/nve=1/member'),
        (expected_path / 'ref_002_nve_bd_service_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:interface/nve=1/member')
    ], indirect=['expected'])
    def test_002_nve(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_003_evpn_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:evpn/vni'),
        (expected_path / 'ref_003_evpn_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:evpn/vni'),
        (expected_path / 'ref_003_evpn_bd_service_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:evpn/vni'),
        (expected_path / 'ref_003_evpn_bd_service_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:evpn/vni')
    ], indirect=['expected'])
    def test_003_evpn(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_004_svi_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Vlan'),
        (expected_path / 'ref_004_svi_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Vlan'),
        (expected_path / 'ref_004_svi_bd_service_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/Vlan'),
        (expected_path / 'ref_004_svi_bd_service_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:interface/Vlan')
    ], indirect=['expected'])
    def test_004_svi(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_005_vrf_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:vrf'),
        (expected_path / 'ref_005_vrf_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:vrf'),
        (expected_path / 'ref_005_vrf_bd_service_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:vrf'),
        (expected_path / 'ref_005_vrf_bd_service_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:vrf')
    ], indirect=['expected'])
    def test_005_vrf(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_006_bgp_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf'),
        (expected_path / 'ref_006_bgp_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf'),
        (expected_path / 'ref_006_bgp_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf'),
        (expected_path / 'ref_006_bgp_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf')
    ], indirect=['expected'])
    def test_006_bgp(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, patch_payload, patch_path', [
        (expected_path / 'ref_007_bd_service_1_error.json',
         payload_path / 'test_007_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1'),
        (expected_path / 'ref_007_bd_service_2_error.json',
         payload_path / 'test_007_config_02.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2'),
        (expected_path / 'ref_007_bd_service_3_error.json',
         payload_path / 'test_007_config_03.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-3')
    ], indirect=['expected'])
    def test_007_bd_subnet_preferred(self, expected, patch_payload, patch_path):
        resp = self.nso.patch(payload=patch_payload,
                              path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, patch_payload, patch_path', [
        (expected_path / 'ref_008_bd_service_1_error.json',
         payload_path / 'test_008_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1')
    ], indirect=['expected'])
    def test_008_bd_access_port_group(self, expected, patch_payload, patch_path):
        resp = self.nso.patch(payload=patch_payload,
                              path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, patch_payload, patch_path', [
        (expected_path / 'ref_009_bd_service_1_error.json',
         payload_path / 'test_009_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/vrf')
    ], indirect=['expected'])
    def test_009_bd_vrf(self, expected, patch_payload, patch_path):
        resp = self.nso.patch(payload=patch_payload,
                              path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, delete_path', [
        (expected_path / 'ref_010_tenant_service_1_error.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL'),
        (expected_path / 'ref_010_tenant_service_2_error.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0002_TURKCELL')
    ], indirect=['expected'])
    def test_010_tenant_delete(self, expected, delete_path):
        resp = self.nso.delete(path=delete_path)
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, post_payload, post_path', [
        (expected_path / 'ref_011_vrf_service_1_error.json',
         payload_path / 'test_011_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=vrf-100002')
    ], indirect=['expected'])
    def test_011_vrf_external_vlan_is_used(self, expected, post_payload, post_path):
        resp = self.nso.post(post_payload, post_path, params='', action=False)
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
        pprint(resp.json())

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_012_bd_service_sw_1_ETH100001.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1/switchport'),
        (expected_path / 'ref_012_bd_service_sw_1_VPC100001.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=10/switchport'),
        (expected_path / 'ref_012_bd_service_sw_1_VPC100002.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=20/switchport'),
        (expected_path / 'ref_012_bd_service_sw_2_ETH100002_1_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F1/switchport'),
        (expected_path / 'ref_012_bd_service_sw_2_ETH100002_1_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Ethernet=1%2F2/switchport'),
        (expected_path / 'ref_012_bd_service_sw_2_VPC100001.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=10/switchport'),
        (expected_path / 'ref_012_bd_service_sw_2_VPC100002.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=20/switchport'),
        (expected_path / 'ref_012_bd_service_sw_3_PC100001.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=1/switchport'),
        (expected_path / 'ref_012_bd_service_sw_4_PC100002.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=2/switchport'),
    ], indirect=['expected'])
    def test_012_bd_vlan_trunking(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected
        pprint(resp.json())