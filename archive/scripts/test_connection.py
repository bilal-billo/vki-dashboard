#!/usr/bin/env python3
"""
Test script to verify Power BI MCP server setup
"""
from pathlib import Path
import sys
import os

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("=" * 60)
    print("Power BI MCP Server - Setup Verification")
    print("=" * 60)
    print()
    
    issues = []
    
    # Check Python version
    print("✓ Checking Python version...")
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
        print(f"  ❌ Python {sys.version_info.major}.{sys.version_info.minor} found (3.8+ required)")
    else:
        print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor} found")
    
    # Check pythonnet
    print("\n✓ Checking pythonnet...")
    try:
        import clr
        print("  ✅ pythonnet is installed")
    except ImportError:
        issues.append("pythonnet not installed")
        print("  ❌ pythonnet not found. Run: pip install pythonnet")
    
    # Check MCP SDK
    print("\n✓ Checking MCP SDK...")
    try:
        import mcp
        print("  ✅ MCP SDK is installed")
    except ImportError:
        issues.append("MCP SDK not installed")
        print("  ❌ MCP SDK not found. Run: pip install mcp")
    
    # Check TOM_DLL_PATH environment variable
    print("\n✓ Checking TOM_DLL_PATH environment variable...")
    tom_path = os.environ.get("TOM_DLL_PATH")
    if tom_path:
        print(f"  ✅ TOM_DLL_PATH is set: {tom_path}")
        if not os.path.exists(tom_path):
            issues.append("TOM_DLL_PATH points to non-existent directory")
            print(f"  ⚠️  Warning: Path does not exist")
    else:
        print("  ⚠️  TOM_DLL_PATH not set (using default paths)")
    
    # Check for Power BI workspaces
    print("\n✓ Checking for Power BI Desktop...")
    pbi_workspace_path = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Microsoft",
        "Power BI Desktop",
        "AnalysisServicesWorkspaces"
    )
    
    if os.path.exists(pbi_workspace_path):
        workspaces = [d for d in os.listdir(pbi_workspace_path) 
                     if os.path.isdir(os.path.join(pbi_workspace_path, d))]
        if workspaces:
            print(f"  ✅ Found {len(workspaces)} Power BI workspace(s)")
        else:
            print("  ⚠️  No active Power BI workspaces found")
            print("     Make sure Power BI Desktop is running with a file open")
    else:
        issues.append("Power BI workspace directory not found")
        print("  ❌ Power BI Desktop workspace directory not found")
        print("     Is Power BI Desktop installed?")
    
    return issues


def test_connection():
    """Test connection to Power BI Desktop."""
    print("\n" + "=" * 60)
    print("Testing Connection to Power BI Desktop")
    print("=" * 60)
    print()
    
    try:
        from powerbi_mcp.powerbi_connector import PowerBIConnector
        
        print("Attempting to connect to Power BI Desktop...")
        connector = PowerBIConnector()
        result = connector.connect()
        
        if result["success"]:
            print("\n✅ SUCCESS! Connected to Power BI Desktop")
            print(f"\nModel Information:")
            print(f"  Name: {result['model_name']}")
            print(f"  Compatibility Level: {result['compatibility_level']}")
            print(f"  Tables: {result['tables_count']}")
            print(f"  Measures: {result['measures_count']}")
            
            # Try to list tables
            print(f"\nListing tables...")
            tables = connector.list_tables()
            print(f"  Found {len(tables)} table(s):")
            for table in tables[:5]:
                print(f"    - {table['name']} ({table['columns_count']} columns)")
            
            if len(tables) > 5:
                print(f"    ... and {len(tables) - 5} more")
            
            connector.disconnect()
            
            return True
        else:
            print(f"\n❌ Connection failed: {result['error']}")
            print("\nTroubleshooting tips:")
            print("  1. Ensure Power BI Desktop is running")
            print("  2. Open a .pbix file in Power BI Desktop")
            print("  3. Check if Analysis Services libraries are installed")
            print("  4. Verify TOM_DLL_PATH environment variable")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Error during connection test: {str(e)}")
        print("\nThis might be due to:")
        print("  - Missing Analysis Services libraries")
        print("  - Incorrect TOM_DLL_PATH")
        print("  - Power BI Desktop not running")
        
        import traceback
        print("\nFull error trace:")
        traceback.print_exc()
        
        return False


def test_dax_optimizer():
    """Test the DAX optimizer."""
    print("\n" + "=" * 60)
    print("Testing DAX Optimizer")
    print("=" * 60)
    print()
    
    try:
        from powerbi_mcp.dax_optimizer import DAXOptimizer
        
        optimizer = DAXOptimizer()
        
        test_dax = """
        CALCULATE(
            SUM(Sales[Amount]),
            FILTER(ALL(Product[Category]), Product[Category] = "Electronics")
        )
        """
        
        print("Analyzing sample DAX expression...")
        result = optimizer.optimize(test_dax)
        
        print(f"\n✅ DAX Optimizer working")
        print(f"  Complexity: {result['complexity']['level']}")
        print(f"  Issues found: {len(result['issues'])}")
        
        if result['suggestions']:
            print(f"  Sample suggestion: {result['suggestions'][0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing DAX optimizer: {str(e)}")
        return False


def main():
    """Run all tests."""
    print()
    
    # Check prerequisites
    issues = check_prerequisites()
    
    # Test DAX optimizer (doesn't require Power BI connection)
    dax_ok = test_dax_optimizer()
    
    # Test Power BI connection
    connection_ok = test_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print()
    
    if not issues and connection_ok and dax_ok:
        print("✅ ALL TESTS PASSED!")
        print("\nYour Power BI MCP Server is ready to use!")
        print("\nNext steps:")
        print("  1. Add the server to your Claude Desktop config")
        print("  2. Restart Claude Desktop")
        print("  3. Start chatting with your Power BI models!")
        print("\nSee INSTALLATION.md for Claude Desktop configuration.")
    else:
        print("⚠️  SOME ISSUES FOUND\n")
        
        if issues:
            print("Prerequisites issues:")
            for issue in issues:
                print(f"  - {issue}")
        
        if not connection_ok:
            print("\n❌ Power BI connection failed")
            print("   Review the troubleshooting tips above")
        
        if not dax_ok:
            print("\n❌ DAX optimizer test failed")
        
        print("\nPlease fix the issues above and run this test again.")
        print("See INSTALLATION.md for detailed setup instructions.")
    
    print()


if __name__ == "__main__":
    main()
