"""Advanced example showing complex agent workflows and monitoring."""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, List


class AdvancedAgentBuilderClient:
    """Advanced client with monitoring and session management."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.agents: Dict[str, str] = {}  # name -> agent_id mapping
    
    async def create_research_workflow(self):
        """Create a multi-agent research workflow."""
        print("=== Creating Research Workflow ===")
        
        # 1. Research Agent
        research_agent_config = {
            "config": {
                "name": "Research Specialist",
                "description": "An agent specialized in research and information gathering",
                "instructions": """You are a research specialist. Your job is to:
                1. Analyze research questions thoroughly
                2. Use web search to gather relevant information
                3. Provide comprehensive, well-structured research summaries
                4. Always cite your sources and provide balanced perspectives""",
                "model": {
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "temperature": 0.3
                },
                "tools": [
                    {
                        "name": "web_search",
                        "description": "Perform a web search",
                        "function_name": "web_search",
                        "parameters": {
                            "query": {"type": "string", "description": "Search query"},
                            "num_results": {"type": "integer", "description": "Number of results", "default": 5}
                        },
                        "required_params": ["query"]
                    },
                    {
                        "name": "write_file",
                        "description": "Write content to a file",
                        "function_name": "write_file",
                        "parameters": {
                            "file_path": {"type": "string", "description": "Path to file"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required_params": ["file_path", "content"]
                    }
                ],
                "max_iterations": 15
            }
        }
        
        # 2. Analysis Agent
        analysis_agent_config = {
            "config": {
                "name": "Data Analyst",
                "description": "An agent specialized in data analysis and calculations",
                "instructions": """You are a data analyst. Your job is to:
                1. Perform mathematical calculations and statistical analysis
                2. Read and analyze data from files
                3. Create summaries and insights from numerical data
                4. Present findings in a clear, structured format""",
                "model": {
                    "provider": "openai",
                    "model_name": "gpt-3.5-turbo",
                    "temperature": 0.2
                },
                "tools": [
                    {
                        "name": "calculate",
                        "description": "Safely evaluate a mathematical expression",
                        "function_name": "calculate",
                        "parameters": {
                            "expression": {"type": "string", "description": "Mathematical expression"}
                        },
                        "required_params": ["expression"]
                    },
                    {
                        "name": "read_file",
                        "description": "Read content from a file",
                        "function_name": "read_file",
                        "parameters": {
                            "file_path": {"type": "string", "description": "Path to file"}
                        },
                        "required_params": ["file_path"]
                    }
                ],
                "max_iterations": 10
            }
        }
        
        # 3. Report Generator Agent
        report_agent_config = {
            "config": {
                "name": "Report Generator",
                "description": "An agent specialized in creating comprehensive reports",
                "instructions": """You are a report generator. Your job is to:
                1. Compile information from multiple sources
                2. Create well-structured, professional reports
                3. Include executive summaries and key findings
                4. Format reports with proper sections and conclusions""",
                "model": {
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "temperature": 0.4
                },
                "tools": [
                    {
                        "name": "read_file",
                        "description": "Read content from a file",
                        "function_name": "read_file",
                        "parameters": {
                            "file_path": {"type": "string", "description": "Path to file"}
                        },
                        "required_params": ["file_path"]
                    },
                    {
                        "name": "write_file",
                        "description": "Write content to a file",
                        "function_name": "write_file",
                        "parameters": {
                            "file_path": {"type": "string", "description": "Path to file"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required_params": ["file_path", "content"]
                    },
                    {
                        "name": "get_current_time",
                        "description": "Get the current date and time",
                        "function_name": "get_current_time",
                        "parameters": {},
                        "required_params": []
                    }
                ],
                "max_iterations": 8
            }
        }
        
        # Create all agents
        async with httpx.AsyncClient() as client:
            for name, config in [
                ("Research Specialist", research_agent_config),
                ("Data Analyst", analysis_agent_config),
                ("Report Generator", report_agent_config)
            ]:
                response = await client.post(f"{self.api_base}/agents", json=config)
                if response.status_code == 200:
                    agent_data = response.json()
                    self.agents[name] = agent_data["agent_id"]
                    print(f"✓ Created {name}: {agent_data['agent_id']}")
                else:
                    print(f"✗ Failed to create {name}: {response.text}")
    
    async def execute_research_workflow(self, research_topic: str):
        """Execute the complete research workflow."""
        print(f"\n=== Executing Research Workflow: {research_topic} ===")
        
        async with httpx.AsyncClient() as client:
            # Step 1: Research
            print("Step 1: Conducting research...")
            research_response = await client.post(f"{self.api_base}/agents/execute", json={
                "agent_id": self.agents["Research Specialist"],
                "input_message": f"""Please research the topic: "{research_topic}"
                
                Your task:
                1. Search for current information about this topic
                2. Gather key facts, statistics, and recent developments
                3. Save your research findings to a file called 'research_data.txt'
                4. Provide a summary of what you found"""
            })
            
            if research_response.status_code == 200:
                result = research_response.json()
                print(f"Research completed in {result['execution_time']:.2f}s")
                print(f"Tools used: {len(result['tool_calls'])}")
                print(f"Summary: {result['response'][:200]}...")
            
            # Step 2: Analysis
            print("\nStep 2: Analyzing data...")
            analysis_response = await client.post(f"{self.api_base}/agents/execute", json={
                "agent_id": self.agents["Data Analyst"],
                "input_message": """Please read the research data from 'research_data.txt' and perform analysis:
                
                Your task:
                1. Read the research data file
                2. Extract any numerical data or statistics
                3. Perform relevant calculations or analysis
                4. Identify key trends or patterns
                5. Provide analytical insights"""
            })
            
            if analysis_response.status_code == 200:
                result = analysis_response.json()
                print(f"Analysis completed in {result['execution_time']:.2f}s")
                print(f"Analysis summary: {result['response'][:200]}...")
            
            # Step 3: Report Generation
            print("\nStep 3: Generating final report...")
            report_response = await client.post(f"{self.api_base}/agents/execute", json={
                "agent_id": self.agents["Report Generator"],
                "input_message": f"""Please create a comprehensive report about "{research_topic}":
                
                Your task:
                1. Read the research data from 'research_data.txt'
                2. Incorporate any analysis findings
                3. Create a well-structured report with:
                   - Executive Summary
                   - Key Findings
                   - Analysis and Insights
                   - Conclusions and Recommendations
                4. Save the final report as 'final_report.txt'
                5. Include the current date and time in the report"""
            })
            
            if report_response.status_code == 200:
                result = report_response.json()
                print(f"Report generated in {result['execution_time']:.2f}s")
                print(f"Report summary: {result['response'][:200]}...")
            
            return {
                "research": research_response.json() if research_response.status_code == 200 else None,
                "analysis": analysis_response.json() if analysis_response.status_code == 200 else None,
                "report": report_response.json() if report_response.status_code == 200 else None
            }
    
    async def monitor_agents(self):
        """Monitor agent performance and metrics."""
        print("\n=== Agent Performance Monitoring ===")
        
        async with httpx.AsyncClient() as client:
            # Get system metrics
            system_response = await client.get(f"{self.api_base}/metrics/system")
            if system_response.status_code == 200:
                metrics = system_response.json()
                print(f"System Metrics:")
                print(f"  Total Agents: {metrics['total_agents']}")
                print(f"  Total Executions: {metrics['total_executions']}")
                print(f"  Success Rate: {metrics['system_success_rate']:.2%}")
            
            # Get individual agent metrics
            for name, agent_id in self.agents.items():
                agent_response = await client.get(f"{self.api_base}/metrics/agents/{agent_id}")
                if agent_response.status_code == 200:
                    metrics = agent_response.json()
                    print(f"\n{name} Metrics:")
                    print(f"  Executions: {metrics['total_executions']}")
                    print(f"  Success Rate: {metrics['success_rate']:.2%}")
                    print(f"  Avg Duration: {metrics['average_duration']:.2f}s")
                    print(f"  Total Tokens: {metrics['total_tokens']}")
    
    async def cleanup(self):
        """Clean up created agents."""
        print("\n=== Cleaning Up ===")
        
        async with httpx.AsyncClient() as client:
            for name, agent_id in self.agents.items():
                response = await client.delete(f"{self.api_base}/agents/{agent_id}")
                if response.status_code == 200:
                    print(f"✓ Deleted {name}")
                else:
                    print(f"✗ Failed to delete {name}")


async def demo_session_management():
    """Demonstrate session management and conversation continuity."""
    print("\n=== Session Management Demo ===")
    
    client = AdvancedAgentBuilderClient()
    
    # Create a conversational agent
    agent_config = {
        "config": {
            "name": "Conversational Assistant",
            "description": "An assistant that maintains conversation context",
            "instructions": """You are a helpful conversational assistant. 
            Remember the context of our conversation and refer back to previous topics when relevant.
            Be engaging and maintain continuity across multiple interactions.""",
            "model": {
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7
            },
            "tools": [
                {
                    "name": "get_current_time",
                    "description": "Get the current date and time",
                    "function_name": "get_current_time",
                    "parameters": {},
                    "required_params": []
                }
            ],
            "memory_enabled": True
        }
    }
    
    async with httpx.AsyncClient() as client_http:
        # Create agent
        response = await client_http.post(f"{client.api_base}/agents", json=agent_config)
        agent_data = response.json()
        agent_id = agent_data["agent_id"]
        
        # Start a conversation with session management
        session_id = "demo_session_001"
        
        conversations = [
            "Hello! I'm planning a trip to Japan. Can you help me?",
            "What's the best time of year to visit?",
            "How much should I budget for a 2-week trip?",
            "What time is it now? I want to know when to book flights.",
            "Based on our conversation, can you summarize the key points for my Japan trip?"
        ]
        
        for i, message in enumerate(conversations, 1):
            print(f"\n--- Conversation Turn {i} ---")
            print(f"User: {message}")
            
            response = await client_http.post(f"{client.api_base}/agents/execute", json={
                "agent_id": agent_id,
                "input_message": message,
                "session_id": session_id
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"Assistant: {result['response']}")
                print(f"(Execution time: {result['execution_time']:.2f}s)")
            
            # Small delay between messages
            await asyncio.sleep(1)
        
        # Cleanup
        await client_http.delete(f"{client.api_base}/agents/{agent_id}")


async def main():
    """Run the advanced example."""
    print("LangGraph Agent Builder System - Advanced Examples")
    print("=" * 60)
    
    # Check server availability
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/health")
            if response.status_code != 200:
                print("✗ Server is not responding correctly")
                return
    except Exception:
        print("✗ Server is not running. Please start it with: python -m src.main")
        return
    
    print("✓ Server is running")
    
    # Initialize client
    client = AdvancedAgentBuilderClient()
    
    try:
        # Demo 1: Multi-agent research workflow
        await client.create_research_workflow()
        workflow_results = await client.execute_research_workflow(
            "The impact of artificial intelligence on job markets in 2024"
        )
        
        # Demo 2: Session management
        await demo_session_management()
        
        # Demo 3: Monitoring
        await client.monitor_agents()
        
        print("\n" + "=" * 60)
        print("Advanced examples completed successfully!")
        
        # Show final summary
        print("\nWorkflow Summary:")
        if workflow_results["research"]:
            print(f"✓ Research: {workflow_results['research']['status']}")
        if workflow_results["analysis"]:
            print(f"✓ Analysis: {workflow_results['analysis']['status']}")
        if workflow_results["report"]:
            print(f"✓ Report: {workflow_results['report']['status']}")
        
    except Exception as e:
        print(f"Error during execution: {e}")
    
    finally:
        # Cleanup
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 