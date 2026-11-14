import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model

tbl = model.Tables.Find('BOB_OUT')
if not tbl:
    print("Table BOB_OUT introuvable")
    srv.Disconnect()
    exit()

# Lire la M query actuelle
part = list(tbl.Partitions)[0]
current_expr = part.Source.Expression
print("=== M Query actuelle BOB_OUT (fin) ===")
print(current_expr[-300:])
print("\n=== Ajout colonne MainAccount ===")

# Ajouter l'extraction du MainAccount depuis LedgerDimensionValuesJson
# On cherche le dernier "in" et on insère avant
# Pattern: ajouter une étape Table.AddColumn avant le dernier "in"

lines = current_expr.strip().split('\n')
# Trouver la ligne "in" finale
in_idx = -1
for i in range(len(lines)-1, -1, -1):
    if lines[i].strip().startswith('in'):
        in_idx = i
        break

new_expr = """let
    Source = OData.Feed(
        "https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType",
        null, [Implementation="2.0"]
    ),
    AddedMainAccount = Table.AddColumn(Source, "MainAccount", each try Json.Document([LedgerDimensionValuesJson]){0}[MAINACCOUNT] otherwise null, type text)
in
    AddedMainAccount"""
part.Source.Expression = new_expr
print("Colonne MainAccount ajoutée")
print("=== Nouvelle fin M Query ===")
print(new_expr[-400:])

model.SaveChanges()
print("\nSauvegarde OK")
srv.Disconnect()
