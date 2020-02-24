import pandas as pd
from nubia import command, argument, context
import typing


@argument(
    "engine",
    description="which analytical engine to use",
    choices=["pandas"],
)
@argument(
    "datacenter", description="Space separated list of datacenters to qualify"
)
@argument("hostname", description="Space separated list of hostnames to qualify")
@argument(
    "start_time", description="Start of time window in YYYY-MM-dd HH:mm:SS pformat"
)
@argument(
    "end_time", description="End of time window in YYYY-MM-dd HH:mm:SS pformat"
)
@argument(
    "view",
    description="view all records or just the latest",
    choices=["all", "changes", "latest"],
)
@argument("columns", description="Space separated list of columns, * for all")
@argument(
    "format",
    description="select the pformat of the output",
    choices=["text", "json", "csv"],
)
class SqCommand:
    """Base Command Class for use with all verbs"""
    datacenter = None
    hostname = None
    columns = None

    def __init__(
            self,
            engine: str = "",
            hostname: str = "",
            start_time: str = "",
            end_time: str = "",
            view: str = "latest",
            datacenter: str = "",
            format: str = "",
            columns: str = "default",
            sqobj=None,
    ) -> None:
        self.ctxt = context.get_context()
        self._cfg = self.ctxt.cfg
        self._schemas = self.ctxt.schemas

        if not isinstance(datacenter, str):
            print('datacenter must be a space separated list of strings')
            return
        if not isinstance(hostname, str):
            print('hostname must be a space separated list of strings')
            return
        if not isinstance(columns, str):
            print('columns must be a space separated list of strings')
            return

        if not datacenter and self.ctxt.datacenter:
            self.datacenter = self.ctxt.datacenter
        else:
            self.datacenter = datacenter.split()
        if not hostname and self.ctxt.hostname:
            self.hostname = self.ctxt.hostname
        else:
            self.hostname = hostname.split()

        if not start_time and self.ctxt.start_time:
            self.start_time = self.ctxt.start_time
        else:
            self.start_time = start_time

        if not end_time and self.ctxt.end_time:
            self.end_time = self.ctxt.end_time
        else:
            self.end_time = end_time

        self.view = view
        self.columns = columns.split()
        self.format = format or "text"

        if not sqobj:
            raise AttributeError('mandatory parameter sqobj missing')

        self.sqobj = sqobj(context=self.ctxt,
                           hostname=self.hostname,
                           start_time=self.start_time,
                           end_time=self.end_time,
                           view=self.view,
                           datacenter=self.datacenter,
                           columns=self.columns)

    @property
    def cfg(self):
        return self._cfg

    @property
    def schemas(self):
        return self._schemas

    def _gen_output(self, df: pd.DataFrame):
        if self.format == 'json':
            print(df.to_json(orient="records"))
        elif self.format == 'csv':
            print(df.to_csv())
        elif self.format == 'dataframe':
            return df
        else:
            print(df)
        if df.columns.to_list() == ['error']:
            return 1
        return 0

    def show(self, **kwargs):
        raise NotImplementedError

    def analyze(self, **kwargs):
        raise NotImplementedError

    def aver(self, **kwargs):
        raise NotImplementedError

    def summarize(self, **kwargs):
        raise NotImplementedError

    def top(self, **kwargs):
        raise NotImplementedError

    @command("unique", help="find the list of unique items in a colum")
    def unique(self, **kwargs):
        column = None
        if self.columns == ['default']:
            return self._gen_output(pd.DataFrame.from_dict(
                {'error': ['ERROR: Must specify columns with unique']},
                orient='columns'))
        if len(self.columns) > 1:
            return self._gen_output(pd.DataFrame.from_dict(
                {'error': ['ERROR: Specify a single column with unique']},
                orient='columns'))
        column = self.columns[0]
        format = self.format
        self.format = 'dataframe'
        df = self.show(**kwargs)
        self.format = format
        if column in df.columns:
            r = df[column].unique()
            if isinstance(r, pd.Categorical):
                r = r.categories
            return self._gen_output(pd.DataFrame({column: r}))
        return self._gen_output(pd.DataFrame())
