## Contributing Guidelines

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional documentation, we greatly value feedback and contributions from our community.

## Reporting Bugs/Feature Requests

We welcome you to use the GitHub issue tracker to report bugs or suggest features.

When filing an issue, please check existing open and closed issues to make sure somebody else hasn't already reported the issue. Please try to include as much information as you can. We have added issue template that will guide you with details expected from an issue.

## How do I make a contribution?
Never made an open source contribution before? Wondering how contributions work in the in our project? Here's a quick rundown!

1. Find an issue that you are interested in addressing or a feature that you would like to add.
2. Fork the repository associated with the issue to your local GitHub organization. This means that you will have a copy of the repository under `your-GitHub-username/repository-name`.
3. Clone the repository to your local machine using `git clone https://github.com/github-username/repository-name.git`.
4. Create a new branch for your fix using `git checkout -b branch-name-here`.
5. Make the appropriate changes for the issue you are trying to address or the feature that you want to add.
6. Use `git add insert-paths-of-changed-files-here` to add the file contents of the changed files to the "snapshot" git uses to manage the state of the project, also known as the index.
7. Use `git commit -m "Insert a short message of the changes made here"` to store the contents of the index with a descriptive message.
8. Push the changes to the remote repository using `git push origin branch-name-here`.
9. Submit a pull request to the upstream repository.
10. Title the pull request with a short description of the changes made and the issue or bug number associated with your change. For example, you can title an issue like so "Added more log outputting to resolve #4352".
11. In the description of the pull request, explain the changes that you made, any issues you think exist with the pull request you made, and any questions you have for the maintainer. It's OK if your pull request is not perfect (no pull request is), the reviewer will be able to help you fix any problems and improve it!
12. Wait for the pull request to be reviewed by a maintainer.
13. Make changes to the pull request if the reviewing maintainer recommends them.
14. Celebrate your success after your pull request is merged!

## Finding contributions to work on

Looking at the existing issues is a great way to find something to contribute on.
As our projects, by default, use the default GitHub issues is a great place to start.

### Running tests  
  
Please check the tests by running them with:
```
python -m unittest
```