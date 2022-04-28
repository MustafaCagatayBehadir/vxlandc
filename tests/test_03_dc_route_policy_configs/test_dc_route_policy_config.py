import json
from pathlib import Path
from nsoapi import NsoRestconfCall
from pytest import mark
import json


class DCRoutePolicyConfigsTests:
    """
    A Test Class for NSO dc-route-policy service
    """

    payload_path = Path.cwd() / "tests" / "test_03_dc_route_policy_configs" / "payload"
    expected_path = Path.cwd() / "tests" / "test_03_dc_route_policy_configs" / "expected"
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
        )

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_001_dc_route_policy_service_sw_1.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:route-map'),
        (expected_path / 'ref_001_dc_route_policy_service_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:route-map'),
    ], indirect=['expected'])
    def test_001_vrf_dc_route_policy(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_002_vrf_bgp_dc_route_policy_sw_1.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_001.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt'),
        (expected_path / 'ref_002_vrf_bgp_dc_route_policy_sw_2.json',
         '/tailf-ncs:devices/device=nw_lf_cnx9_002.dsslab_site1/config/tailf-ned-cisco-nx:router/bgp=65001/vrf=tcell-grt'),
    ], indirect=['expected'])
    def test_002_vrf_bgp_dc_route_policy(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @classmethod
    def teardown_class(cls):
        cls.nso.delete(path="cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric")
        cls.nso.delete(path="resource-allocator:resource-pools")