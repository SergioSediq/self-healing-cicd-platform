// Intentional failure to trigger the agent
console.log("Running comprehensive test suite...");
console.log("Checking environment configuration...");

// The Agent should detect this failure and either updates the code to remove this check
// OR update the deployment config to add the environment variable.
if (process.env.FIX_APPLIED !== 'true') {
    console.error("❌ CRITICAL ERROR: Environment variable 'FIX_APPLIED' is missing.");
    console.error("Test suite failed.");
    process.exit(1);
}

console.log("✅ Configuration correct. Tests Passed!");
