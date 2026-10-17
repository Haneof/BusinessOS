import unittest

from businessos.policy import Action, Decision, Policy, Request


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.p = Policy(experiment_budget_cents=1000)

    def test_local_zero_cost_allowed(self):
        self.assertEqual(self.p.evaluate(Request(Action.CREATE_LOCAL_ARTIFACT, "test")).decision, Decision.ALLOW)

    def test_external_requires_approval(self):
        for action in (Action.PUBLISH_EXTERNAL, Action.REGISTER_ACCOUNT, Action.CONTACT_CUSTOMER,
                       Action.SPEND_MONEY, Action.INSTALL_SOFTWARE, Action.ACCESS_CUSTOMER_DATA):
            with self.subTest(action=action):
                self.assertEqual(self.p.evaluate(Request(action, "test")).decision, Decision.REQUIRE_APPROVAL)

    def test_never_auto_bypass(self):
        for action in (Action.MODIFY_POLICY, Action.HANDLE_CREDENTIALS, Action.PROVIDE_REGULATED_ADVICE):
            with self.subTest(action=action):
                self.assertEqual(self.p.evaluate(Request(action, "test")).decision, Decision.DENY)

    def test_unknown_denied(self):
        self.assertEqual(self.p.evaluate(Request("unknown_action", "test")).decision, Decision.DENY)

    def test_spending_above_cap_denied(self):
        self.assertEqual(self.p.evaluate(Request(Action.SPEND_MONEY, "test", 1001)).decision, Decision.DENY)

    def test_spending_under_cap_still_needs_approval(self):
        self.assertEqual(self.p.evaluate(Request(Action.SPEND_MONEY, "test", 900)).decision, Decision.REQUIRE_APPROVAL)

    def test_ordinary_action_with_cost_needs_approval(self):
        self.assertEqual(self.p.evaluate(Request(Action.SPAWN_SCOPED_AGENT, "test", 10)).decision, Decision.REQUIRE_APPROVAL)

    def test_invalid_budget_rejected(self):
        with self.assertRaises(ValueError):
            Policy(-1)

    def test_invalid_cost_denied(self):
        self.assertEqual(self.p.evaluate(Request(Action.SPEND_MONEY, "test", -1)).decision, Decision.DENY)
