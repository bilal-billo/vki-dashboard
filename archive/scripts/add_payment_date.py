import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()

import System.Globalization as Globalization
import System.Threading as Threading
Threading.Thread.CurrentThread.CurrentCulture = Globalization.CultureInfo.GetCultureInfo('en-US')

from Microsoft.AnalysisServices.Tabular import (
    Server, CalculatedColumn, DataType
)

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model
EN_US = Globalization.CultureInfo.GetCultureInfo('en-US')

actual_tbl = model.Tables.Find('msdyn_actual')

# Supprimer si existe déjà
old = actual_tbl.Columns.Find('Payment Date Finance')
if old:
    actual_tbl.Columns.Remove(old)
    print("Supprimée [Payment Date Finance]")

# Colonne calculée: date GL Finance via PINV voucher number
# GL_HEADER[SubledgerVoucher] = msdyn_actual[Voucher Number] pour les factures projet (PINV)
col = CalculatedColumn()
col.Name = 'Payment Date Finance'
col.DataType = DataType.DateTime
col.Locale = EN_US
col.Expression = """
LOOKUPVALUE(
    GL_HEADER[AccountingDate],
    GL_HEADER[SubledgerVoucher], [Voucher Number]
)
"""
col.FormatString = 'dd/mm/yyyy'
actual_tbl.Columns.Add(col)
print("Créée [msdyn_actual][Payment Date Finance]")
print("  Source: GL_HEADER[AccountingDate] via PINV voucher match")
print("  Avantage: date réelle Finance vs date milestone Project Operations")

model.SaveChanges()
print("\nSauvegarde OK")
print("\nUtilisation dans Table 1 (Payments In/Out):")
print("  Date → msdyn_actual[Payment Date Finance]  (au lieu de [Accounting Date])")
srv.Disconnect()
