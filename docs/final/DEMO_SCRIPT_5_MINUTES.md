# CodeGate: 5-Minute Demo Script

*This script is designed for a strict 5-minute academic or professional presentation.*

## [00:00 - 00:30] The Problem
**Action**: Display Slide 2 (Why AI Code Review Isn't Enough).
**Speaker**: "Hello, my name is [Name], and this is CodeGate. Today, many teams use AI to review Pull Requests. But AI is probabilistic—it hallucinates. You cannot block a production merge based on an LLM's hallucination. Teams need hard, deterministic evidence—tests, security scans, and code metrics—anchoring the AI."

## [00:30 - 01:00] The Architecture
**Action**: Display Slide 5 (System Architecture).
**Speaker**: "CodeGate solves this by acting as an orchestrator. When a PR is opened on GitHub, CodeGate catches the webhook. It queries the AI for semantic review, but simultaneously runs static analyzers like Ruff and Bandit, and test coverage tools. Everything is persisted into PostgreSQL to generate explainable Quality and Risk scores."

## [01:00 - 01:45] The Dashboard
**Action**: Switch to browser. Open CodeGate Dashboard at `http://127.0.0.1:5173`.
**Speaker**: "This is the CodeGate Dashboard, built in React. Here, engineering managers have real-time visibility into the health of their repositories. You can immediately see which PRs are passing, which are warned, and which are blocked, along with aggregated quality metrics."

## [01:45 - 02:30] PR Detail
**Action**: Click into a "BLOCK" PR in the dashboard.
**Speaker**: "Let's look at this specific Pull Request. CodeGate has analyzed it and issued a strict BLOCK policy. Notice that the AI review provided helpful feedback, but the BLOCK decision was not made by the AI. It was made deterministically."

## [02:30 - 03:15] Quality / Risk / Policy
**Action**: Scroll down to the Quality and Risk breakdown cards.
**Speaker**: "The Quality Score is 42, and the Risk Score is high. If we look at the evidence, Bandit detected a critical security vulnerability—a hardcoded secret or unsafe execution. Our Policy Engine evaluated this evidence against our strict thresholds, overriding the AI, and blocked the merge."

## [03:15 - 04:00] GitHub Integration
**Action**: Open the corresponding Pull Request on GitHub.
**Speaker**: "To ensure developers don't have to leave their workflow, CodeGate publishes this decision directly back to GitHub as a Check Run. As you can see, the Check Run has failed, natively preventing the developer from clicking the merge button."

## [04:00 - 04:30] Reviewer Recommendation & Analytics
**Action**: Switch back to the CodeGate PR Dashboard and point to the Reviewers section.
**Speaker**: "Additionally, CodeGate recommends the best human reviewers for this code by scanning Git history, directory expertise, and CODEOWNERS files, ensuring the right manager reviews the vulnerability."

## [04:30 - 05:00] Conclusion
**Action**: Return to Slide 15 (Conclusion).
**Speaker**: "In just 5 minutes, you've seen how CodeGate bridges the gap between raw AI assistance and enterprise-grade merge policies, all backed by a secure Docker and PostgreSQL infrastructure. Thank you for your time."
