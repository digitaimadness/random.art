import config
import status
import logger
from random import randint
from argparse import ArgumentParser
from sys import argv
from time import sleep
from re import sub

"""uses all other modules to post tweets if chance is met calls logger and parses arguments"""


def main():
    """runs the whole program"""
    global api  #it's used absolutely everywhere so might as well be global
    api = config.api
    status.welcome()
    args = parse_args(argv[1:])
    if args.g:
        gif_arg = args.g
    else:
        gif_arg = False
    while True:
        if randint(0, 99) < config.chance or args.t or gif_arg:
            try:
                post_tweet(gif_arg)
            except Exception as eeee:
                print(eeee)
                print ('something fucked up, restarting bot in 60 seconds..\n\nif this happens right after start pls check if you filled settings.txt correctly\nor contact https://twitter.com/digitaImadness')
                sleep(60)
                main()
            if args.t or gif_arg:
                break
        else:
            print('sleeping for',config.interval,'s..')
        sleep(config.interval)


def post_tweet(gif_arg):
    """check media state and send tweet"""
    characters = []
    copyright = []
    api = config.api
    media,tweetxt,media_state,predictions,faces_detected,danbooru_id = status.media(config.source_folder, gif_arg)
    log = config.log_file
    tolerance = config.tolerance
    if media_state == 'retry' or media_state == 'not_art':
        if media_state == 'not_art':
            logger.addPost(media, media_state, config.log_file)
        return post_tweet(gif_arg)  # just try again
    if danbooru_id != 0:
            post = status.danbooru(danbooru_id)
            characters = ['{0}'.format(sub(r'\([^)]*\)', '', tag)) for tag in post['tag_string_character'].split()]
            characters = ['{0}'.format(tag.replace("_", " ")) for tag in characters]
            copyright = ['{0}'.format(tag.replace("_", " ")) for tag in post['tag_string_copyright'].split()]
    if bool(config.neural_opt) and faces_detected:
        if len(predictions) == 1:
                tweetxt += '\nface recognized'
        elif len(predictions) > 1 and len(predictions) == len(characters):
            tweetxt += '\n' + str(len(predictions)) + ' faces recognized'
        else:
            tweetxt += '\nfaces recognized'
        if characters != []:
            tweetxt += ': ' + ", ".join(characters)
            for waifu in predictions:
                if waifu[1] > 0.77:
                    tweetxt += ': ' + waifu[0] + ' (' + str(int(waifu[1]*100)) + '%) '
    else:
        if characters != [] and len(characters) == 1:
            tweetxt += '\ncharacter: ' + ", ".join(characters)
        elif characters != [] and len(characters) > 1:
            tweetxt += '\ncharacters: ' + ", ".join(characters)
    if copyright != []:
        tweetxt += '\nfrom: ' + copyright[0]
    status.tweet(media, tweetxt, api)
    logger.addPost(media, media_state, config.log_file)


def parse_args(args):
    """parsing arguments from command line"""
    parser = ArgumentParser()
    parser.add_argument("-t", help="manual tweet", action="store_true")
    parser.add_argument("-g", help="manual tweet GIF", action="store_true")
    return parser.parse_args(args)


if __name__ == "__main__":
    main()
