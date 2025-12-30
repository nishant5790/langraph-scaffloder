#!/usr/bin/env python3
"""Simple test script to verify the LangGraph Agent Builder System."""

import asyncio
import sys
import traceback
from src.core import LangGraphAgentBuilder, ModelFactory, ToolManager
from src.models import AgentConfig, ModelConfig, ToolConfig, ModelProvider


async def test_basic_functionality():
    """Test basic system functionality without external dependencies."""
    print("🧪 Testing LangGraph Agent Builder System")
    print("=" * 50)
    
    try:
        # Test 1: Model Factory
        print("1. Testing Model Factory...")
        supported_models = ModelFactory.get_supported_models()
        assert ModelProvider.OPENAI in supported_models
        assert ModelProvider.BEDROCK in supported_models
        print("   ✅ Model factory working correctly")
        
        # Test 2: Tool Manager
        print("2. Testing Tool Manager...")
        tool_manager = ToolManager()
        available_tools = tool_manager.get_available_tools()
        assert len(available_tools) > 0
        
        # Test a simple tool
        calc_tool = tool_manager.create_tool(
            ToolConfig(
                name="calculate",
                description="Calculator tool",
                function_name="calculate",
                parameters={"expression": {"type": "string"}},
                required_params=["expression"]
            )
        )
        result = calc_tool.func("2 + 2")
        assert "4" in str(result)
        print("   ✅ Tool manager working correctly")
        
        # Test 3: Agent Builder (without LLM)
        print("3. Testing Agent Builder...")
        agent_builder = LangGraphAgentBuilder()
        
        # Create a test config (this won't work without API keys, but should validate)
        test_config = AgentConfig(
            name="Test Agent",
            description="A test agent",
            instructions="You are a test agent",
            model=ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                temperature=0.7
            ),
            tools=[
                ToolConfig(
                    name="calculate",
                    description="Calculator tool",
                    function_name="calculate",
                    parameters={"expression": {"type": "string"}},
                    required_params=["expression"]
                )
            ]
        )
        
        # Validate configuration
        try:
            ModelFactory.validate_model_config(test_config.model)
            print("   ✅ Agent configuration validation working")
        except Exception as e:
            print(f"   ⚠️  Model validation failed (expected without API keys): {e}")
        
        print("\n🎉 Basic functionality tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        return False


async def test_api_imports():
    """Test that all API components can be imported."""
    print("\n4. Testing API imports...")
    
    try:
        from src.api import router
        from src.monitoring import metrics_collector
        from src.config import get_settings
        
        # Test settings
        settings = get_settings()
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'app_version')
        
        print("   ✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        traceback.print_exc()
        return False


async def test_monitoring():
    """Test monitoring components."""
    print("\n5. Testing monitoring system...")
    
    try:
        from src.monitoring import MetricsCollector, PerformanceMonitor
        
        # Test metrics collector
        collector = MetricsCollector()
        collector.record_agent_execution(
            agent_id="test-agent",
            status="completed",
            duration=1.5,
            token_usage={"input": 100, "output": 50}
        )
        
        # Test getting metrics
        metrics = collector.get_agent_metrics("test-agent")
        assert metrics["total_executions"] == 1
        assert metrics["success_rate"] == 1.0
        
        # Test system metrics
        system_metrics = collector.get_system_metrics()
        assert "total_agents" in system_metrics
        
        print("   ✅ Monitoring system working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Monitoring test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("LangGraph Agent Builder System - System Test")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_api_imports,
        test_monitoring
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\nThe system is ready to use!")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Start the server: ./start.sh")
        print("3. Try the examples: python examples/basic_usage.py")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        print("\nPlease check the errors above and fix any issues.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 