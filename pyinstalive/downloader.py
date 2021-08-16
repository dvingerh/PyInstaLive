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
            logger.error("PyInstaLive must be installed to use the -df argument.")
            logger.separator()
        else:
            dlfuncs.download_following()
    else:
        if not helpers.download_folder_has_lockfile():
            helpers.create_lock_user()
            checking_self = pil.dl_user == pil.ig_user
            logger.info('Getting livestream information for user: {:s}'.format(pil.dl_user))
            logger.separator()
            broadcast_info_result = dlfuncs.get_broadcasts_info()
            if broadcast_info_result == True:
                if checking_self:
                    logger.warn("Login with a different account to download your own livestreams.")
                elif pil.initial_broadcast_obj:
                    logger.info("Livestream available, starting download.")
                    dlfuncs.download_livestream()
            elif broadcast_info_result == False:
                logger.info('There is currently no available livestream.')
            elif not broadcast_info_result:
                logger.binfo('The checking process was aborted by the user.')
            helpers.remove_lock()
            logger.separator()
        else:
            logger.warn("Lock file is already present for this user, there is probably another download ongoing.")
            logger.warn("If this is not the case, manually delete the file '{:s}' and try again.".format(
                pil.dl_user + '.lock'))
            logger.separator()
