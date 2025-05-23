import unittest
from pact_core import PACTMessage
from examples.agent_a import SchedulerProAgent
from examples.agent_b import BasicCalendarAgent

class TestCrossAgentFallback(unittest.TestCase):

    def test_scheduler_pro_fallback_to_basic_calendar(self):
        agent_a = SchedulerProAgent()
        agent_b = BasicCalendarAgent()

        complex_intent = {
            "action": "schedule_meeting",
            "parameters": {
                "participants": ["a", "b", "c", "d", "e", "f"],
                "duration": "60",
                "preferences": {"avoid_conflicts": True}
            }
        }

        # Step 1: Basic agent can't handle
        response = agent_b.schedule_simple_meeting({
            "action": complex_intent["action"],
            "parameters": complex_intent["parameters"]
        })
        self.assertEqual(response["status"], "partial")

        # Step 2: Scheduler Pro applies fallback
        fallback_result = agent_a.handle_capability_mismatch(complex_intent, agent_b.capabilities)
        self.assertEqual(fallback_result["status"], "fallback_adjusted")
        self.assertLessEqual(len(fallback_result["simplified_intent"]["parameters"]["participants"]), 5)

if __name__ == "__main__":
    unittest.main()
