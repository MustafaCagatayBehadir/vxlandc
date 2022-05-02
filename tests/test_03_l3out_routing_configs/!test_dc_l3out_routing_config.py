import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


class DCRoutePolicyConfigsTests:
    """
    A Test Class for NSO dc-route-policy service
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
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_001_l3out_bgp_config_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt/neighbor=10.0.0.2'),
        (expected_path / 'ref_001_l3out_bgp_loopback_config_sw_1.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:interface/loopback=100'),
        (expected_path / 'ref_001_l3out_bgp_loopback_config_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:interface/loopback=100'),
    ], indirect=['expected'])
    def test_001_l3out_bgp_config(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    # @mark.parametrize('expected, path', [
    #     (expected_path / 'ref_002_vrf_bgp_dc_route_policy_sw_1.json',
    #      '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt'),
    #     (expected_path / 'ref_002_vrf_bgp_dc_route_policy_sw_2.json',
    #      '/tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt'),
    # ], indirect=['expected'])
    # def test_002_vrf_bgp_dc_route_policy(self, expected, path):
    #     resp = self.nso.get(path=path)
    #     assert resp.status_code == 200
    #     assert json.loads(resp.text) == expected