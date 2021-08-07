try:
    import logger
    import helpers
    import pil
    import dlfuncs
except ImportError:
    from . import logger
    from . import helpers
    from . import pil
    from . import dlfuncs


def start():
    if pil.args.downloadfollowing:
        if not helpers.command_exists("pyinstalive") and not pil.winbuild_path:
            logger.error("PyInstaLive must be properly installed when using the -df argument.")
            logger.separator()
        else:
            dlfuncs.download_following()
    else:
        if not helpers.download_folder_has_lockfile():
            helpers.create_lock_user()
            checking_self = pil.dl_user == pil.ig_user
            logger.info('Getting livestream info for user: {:s}'.format(pil.dl_user))
            logger.separator()
            if dlfuncs.get_broadcasts_info():
                if checking_self:
                    logger.warn("Login with a different account to download your own livestreams.")
                elif pil.livestream_obj:
                    logger.info("Livestream available, starting download.")
                    dlfuncs.download_livestream()
            else:
                logger.info('There is currently no active livestream.')

            helpers.remove_lock()
            logger.separator()
        else:
            logger.warn("Lock file is already present for this user, there is probably another download ongoing.")
            logger.warn("If this is not the case, manually delete the file '{:s}' and try again.".format(
                pil.dl_user + '.lock'))
            logger.separator()
