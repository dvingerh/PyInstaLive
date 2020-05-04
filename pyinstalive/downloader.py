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
        if not pil.dl_lives:
            logger.binfo("Livestream downloading is disabled either with an argument or in the config file.")
            logger.separator()
        if not pil.dl_replays:
            logger.binfo("Replay downloading is disabled either with an argument or in the config file.")
            logger.separator()
        if not helpers.command_exists("pyinstalive") and not pil.winbuild_path:
            logger.error("PyInstaLive must be properly installed when using the -df argument.")
            logger.separator()
        else:
            dlfuncs.download_following()
    else:
        if not helpers.download_folder_has_lockfile():
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
                            '{:s} available, beginning download.'.format("Replays" if len(
                                pil.replays_obj) > 1 else "Replay"))
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
