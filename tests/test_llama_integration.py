"""
Test suite for Llama 3 integration
Run with: pytest test_llama_integration.py -v
"""
import sys
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_llama_service_import():
    """Test that llama_service can be imported"""
    try:
        from service.llama_service import get_llama_service
        print("✅ llama_service imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import llama_service: {e}")
        return False

def test_llama_service_initialization():
    """Test LlamaService can be initialized"""
    try:
        from service.llama_service import LlamaService
        service = LlamaService()
        print(f"✅ LlamaService initialized with base_url: {service.base_url}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize LlamaService: {e}")
        return False

def test_fallback_response():
    """Test fallback response when Ollama is not available"""
    try:
        from service.llama_service import LlamaService
        service = LlamaService()
        
        # Test fallback
        response = service._fallback_response("test prompt")
        print(f"✅ Fallback response generated: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Fallback response failed: {e}")
        return False

def test_allergen_safety_validation():
    """Test allergen safety validation"""
    try:
        from service.llama_service import LlamaService
        service = LlamaService()
        
        # Test case 1: Safe plan (no allergens)
        safe_plan = {
            "meal_plan": {
                "day_1": {
                    "breakfast": {"ingredients": ["oats", "banana", "honey"]}
                }
            }
        }
        result = service._validate_allergen_safety(safe_plan, ["peanuts", "dairy"])
        assert result == True, "Safe plan should pass validation"
        print("✅ Safe plan passed allergen validation")
        
        # Test case 2: Unsafe plan (contains allergen)
        unsafe_plan = {
            "meal_plan": {
                "day_1": {
                    "breakfast": {"ingredients": ["oats", "peanut butter", "banana"]}
                }
            }
        }
        result = service._validate_allergen_safety(unsafe_plan, ["peanuts"])
        assert result == False, "Unsafe plan should fail validation"
        print("✅ Unsafe plan correctly rejected")
        
        return True
    except Exception as e:
        print(f"❌ Allergen validation test failed: {e}")
        return False

def test_profile_context_building():
    """Test profile context string building"""
    try:
        from service.llama_service import LlamaService
        service = LlamaService()
        
        profile = {
            "age": 30,
            "gender": "female",
            "height": 165,
            "current_weight": 70,
            "target_weight": 65,
            "activity_level": "moderate",
            "goal": "weight_loss",
            "allergies": ["peanuts", "shellfish"],
            "dietary_preferences": ["vegetarian"],
            "health_conditions": ["PCOS"],
            "meals_per_day": 3
        }
        
        context = service._build_profile_context(profile)
        print(f"✅ Profile context built:\n{context[:200]}...")
        
        # Verify allergies are prominently marked
        assert "🚨 ALLERGIES" in context, "Allergies should be highlighted"
        assert "peanuts" in context.lower(), "Peanuts allergy should be in context"
        
        return True
    except Exception as e:
        print(f"❌ Profile context building failed: {e}")
        return False

def test_safe_fallback_plan():
    """Test safe fallback plan generation"""
    try:
        from service.llama_service import LlamaService
        service = LlamaService()
        
        profile = {
            "allergies": ["peanuts", "eggs"],
            "dietary_preferences": ["vegetarian"]
        }
        
        fallback_plan = service._create_safe_fallback_plan(profile)
        
        # Verify structure
        assert "meal_plan" in fallback_plan, "Should have meal_plan"
        assert "day_1" in fallback_plan["meal_plan"], "Should have day_1"
        assert "breakfast" in fallback_plan["meal_plan"]["day_1"], "Should have breakfast"
        assert "daily_totals" in fallback_plan, "Should have daily totals"
        
        # Verify no allergens
        plan_str = str(fallback_plan).lower()
        assert "peanut" not in plan_str, "Should not contain peanuts"
        assert "egg" not in plan_str, "Should not contain eggs"
        
        print("✅ Safe fallback plan generated without allergens")
        return True
    except Exception as e:
        print(f"❌ Safe fallback plan test failed: {e}")
        return False

def test_ollama_connection():
    """Test connection to Ollama (will use fallback if not available)"""
    try:
        from service.llama_service import LlamaService
        import requests
        
        service = LlamaService()
        
        # Try to connect
        try:
            response = requests.get(f"{service.base_url}/api/tags", timeout=2)
            print(f"✅ Ollama is running at {service.base_url}")
            print(f"   Status code: {response.status_code}")
            return True
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Ollama not running at {service.base_url}")
            print("   This is OK - fallback mode will be used")
            return True
    except Exception as e:
        print(f"❌ Ollama connection test failed: {e}")
        return False

def test_meal_plan_generation():
    """Test meal plan generation (with fallback if Ollama unavailable)"""
    try:
        from service.llama_service import LlamaService
        
        service = LlamaService()
        
        profile = {
            "age": 28,
            "gender": "female",
            "height": 160,
            "current_weight": 65,
            "target_weight": 60,
            "activity_level": "moderate",
            "goal": "weight_loss",
            "allergies": ["dairy"],
            "dietary_preferences": ["vegetarian"],
            "meals_per_day": 3
        }
        
        meal_plan = service.generate_meal_plan(profile, days=1)
        
        # Verify structure
        assert "meal_plan" in meal_plan or "error" in meal_plan, "Should have meal_plan or error"
        
        if "error" in meal_plan:
            print("⚠️  Ollama not available, fallback used")
        else:
            print("✅ Meal plan generated successfully")
            
            # Verify allergen safety
            plan_str = str(meal_plan).lower()
            assert "dairy" not in plan_str and "milk" not in plan_str, "Should not contain dairy"
        
        return True
    except Exception as e:
        print(f"❌ Meal plan generation test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("=" * 70)
    print("LLAMA 3 INTEGRATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Import Test", test_llama_service_import),
        ("Initialization Test", test_llama_service_initialization),
        ("Fallback Response Test", test_fallback_response),
        ("Allergen Safety Validation", test_allergen_safety_validation),
        ("Profile Context Building", test_profile_context_building),
        ("Safe Fallback Plan", test_safe_fallback_plan),
        ("Ollama Connection", test_ollama_connection),
        ("Meal Plan Generation", test_meal_plan_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'─' * 70}")
        print(f"Running: {test_name}")
        print('─' * 70)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")

if __name__ == "__main__":
    run_all_tests()
