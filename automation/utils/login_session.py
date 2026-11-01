"""
login_session.py: remembers which user each browser tab is signed in as.

Why this file exists:
    Some flows use two tabs signed in as two different users (for example the
    user who assigns an asset and the employee who acknowledges it). When the ERP
    ends a session, `BasePage.sign_in_again()` must sign in again as the user of
    THAT tab, not always as the main user. `remember_user` is called once after
    each sign-in; `user_of` is read when a sign-in is needed again.
"""
from config.settings import DEFAULT_BRANCH, ERP_PASSWORD, ERP_USERNAME

# The browser tabs signed in so far -> (username, password, branch)
TAB_USERS = {}


def remember_user(page, username: str, password: str, branch: str) -> None:
    """Remember that this browser tab is signed in as this user."""
    TAB_USERS[page] = (username, password, branch)


def user_of(page) -> tuple:
    """Return (username, password, branch) of the user signed in on this tab; the main user when the tab is not known."""
    return TAB_USERS.get(page, (ERP_USERNAME, ERP_PASSWORD, DEFAULT_BRANCH))
