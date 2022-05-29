import imp
import ncs
import _ncs
import ncs.maapi as maapi
import re


class DiffIterator:
    def __init__(self):
        self._data = []

    def __call__(self, kp, op, ov, nv):
        self._data.append({
            "kp": str(kp),
            "op": op,
            "ov": ncs.maagic.as_pyval(ov) if ov else "",
            "nv": ncs.maagic.as_pyval(nv) if nv else ""
        })


class TenantServiceValidator(object):
    def __init__(self, log):
        self.log = log

    def cb_validate(self, tctx, kp, newval):
        '''
        Validating tenant service can not be deleted if it has bridge domains under it
        '''

        try:
            self.log.debug("Validating tenant service")
            m = maapi.Maapi()
            th = m.attach(tctx)

            self.log.info('Tenant service validation kp: ', str(kp))
            # raise Exception("Tenant has bd")
            self._is_tenant_used(th)

        except Exception as e:
            self.log.error(e)
            raise
        return _ncs.OK

    def _is_tenant_used(self, th):
        """Function to check if tenant has bd

        Args:
            th: ncs.maapi.Transaction

        """
        _di = DiffIterator()
        th.diff_iterate(_di, ncs.ITER_WANT_ATTR)
        tenant_delete_regex = "{'kp': '\/cisco-dc:dc-site{.*}\/tenant-service{.*}', 'op': 2, 'ov': '', 'nv': ''}"
        flag = False
        for _data in _di._data:
            if re.match(tenant_delete_regex, str(_data)):
                kp = _data['kp']
                site = kp[kp.find('{')+1:kp.find('}')]
                tenant = kp[kp.rfind('{')+1:kp.rfind('}')]
                self.log.info(f'Site {site} tenant {tenant} is deleted.')
                flag = True
                break
        if flag:
            bd_delete_regex = "{'kp': '\/ralloc:resource-pools\/idalloc:id-pool{.*}\/allocation{.*}', 'op': 2, 'ov': '', 'nv': ''}"
            for _data in _di._data:
                if re.match(bd_delete_regex, str(_data)):
                    if site in _data['kp'] and tenant in _data['kp']:
                        raise Exception(
                            f'Tenant {tenant} can not be deleted because there are bridge-domains under it.')
