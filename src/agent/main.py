"""AI CI/CD Healer Agent - Main entry point."""
import os
import sys
import argparse
import json
import time

from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.providers import get_provider
from lib.llm_utils import truncate_logs_smart, with_retry
from lib.audit import log_audit
from lib.file_resolver import find_file
from lib.cache import get_cached_analysis, set_cached_analysis
from lib.circuit_breaker import get_llm_circuit
from lib.logger import info, warn, error
from lib.logger import correlation_id_var
from lib.sanitize import sanitize_logs
from lib.guardrails import is_path_allowed, validate_llm_output_corrected_code
from lib.secret_detect import has_secret
from lib.signals import setup_graceful_shutdown, is_shutdown_requested, check_shutdown
from lib.token_tracker import log_token_usage, check_budget_alert
from lib.prompts import FEW_SHOT_EXAMPLES
from lib.alert import alert_heal_failures
from lib.rollback import rollback_last, rollback_n
from lib.pre_verify import run_pre_verify

load_dotenv()

# --- Config ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DASHBOARD_STATUS_FILE = Path(os.getenv("DASHBOARD_STATUS_FILE", "src/dashboard/public/status.json"))
LOG_MAX_CHARS = int(os.getenv("LOG_MAX_CHARS", "16000"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.8"))
PRIMARY_MODEL = os.getenv("LLM_PRIMARY_MODEL", "gemini-2.0-flash")
FALLBACK_MODEL = os.getenv("LLM_FALLBACK_MODEL", "gemini-1.5-flash")
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
ALLOW_RESTRICTED = os.getenv("ALLOW_RESTRICTED_FILES", "").lower() in ("1", "true", "yes")


def validate_env() -> None:
    if not GOOGLE_API_KEY or not GOOGLE_API_KEY.strip():
        error("GOOGLE_API_KEY not found")
        if os.getenv("CI"):
            info("Running in CI. Ensure GOOGLE_API_KEY secret is set.")
        sys.exit(1)


class LogAnalysisResult(BaseModel):
    root_cause: str = Field(description="The technical root cause of the failure based on the logs")
    suggested_fix: str = Field(description="The specific code or configuration change to fix the issue")
    file_path: str = Field(description="The relative file path that likely needs to be changed")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")


class CodeFixResult(BaseModel):
    corrected_code: str = Field(description="The complete, corrected content of the file")
    explanation: str = Field(description="Brief explanation of changes made")


def update_dashboard(status: str, run_id: str, logs: str = "", analysis: dict | None = None,
                     action: str | None = None, provider_context: str = "",
                     correlation_id: str | None = None) -> None:
    data: dict = {
        "last_run_id": run_id,
        "status": status,
        "logs": logs[:500] + "..." if len(logs) > 500 else logs,
        "timestamp": time.time(),
        "provider": provider_context,
    }
    if correlation_id:
        data["correlation_id"] = correlation_id
    if analysis:
        data["analysis"] = analysis
    else:
        data["analysis"] = {"root_cause": None, "suggested_fix": None, "confidence_score": 0}
    if action:
        data["last_action"] = action
    try:
        if not DASHBOARD_STATUS_FILE.parent.exists() and os.getenv("CI"):
            return
        DASHBOARD_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DASHBOARD_STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        warn("Failed to update dashboard", error=str(e))


def get_llm(model: str | None = None) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model or PRIMARY_MODEL,
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
    )


def analyze_with_gemini(logs: str, context: str, correlation_id: str) -> LogAnalysisResult:
    truncated = truncate_logs_smart(sanitize_logs(logs), LOG_MAX_CHARS)
    parser = PydanticOutputParser(pydantic_object=LogAnalysisResult)
    prompt = PromptTemplate(
        template="""You are an expert DevOps AI Agent capable of diagnosing CI/CD failures.

{few_shot}

CONTEXT: {context}

Analyze the following CI/CD build logs. Provide root cause, suggested fix, file path, and confidence (0.0-1.0).

LOGS:
{logs}

{format_instructions}
""",
        input_variables=["logs", "context"],
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
            "few_shot": FEW_SHOT_EXAMPLES,
        },
    )

    def _try(model: str) -> LogAnalysisResult:
        circuit = get_llm_circuit()
        result = circuit.execute(
            lambda: with_retry(
                lambda: (prompt | get_llm(model) | parser).invoke({"logs": truncated, "context": context}),
                max_retries=MAX_RETRIES,
            )
        )
        # Approximate token usage
        inp, out = len(truncated) // 4, len(str(result)) // 4
        log_token_usage("", model, inp, out, correlation_id)
        if check_budget_alert(correlation_id):
            warn("Token budget threshold exceeded", correlation_id=correlation_id)
        return result

    try:
        return _try(PRIMARY_MODEL)
    except Exception as e1:
        info("Primary model failed, trying fallback", error=str(e1))
        return _try(FALLBACK_MODEL)


