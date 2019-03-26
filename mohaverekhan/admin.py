from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (Normalizer, Text, NormalText, 
            TagSet, Tag, Tagger,
            Sentence, TaggedSentence, TranslationCharacter, 
            RefinementPattern)

class NormalTextInline(admin.TabularInline):
    model = Text.normalizers.through
    fk_name = 'text'
    fields = ('id', 'content', 'is_valid', 
            'text', 'normalizer', 'created')
    readonly_fields = ['created', 'id']
    extra = 0
    max_num = 25

class TaggedSentenceInline(admin.TabularInline):
    model = Sentence.taggers.through
    fields = ('id', 'tokens', 'is_valid', 'tagger', 'sentence', 'created')
    readonly_fields = ['created', 'id']
    extra = 0
    max_num = 25

class TextSentenceInline(admin.TabularInline):
    model = Sentence
    fields = ('content', 'text', 'order', 'id', 'created')
    readonly_fields = ['created', 'id']
    extra = 0
    max_num = 25

class NormalTextSentenceInline(admin.TabularInline):
    model = Sentence
    fields = ('content', 'order', 'id', 'created')
    readonly_fields = ['created', 'id']
    extra = 0
    max_num = 25

class TagInLine(admin.TabularInline):
    model = Tag
    fields = ('name', 'persian', 'color', 'examples', 'id', 'created')
    readonly_fields = ['examples', 'created', 'id']
    extra = 0
    max_num = 25

class TagAdmin(admin.ModelAdmin):

    def get_color_html(self, obj):
        return format_html(
            f'''
            <div class="color-outer">
                <div class="color-text" >{obj.color}</div>
                <div class="color-box" style="background-color: {obj.color};"></div>
            </div>
            ''')
    get_color_html.admin_order_field = 'created' 
    get_color_html.short_description = 'Color'

    list_display = ('name', 'persian', 
                'get_color_html', 'examples', 'tag_set', 'created')
    ordering = ('-tag_set', '-created')
    readonly_fields = ['created', 'id']

    fieldsets = (
        (None, {
            'fields': ('id', 'created', 'name', 
                'persian', 'color', 'examples')
        }),
        ('Relation', {
            'fields': ('tag_set',),
        }),
    )

class TagSetAdmin(admin.ModelAdmin):
    list_display = ('name',
            'number_of_tags', 'number_of_taggers',
            'total_tagged_sentence_count',
            'total_valid_tagged_sentence_count', 'created')
    ordering = ('-created',)
    readonly_fields = ['created', 'id', 'number_of_tags', 'number_of_taggers',
            'total_tagged_sentence_count',
            'total_valid_tagged_sentence_count']

    fieldsets = (
        (None, {
            'fields': ('id', 'created', 
                'name', 'unknown_tag')
        }),
        ('Rank', {
            'fields': ('number_of_tags', 'number_of_taggers',
                'total_tagged_sentence_count',
                'total_valid_tagged_sentence_count'),
        }),
    )

    inlines = [
        TagInLine
    ]

class NormalizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'model_type', 'total_normal_text_count', 
                'total_valid_normal_text_count', 
                'get_model_details', 'last_update', 'created')
    ordering = ('model_type', '-created')
    readonly_fields = ['created', 'id', 'texts', 'last_update',
                'total_normal_text_count', 
                'total_valid_normal_text_count']
    list_filter = ['owner', 'model_type']

    fieldsets = (
        (None, {
            'fields': ('id', 'created', 'last_update', 'name', 
                'owner', 'model_type', 'model_details' )
        }),
        ('Rank', {
            'fields': ('total_normal_text_count', 
                'total_valid_normal_text_count'),
        }),
    )

    # inlines = [
    #     NormalTextInline
    # ]

    def get_model_details(self, obj):
        model_details = ''
        for key, value in obj.model_details.items():
            model_details += f'{key} = {value}<br>'
        return format_html(model_details)
    get_model_details.admin_order_field = 'created' 
    get_model_details.short_description = 'Model Details'

class TextAdmin(admin.ModelAdmin):
    list_display = ('content', 'is_normal_text', 'created')
    search_fields = ['content', 'id']
    ordering = ('-created',)
    list_filter = ['is_normal_text',]
    readonly_fields = ['created', 'id', 'normalizers', 'is_normal_text']
    # exclude = ('normalizers',)

    fieldsets = (
        (None, {
            'fields': ('id', 'created', 'content', 'is_normal_text')
        }),
    )

    inlines = [
        TextSentenceInline,
        NormalTextInline
    ]

