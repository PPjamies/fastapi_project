import re
import sys

COMMIT_TYPES = {
    "feat", "fix", "perf", "docs", "style", "refactor",
    "test", "build", "ci", "chore", "revert",
}

# <type><(optional)!><:description>
# feat: added a new api endpoint for user
# feat!: create user requires a new parameter
TITLE_PATTERN = re.compile(r"^(?P<type>\w+)(\([^)]+\))?(?P<breaking>!)?: .+")


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ("yes", "no"):
        print('Usage: python scripts/check_label.py "<pr title>" <yes|no>')
        sys.exit(2)

    pr_title = sys.argv[1]
    api_is_breaking = sys.argv[2] == "yes"

    # title must adhere to naming convention
    match = TITLE_PATTERN.match(pr_title)
    if not match:
        print(f'PR title "{pr_title}" is not in the format "<commit_type>: <commit_message>"')
        sys.exit(1)

    # commit type must match one of the valid types
    commit_type = match.group("type")
    if commit_type not in COMMIT_TYPES:
        print(f'Unknown type "{commit_type}". Use one of: {", ".join(sorted(COMMIT_TYPES))}')
        sys.exit(1)

    label_is_breaking = match.group("breaking") == "!"

    if api_is_breaking and not label_is_breaking:
        print("oasdiff found breaking API changes, but the title is not marked breaking.")
        print(f'Did you mean: "{commit_type}!: ..."?  Or change the code so it is not breaking.')
        sys.exit(1)

    if label_is_breaking and not api_is_breaking:
        print("Title is marked breaking, but oasdiff found no breaking API changes.")
        print("That's allowed (some breaks don't show in the schema). Double-check it's intended.")
        sys.exit(0)

    print(f'Label "{commit_type}{"!" if label_is_breaking else ""}" matches the API changes.')


if __name__ == "__main__":
    main()
