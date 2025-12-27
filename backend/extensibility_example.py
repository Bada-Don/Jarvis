"""
Example demonstrating FunctionRegistry extensibility features.

This example shows how to:
1. Register functions with automatic schema generation
2. Add custom categories
3. Use placeholder functions
4. Import/export schemas
5. Unregister functions
"""

from function_registry import FunctionRegistry
from typing import List, Dict
import json


def main():
    print("=" * 70)
    print("FunctionRegistry Extensibility Features Demo")
    print("=" * 70)
    
    # Create registry
    registry = FunctionRegistry()
    
    # ========================================================================
    # 1. Automatic Schema Generation
    # ========================================================================
    print("\n1. AUTOMATIC SCHEMA GENERATION")
    print("-" * 70)
    
    def send_email(to: str, subject: str, body: str, cc: List[str] = None) -> dict:
        """Send an email message.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            body: Email body content
            cc: Optional list of CC recipients
        
        Returns:
            Result dictionary with success status
        """
        print(f"  Sending email to {to}: {subject}")
        return {"success": True, "message": "Email sent"}
    
    # Register with automatic schema generation
    registry.add_category("email_operations")
    registry.register_function_auto(
        name="send_email",
        implementation=send_email,
        category="email_operations"
    )
    
    print("✓ Registered 'send_email' with auto-generated schema")
    
    # Show generated schema
    schema = registry.get_schema("send_email")
    print(f"  Description: {schema.description}")
    print(f"  Parameters: {list(schema.parameters['properties'].keys())}")
    print(f"  Required: {schema.parameters.get('required', [])}")
    
    # ========================================================================
    # 2. Custom Categories
    # ========================================================================
    print("\n2. CUSTOM CATEGORIES")
    print("-" * 70)
    
    # Add custom categories
    registry.add_category("network_operations")
    registry.add_category("database_operations")
    
    print("✓ Added custom categories:")
    print(f"  - network_operations")
    print(f"  - database_operations")
    
    # Register functions in custom categories
    def http_get(url: str, timeout: int = 30) -> dict:
        """Make an HTTP GET request.
        
        Args:
            url: URL to request
            timeout: Request timeout in seconds
        
        Returns:
            Response data
        """
        return {"success": True, "data": "response"}
    
    def db_query(query: str, params: Dict[str, str] = None) -> dict:
        """Execute a database query.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Query results
        """
        return {"success": True, "rows": []}
    
    registry.register_function_auto("http_get", http_get, "network_operations")
    registry.register_function_auto("db_query", db_query, "database_operations")
    
    print("✓ Registered functions in custom categories")
    
    # Show category summary
    summary = registry.get_category_summary()
    print("\nCategory Summary:")
    for category, count in sorted(summary.items()):
        if count > 0:
            print(f"  {category}: {count} function(s)")
    
    # ========================================================================
    # 3. Placeholder Functions
    # ========================================================================
    print("\n3. PLACEHOLDER FUNCTIONS")
    print("-" * 70)
    
    def future_feature(param: str) -> dict:
        """Feature to be implemented in the future.
        
        Args:
            param: Feature parameter
        
        Returns:
            Result dictionary
        """
        return {"success": False, "message": "Not implemented"}
    
    registry.register_function_auto(
        name="future_feature",
        implementation=future_feature,
        category="network_operations",
        is_placeholder=True
    )
    
    print("✓ Registered placeholder function: 'future_feature'")
    
    # List all placeholders
    placeholders = registry.get_placeholder_functions()
    print(f"  Total placeholders: {len(placeholders)}")
    for name in placeholders:
        print(f"    - {name}")
    
    # Try to validate placeholder (should fail)
    is_valid, error = registry.validate_parameters("future_feature", {"param": "test"})
    print(f"  Validation result: {is_valid}")
    print(f"  Error message: {error}")
    
    # ========================================================================
    # 4. Schema Export/Import
    # ========================================================================
    print("\n4. SCHEMA EXPORT/IMPORT")
    print("-" * 70)
    
    # Export schemas
    export_file = "function_schemas.json"
    registry.export_schemas(export_file)
    print(f"✓ Exported {registry.get_function_count()} schemas to '{export_file}'")
    
    # Show exported content (first schema only)
    with open(export_file, 'r') as f:
        exported = json.load(f)
    
    print(f"\nExample exported schema (first one):")
    print(json.dumps(exported[0], indent=2))
    
    # Create new registry and import
    new_registry = FunctionRegistry()
    count = new_registry.import_schemas(export_file)
    print(f"\n✓ Imported {count} schemas into new registry")
    print(f"  All imported functions are placeholders: {len(new_registry.get_placeholder_functions()) == count}")
    
    # ========================================================================
    # 5. Function Unregistration
    # ========================================================================
    print("\n5. FUNCTION UNREGISTRATION")
    print("-" * 70)
    
    print(f"Functions before unregistration: {registry.get_function_count()}")
    
    # Unregister a function
    result = registry.unregister_function("future_feature")
    print(f"✓ Unregistered 'future_feature': {result}")
    
    print(f"Functions after unregistration: {registry.get_function_count()}")
    
    # ========================================================================
    # 6. Complete API Overview
    # ========================================================================
    print("\n6. COMPLETE API OVERVIEW")
    print("-" * 70)
    
    print("\nExtensibility API Methods:")
    print("  ✓ register_function_auto()     - Auto-generate schema from function")
    print("  ✓ add_category()               - Add custom category")
    print("  ✓ remove_category()            - Remove category")
    print("  ✓ unregister_function()        - Remove function")
    print("  ✓ get_placeholder_functions()  - List placeholder functions")
    print("  ✓ export_schemas()             - Export schemas to JSON")
    print("  ✓ import_schemas()             - Import schemas from JSON")
    print("  ✓ get_category_summary()       - Get function counts by category")
    
    print("\nAll registered functions:")
    for name in sorted(registry.list_all_functions()):
        schema = registry.get_schema(name)
        placeholder = " [PLACEHOLDER]" if schema.is_placeholder else ""
        print(f"  - {name} ({schema.category}){placeholder}")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    
    # Cleanup
    import os
    if os.path.exists(export_file):
        os.unlink(export_file)


if __name__ == "__main__":
    main()
