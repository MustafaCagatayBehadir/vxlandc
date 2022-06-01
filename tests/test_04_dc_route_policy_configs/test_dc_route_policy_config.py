import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


class DCRoutePolicyConfigsTests:
    """
    A Test Class for NSO dc-route-policy service
    """

    payload_path = Path.cwd() / "tests" / "test_04_dc_route_policy_configs" / "payload"
    expected_path = Path.cwd() / "tests" / "test_04_dc_route_policy_configs" / "expected"
    nso = NsoRestconfCall()

    @classmethod
    def setup_class(cls):
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_dc_route_policy_config.json",
            path="",
            params="",
        )
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_vrf_route_policy_config.json",
            path="",
            params="",
        ),
        cls.nso.patch(
            payload=cls.payload_path / "test_setup_bgp_route_policy_config.json",
            path="",
            params="",
        )

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_001_dc_route_policy_service_sw_1.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:route-map'),
        (expected_path / 'ref_001_dc_route_policy_service_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:route-map'),
        (expected_path / 'ref_001_dc_route_policy_service_sw_3.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:route-map'),
        (expected_path / 'ref_001_dc_route_policy_service_sw_4.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:route-map'),
        (expected_path / 'ref_001_dc_route_policy_service_blf_sw_1.json',
         '/tailf-ncs:devices/device=nw_blf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:route-map'),
        (expected_path / 'ref_001_dc_route_policy_service_blf_sw_2.json',
         '/tailf-ncs:devices/device=nw_blf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:route-map')
    ], indirect=['expected'])
    def test_001_dc_route_policy_route_map(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_002_vrf_dc_route_policy_sw_1.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/address-family'),
        (expected_path / 'ref_002_vrf_dc_route_policy_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/address-family'),
        (expected_path / 'ref_002_vrf_dc_route_policy_sw_3.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/address-family'),
        (expected_path / 'ref_002_vrf_dc_route_policy_sw_4.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/address-family'),
    ], indirect=['expected'])
    def test_002_vrf_dc_route_policy(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_003_bgp_dc_route_policy_sw_1.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2/address-family'),
        (expected_path / 'ref_003_bgp_dc_route_policy_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2/address-family'),
        (expected_path / 'ref_003_bgp_dc_route_policy_sw_3.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2/address-family'),
        (expected_path / 'ref_003_bgp_dc_route_policy_sw_4.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=2001:db8:cafe::2/address-family'),
    ], indirect=['expected'])
    def test_003_bgp_dc_route_policy(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_004_bgp_dc_route_policy_prefix_list_sw_1.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:ip/prefix-list'),
        (expected_path / 'ref_004_bgp_dc_route_policy_prefix_list_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:ip/prefix-list'),
        (expected_path / 'ref_004_bgp_dc_route_policy_prefix_list_sw_3.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_003.dsslab_site1/config/tailf-ned-cisco-nx:ipv6/prefix-list'),
        (expected_path / 'ref_004_bgp_dc_route_policy_prefix_list_sw_4.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_004.dsslab_site1/config/tailf-ned-cisco-nx:ipv6/prefix-list'),
    ], indirect=['expected'])
    def test_004_dc_route_policy_prefix_list(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected    

    # @classmethod
    # def teardown_class(cls):
    #     cls.nso.delete(path="cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric")
    #     cls.nso.delete(path="resource-allocator:resource-pools")