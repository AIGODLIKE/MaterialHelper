is_sync = False


def sync_lock():
    global is_sync
    if is_sync:
        is_sync = False
        return True
    is_sync = True
    return False
