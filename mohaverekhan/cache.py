from django.apps import apps
import logging
import random
import re
repetition_pattern = re.compile(r"([^A-Za-z])\1{1,}")
# debug_pattern = re.compile(r'[0-9۰۱۲۳۴۵۶۷۸۹]')
# debug_pattern = re.compile(r'^گرون$|^میدون$|^خونه$|^نون$|^ارزون$|^اون$|^قلیون$')
# debug_pattern = re.compile(r'هایمان')
debug_pattern = re.compile(r'باید|دنبال')

logger = None
token_set = set()
repetition_word_set = set()

def cache_tokens():
    # tokens = set()
    TaggedSentence = apps.get_model(app_label='mohaverekhan', model_name='TaggedSentence')
    # tokens = TaggedSentence.objects.only('tokens__content')
    token_content, tag_name = '', ''
    sentence_tokens_list = TaggedSentence.objects.filter(is_valid=True).values_list('tokens', flat=True)
    if sentence_tokens_list.count() == 0:
        return
    for sentence_tokens in sentence_tokens_list:
        for token in sentence_tokens:
            token_content = token['content']
            tag_name = token['tag']['name']
            if debug_pattern.search(token_content):
                # if tag_name != 'U':
                logger.info(f'> Token [{token_content}] has tag [{tag_name}]')
            if tag_name not in ('O', 'U'):
                token_set.add(token_content)
    logger.info(f'> len(token_set) : {len(token_set)}')
    logger.info(f'> token_set samples : {set(random.sample(token_set, 20)) }')
    for token in token_set:
        if repetition_pattern.search(token):
            repetition_word_set.add(token)
    logger.info(f'> len(repetition_word_set) : {len(repetition_word_set)}')
    logger.info(f'> repetition_word_set samples: {set(random.sample(repetition_word_set, 100))}')


    # logger.info(f'> debug_pattern : {debug_pattern}')
    # for token in token_set:
    #     if debug_pattern.search(token):
    #         logger.info(token)
    # tokens = TaggedSentence.objects.only('tokens__content').order_by('-tokens__content').distinct('tokens__content')
    # logger.info(f'tokens.count() : {tokens.count()}')

bitianist_validator = None

def cache_bitianist_validator():
    global bitianist_validator
    Validator = apps.get_model(app_label='mohaverekhan', model_name='Validator')
    bitianist_validator = Validator.objects.filter(name='bitianist-validator').first()


def init():
    global logger
    logger = logging.getLogger(__name__)
    cache_bitianist_validator()
    cache_tokens()