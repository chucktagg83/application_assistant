import logging

from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class ResumeAIError(Exception):
    """Raised when the resume analysis cannot be completed."""


class ResumeAIResult(BaseModel):
    """
    Defines the exact information OpenAI must return.
    """

    match_score: int = Field(
        ge=0,
        le=100,
        description=(
            "Estimated resume-to-job match from 0 to 100. "
            "Base the score only on evidence in the supplied resume."
        ),
    )

    keyword_coverage: int = Field(
        ge=0,
        le=100,
        description=(
            "Estimated percentage of important job keywords "
            "supported by the supplied resume."
        ),
    )

    strong_matches: list[str]

    missing_requirements: list[str]

    suggested_keywords: list[str]

    interview_talking_points: list[str]

    match_summary: str

    tailored_resume: str


def tailor_resume(
    job_requirements: str,
    current_resume: str,
    target_style: str,
) -> ResumeAIResult:
    """
    Analyze and tailor a resume without inventing qualifications.
    """

    if not settings.OPENAI_API_KEY:
        raise ResumeAIError(
            "The OpenAI API key is not configured."
        )

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    system_instructions = """
You are an expert resume editor and applicant tracking system analyst.

Compare the supplied resume with the supplied job description.

Rules:

1. Do not invent experience, education, certifications, metrics,
   technologies, security clearances, dates, or accomplishments.
2. Only count a requirement as matched when the resume supports it.
3. The match score must reflect actual evidence in the resume.
4. The keyword coverage score must reflect important job-description
   terms that are truthfully supported by the resume.
5. Reorganize and rewrite the resume to improve relevance and clarity.
6. Use ATS-friendly formatting.
7. Do not use tables, graphics, icons, columns, or first-person pronouns.
8. Do not keyword-stuff.
9. Clearly identify unsupported or missing requirements.
10. Return a complete tailored resume.
""".strip()

    user_content = f"""
TARGET STYLE:
{target_style}

JOB REQUIREMENTS:
{job_requirements}

CURRENT RESUME:
{current_resume}
""".strip()

    try:
        response = client.responses.parse(
            model=settings.OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": system_instructions,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            text_format=ResumeAIResult,
        )

        result = response.output_parsed

    except Exception as error:
        logger.exception(
            "OpenAI resume analysis failed."
        )

        raise ResumeAIError(
            "The resume analysis could not be completed. "
            "Check your API key, model setting, billing, "
            "and internet connection."
        ) from error

    if result is None:
        raise ResumeAIError(
            "OpenAI did not return a usable resume analysis."
        )

    return result