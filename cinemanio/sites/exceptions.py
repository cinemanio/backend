class PossibleDuplicate(Exception):
    """
    Raised, when possible duplicate found
    """
    pass


class NothingFound(Exception):
    """
    Raised, when no any search results found
    """
    pass


class WrongValue(Exception):
    """
    Raised, when trying to assign wrong value
    """
    pass


class SiteIDDoesNotExist(Exception):
    """
    Raised, when trying to sync unexisted site link
    """
    pass
