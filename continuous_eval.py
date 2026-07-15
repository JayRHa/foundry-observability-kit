#!/usr/bin/env python3
"""Create a continuous evaluation rule for a Microsoft Foundry agent.

Scores sampled live traffic with built-in evaluators; results land in the
Application Insights resource connected to the project, next to the traces.

Requires azure-ai-projects >= 2.0.0 and the project managed identity holding
the Foundry User role.

Usage:
  python continuous_eval.py --agent my-agent \
      --evaluators groundedness task_adherence violence --max-hourly-runs 100
"""
import argparse
import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ContinuousEvaluationRuleAction,
    EvaluationRule,
    EvaluationRuleEventType,
    EvaluationRuleFilter,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

# friendly name -> built-in evaluator id
EVALUATORS = {
    "groundedness": "builtin.groundedness",
    "relevance": "builtin.relevance",
    "coherence": "builtin.coherence",
    "fluency": "builtin.fluency",
    "task_adherence": "builtin.task_adherence",
    "intent_resolution": "builtin.intent_resolution",
    "tool_call_accuracy": "builtin.tool_call_accuracy",
    "violence": "builtin.violence",
    "hate_unfairness": "builtin.hate_unfairness",
    "self_harm": "builtin.self_harm",
    "sexual": "builtin.sexual",
    "indirect_attack": "builtin.indirect_attack",
}


def main() -> None:
    p = argparse.ArgumentParser(description="Continuous evaluation on live Foundry agent traffic")
    p.add_argument("--agent", required=True, help="agent name to evaluate")
    p.add_argument("--evaluators", nargs="+", default=["groundedness", "task_adherence", "violence"],
                   choices=sorted(EVALUATORS), metavar="EVALUATOR",
                   help=f"choices: {', '.join(sorted(EVALUATORS))}")
    p.add_argument("--max-hourly-runs", type=int, default=100,
                   help="sampling ceiling per hour (default 100) - this is also your cost dial")
    p.add_argument("--rule-id", default=None, help="default: continuous-eval-<agent>")
    args = p.parse_args()

    project_client = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()

    eval_object = openai_client.evals.create(
        name=f"Continuous evaluation - {args.agent}",
        data_source_config={"type": "azure_ai_source", "scenario": "responses"},
        testing_criteria=[
            {"type": "azure_ai_evaluator", "name": name, "evaluator_name": EVALUATORS[name]}
            for name in args.evaluators
        ])

    rule_id = args.rule_id or f"continuous-eval-{args.agent}"
    project_client.evaluation_rules.create_or_update(
        id=rule_id,
        evaluation_rule=EvaluationRule(
            action=ContinuousEvaluationRuleAction(
                eval_id=eval_object.id, max_hourly_runs=args.max_hourly_runs),
            event_type=EvaluationRuleEventType.RESPONSE_COMPLETED,
            filter=EvaluationRuleFilter(agent_name=args.agent),
            enabled=True))

    print(f"evaluation rule '{rule_id}' active for agent '{args.agent}'")
    print(f"evaluators: {', '.join(args.evaluators)}  |  ceiling: {args.max_hourly_runs} runs/hour")
    print("scores appear in the connected Application Insights and the agent Monitor tab")


if __name__ == "__main__":
    main()
