import pandas as pd

from suzieq.sqobjects.basicobj import SqObject


class IfObj(SqObject):
    def __init__(self, **kwargs):
        super().__init__(table='interfaces', **kwargs)
        self._valid_get_args = ['namespace', 'hostname', 'ifname',
                                'state', 'type', ]
        self._valid_assert_args = ['namespace', 'hostname', 'start_time',
                                  'end_time', 'ifname', 'matchval', 'peerIfname']

    def summarize(self, namespace=[]):
        """Summarize routing info for one or more namespaces"""

        return self.engine_obj.summarize(namespace=namespace)

    def aver(self, what='mtu-match', **kwargs) -> pd.DataFrame:
        """Assert that interfaces are in good state"""
        try:
            self.validate_assert_input(**kwargs)
        except Exception as error:
            df = pd.DataFrame({'error': [f'{error}']})
            return df

        return self.engine_obj.aver(what=what, **kwargs)
