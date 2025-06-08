from examples.agent_a import SchedulerProAgent
from examples.agent_b import BasicCalendarAgent
from pact_core import PACTMessage

class DemonstrationScenario:
    def __init__(self):
        self.scheduler_pro = SchedulerProAgent()
        self.basic_calendar = BasicCalendarAgent()
        self.communication_log = []

    def log_step(self, message):
        print(f"==> {message}")
        self.communication_log.append(message)

    def create_complex_scheduling_intent(self):
        return PACTMessage(
            intent="schedule_meeting",
            metadata={
                "participants": ["alice@startup.com", "bob@enterprise.com", "carol@startup.com"],
                "duration": 120,
                "timezone_preferences": {"alice": "PST", "bob": "EST"},
                "preparation_required": True
            }
        )

    def execute_full_scenario(self):
        self.log_step("Scheduler Pro attempts complex scheduling...")
        complex_intent = self.create_complex_scheduling_intent()

        self.log_step("Basic Calendar discovers capabilities...")
        capabilities = self.basic_calendar.capability_manager.advertise_capabilities()
        self.log_step(f"Capabilities: {capabilities}")

        self.log_step("Basic Calendar receives intent...")
        response = self.basic_calendar.schedule_simple_meeting({
            "action": complex_intent.intent,
            "parameters": complex_intent.metadata
        })
        self.log_step(f"Initial Response: {response}")

        if response.get("status") == "partial":
            self.log_step("Scheduler Pro applies fallback...")
            adjusted = self.scheduler_pro.handle_capability_mismatch({
                "action": complex_intent.intent,
                "parameters": complex_intent.metadata
            }, self.basic_calendar.capabilities)
            self.log_step(f"Adjusted Intent: {adjusted}")

            self.log_step("Basic Calendar attempts rescheduling...")
            retry = self.basic_calendar.schedule_simple_meeting({
                "action": adjusted["simplified_intent"]["action"],
                "parameters": adjusted["simplified_intent"]["parameters"]
            })
            self.log_step(f"Final Outcome: {retry}")
        else:
            self.log_step("Scheduling succeeded without fallback.")

# CLI Simulation
if __name__ == "__main__":
    print("\n🚀 PACT Protocol Demonstration: Multi-Company Scheduling")
    print("========================================================\n")
    demo = DemonstrationScenario()
    demo.execute_full_scenario()
