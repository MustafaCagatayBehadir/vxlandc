vrf_config_template = """
<group name="results">
vrf {{ vrf }}
</group>
"""

route_table_template = """
<group name="results" method="table">
Routing entry for {{ network | re("IP") }}/{{ mask }}
</group>
"""

route_table_longer_template = """
<group name="results" method="table">
{{ protocol }} {{ network | re("IP") }}/{{ mask }} {{ ignore(".*") }}
</group>
"""