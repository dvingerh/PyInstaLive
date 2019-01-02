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
        if not helpers.command_exists("pyinstalive"):
            logger.error("PyInstaLive must be properly installed when using the -df argument.")
            logger.separator()
        else:
            dlfuncs.download_following()
    else:
        if not helpers.check_lock_file():
            helpers.create_lock_user()
            checking_self = pil.dl_user == pil.ig_api.authenticated_user_name
            if dlfuncs.get_broadcasts_info():
                if pil.dl_lives:
                    if checking_self:
                        logger.warn("Login with a different account to download your own livestreams.")
                    elif pil.livestream_obj:
                        logger.info("Livestream available, starting download.")
                        dlfuncs.download_livestream()
                    else:
                        logger.info('There are no available livestreams.')
                else:
                    logger.binfo("Livestream downloading is disabled either with an argument or in the config file.")

                logger.separator()

                if pil.dl_replays:
                    if pil.replays_obj:
                        logger.info(
                            '{:d} {:s} available, beginning download.'.format(len(pil.replays_obj), "replays" if len(
                                pil.replays_obj) > 1 else "replay"))
                        dlfuncs.download_replays()
                    else:
                        logger.info('There are no available replays{:s}.'.format(" saved on your account" if checking_self else ""))
                else:
                    logger.binfo("Replay downloading is disabled either with an argument or in the config file.")

            helpers.remove_lock()
            logger.separator()
        else:
            logger.warn("Lock file is already present for this user, there is probably another download ongoing.")
            logger.warn("If this is not the case, manually delete the file '{:s}' and try again.".format(
                pil.dl_user + '.lock'))
            logger.separator()
