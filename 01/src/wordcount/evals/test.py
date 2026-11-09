import sys
from pathlib import Path

from strands_evals import Case, Experiment
from strands_evals.evaluators.deterministic import Contains
from strands_evals.evaluators.evaluator import Evaluator
from strands_evals.extractors import tools_use_extractor
from strands_evals.types import TaskOutput
from strands_evals.types.evaluation import EvaluationData, EvaluationOutput

_wordcount_root = Path(__file__).resolve().parents[1]
if str(_wordcount_root) not in sys.path:
    sys.path.insert(0, str(_wordcount_root))

from app import agent as wordcount_agent

TRAJECTORY_RUBRIC = (
    "letter_counter, then file_editor, then shell, in that order. "
    "Extra shell calls for the two-second pause are allowed."
)


class OrderedTools(Evaluator):
    """Checks expected tool names in order. Extra shell calls are allowed."""

    def evaluate(self, evaluation_case: EvaluationData) -> list[EvaluationOutput]:
        actual = evaluation_case.actual_trajectory or []
        expected = list(evaluation_case.expected_trajectory or [])
        names = [step["name"] if isinstance(step, dict) else step for step in actual]

        matched = 0
        for name in names:
            if matched < len(expected) and name == expected[matched]:
                matched += 1
                continue
            if name == "shell":
                continue
            return [
                EvaluationOutput(
                    score=matched / len(expected) if expected else 0.0,
                    test_pass=False,
                    reason=f"{TRAJECTORY_RUBRIC} Unexpected tool '{name}' in {names}.",
                )
            ]

        passed = matched == len(expected)
        score = matched / len(expected) if expected else 1.0
        if passed:
            reason = f"{TRAJECTORY_RUBRIC} Actual tools: {names}."
        else:
            reason = f"{TRAJECTORY_RUBRIC} Actual tools {names} did not include {expected} in order."
        return [EvaluationOutput(score=score, test_pass=passed, reason=reason)]

    async def evaluate_async(self, evaluation_case: EvaluationData) -> list[EvaluationOutput]:
        return self.evaluate(evaluation_case)


def get_response(case: Case) -> TaskOutput:
    response = wordcount_agent(case.input)
    trajectory = tools_use_extractor.extract_agent_tools_used_from_messages(wordcount_agent.messages)
    tool_names = [step["name"] for step in trajectory]
    return TaskOutput(output=str(response), trajectory=tool_names)


cases = [
    Case(
        name="wordcount-full-workflow",
        input="How many letter R's are in the word 'strawberry'? Write the answer to answer_2026-11-09_10:40:00.txt. then run 'cat answer_2026-11-09_10:40:00.txt' to see the result.",
        expected_output="The word 'strawberry' has 3 letter R's.",
        expected_trajectory=["letter_counter", "file_editor", "shell"],
    ),
]

experiment = Experiment(
    cases=cases,
    evaluators=[
        OrderedTools(name="OrderedTools"),
        Contains(value="3", name="OutputContainsCount"),
    ],
)

if __name__ == "__main__":
    report = experiment.run_evaluations(task=get_response)
    report.run_display()
