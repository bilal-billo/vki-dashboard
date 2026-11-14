import clr, sys
sys.path.append(r'C:\Program Files\Microsoft SQL Server Management Studio 21\Release\Common7\IDE')
clr.AddReference('Microsoft.AnalysisServices.Tabular')
import Microsoft.AnalysisServices.Tabular as TOM_NS
import System.Globalization as Glob
import System.Threading as Thr
Thr.Thread.CurrentThread.CurrentCulture = Glob.CultureInfo.GetCultureInfo('en-US')

srv = TOM_NS.Server()
srv.Connect('localhost:49640')
db = srv.Databases[0]
m = db.Model

def upsert_measure(table_name, name, expr, fmt=None, desc=None):
    t = m.Tables[table_name]
    existing = None
    for ms in t.Measures:
        if ms.Name == name:
            existing = ms
            break
    if existing:
        existing.Expression = expr
        if fmt: existing.FormatString = fmt
        if desc: existing.Description = desc
        print(f"  Updated: {name}")
    else:
        ms = TOM_NS.Measure()
        ms.Name = name
        ms.Expression = expr
        if fmt: ms.FormatString = fmt
        if desc: ms.Description = desc
        t.Measures.Add(ms)
        print(f"  Added:   {name}")

# ========== MESURES PLANNING ==========

# 1. Approved Milestones — montant des milestones Posted (= Approved dans CSV)
upsert_measure('Milestones', 'Approved Milestones',
    'CALCULATE(SUM(Milestones[Amount]), Milestones[MilestoneStatus] = "Posted")',
    '"€"#,0.00',
    'Sum of milestone amounts with status=Posted')

# 2. Planned Milestones — montant total planifié (tous statuts)
upsert_measure('Milestones', 'Planned Milestones',
    'SUM(Milestones[Amount])',
    '"€"#,0.00',
    'Sum of all milestone amounts')

# 3. Requested Amount — montant Billed Sales depuis msdyn_actual (= "Requested" dans Reporting Schedule)
upsert_measure('Milestones', 'Requested Amount',
    '''CALCULATE(
    SUM(msdyn_actual[Amount]),
    msdyn_actual[Transaction Type] = "Billed Sales"
)''',
    '"€"#,0.00',
    'Billed Sales from msdyn_actual = amount submitted to client')

# 4. Not Ready Count — nb milestones pas encore prêts
upsert_measure('Milestones', 'Not Ready Count',
    'CALCULATE(COUNTROWS(Milestones), Milestones[MilestoneStatus] = "Not Ready")',
    '0',
    'Count of Not Ready milestones')

# 5. Posted Count — nb milestones posted/approved
upsert_measure('Milestones', 'Posted Count',
    'CALCULATE(COUNTROWS(Milestones), Milestones[MilestoneStatus] = "Posted")',
    '0',
    'Count of Posted (Approved) milestones')

# 6. Milestone Completion % — % du montant total qui est approuvé
upsert_measure('Milestones', 'Milestone Completion %',
    '''DIVIDE(
    CALCULATE(SUM(Milestones[Amount]), Milestones[MilestoneStatus] = "Posted"),
    SUM(Milestones[Amount]),
    0
)''',
    '0.0%',
    'Approved amount / Total planned amount')

m.SaveChanges()
print("\nSaveChanges() OK — mesures Planning ajoutées")
srv.Disconnect()
