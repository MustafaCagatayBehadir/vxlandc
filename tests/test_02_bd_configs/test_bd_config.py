import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


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

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_004_svi_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/Vlan'),
        (expected_path / 'ref_004_svi_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/Vlan')
    ], indirect=['expected'])
    def test_004_svi(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_005_vrf_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:vrf/context=tcell-grt'),
        (expected_path / 'ref_005_vrf_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:vrf/context=tcell-grt')
    ], indirect=['expected'])
    def test_005_vrf(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_006_bgp_bd_service_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt'),
        (expected_path / 'ref_006_bgp_bd_service_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt')
    ], indirect=['expected'])
    def test_006_bgp(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, post_payload, post_path', [
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
    def test_007_bd_subnet_preferred(self, expected, post_payload, post_path):
        resp = self.nso.patch(payload=post_payload, path=post_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, post_payload, post_path', [
        (expected_path / 'ref_008_bd_service_1_error.json',
         payload_path / 'test_008_config_01.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1')
    ], indirect=['expected'])
    def test_008_bd_access_port_group(self, expected, post_payload, post_path):
        resp = self.nso.patch(payload=post_payload, path=post_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
