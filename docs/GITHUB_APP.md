# GitHub App Integration

For production, use a GitHub App instead of a personal access token:

1. Create a GitHub App with permissions: `contents: read/write`, `actions: read`
2. Install the app on your repo
3. Use the app's JWT to get installation access token
4. Set `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY` (base64 or path)
5. Agent uses installation token for API calls

See: https://docs.github.com/en/apps