class NormalTextAdmin(admin.ModelAdmin):
    list_display = ('content', 'is_valid', 'get_normalizer_name', 
            'get_text_id', 'created')
    search_fields = ['content', 'id']
    list_filter = ['is_valid', 'normalizer__name']
    ordering = ('-created',)
    readonly_fields = ['created', 'id']

    fieldsets = (
        (None, {
            'fields': ('id', 'created',
                'content',)
        }),
        ('Relations', {
            'fields': ('normalizer', 'text'),
        }),
    )

    inlines = [
        TextSentenceInline,
        # NormalTextSentenceInline,
    ]

    def get_normalizer_name(self, obj):
        if not obj.normalizer:
            return None
        return obj.normalizer.name
    get_normalizer_name.admin_order_field = 'created' 
    get_normalizer_name.short_description = 'Normalizer Name'

    def get_text_id(self, obj):
        if not obj.text:
            return None
        return obj.text.id
    get_text_id.admin_order_field = 'created' 
    get_text_id.short_description = 'Text ID'

class TaggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'model_type', 'total_tagged_sentence_count', 
                'total_valid_tagged_sentence_count', 
                'get_model_details', 'last_update', 'created')
    ordering = ('model_type', '-created')
    readonly_fields = ['created', 'id', 'sentences', 'last_update',
                'total_tagged_sentence_count', 'total_valid_tagged_sentence_count']
    list_filter = ['owner', 'model_type']

    fieldsets = (
        (None, {
            'fields': ('id', 'created', 'last_update', 'name',
                    'owner', 'model_type', 'model_details', 'tag_set')
        }),
        ('Rank', {
            'fields': ('total_tagged_sentence_count', 
            'total_valid_tagged_sentence_count'),
        }),
    )

    # inlines = [
    #     TaggedSentenceInline
    # ]

    def get_model_details(self, obj):
        model_details = ''
        for key, value in obj.model_details.items():
            model_details += f'{key} = {value}<br>'
        return format_html(model_details)
    get_model_details.admin_order_field = 'created' 
    get_model_details.short_description = 'Model Details'

class SentenceAdmin(admin.ModelAdmin):
    list_display = ('content', 'get_text_id', 
                    'created',)
    search_fields = ['content', 'id']
    ordering = ('-created', 'text__id')
    readonly_fields = ['created', 'id', 'taggers']
    # exclude = ('taggers',)
    
    fieldsets = (
        (None, {
            'fields': ('created', 'content', 'taggers')
        }),
        ('Relations', {
            'fields': ('text',),
        }),
    )

    inlines = [
        TaggedSentenceInline
    ]

    def get_text_id(self, obj):
        if not obj.text:
            return None
        return obj.text.id
    get_text_id.admin_order_field = 'created' 
    get_text_id.short_description = 'Text ID'

class TaggedSentenceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'get_sentence_content', 
                    'get_tagger_name', 'is_valid', 'created')
    search_fields = ['id']
    list_filter = ['is_valid', 'tagger__name']
    ordering = ('-created',)
    readonly_fields = ['created', 'id', 'sentence', 'get_sentence_content']

    fieldsets = (
        (None, {
            'fields': ('id', 'created', 'get_sentence_content',
             'tokens', 'is_valid')
        }),
        ('Relations', {
            'fields': ('sentence', 'tagger'),
        }),
    )
    
    def get_sentence_content(self, obj):
        if not obj.sentence:
            return None
        return obj.sentence.content
    get_sentence_content.admin_order_field = 'created' 
    get_sentence_content.short_description = 'Sentence Content'

    def get_tagger_name(self, obj):
        if not obj.tagger:
            return None
        return obj.tagger.name
    get_tagger_name.admin_order_field = 'created' 
    get_tagger_name.short_description = 'Tagger Name'

class TranslationCharacterAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'description', 'owner', 'is_valid', 'created')
    list_filter = ('owner', 'is_valid')
    ordering = ('is_valid', 'owner')
    readonly_fields = ['created',]

class RefinementPatternsAdmin(admin.ModelAdmin):
    list_display = ('pattern', 'replacement', 'description', 'order', 'owner', 'is_valid', 'created')
    list_filter = ('owner', 'is_valid')
    ordering = ('order', 'is_valid', 'owner')
    readonly_fields = ['created',]

admin.site.register(Normalizer, NormalizerAdmin)
admin.site.register(Text, TextAdmin)
admin.site.register(NormalText, NormalTextAdmin)
admin.site.register(TagSet, TagSetAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Tagger, TaggerAdmin)
admin.site.register(Sentence, SentenceAdmin)
admin.site.register(TaggedSentence, TaggedSentenceAdmin)
admin.site.register(TranslationCharacter, TranslationCharacterAdmin)
admin.site.register(RefinementPattern, RefinementPatternsAdmin)