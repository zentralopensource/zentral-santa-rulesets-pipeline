# Zentral Santa Rulset Pipeline

This is an example of a CI/CD pipeline to manage Zentral Santa Rulesets with code reviews and multiple branches.

## Workflow

There are two branches, `staging` and `main`, and two Zentral Santa configurations, `Testing` and `Default` (All four names can be changed in the `Jenkinsfile`).

The rulesets are in the `rulesets` folder.

Pull requests with the `staging` or `main` branch as target will trigger a **dry-run** apply to their respective configuration (`Testing` or `Default`).

Merges to the `staging` or `main` branch will be applied to their respective configuration.

Changes should be introduced in feature branches. Once ready, a pull request should be made with the `staging` branch as the base. A **dry-run** apply to the `Testing` configuration will be triggered. If everything looks good, the changes should be merged into the `staging` branch, after which, the changes will be applied to the `Testing` configuration.

After a while, once the effects on the endpoints have been evaluated, a pull request can be made with the `main` branch as the base. A **dry-run** apply to the `Default` configuration will be triggered. If everything looks good, the changes should be merged into the `main` branch, after which the changes will be applied to the `Default` configuration.

The `main` and `staging` branches **must be protected**. The dry-run status check must be **required** before a merge. Changes to the `main` branch without a pull request must be **rejected**. You may allow them on the `staging` branch, to speed-up the testing of new rules.

## Jenkins setup

Multibranch job, with automatic branch discovery (via a Github application with webhooks for example), and a [`Jenkinsfile`](Jenkinsfile).

The Zentral API token is saved as a credential in Jenkins, with the `zentral-api-token` ID.

The [`Jenkinsfile`](Jenkinsfile) has 2 steps:

- Check rulesets, when pull request with the `main` or `staging` branch as targets
- Apply rulesets, when branch is `main` or `staging`

`python3` has to be available in the agent.

## Push script

The [`scripts/post_rulesets.py`](scripts/post_rulesets.py) python script is used to push all the rulesets present in the `rulesets` folder. It has no external dependencies. (**TODO** we might need the `pyyaml` at one point)

This script will **automatically set the configuration** in the ruleset. This allows the same rulesets to be applied to the `Testing` or `Default` configurations, in a dry-run or not, depending on the branch or pull request context.

Configurations set in the rulesets **will be overwritten**.