def generate_code_fix(file_content: str, suggestion: str, filename: str, correlation_id: str) -> CodeFixResult:
    parser = PydanticOutputParser(pydantic_object=CodeFixResult)
    prompt = PromptTemplate(
        template="""You are an expert Software Engineer. Return the COMPLETE corrected file content.

FILENAME: {filename}

CURRENT CONTENT:
{file_content}

SUGGESTION:
{suggestion}

{format_instructions}
""",
        input_variables=["file_content", "suggestion", "filename"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    def _try(model: str) -> CodeFixResult:
        result = (prompt | get_llm(model) | parser).invoke({
            "file_content": file_content,
            "suggestion": suggestion,
            "filename": filename,
        })
        log_token_usage("", model, len(file_content) // 4, len(result.corrected_code) // 4, correlation_id)
        return result

    try:
        return _try(PRIMARY_MODEL)
    except Exception as e1:
        info("Primary model failed, trying fallback", error=str(e1))
        return _try(FALLBACK_MODEL)


def apply_fix_real(analysis: LogAnalysisResult, run_id: str, provider_name: str,
                   correlation_id: str, dry_run: bool = False) -> str | None:
    allowed, reason = is_path_allowed(analysis.file_path, allow_restricted=ALLOW_RESTRICTED)
    if not allowed:
        error("Guardrail blocked path", path=analysis.file_path, reason=reason)
        return None

    target_file = find_file(analysis.file_path)
    if not target_file or not target_file.exists():
        error("Could not locate file", path=analysis.file_path)
        return None

    info("Located target file", path=str(target_file))
    try:
        with open(target_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        error("Error reading file", error=str(e))
        return None

    fix_result = generate_code_fix(content, analysis.suggested_fix, analysis.file_path, correlation_id)
    ok, msg = validate_llm_output_corrected_code(fix_result.corrected_code)
    if not ok:
        error("Output validation failed", reason=msg)
        return None
    secret_ok, secret_msg = has_secret(fix_result.corrected_code)
    if secret_ok:
        error("Secret detection blocked output", reason=secret_msg)
        return None

    if dry_run:
        info("Dry-run: would apply fix", path=str(target_file), explanation=fix_result.explanation)
        return fix_result.explanation

    passed, pv_msg = run_pre_verify(str(target_file))
    if not passed:
        error("Pre-verify failed", message=pv_msg)
        return None

    # Backup before write
    backup_dir = Path("logs/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{target_file.name}_{int(time.time())}.bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(fix_result.corrected_code)

    log_audit("fix_applied", run_id, provider_name, {
        "file": str(target_file),
        "explanation": fix_result.explanation,
        "backup": str(backup_path),
    })
    info("Fix applied", path=str(target_file))
    return fix_result.explanation


def run_heal(args: argparse.Namespace) -> int:
    setup_graceful_shutdown()
    validate_env()

    if getattr(args, "rollback", False):
        n = getattr(args, "rollback_n", 1)
        ok, msg = rollback_n(n) if n > 1 else rollback_last()
        info("Rollback", success=ok, message=msg)
        return 0 if ok else 1

    run_id = args.run_id or "local-simulation"
    provider_name = "github" if args.mode == "ci" else (args.provider or "local")
    correlation_id = f"heal-{run_id}-{int(time.time())}"
    correlation_id_var.set(correlation_id)
    dry_run = getattr(args, "dry_run", False)

    provider = get_provider(provider_name)
    if provider_name not in ("local", "github"):
        valid, err = provider.validate_env()
        if not valid:
            error("Provider config", error=err)
            return 1

    context = provider.get_context()
    info("Agent starting", provider=provider_name, correlation_id=correlation_id)

    if args.logs:
        logs = args.logs
    elif getattr(args, "simulate_failure", False):
        from lib.simulate import get_simulated_logs
        logs = get_simulated_logs()
    else:
        logs = provider.fetch_logs(run_id)

    check_shutdown()

    # Cache lookup (idempotency for identical logs)
    cached = get_cached_analysis(logs)
    if cached:
        info("Using cached analysis")
        from pydantic import BaseModel
        analysis = LogAnalysisResult(**cached)
    else:
        if provider_name == "local":
            update_dashboard("analyzing", run_id, logs, provider_context=context, correlation_id=correlation_id)
        log_audit("analysis_started", run_id, provider_name, {"correlation_id": correlation_id})

        try:
            analysis = analyze_with_gemini(logs, context, correlation_id)
            set_cached_analysis(logs, analysis.model_dump())
            if provider_name == "local":
                update_dashboard("review_needed", run_id, logs, analysis.model_dump(),
                                 provider_context=context, correlation_id=correlation_id)
        except Exception as e:
            error("Analysis failed", error=str(e))
            log_audit("analysis_failed", run_id, provider_name, {"error": str(e)})
            cb = get_llm_circuit()
            alert_heal_failures(run_id, str(e), cb.failures)
            if provider_name == "local":
                update_dashboard("error", run_id, str(e), provider_context=context, correlation_id=correlation_id)
            return 1

    check_shutdown()

    info("Analysis complete", root_cause=analysis.root_cause[:100], confidence=analysis.confidence_score)

    if analysis.confidence_score > CONFIDENCE_THRESHOLD:
        explanation = apply_fix_real(analysis, run_id, provider_name, correlation_id, dry_run)
        if provider_name == "local":
            update_dashboard("healed", run_id, logs, analysis.model_dump(),
                             f"Fix Applied: {explanation}" if explanation else "", provider_context=context,
                             correlation_id=correlation_id)
    else:
        info("Confidence too low for auto-fix")
        log_audit("needs_human_review", run_id, provider_name, {"confidence": analysis.confidence_score})
        if provider_name == "local":
            update_dashboard("needs_human_review", run_id, logs, analysis.model_dump(),
                             provider_context=context, correlation_id=correlation_id)

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI CI/CD Healer Agent (Powered by Gemini)",
        epilog="""
Examples:
  python main.py --provider local
  python main.py --mode ci --logs "$(cat build_logs.txt)"
  python main.py --provider jenkins --run-id myjob/123
  python main.py --dry-run --provider local
  python main.py --rollback
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--run-id", help="Run/build ID to analyze")
    parser.add_argument("--provider", default="local",
                        choices=["local", "github", "jenkins", "aws", "azure", "gitlab"],
                        help="CI provider (default: local)")
    parser.add_argument("--mode", choices=["ci", "local"],
                        help="ci = use github provider in CI context")
    parser.add_argument("--logs", help="Raw build logs (overrides provider fetch)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Analyze and propose fix but do not apply")
    parser.add_argument("--rollback", action="store_true",
                        help="Rollback last applied fix from backup")
    parser.add_argument("--rollback-n", type=int, default=1,
                        help="When using --rollback, number of fixes to undo (default: 1)")
    parser.add_argument("--simulate-failure", action="store_true",
                        help="Use simulated failure logs for local testing")
    args = parser.parse_args()
    sys.exit(run_heal(args))


if __name__ == "__main__":
    main()
