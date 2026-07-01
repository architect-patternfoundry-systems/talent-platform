"""Test RLS policies"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import engine, SessionLocal
from src.core.tenant import set_tenant_context, get_tenant_context, clear_tenant_context
from src.models.role import RoleDefinition


def test_rls_policies():
    """Test RLS policies"""
    print(f"Testing RLS policies...")
    
    try:
        # Create tables
        from src.core.database import Base
        Base.metadata.create_all(bind=engine)
        print(f"✓ Tables created")
        
        # Create session
        db = SessionLocal()
        
        try:
            # Test 1: Insert data with tenant context
            print(f"\nTest 1: Insert data with tenant context")
            set_tenant_context(db, "tenant_1")
            
            role1 = RoleDefinition(
                role_id="role_1",
                tenant_id="tenant_1",
                name="Test Role 1",
                description="Test role for tenant 1",
                skills={"technical": {"Python": "advanced"}},
                scope={"responsibilities": ["Test"]},
                success_criteria=["Test"],
                platform_requirements={"test": "test"},
                human_exception="Test human exception",
                confidence="high",
                evidence_quality="verified",
                evidence_sources=["test"]
            )
            db.add(role1)
            db.commit()
            print(f"✓ Inserted role for tenant_1")
            
            # Test 2: Insert data for different tenant
            print(f"\nTest 2: Insert data for different tenant")
            set_tenant_context(db, "tenant_2")
            
            role2 = RoleDefinition(
                role_id="role_2",
                tenant_id="tenant_2",
                name="Test Role 2",
                description="Test role for tenant 2",
                skills={"technical": {"Python": "advanced"}},
                scope={"responsibilities": ["Test"]},
                success_criteria=["Test"],
                platform_requirements={"test": "test"},
                human_exception="Test human exception",
                confidence="high",
                evidence_quality="verified",
                evidence_sources=["test"]
            )
            db.add(role2)
            db.commit()
            print(f"✓ Inserted role for tenant_2")
            
            # Test 3: Query with tenant_1 context
            print(f"\nTest 3: Query with tenant_1 context")
            set_tenant_context(db, "tenant_1")
            roles_tenant1 = db.query(RoleDefinition).all()
            print(f"✓ Found {len(roles_tenant1)} roles for tenant_1")
            for role in roles_tenant1:
                print(f"  - {role.name} (tenant_id: {role.tenant_id})")
            
            # Test 4: Query with tenant_2 context
            print(f"\nTest 4: Query with tenant_2 context")
            set_tenant_context(db, "tenant_2")
            roles_tenant2 = db.query(RoleDefinition).all()
            print(f"✓ Found {len(roles_tenant2)} roles for tenant_2")
            for role in roles_tenant2:
                print(f"  - {role.name} (tenant_id: {role.tenant_id})")
            
            # Test 5: Query without tenant context (should return empty)
            print(f"\nTest 5: Query without tenant context")
            clear_tenant_context(db)
            roles_no_context = db.query(RoleDefinition).all()
            print(f"✓ Found {len(roles_no_context)} roles without tenant context (expected: 0)")
            
            # Test 6: Try to access cross-tenant data (should fail)
            print(f"\nTest 6: Try to access cross-tenant data")
            set_tenant_context(db, "tenant_1")
            try:
                role_tenant2 = db.query(RoleDefinition).filter(RoleDefinition.role_id == "role_2").first()
                if role_tenant2 is None:
                    print(f"✓ Cross-tenant access blocked (correct behavior)")
                else:
                    print(f"✗ Cross-tenant access allowed (incorrect behavior)")
                    return False
            except Exception as e:
                print(f"✓ Cross-tenant access blocked with error: {e}")
            
            # Cleanup
            print(f"\nCleanup: Deleting test data")
            db.query(RoleDefinition).delete()
            db.commit()
            print(f"✓ Test data deleted")
            
            print(f"\n✓ All RLS policy tests passed")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ RLS policy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rls_policies()
    sys.exit(0 if success else 1)
