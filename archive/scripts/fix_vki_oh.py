import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, Measure

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model
tbl = model.Tables.Find('_Measures')

def upsert_measure(name, expr):
    old = tbl.Measures.Find(name)
    if old:
        tbl.Measures.Remove(old)
        print(f"Supprimée [{name}]")
    m = Measure()
    m.Name = name
    m.Expression = expr
    tbl.Measures.Add(m)
    print(f"Créée   [{name}]")

# OH = coef_claimable - 1, par expense type et project type
upsert_measure('Direct Costs OH msdyn D365', """
SUMX(
    FILTER(
        msdyn_actual,
        msdyn_actual[Transaction Type] = "Cost"
        && NOT ISBLANK(msdyn_actual[Expense Type D365])
    ),
    VAR _exp  = msdyn_actual[Expense Type D365]
    VAR _proj = RELATED(Projects[ContractType])
    VAR _isT1T3    = _exp = "T1/T3 Manpower"
    VAR _isT5Subco = _exp = "T5 Subcontractors"
    VAR _isT4      = _exp IN {"T4 Amortization", "T4 Amortization ICT"}
    VAR _oh = SWITCH(TRUE(),
        LEFT(_proj, 2) = "EU",   IF(_isT5Subco, 0.0, 0.25),
        _proj = "FOD",            0.15,
        _proj = "PRODEX",         IF(_isT5Subco || _isT4, 0.0, 0.05),
        _proj = "RW",             IF(_isT1T3, BLANK(), 0.17),
        _proj = "VLAIO16",        IF(_isT1T3, BLANK(), 0.0),
        _proj = "VLAIO21",        IF(_isT1T3, BLANK(), 0.0),
        0.0
    )
    RETURN msdyn_actual[Amount] * _oh
)
""")

model.SaveChanges()
print("Sauvegarde OK")
srv.Disconnect()
