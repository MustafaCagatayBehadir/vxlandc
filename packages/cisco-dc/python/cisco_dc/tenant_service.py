import ncs
import _ncs
import ncs.maapi as maapi
import re

from .diff_iterate import DiffIterator


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
            for _data in _di._data:
                if site in _data['kp'] and tenant in _data['kp'] and 'bridge-domain' in _data['kp']:
                    raise Exception(
                        f'Tenant {tenant} can not be deleted because there are bridge-domains under it.')
