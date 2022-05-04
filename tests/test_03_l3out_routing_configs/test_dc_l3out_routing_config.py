import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


class L3OutRoutingConfigsTests:
    """
    A Test Class for NSO l3out routing configurations
    """

    payload_path = Path.cwd() / "tests" / "test_03_l3out_routing_configs" / "payload"
    expected_path = Path.cwd() / "tests" / "test_03_l3out_routing_configs" / "expected"
    nso = NsoRestconfCall()

    @classmethod
    def setup_class(cls):
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_l3out_bgp_config.json",
            path="",
            params="",
        )

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_001_l3out_bgp_config_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_001_l3out_bgp_config_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_001_l3out_bgp_loopback_config_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/loopback=100'),
        (expected_path / 'ref_001_l3out_bgp_loopback_config_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/loopback=100'),
    ], indirect=['expected'])
    def test_001_l3out_fabric_internal_bgp_config(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_002_l3out_bgp_config_blf_sw_1.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1//config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt'),
        (expected_path / 'ref_002_l3out_bgp_config_blf_sw_2.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1//config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt'),
    ], indirect=['expected'])
    def test_002_l3out_fabric_external_bgp_config(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_003_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_003_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_003_l3out_fabric_internal_bgp_local_as(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_003_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_004_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_004_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_004_l3out_fabric_internal_bgp_peer_af_controls(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_004_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected