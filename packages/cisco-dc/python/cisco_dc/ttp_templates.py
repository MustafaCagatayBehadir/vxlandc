"""
<vars>
# Definition of protocol field regular expression
PROTO = "[A-Z]" 
</vars>
"""

vrf_config_template = """
<group name="results">
vrf {{ vrf }}
</group>
"""

route_table_template = """
<group name="results" method="table">
Routing entry for {{ network }}/{{ mask }}
Known via {{ protocol }} {{ignore}}
</group>
"""

route_table_longer_template = """
<group name="results" method="table">
{{ protocol | re("PROTO") }} {{ network }}/{{ mask }}
</group>
"""