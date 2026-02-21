"""Few-shot examples for log analysis prompts."""
FEW_SHOT_EXAMPLES = """
EXAMPLE 1:
LOGS:
> node test.js
❌ CRITICAL ERROR: Environment variable 'FIX_APPLIED' is missing.
Test suite failed.
ROOT CAUSE: Missing required environment variable FIX_APPLIED in Dockerfile or test setup.
SUGGESTED FIX: Add ENV FIX_APPLIED=true to Dockerfile or set the variable before running tests.
FILE: Dockerfile or src/target_app/Dockerfile
CONFIDENCE: 0.95

EXAMPLE 2:
LOGS:
npm ERR! 404 Not Found: package 'typo-package@1.0.0'
ROOT CAUSE: Invalid or non-existent npm package name in package.json.
SUGGESTED FIX: Fix the package name in package.json dependencies.
FILE: package.json
CONFIDENCE: 0.9
"""
