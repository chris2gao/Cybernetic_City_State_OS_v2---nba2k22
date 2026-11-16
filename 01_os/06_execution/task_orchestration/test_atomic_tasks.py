import unittest
from atomic_tasks import Atom, Chain, Executor, Ready


class AtomicTaskBehavior(unittest.TestCase):
    def test_full_five_step_research_loop(self):
        state = {"baseline": False, "setters": False, "games": 0,
                 "postgame": False, "analysis": False}
        acts = []
        steps = []
        phases = [
            ("acquire", "baseline", None),
            ("intervene", "setters", "baseline"),
            ("simulate", "games", "setters"),
            ("reacquire", "postgame", "games"),
            ("analyze", "analysis", "postgame"),
        ]
        for key, field, pre in phases:
            def ready(field=field, pre=pre):
                return Ready(pre is None or bool(state[pre]), "missing predecessor")
            def done(field=field):
                return bool(state[field])
            def action(field=field, key=key):
                acts.append(key)
                state[field] = 7 if field == "games" else True
            steps.append(Atom(key, key, ready, action, done))
        root = Chain("round", "usable experimental observations", lambda: Ready(True),
                     tuple(steps), lambda: state["analysis"] and state["games"] == 7)
        runner = Executor(root)
        self.assertEqual(runner.inspect().node, "acquire")
        events = runner.run_available()
        self.assertEqual(acts, ["acquire", "intervene", "simulate", "reacquire", "analyze"])
        self.assertEqual([e.status for e in events], ["ADVANCED"] * 5 + ["DONE"])
        self.assertEqual(runner.inspect().status, "DONE")

    def test_qualification_without_calendar_never_finishes_round(self):
        state = {"qualified": 16, "games": 0, "post": False, "analysis": False}
        simulated = []
        root = Chain("round", "real mechanism study", lambda: Ready(True), (
            Atom("qualify", "native qualification", lambda: Ready(True),
                 lambda: None, lambda: state["qualified"] == 16),
            Atom("simulate", "real calendar games", lambda: Ready(True),
                 lambda: simulated.append("called"), lambda: state["games"] > 0),
            Atom("post", "post game capture", lambda: Ready(state["games"] > 0),
                 lambda: None, lambda: state["post"]),
        ), lambda: state["games"] > 0 and state["post"] and state["analysis"])
        runner = Executor(root)
        self.assertEqual(runner.inspect().node, "simulate")
        result = runner.advance()
        self.assertEqual(result.status, "NOT_DONE")
        self.assertEqual(result.next.status, "RECONCILE")
        self.assertEqual(runner.advance().status, "RECONCILE")
        self.assertEqual(len(simulated), 1)

    def test_no_authority_prevents_any_action(self):
        invoked = []
        task = Atom("native", "edit target", lambda: Ready(False, "Native scope not authorized"),
                    lambda: invoked.append(1), lambda: False)
        e = Executor(task)
        self.assertEqual(e.run_available()[0].status, "BLOCKED")
        self.assertEqual(invoked, [])

    def test_parent_done_is_independent_of_child_flags(self):
        root = Chain("study", "causal mechanism established", lambda: Ready(True), (
            Atom("capture", "data exists", lambda: Ready(True), lambda: None, lambda: True),
        ), lambda: False)
        e = Executor(root)
        self.assertEqual(e.inspect().status, "PARENT_INCOMPLETE")
        self.assertEqual(e.advance().status, "PARENT_INCOMPLETE")

    def test_action_exception_stops_without_replay(self):
        executed = []
        def action():
            executed.append(1)
            raise RuntimeError("may have altered external state")
        e = Executor(Atom("write", "native write", lambda: Ready(True), action, lambda: False))
        self.assertEqual(e.advance().status, "ACTION_UNCERTAIN")
        self.assertEqual(e.advance().status, "RECONCILE")
        self.assertEqual(len(executed), 1)

    def test_nested_chains_and_already_completed_atoms(self):
        values = {"a": True, "b": False}
        invoked = []
        inner = Chain("inner", "two outcomes", lambda: Ready(True), (
            Atom("a", "a goal", lambda: Ready(True), lambda: invoked.append("a"), lambda: values["a"]),
            Atom("b", "b goal", lambda: Ready(True),
                 lambda: (invoked.append("b"), values.__setitem__("b", True)), lambda: values["b"]),
        ), lambda: values["a"] and values["b"])
        outer = Chain("outer", "whole system", lambda: Ready(True), (inner,),
                      lambda: values["a"] and values["b"])
        x = Executor(outer)
        self.assertEqual(x.run_available()[-1].status, "DONE")
        self.assertEqual(invoked, ["b"])

    def test_duplicate_ids_are_rejected(self):
        a = Atom("same", "a", lambda: Ready(True), lambda: None, lambda: False)
        b = Atom("same", "b", lambda: Ready(True), lambda: None, lambda: False)
        with self.assertRaises(ValueError):
            Executor(Chain("parent", "p", lambda: Ready(True), (a, b), lambda: False))


if __name__ == "__main__":
    unittest.main()
