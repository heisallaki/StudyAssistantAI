PLANNER_RECOMMENDATION_INSTRUCTIONS = (
    "You are an academic study planning assistant. Based on the student's current subjects, "
    "goals, deadlines, and recent quiz performance, recommend what they should focus on next. "
    "Respond with ONLY a JSON object (no markdown, no commentary, no code fences) matching "
    "exactly this structure:\n\n"
    '{"recommendations": [{"subject": "...", "action": "...", "reason": "..."}]}\n\n'
    "Rules:\n"
    '- "subject" names a subject from the list given, or "General" if not subject-specific\n'
    '- "action" is a short, concrete suggestion, a few words to one sentence\n'
    '- "reason" is a brief, specific justification referencing the actual data given\n'
    "- Return at most 5 recommendations, ordered by priority with the most urgent first\n"
    "- Only use the information given. Never invent deadlines, scores, or subjects not listed."
)


def build_planner_recommendation_prompt(
    subjects_summary: str,
    goals_summary: str,
    deadlines_summary: str,
    quiz_performance_summary: str | None,
) -> str:
    parts = [PLANNER_RECOMMENDATION_INSTRUCTIONS, subjects_summary, goals_summary, deadlines_summary]
    if quiz_performance_summary:
        parts.append(quiz_performance_summary)
    return "\n\n".join(parts)