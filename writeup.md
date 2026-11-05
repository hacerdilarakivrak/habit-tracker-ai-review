# Week 6 — AI Code Review & Testing

## 1. Implemented Features

I implemented two features in separate branches and opened two pull requests.

**PR #1 — Input Validation**
- Branch: `feature/validation`
- Added validation to reject empty or whitespace-only habit names.
- Added validation for check-in dates using the YYYY-MM-DD format and valid calendar dates.
- Added tests for valid and invalid inputs.

**PR #2 — Weekly Summary**
- Branch: `feature/weekly-summary`
- Added `GET /habits/{id}/summary`.
- The endpoint counts distinct check-in dates within the last seven days, including today.
- Returns a 404 error for an unknown habit.
- Added tests for duplicate check-ins, date boundaries, invalid stored dates, and timezone offsets.

## 2. Manual Code Review

I manually inspected the changes in `main.py` and `test_main.py`.

For input validation, I checked whether invalid names and dates were rejected with appropriate HTTP responses and whether valid inputs continued to work.

For the weekly summary, I checked the seven-day date range, distinct-day counting, unknown habit handling, and test coverage.

My initial review focused on the expected functionality and basic edge cases. I did not initially identify all the problems related to stored date formats, database isolation, and timezone offsets.

## 3. AI Code Review — CodeRabbit

I used CodeRabbit to review the pull requests.

**PR #1:** CodeRabbit reported a documentation coverage warning related to missing docstrings.

**PR #2:** CodeRabbit identified the following issues:

1. **Date counting:** The original SQL query counted raw date strings rather than normalized calendar dates. This could produce incorrect weekly counts.
2. **Test database isolation:** Tests were using the application's database file, potentially leaving test data behind.
3. **Timezone handling:** A later review found that SQLite's `date(day)` could shift timezone-offset timestamps to a different UTC date, causing incorrect weekly counts.

I addressed these issues by updating the weekly summary query, adding temporary SQLite databases for tests, and introducing regression tests for malformed dates and timezone offsets.

After the fixes, the local tests and formatting checks passed, and the updated PR #2 completed its GitHub checks successfully.

## 4. Manual Review vs. AI Review

My manual review was useful for understanding the code, checking the feature requirements, and confirming basic API behavior.

CodeRabbit provided additional value by identifying less obvious problems, especially database test isolation and timezone-related date calculations.

The AI review was not a replacement for manual review. I still needed to examine each suggestion, understand the underlying problem, apply a suitable fix, and verify the result with tests.

The most important difference was that manual review helped me assess the intended behavior, while AI review helped reveal edge cases I had initially overlooked.

## 5. Automated Guardrails

The project uses the following tools:

- **Black:** Checks Python code formatting.
- **Ruff:** Checks Python code quality and linting.
- **pytest:** Runs automated tests.
- **GitHub Actions:** Runs these checks automatically in CI.

I verified that the weekly summary branch passed nine automated tests along with Black and Ruff checks.

To confirm that CI detects failures, I created a separate branch named `test/ci-failure-proof` and added an intentionally failing test:

```python
def test_ci_detects_failure():
    assert 1 == 2
```

The local pytest run reported **1 failed, 3 passed**, and the GitHub Actions workflow also failed, as expected.

This failing test was kept on a separate branch and was not merged into the main application.

## 6. What I Learned

This assignment taught me that AI-generated code should always be reviewed and tested before it is accepted. I learned how to use feature branches and pull requests to organize changes and how an AI reviewer can detect issues that are easy to miss during manual review. I also learned that automated guardrails such as Black, Ruff, pytest, and GitHub Actions help prevent incorrect changes from being merged. Most importantly, I learned that AI feedback is most useful when I verify its suggestions rather than accepting them automatically.

## Pull Request Links

- [PR #1 — Input Validation](https://github.com/hacerdilarakivrak/habit-tracker-ai-review/pull/1)
- [PR #2 — Weekly Summary](https://github.com/hacerdilarakivrak/habit-tracker-ai-review/pull/2)

## CI Failure Evidence

- [GitHub Actions runs](https://github.com/hacerdilarakivrak/habit-tracker-ai-review/actions)
- Evidence branch: `test/ci-failure-proof`