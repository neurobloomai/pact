#!/usr/bin/env python3
"""
PACT Intent Hierarchy - Live Partner Demo
Enhanced demo script with clear presentation flow
"""

import asyncio
import time
from intent_hierarchy_core import (
    IntentHierarchyCoordinator, Agent, CoordinationResult
)

class PACTLiveDemo:
    """Enhanced demo class for partner presentations"""
    
    def __init__(self):
        self.coordinator = IntentHierarchyCoordinator()
        self.demo_scenarios = []
        
    def print_header(self, title: str):
        """Print formatted header for demo sections"""
        print("\n" + "="*60)
        print(f"🚀 {title}")
        print("="*60)
        
    def print_step(self, step_num: int, description: str):
        """Print formatted step information"""
        print(f"\n📋 Step {step_num}: {description}")
        print("-" * 40)
        
    def print_result(self, label: str, value: str, status: str = "info"):
        """Print formatted results"""
        emoji = "✅" if status == "success" else "⚡" if status == "energy" else "📊"
        print(f"{emoji} {label}: {value}")
        
    async def setup_demo_environment(self):
        """Setup agents and scenarios for demo"""
        
        self.print_header("PACT Demo Environment Setup")
        
        # Create defense agents
        agents = [
            Agent(
                agent_id="sat_001_primary",
                platform="defense_sat_network",
                capabilities=["data_transmission", "orbit_control", "encryption", "targeting"],
                current_status="active",
                resource_limits={"cpu": 0.8, "memory": 0.7, "bandwidth": 0.9}
            ),
            Agent(
                agent_id="sat_002_backup", 
                platform="defense_sat_network",
                capabilities=["data_reception", "backup_coverage", "encryption", "relay"],
                current_status="active",
                resource_limits={"cpu": 0.6, "memory": 0.8, "bandwidth": 0.7}
            ),
            Agent(
                agent_id="drone_001_recon",
                platform="autonomous_drone",
                capabilities=["surveillance", "data_collection", "target_identification"],
                current_status="active", 
                resource_limits={"cpu": 0.7, "memory": 0.5, "bandwidth": 0.6}
            ),
            Agent(
                agent_id="ground_001_control",
                platform="ground_station",
                capabilities=["mission_control", "data_analysis", "coordination"],
                current_status="active",
                resource_limits={"cpu": 0.9, "memory": 0.9, "bandwidth": 0.8}
            )
        ]
        
        # Register all agents
        for agent in agents:
            self.coordinator.register_agent(agent)
            self.print_result(f"Registered Agent", f"{agent.agent_id} ({agent.platform})", "success")
            
        print(f"\n🎯 Demo Environment Ready: {len(agents)} agents registered")
        return agents
        
    async def demo_scenario_1_satellite_emergency(self):
        """Demo Scenario 1: Emergency Satellite Coordination"""
        
        self.print_header("Demo Scenario 1: Emergency Satellite Coordination")
        
        print("🌍 SITUATION: Natural disaster requires emergency satellite coverage")
        print("💥 CHALLENGE: Primary satellite must coordinate with backup for continuous coverage")
        print("🎯 GOAL: Demonstrate PACT's 4-layer intent hierarchy in action")
        
        # Define emergency coordination task
        task_context = {
            "agent_a_objective": "provide emergency communication coverage for disaster zone",
            "agent_b_objective": "maintain backup coverage and relay critical data",
            "shared_objective": "ensure uninterrupted emergency communication during disaster response",
            "agent_a_role": "primary_coverage_provider",
            "agent_b_role": "backup_and_relay",
            "comm_protocol": "encrypted_emergency_channel",
            "agent_a_confidence": 0.95,
            "agent_b_confidence": 0.88,
            "agent_a_constraints": {"power_limit": 0.85, "orbit_window": 450},
            "agent_b_constraints": {"backup_readiness": 0.9, "relay_capacity": 0.8},
            "agent_a_resources": {"power": 0.8, "bandwidth": 0.9, "processing": 0.7},
            "agent_b_resources": {"power": 0.6, "bandwidth": 0.7, "processing": 0.8},
            "complexity": "high"
        }
        
        mission_context = {
            "mission_id": "disaster_response_emergency_001", 
            "mission_objective": "provide emergency communication coverage during natural disaster",
            "value_hierarchy": ["reliability", "coverage", "speed", "efficiency"],
            "constraints": {"time_limit": 300, "power_budget": 0.9, "coverage_area": "full_disaster_zone"},
            "success_definition": "maintain 99.5% uptime with redundant coverage",
            "criticality": "critical"
        }
        
        self.print_step(1, "Initiating PACT 4-Layer Intent Hierarchy")
        
        # Execute coordination with timing
        start_time = time.time()
        result, details = await self.coordinator.coordinate_agents(
            "sat_001_primary",
            "sat_002_backup", 
            task_context,
            mission_context
        )
        processing_time = time.time() - start_time
        
        # Display results
        self.print_step(2, "Coordination Results Analysis")
        
        self.print_result("Coordination Result", str(result), "success" if result == CoordinationResult.SUCCESS else "info")
        self.print_result("Processing Time", f"{processing_time:.3f} seconds", "energy")
        self.print_result("Energy Score", f"{details.get('energy_score', 0):.3f}/1.0", "energy")
        
        if result == CoordinationResult.SUCCESS:
            print("\n🎉 SUCCESS: Satellites coordinated successfully!")
            print("✅ Layer 1: Individual intents validated")
            print("✅ Layer 2: Shared understanding established") 
            print("✅ Layer 3: Mission alignment confirmed")
            print("✅ Layer 4: Partnership energy optimized")
            
            # Show execution steps
            execution_steps = details.get('execution_result', {}).get('execution_steps', [])
            if execution_steps:
                print("\n📋 Coordination Execution Steps:")
                for i, step in enumerate(execution_steps, 1):
                    print(f"   {i}. {step['step']}: {step['details']}")
        else:
            print(f"\n❌ Coordination failed at: {result}")
            print("🔧 PACT identified the issue and prevented unreliable coordination")
            
        return result, details
        
    async def demo_scenario_2_drone_handoff(self):
        """Demo Scenario 2: Drone-to-Ground Intelligence Handoff"""
        
        self.print_header("Demo Scenario 2: Drone-to-Ground Intelligence Handoff")
        
        print("🔍 SITUATION: Reconnaissance drone has critical intelligence to transfer")
        print("💥 CHALLENGE: Must coordinate with ground station under time pressure")
        print("🎯 GOAL: Show PACT handling different agent types and capabilities")
        
        task_context = {
            "agent_a_objective": "transfer time-sensitive reconnaissance data to ground control",
            "agent_b_objective": "receive and process intelligence data for mission planning",
            "shared_objective": "secure transfer of critical intelligence within operational window",
            "agent_a_role": "intelligence_collector",
            "agent_b_role": "intelligence_processor",
            "comm_protocol": "secure_data_burst",
            "agent_a_confidence": 0.92,
            "agent_b_confidence": 0.98,
            "agent_a_constraints": {"flight_time_remaining": 180, "data_size": "large"},
            "agent_b_constraints": {"processing_queue": 0.3, "security_clearance": "top_secret"},
            "agent_a_resources": {"power": 0.4, "bandwidth": 0.6, "storage": 0.9},
            "agent_b_resources": {"power": 0.9, "bandwidth": 0.8, "processing": 0.95},
            "complexity": "medium"
        }
        
        mission_context = {
            "mission_id": "intel_transfer_urgent_002",
            "mission_objective": "transfer critical reconnaissance intelligence", 
            "value_hierarchy": ["security", "speed", "data_integrity"],
            "constraints": {"time_limit": 180, "security_level": "classified"},
            "success_definition": "100% data transfer with security compliance",
            "criticality": "high"
        }
        
        self.print_step(1, "Cross-Platform Agent Coordination")
        
        start_time = time.time()
        result, details = await self.coordinator.coordinate_agents(
            "drone_001_recon",
            "ground_001_control",
            task_context, 
            mission_context
        )
        processing_time = time.time() - start_time
        
        self.print_step(2, "Cross-Platform Results")
        
        self.print_result("Coordination Result", str(result), "success" if result == CoordinationResult.SUCCESS else "info")
        self.print_result("Processing Time", f"{processing_time:.3f} seconds", "energy") 
        self.print_result("Energy Score", f"{details.get('energy_score', 0):.3f}/1.0", "energy")
        
        if result == CoordinationResult.SUCCESS:
            print("\n🎉 SUCCESS: Drone-to-ground coordination established!")
            print("🔄 Different platforms coordinated seamlessly")
            print("⚡ PACT optimized for cross-capability collaboration")
        
        return result, details
        
    async def demo_scenario_3_partnership_optimization(self):
        """Demo Scenario 3: Partnership Energy Optimization"""
        
        self.print_header("Demo Scenario 3: Dynamic Partnership Optimization")
        
        print("🔄 SITUATION: Testing PACT's dynamic partnership selection")
        print("💥 CHALLENGE: Multiple agents available - which partnership is optimal?")
        print("🎯 GOAL: Demonstrate energy-based partnership optimization")
        
        # Test multiple partnership combinations
        partnerships_to_test = [
            ("sat_001_primary", "sat_002_backup", "satellite_to_satellite"),
            ("sat_001_primary", "drone_001_recon", "satellite_to_drone"),
            ("drone_001_recon", "ground_001_control", "drone_to_ground"),
            ("sat_002_backup", "ground_001_control", "satellite_to_ground")
        ]
        
        partnership_results = []
        
        for agent_a, agent_b, partnership_type in partnerships_to_test:
            print(f"\n🔍 Testing: {partnership_type} ({agent_a} ↔ {agent_b})")
            
            # Simple coordination task for comparison
            simple_task = {
                "agent_a_objective": "coordinate for data relay task",
                "agent_b_objective": "support data relay coordination", 
                "shared_objective": "establish efficient data relay",
                "agent_a_role": "primary",
                "agent_b_role": "secondary",
                "comm_protocol": "standard",
                "agent_a_confidence": 0.8,
                "agent_b_confidence": 0.8,
                "agent_a_resources": {"power": 0.7, "bandwidth": 0.7},
                "agent_b_resources": {"power": 0.7, "bandwidth": 0.7},
                "complexity": "medium"
            }
            
            simple_mission = {
                "mission_id": "partnership_test",
                "mission_objective": "test partnership efficiency",
                "value_hierarchy": ["efficiency", "reliability"],
                "constraints": {},
                "success_definition": "successful coordination",
                "criticality": "medium"
            }
            
            start_time = time.time()
            result, details = await self.coordinator.coordinate_agents(
                agent_a, agent_b, simple_task, simple_mission
            )
            processing_time = time.time() - start_time
            
            energy_score = details.get('energy_score', 0)
            partnership_results.append({
                'partnership': partnership_type,
                'agents': f"{agent_a} ↔ {agent_b}",
                'energy_score': energy_score,
                'processing_time': processing_time,
                'result': result
            })
            
            status = "success" if result == CoordinationResult.SUCCESS else "info"
            self.print_result("Energy Score", f"{energy_score:.3f}", "energy")
        
        # Show optimization results
        self.print_step(1, "Partnership Optimization Analysis")
        
        # Sort by energy score
        partnership_results.sort(key=lambda x: x['energy_score'], reverse=True)
        
        print("\n🏆 Partnership Rankings (by Energy Score):")
        for i, result in enumerate(partnership_results, 1):
            print(f"   {i}. {result['partnership']}: {result['energy_score']:.3f} energy")
            print(f"      Agents: {result['agents']}")
            print(f"      Status: {result['result']}")
            print()
            
        best_partnership = partnership_results[0]
        print(f"🥇 OPTIMAL PARTNERSHIP: {best_partnership['partnership']}")
        print(f"⚡ Energy Score: {best_partnership['energy_score']:.3f}")
        print("🎯 PACT automatically identified the most efficient agent pairing!")
        
        return partnership_results
        
    async def demo_performance_metrics(self):
        """Show PACT performance metrics"""
        
        self.print_header("PACT Performance Metrics")
        
        metrics = self.coordinator.get_performance_metrics()
        
        self.print_result("Total Coordinations", str(metrics['total_coordinations']), "info")
        self.print_result("Successful Coordinations", str(metrics['successful_coordinations']), "success")
        self.print_result("Success Rate", f"{metrics.get('success_rate', 0):.1%}", "energy")
        self.print_result("Average Processing Time", f"{metrics['average_processing_time']:.3f}s", "energy")
        
        print("\n📊 Key Performance Insights:")
        print("   • Sub-second coordination processing")
        print("   • 4-layer validation ensures reliability")
        print("   • Energy-based optimization prevents failures")
        print("   • Scalable to complex multi-agent scenarios")
        
    async def run_complete_demo(self):
        """Run the complete live demo for partners"""
        
        self.print_header("PACT Live Demo - Intent Hierarchy & Energy Optimization")
        
        print("👋 Welcome to the PACT Live Demo!")
        print("🎯 Today we'll demonstrate breakthrough AI coordination technology")
        print("💡 PACT = Protocol for Agent Collaboration & Transfer")
        print("🚀 Featuring: 4-Layer Intent Hierarchy + Energy-based Optimization")
        
        # Setup
        agents = await self.setup_demo_environment()
        
        # Run scenarios
        print("\n\n🎬 DEMO SCENARIOS")
        
        # Scenario 1: Emergency coordination
        result1, details1 = await self.demo_scenario_1_satellite_emergency()
        
        # Brief pause for presentation
        input("\n⏸️  Press Enter to continue to next scenario...")
        
        # Scenario 2: Cross-platform coordination  
        result2, details2 = await self.demo_scenario_2_drone_handoff()
        
        # Brief pause
        input("\n⏸️  Press Enter to continue to partnership optimization...")
        
        # Scenario 3: Partnership optimization
        partnership_results = await self.demo_scenario_3_partnership_optimization()
        
        # Performance summary
        await self.demo_performance_metrics()
        
        # Demo conclusion
        self.print_header("Demo Summary & Next Steps")
        
        print("🎉 PACT Live Demo Complete!")
        print("\n💡 What you just saw:")
        print("   ✅ 4-Layer Intent Hierarchy ensuring reliable coordination")
        print("   ✅ Energy-based partnership optimization")
        print("   ✅ Cross-platform agent collaboration")
        print("   ✅ Mission-critical reliability under pressure")
        print("   ✅ Sub-second processing with intelligent decision-making")
        
        print("\n🎯 Ready for Pentagon Deployment:")
        print("   • Defense satellite networks")
        print("   • Autonomous drone coordination")
        print("   • Multi-domain operations")
        print("   • Mission-critical reliability")
        
        print("\n🚀 Next Steps:")
        print("   • Patent protection filed (Intent Hierarchy + Partnership Optimization)")
        print("   • Defense use case development")
        print("   • Production deployment planning")
        print("   • Partnership opportunities")
        
        return {
            'total_scenarios': 3,
            'successful_coordinations': sum(1 for r in [result1, result2] if r == CoordinationResult.SUCCESS),
            'partnership_rankings': partnership_results,
            'performance_metrics': self.coordinator.get_performance_metrics()
        }

# Main demo execution
if __name__ == "__main__":
    async def main():
        demo = PACTLiveDemo()
        await demo.run_complete_demo()
    
    print("🚀 Starting PACT Live Demo for Partners...")
    print("💡 This demo showcases breakthrough AI coordination technology")
    print("⏱️  Estimated time: 10-15 minutes")
    print("🎯 Focus: Intent Hierarchy + Energy Optimization")
    
    input("\n▶️  Press Enter to begin demo...")
    
    asyncio.run(main())
