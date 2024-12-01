import logging
import subprocess
from packaging.version import parse as parse_version

logger = logging.getLogger(__name__)


def get_parent_release_branch() -> str:
    try:
        # Get list of branches and their commit hashes
        branch_info = subprocess.check_output(
            ["git", "for-each-ref", "--format=%(objectname) %(refname)", "refs/remotes/origin/release/*"]
        ).decode("utf-8").strip().split("\n")

        if not branch_info or branch_info == ['']:
            logger.info("No remote release branches found.")
            return "dev"

        logger.debug(f"Found remote release branches: {branch_info}")

        valid_versions = []

        for line in branch_info:
            commit_hash, ref_name = line.strip().split(' ', 1)
            version = ref_name.split("/")[-1]
            logger.debug(f"Processing branch {ref_name} with version {version} and commit hash {commit_hash}")

            # Use the commit hash in the merge-base command
            is_ancestor = subprocess.run(
                ["git", "merge-base", "--is-ancestor", commit_hash, "HEAD"],
                capture_output=True
            )

            logger.debug(
                f"Checking if commit {commit_hash} is an ancestor of HEAD: Return code = {is_ancestor.returncode}"
            )

            if is_ancestor.returncode == 0:  # 0 means it's an ancestor
                logger.debug(f"Parent release branch found: {version}")
                valid_versions.append(version)

        if valid_versions:
            highest_version = max(valid_versions, key=lambda s: parse_version(s))
            return highest_version
        else:
            logger.debug("No parent release branch found.")
            return "dev"
    except Exception as e:
        logger.error(f"Error: {e}")
        return "unknown"
