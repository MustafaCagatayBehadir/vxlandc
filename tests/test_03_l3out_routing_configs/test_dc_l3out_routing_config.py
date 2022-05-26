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
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_l3out_static_config.json",
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

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_002_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_002_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_002_l3out_fabric_internal_bgp_local_as(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_002_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_003_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_003_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_003_l3out_fabric_internal_bgp_peer_af_controls(self, expected, patch_path, get_path):
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
    def test_004_l3out_fabric_internal_bgp_bfd(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_004_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_005_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_005_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_005_l3out_fabric_internal_bgp_disable_connected_check(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_005_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_006_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_006_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_006_l3out_fabric_internal_bgp_weight(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_006_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_007_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_007_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_007_l3out_fabric_internal_bgp_timers(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_007_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_008_l3out_bgp_config_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_008_l3out_bgp_config_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-1/routing/bgp=10.0.0.2',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
    ], indirect=['expected'])
    def test_008_l3out_fabric_internal_bgp_password(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_008_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        data['tailf-ned-cisco-nx:neighbor'][0]['password']['passwd'] = ".*"
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_009_l3out_bgpv6_config_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_009_l3out_bgpv6_config_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_009_l3out_bgpv6_loopback_config_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:interface/loopback=100'),
        (expected_path / 'ref_009_l3out_bgpv6_loopback_config_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:interface/loopback=100'),
    ], indirect=['expected'])
    def test_009_l3out_fabric_internal_bgpv6_config(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_010_l3out_bgpv6_config_sw_3.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_010_l3out_bgpv6_config_sw_4.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
    ], indirect=['expected'])
    def test_010_l3out_fabric_internal_bgpv6_local_as(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_010_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_011_l3out_bgpv6_config_sw_3.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_011_l3out_bgpv6_config_sw_4.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
    ], indirect=['expected'])
    def test_011_l3out_fabric_internal_bgpv6_peer_af_controls(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_011_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_012_l3out_bgpv6_config_sw_3.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_012_l3out_bgpv6_config_sw_4.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
    ], indirect=['expected'])
    def test_012_l3out_fabric_internal_bgpv6_bfd(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_012_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_013_l3out_bgpv6_config_sw_3.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_013_l3out_bgpv6_config_sw_4.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
    ], indirect=['expected'])
    def test_013_l3out_fabric_internal_bgpv6_disable_connected_check(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_013_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_014_l3out_bgpv6_config_sw_3.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_014_l3out_bgpv6_config_sw_4.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
    ], indirect=['expected'])
    def test_014_l3out_fabric_internal_bgpv6_weight(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_014_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_015_l3out_bgpv6_config_sw_3.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_015_l3out_bgpv6_config_sw_4.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
    ], indirect=['expected'])
    def test_015_l3out_fabric_internal_bgpv6_timers(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_015_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_016_l3out_bgpv6_config_sw_3.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
        (expected_path / 'ref_016_l3out_bgpv6_config_sw_4.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0001_TURKCELL/bridge-domain=BD-SERVICE-2/routing/bgp=2001:db8:cafe::2',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2'),
    ], indirect=['expected'])
    def test_016_l3out_fabric_internal_bgpv6_passwords(self, expected, patch_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_016_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        data['tailf-ned-cisco-nx:neighbor'][0]['password']['passwd'] = ".*"
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_017_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1'),
        (expected_path / 'ref_017_l3out_bgp_config_to_dcpe_2_border_sw_1.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.5'),
        (expected_path / 'ref_017_l3out_bgp_port_channel_config_to_dcpe_1_border_sw_1.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=501.3'),
        (expected_path / 'ref_017_l3out_bgp_port_channel_config_to_dcpe_2_border_sw_1.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=502.3'),
    ], indirect=['expected'])
    def test_017_l3out_fabric_external_bgp_config(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_018_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.1',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1'),
        (expected_path / 'ref_018_l3out_bgp_config_to_dcpe_2_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.5',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.5'),
    ], indirect=['expected'])
    def test_018_l3out_fabric_external_bgp_local_as(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_018_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_019_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.1',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1'),
        (expected_path / 'ref_019_l3out_bgp_config_to_dcpe_2_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.5',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.5'),
    ], indirect=['expected'])
    def test_019_l3out_fabric_external_bgp_peer_af_controls(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_019_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_020_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.1',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1'),
        (expected_path / 'ref_020_l3out_bgp_config_to_dcpe_2_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.5',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.5'),
    ], indirect=['expected'])
    def test_020_l3out_fabric_external_bgp_bfd(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_020_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_021_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.1',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1')
    ], indirect=['expected'])
    def test_021_l3out_fabric_external_bgp_disable_connected_check(self, expected, post_path, get_path):
        patch_resp = self.nso.patch(
            payload=self.payload_path / 'test_021_config.json', path=post_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert patch_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_022_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.1',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1'),
        (expected_path / 'ref_022_l3out_bgp_config_to_dcpe_2_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.5',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.5'),
    ], indirect=['expected'])
    def test_022_l3out_fabric_external_bgp_weight(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_022_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_023_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.1',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1'),
        (expected_path / 'ref_023_l3out_bgp_config_to_dcpe_2_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.5',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.5'),
    ], indirect=['expected'])
    def test_023_l3out_fabric_external_bgp_timers(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_023_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_024_l3out_bgp_config_to_dcpe_1_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.1',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.1'),
        (expected_path / 'ref_024_l3out_bgp_config_to_dcpe_2_border_sw_1.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=172.16.0.5',
         'tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=172.16.0.5'),
    ], indirect=['expected'])
    def test_024_l3out_fabric_external_bgp_password(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_024_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        data['tailf-ned-cisco-nx:neighbor'][0]['password']['passwd'] = ".*"
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_025_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
        (expected_path / 'ref_025_l3out_bgpv6_config_to_dcpe_2_border_sw_2.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A5%3A%3A1'),
        (expected_path / 'ref_025_l3out_bgpv6_port_channel_config_to_dcpe_1_border_sw_2.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=501.3'),
        (expected_path / 'ref_025_l3out_bgpv6_port_channel_config_to_dcpe_2_border_sw_2.json',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/port-channel=502.3'),
    ], indirect=['expected'])
    def test_025_l3out_fabric_external_bgpv6_config(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_026_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A4%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
        (expected_path / 'ref_026_l3out_bgpv6_config_to_dcpe_2_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A5%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A5%3A%3A1'),
    ], indirect=['expected'])
    def test_026_l3out_fabric_external_bgpv6_local_as(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_026_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_027_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A4%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
        (expected_path / 'ref_027_l3out_bgpv6_config_to_dcpe_2_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A5%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A5%3A%3A1'),
    ], indirect=['expected'])
    def test_027_l3out_fabric_external_bgpv6_peer_af_controls(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_027_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_028_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A4%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
        (expected_path / 'ref_028_l3out_bgpv6_config_to_dcpe_2_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A5%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A5%3A%3A1'),
    ], indirect=['expected'])
    def test_028_l3out_fabric_external_bgpv6_bfd(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_028_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, patch_path, get_path', [
        (expected_path / 'ref_029_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A4%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
    ], indirect=['expected'])
    def test_029_l3out_fabric_external_bgpv6_disable_connected_check(self, expected, patch_path, get_path):
        post_resp = self.nso.patch(
            payload=self.payload_path / 'test_029_config.json', path=patch_path, params='')
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 204
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_030_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A4%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
        (expected_path / 'ref_030_l3out_bgpv6_config_to_dcpe_2_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A5%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A5%3A%3A1'),
    ], indirect=['expected'])
    def test_030_l3out_fabric_external_bgpv6_weight(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_030_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_031_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A4%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
        (expected_path / 'ref_031_l3out_bgpv6_config_to_dcpe_2_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A5%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A5%3A%3A1'),
    ], indirect=['expected'])
    def test_031_l3out_fabric_external_bgpv6_timers(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_031_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert json.loads(get_resp.text) == expected

    @mark.parametrize('expected, post_path, get_path', [
        (expected_path / 'ref_032_l3out_bgpv6_config_to_dcpe_1_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A4%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A4%3A%3A1'),
        (expected_path / 'ref_032_l3out_bgpv6_config_to_dcpe_2_border_sw_2.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/vrf-config=tcell-grt/routing/bgp=2001%3Adb8%3Acafe%3A5%3A%3A1',
         'tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001%3Adb8%3Acafe%3A5%3A%3A1'),
    ], indirect=['expected'])
    def test_032_l3out_fabric_external_bgpv6_password(self, expected, post_path, get_path):
        post_resp = self.nso.post(
            payload=self.payload_path / 'test_032_config.json', path=post_path, params='', action=False)
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        data['tailf-ned-cisco-nx:neighbor'][0]['password']['passwd'] = ".*"
        assert post_resp.status_code == 201
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, get_path', [
        (expected_path / 'ref_033_l3out_static_route_ipv4_sw_1.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:vrf'),
        (expected_path / 'ref_033_l3out_static_route_ipv4_sw_2.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:vrf'),
    ], indirect=['expected'])
    def test_033_l3out_static_route_ipv4(self, expected, get_path):
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, get_path', [
        (expected_path / 'ref_034_l3out_static_route_ipv6_sw_3.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:vrf'),
        (expected_path / 'ref_034_l3out_static_route_ipv6_sw_4.json',
         'tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:vrf'),
    ], indirect=['expected'])
    def test_034_l3out_static_route_ipv6(self, expected, get_path):
        get_resp = self.nso.get(path=get_path)
        data = json.loads(get_resp.text)
        assert get_resp.status_code == 200
        assert data == expected

    @mark.parametrize('expected, patch_path', [
        (expected_path / 'ref_035_bd_service_4_error.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0002_TURKCELL/bridge-domain=BD-SERVICE-6/routing')
    ], indirect=['expected'])
    def test_035_l3out_static_route_ipv4_node_error(self, expected, patch_path):
        resp = self.nso.patch(
            payload=self.payload_path / 'test_035_config.json', path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, patch_path', [
        (expected_path / 'ref_036_bd_service_5_error.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0002_TURKCELL/bridge-domain=BD-SERVICE-5/routing')
    ], indirect=['expected'])
    def test_036_l3out_static_route_ipv6_node_error(self, expected, patch_path):
        resp = self.nso.patch(
            payload=self.payload_path / 'test_036_config.json', path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, patch_path', [
        (expected_path / 'ref_037_bd_service_4_error.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0002_TURKCELL/bridge-domain=BD-SERVICE-4/routing')
    ], indirect=['expected'])
    def test_037_l3out_static_route_ipv4_address_family_error(self, expected, patch_path):
        resp = self.nso.patch(
            payload=self.payload_path / 'test_037_config.json', path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, patch_path', [
        (expected_path / 'ref_038_bd_service_5_error.json',
         'cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric/tenant-service=0002_TURKCELL/bridge-domain=BD-SERVICE-5/routing')
    ], indirect=['expected'])
    def test_038_l3out_static_route_ipv6_address_family_error(self, expected, patch_path):
        resp = self.nso.patch(
            payload=self.payload_path / 'test_038_config.json', path=patch_path, params='')
        assert resp.status_code == 400
        assert json.loads(resp.text) == expected
