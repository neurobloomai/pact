import unittest
from examples.agent_a import SchedulerProAgent
from examples.agent_b import BasicCalendarAgent
from pact_core import PACTMessage

class TestAgents(unittest.TestCase):

    def setUp(self):
        self.agent_a = SchedulerProAgent()
        self.agent_b = BasicCalendarAgent()

    def test_scheduler_pro_can_schedule_complex(self):
        intent = PACTMessage(
            intent="schedule_meeting",
            metadata={
                "participants": ["a", "b", "c", "d", "e", "f"],
                "duration": "60",
                "preferences": {"time_range": "morning"}
            }
        )
        response = self.agent_a.schedule_complex_meeting({
            "parameters": intent.metadata
        })
        self.assertEqual(response["status"], "success")

    def test_basic_calendar_fallback_on_too_many_participants(self):
        intent = PACTMessage(
            intent="schedule_meeting",
            metadata={
                "participants": ["a", "b", "c", "d", "e", "f"],
                "duration": "30"
            }
        )
        response = self.agent_b.schedule_simple_meeting({
            "action": intent.intent,
            "parameters": intent.metadata
        })
        self.assertEqual(response["status"], "partial")
        self.assertIn("fallback_applied", response)

if __name__ == "__main__":
    unittest.main()
