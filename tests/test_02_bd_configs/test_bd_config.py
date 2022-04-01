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
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:vlan'),
        (expected_path / 'ref_001_vlan_bd_service_sw_2.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-02/config/tailf-ned-cisco-nx:vlan'),
        (expected_path / 'ref_001_vlan_bd_service_sw_3.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-03/config/tailf-ned-cisco-nx:vlan'),
        (expected_path / 'ref_001_vlan_bd_service_sw_4.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-04/config/tailf-ned-cisco-nx:vlan')       
    ], indirect=['expected'])
    def test_001_vlan(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_002_nve_bd_service_sw_1.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:interface/nve=1/member'),
        (expected_path / 'ref_002_nve_bd_service_sw_2.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-02/config/tailf-ned-cisco-nx:interface/nve=1/member'),
        (expected_path / 'ref_002_nve_bd_service_sw_3.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-03/config/tailf-ned-cisco-nx:interface/nve=1/member'),
        (expected_path / 'ref_002_nve_bd_service_sw_4.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-04/config/tailf-ned-cisco-nx:interface/nve=1/member')       
    ], indirect=['expected'])
    def test_002_nve(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_003_evpn_bd_service_sw_1.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:evpn/vni'),
        (expected_path / 'ref_003_evpn_bd_service_sw_2.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-02/config/tailf-ned-cisco-nx:evpn/vni'),
        (expected_path / 'ref_003_evpn_bd_service_sw_3.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-03/config/tailf-ned-cisco-nx:evpn/vni'),
        (expected_path / 'ref_003_evpn_bd_service_sw_4.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-04/config/tailf-ned-cisco-nx:evpn/vni')       
    ], indirect=['expected'])
    def test_003_evpn(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_004_svi_bd_service_sw_1.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:interface/Vlan'),
        (expected_path / 'ref_004_svi_bd_service_sw_2.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-02/config/tailf-ned-cisco-nx:interface/Vlan')      
    ], indirect=['expected'])
    def test_004_svi(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_005_vrf_bd_service_sw_1.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:vrf'),
        (expected_path / 'ref_005_vrf_bd_service_sw_2.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-02/config/tailf-ned-cisco-nx:vrf')      
    ], indirect=['expected'])
    def test_005_vrf(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected

    @mark.parametrize('expected, path', [
        (expected_path / 'ref_006_bgp_bd_service_sw_1.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-01/config/tailf-ned-cisco-nx:router/bgp=64541/vrf=tcell-grt'),
        (expected_path / 'ref_006_bgp_bd_service_sw_2.json',
         'tailf-ncs:devices/device=AVR-DSS1-BIP-SW-02/config/tailf-ned-cisco-nx:router/bgp=64541/vrf=tcell-grt')      
    ], indirect=['expected'])
    def test_006_bgp(self, expected, path):
        resp = self.nso.get(path=path)
        assert resp.status_code == 200
        assert json.loads(resp.text) == expected  

    # @classmethod
    # def teardown_class(cls):
    #     cls.nso.delete(path="cisco-dc:dc-site=avr-dss1-lbox-yaani-fabric")
    #     cls.nso.delete(path="resource-allocator:resource-pools")
