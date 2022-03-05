from slugify import slugify,Slugify,UniqueSlugify
print(slugify('Any text', to_lower=True)) # 'any-text'
print(slugify('Any text', to_lower=True)) # 'any-text'

custom_slugify = Slugify(to_lower=True)
print(custom_slugify('Any text'))    # 'any-text'

custom_slugify.separator = '_'
print(custom_slugify('Any text')) # 'any_text'

custom_slugify = UniqueSlugify(to_lower=True)
print(custom_slugify('Any text'))
print(custom_slugify('Any text1'))