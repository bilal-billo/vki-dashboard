"""
Shared TOM/ADOMD client for VKI Dashboard scripts.
Auto-detects the correct PBI Desktop port by looking for the working file.
"""
import clr
import sys
import os

# TOM DLLs — prioritize SSMS, fallback to local
_DLL_PATHS = [
    r'C:\Program Files\Microsoft SQL Server Management Studio 21\Release\Common7\IDE',
    r'C:\Program Files\Microsoft SQL Server Management Studio 20\Common7\IDE',
    os.path.join(os.path.dirname(__file__), '..', '..', 'archive', 'dlls'),
]

def _load_dlls():
    for path in _DLL_PATHS:
        if os.path.exists(path):
            if path not in sys.path:
                sys.path.append(path)
            break

_load_dlls()
clr.AddReference('Microsoft.AnalysisServices.Tabular')
clr.AddReference('Microsoft.AnalysisServices.AdomdClient')

import Microsoft.AnalysisServices.Tabular as TOM_NS
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand
import System.Globalization as Glob
import System.Threading as Thr

# Fix locale — required before SaveChanges()
Thr.Thread.CurrentThread.CurrentCulture = Glob.CultureInfo.GetCultureInfo('en-US')

WORKING_FILE_HINT = 'VKi14112026'   # substring in the working PBI file name
PORTS_TO_TRY = range(49600, 49700)   # scan range on startup


def _detect_port(hint: str = WORKING_FILE_HINT) -> int:
    """Auto-detect PBI Desktop ADOMD port for the working file."""
    # 1. Try env var first
    env_port = os.environ.get('PBI_PORT_WORKING')
    if env_port:
        return int(env_port)

    # 2. Scan known range
    for port in [49640, 64303] + list(PORTS_TO_TRY):
        try:
            srv = TOM_NS.Server()
            srv.Connect(f'localhost:{port}')
            db = srv.Databases[0]
            name = db.Name
            srv.Disconnect()
            if hint.lower() in name.lower() or 'vki' in name.lower():
                return port
        except Exception:
            continue
    raise RuntimeError(
        f"Could not find PBI Desktop port for file containing '{hint}'. "
        "Make sure the .pbix is open in Power BI Desktop."
    )


class TOMClient:
    """Context manager for TOM (model modification) connections."""

    def __init__(self, port: int = None):
        self.port = port or _detect_port()
        self.srv = None
        self.model = None

    def __enter__(self):
        self.srv = TOM_NS.Server()
        self.srv.Connect(f'localhost:{self.port}')
        db = self.srv.Databases[0]
        self.model = db.Model
        print(f"[TOM] Connected to port {self.port} — model: {db.Name}")
        return self.model

    def __exit__(self, *_):
        if self.srv:
            self.srv.Disconnect()

    def save(self):
        """Save changes and disconnect."""
        if self.model:
            self.model.SaveChanges()
            print("[TOM] SaveChanges() OK")


class DAXClient:
    """Context manager for read-only DAX queries (ADOMD)."""

    def __init__(self, port: int = None):
        self.port = port or _detect_port()
        self.conn = None

    def __enter__(self):
        self.conn = AdomdConnection(f'Data Source=localhost:{self.port};')
        self.conn.Open()
        print(f"[DAX] Connected to port {self.port}")
        return self

    def __exit__(self, *_):
        if self.conn:
            self.conn.Close()

    def query(self, dax: str) -> list[list[str]]:
        """Execute a DAX query and return rows as list of string lists."""
        cmd = AdomdCommand(dax, self.conn)
        r = cmd.ExecuteReader()
        rows = []
        while r.Read():
            rows.append([str(r[i]) for i in range(r.FieldCount)])
        r.Close()
        return rows

    def scalar(self, dax: str):
        """Execute a DAX query returning a single value."""
        rows = self.query(dax)
        return rows[0][0] if rows else None
